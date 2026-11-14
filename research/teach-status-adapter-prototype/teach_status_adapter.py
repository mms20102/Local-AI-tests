"""Offline prototype: carry the teach hook's final decision to the response stream and show one
fixed status line. NOT loaded, NOT registered, NOT part of the running gateway.

It connects three things that already exist:
  teach revision 18      inject_with_status(...) -> (data, used, fingerprint, status)
  teach_status_core      TeachingDecision / encode_status / AttemptNotice   (tested core, unchanged)
  LiteLLM 1.108.5        async_pre_call_hook and async_post_call_streaming_iterator_hook

Flow, per chat request:
  1. the pre-call hook has the final (used, fingerprint, status) from ONE store snapshot;
  2. decision_from_hook() turns it into a TeachingDecision, or None when no notice applies;
  3. attach() puts a small carrier of plain integers and two fixed words into the request data
     under CARRIER_KEY. The key starts with LiteLLM's internal prefix, which LiteLLM filters out of
     what it sends to the engine. That filtering is LiteLLM's behaviour, NOT proved here end to end;
  4. the iterator hook reads the carrier back, validates it again, and StatusStream yields one
     JSON status event followed by every model chunk, untouched.

Nothing here reads the store, the request text, logs or the environment. The carrier holds no note
text, no entry ids and no fingerprint. Streaming only: a non-streamed answer gets no notice.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from teach_status_core import AttemptNotice, TeachingDecision

CARRIER_KEY = "_litellm_teach_status_v1"
CARRIER_FIELDS = ("store", "relevant", "applied", "omitted_cap", "omitted_no_room",
                  "omitted_uncounted", "invalid", "byte_only")
LOCALES = ("en", "ar")
_HEX = set("0123456789abcdef")


def decision_from_hook(used: Any, fingerprint: Any, status: Any) -> Optional[TeachingDecision]:
    """The hook's final result as a TeachingDecision. None means: say nothing.

    fingerprint "not-read": the request was not an eligible plain-text chat. No notice; this is
        not a store problem.
    fingerprint "none" or 12 lowercase hex digits: the store was read (or there is none yet).
    fingerprint "unknown": the store could not be read.
    Anything else, or counts that do not add up, gives the "unknown" decision: the adapter never
    guesses, and never raises into the request.
    """
    if fingerprint == "not-read":
        return None
    if fingerprint == "unknown":
        return TeachingDecision(store="unavailable")
    readable = fingerprint == "none" or (type(fingerprint) is str and len(fingerprint) == 12
                                         and set(fingerprint) <= _HEX)
    if not readable or not isinstance(used, (list, tuple)) or not isinstance(status, dict):
        return TeachingDecision(store="unknown")
    try:
        applied = len(used)
        cap, room, uncounted = status["note_cap"], status["no_room"], status["uncounted"]
        return TeachingDecision(
            store="available", applied=applied, omitted_cap=cap, omitted_no_room=room,
            omitted_uncounted=uncounted, invalid=status["invalid"], byte_only=status["byte_only"],
            relevant=applied + cap + room + uncounted)
    except Exception:
        return TeachingDecision(store="unknown")


def to_carrier(decision: TeachingDecision, locale: str) -> dict:
    """Plain values only: one fixed word, integers (or None), and the locale word."""
    if type(decision) is not TeachingDecision or locale not in LOCALES:
        raise ValueError("Invalid teaching status carrier input")
    carrier = {name: getattr(decision, name) for name in CARRIER_FIELDS}
    carrier["locale"] = locale
    return carrier


def from_carrier(carrier: Any) -> Optional[tuple[TeachingDecision, str]]:
    """Validate a carrier read back from request data. None for anything not exactly well formed."""
    try:
        if type(carrier) is not dict or set(carrier) != set(CARRIER_FIELDS) | {"locale"}:
            return None
        locale = carrier["locale"]
        if type(locale) is not str or locale not in LOCALES:
            return None
        return TeachingDecision(**{name: carrier[name] for name in CARRIER_FIELDS}), locale
    except Exception:
        return None


def attach(data: dict, decision: Optional[TeachingDecision], locale: str) -> dict:
    """Return request data carrying the decision, or `data` itself when there is nothing to show.

    The input dict is not modified. A carrier already present under the key is never trusted: it
    is removed (a client cannot plant one), and replaced only by this call's own decision.
    """
    clean = data
    if CARRIER_KEY in data:
        clean = {key: value for key, value in data.items() if key != CARRIER_KEY}
    if decision is None or decision.notice_kind() is None:
        return clean
    try:
        carrier = to_carrier(decision, locale)
    except Exception:
        return clean
    result = dict(clean)
    result[CARRIER_KEY] = carrier
    return result


def notice_for(request_data: Any) -> Optional[AttemptNotice]:
    """A fresh at-most-once notice for ONE response attempt, or None. Never raises."""
    try:
        parsed = from_carrier(request_data.get(CARRIER_KEY)) if isinstance(request_data, dict) else None
        if parsed is None:
            return None
        return AttemptNotice(parsed[0], parsed[1])
    except Exception:
        return None


class StatusStream:
    """Async iterator: the status event (at most once, as JSON text with no `data:` prefix), then
    every item of `source` in order and unchanged.

    It owns the source: when this stream is closed, cancelled or fails, the source's own aclose()
    is called once. A status that was yielded is not an acknowledgement that anyone displayed it.
    """

    def __init__(self, source: Any, notice: Optional[AttemptNotice]):
        self._source = source
        self._iterator = None
        self._notice = notice
        self._closed = False

    def __aiter__(self) -> "StatusStream":
        return self

    async def __anext__(self) -> Any:
        if self._closed:
            raise StopAsyncIteration
        if self._notice is not None:
            notice, self._notice = self._notice, None
            event = notice.take()
            if event is not None:
                return event
        try:
            if self._iterator is None:
                self._iterator = self._source.__aiter__()
            return await self._iterator.__anext__()
        except BaseException:               # includes StopAsyncIteration, cancellation and failures
            await self.aclose()
            raise

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        for target in (self._iterator, self._source):
            close = getattr(target, "aclose", None)
            if close is not None:
                try:
                    await close()
                except Exception:
                    pass
                return


async def stream_with_status(response: Any, request_data: Any) -> AsyncIterator[Any]:
    """Body for an `async_post_call_streaming_iterator_hook` override.

    Define the override on the REGISTERED LEAF CLASS (LiteLLM looks in that class's own
    attributes), and have it do:   async for item in stream_with_status(response, request_data): yield item
    """
    stream = StatusStream(response, notice_for(request_data))
    try:
        async for item in stream:
            yield item
    finally:
        await stream.aclose()
