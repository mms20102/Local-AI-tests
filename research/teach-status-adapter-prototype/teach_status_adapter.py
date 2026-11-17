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

Trust: the notice is only as trustworthy as the carrier. attach() must run on every chat request
and removes any carrier the client sent. As a second line, a carrier is accepted only if it holds
this process's random token, which a client cannot know.

Resources, stated once (see StatusStream):
  - this adapter is given `response`; it does not create it. It closes what it was given: the
    object itself and, when __aiter__() returned a different object, that iterator too;
  - LiteLLM also closes the stream it handed over; closing twice must be harmless for a source,
    and this adapter calls each close() at most once itself;
  - "closed" here means close() was awaited to the end. It does not mean the engine stopped work.

Nothing here reads the store, the request text, logs or the environment. The carrier holds no note
text, no entry ids and no fingerprint. Streaming only: a non-streamed answer gets no notice.
"""
from __future__ import annotations

import asyncio
import secrets
from typing import Any, Optional

from teach_status_core import AttemptNotice, TeachingDecision

CARRIER_KEY = "_litellm_teach_status_v1"
CARRIER_FIELDS = ("store", "relevant", "applied", "omitted_cap", "omitted_no_room",
                  "omitted_uncounted", "invalid", "byte_only")
LOCALES = ("en", "ar")
# A random value made when this module is loaded and kept inside this process. The carrier must
# hold it, so a carrier that did not come from attach() in this process is not accepted even if
# attach() was somehow not run for a request. It is not a secret worth protecting beyond that.
_PROCESS_TOKEN = secrets.token_hex(16)
CLOSE_TIMEOUT_SECONDS = 5.0          # how long one close() is awaited before cleanup is called uncertain
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
    carrier["token"] = _PROCESS_TOKEN
    return carrier


def from_carrier(carrier: Any) -> Optional[tuple[TeachingDecision, str]]:
    """Validate a carrier read back from request data. None for anything not exactly well formed."""
    try:
        if type(carrier) is not dict or set(carrier) != set(CARRIER_FIELDS) | {"locale", "token"}:
            return None
        token = carrier["token"]
        if type(token) is not str or not secrets.compare_digest(token, _PROCESS_TOKEN):
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

    It is an object, not an async generator, on purpose: closing it before the first item is
    pulled still closes the source (an unstarted generator would skip its own cleanup).

    cleanup is one of:
      "open"       nothing closed yet;
      "closing"    close has started and has not finished;
      "done"       every close() this adapter owed was awaited to the end without error;
      "failed"     a close() raised; the error is kept in close_errors (type names only);
      "uncertain"  a close() did not finish within CLOSE_TIMEOUT_SECONDS and was left behind after
                   being asked to cancel, or the cleanup task itself was cancelled from outside.
                   The resource may still be open.

    Failure and cancellation:
      - an error from the source is re-raised unchanged after cleanup has been attempted;
      - errors raised by close() never replace it and are never raised from here;
      - the cleanup runs in its own task, shielded. If the caller is cancelled while waiting for
        it, the cancellation is raised (it is never swallowed), the source error, if any, stays
        attached as its context, and the cleanup task carries on. A later aclose() waits for that
        same task, so cleanup is not started twice and is not abandoned half way.
      - a CancelledError raised BY a close() is a failed close ("failed", recorded by name). It
        is not treated as cancellation of anyone and does not replace the source error.
    Time: this adapter's own wait for each close() ends at the deadline even if the close code
    resists cancellation; that close is then left behind unfinished and the state is "uncertain".
    Nothing here can force arbitrary close code to stop.

    Who must close: see aclose(). This object cannot notice a consumer that stops between pulls.
    """

    def __init__(self, source: Any, notice: Optional[AttemptNotice]):
        self._source = source
        self._iterator = None
        self._notice = notice
        self._finished = False
        self._close_task: Optional[asyncio.Future] = None
        self.cleanup = "open"
        self.close_errors: list[str] = []
        self._timed_out = False

    def __aiter__(self) -> "StatusStream":
        return self

    async def __anext__(self) -> Any:
        if self._finished:
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
        except BaseException:               # normal end, upstream failure, or cancellation
            self._finished = True
            await self.aclose()             # a cancellation here keeps the error above as its context
            raise

    async def _close_one(self, target: Any) -> None:
        close = getattr(target, "aclose", None)
        if close is None:
            return
        try:
            inner = asyncio.ensure_future(close())
        except Exception as error:          # close() itself raised before returning an awaitable
            self.close_errors.append(type(error).__name__)
            return
        # asyncio.wait, not wait_for: wait_for keeps waiting while a close handles its cancellation,
        # so close code that resists cancellation could hold this up indefinitely. Here the wait
        # really ends at the deadline; the unfinished close is asked to cancel and is left behind.
        done, _ = await asyncio.wait({inner}, timeout=CLOSE_TIMEOUT_SECONDS)
        if not done:
            self._timed_out = True
            inner.add_done_callback(_discard_result)
            inner.cancel()
            return
        if inner.cancelled():
            # The close raised CancelledError ITSELF. Nobody cancelled this cleanup, so it is a
            # failed close, not a cancellation to propagate: record it and go on to the next resource.
            self.close_errors.append("CancelledError")
        elif inner.exception() is not None: # a close error must not replace the primary outcome
            self.close_errors.append(type(inner.exception()).__name__)

    async def _close_all(self) -> None:
        targets = [self._iterator] if self._iterator is not None else []
        if self._source is not self._iterator:
            targets.append(self._source)
        try:
            for target in targets:
                await self._close_one(target)
        except asyncio.CancelledError:      # this cleanup task was cancelled from outside
            self.cleanup = "uncertain"
            raise
        self.cleanup = "uncertain" if self._timed_out else ("failed" if self.close_errors else "done")

    async def aclose(self) -> None:
        """Close what this stream was given. Safe to call more than once and from several tasks.

        THE CALLER MUST CALL THIS. An object iterator is not told when its consumer stops between
        two pulls, for example when the consuming task is cancelled while handling an item. LiteLLM's
        proxy does call it, in a `finally` around its loop over the hook's stream. Any other
        consumer has to do the same; nothing here closes the source behind the consumer's back.
        """
        self._finished = True
        if self._close_task is None:
            self.cleanup = "closing"
            self._close_task = asyncio.ensure_future(self._close_all())
        if self._close_task.done():
            return
        try:
            await asyncio.shield(self._close_task)      # cancellation of the caller does not stop cleanup
        except asyncio.CancelledError:
            if self._close_task.cancelled():            # the cleanup task was cancelled, not this caller
                self.cleanup = "uncertain"
                return
            raise


def _discard_result(task: "asyncio.Future") -> None:
    """Read an abandoned close's outcome so the event loop does not report it as unretrieved."""
    if not task.cancelled():
        task.exception()


def status_stream(response: Any, request_data: Any) -> StatusStream:
    """What an `async_post_call_streaming_iterator_hook` override returns.

    Define the override on the REGISTERED LEAF CLASS (LiteLLM looks in that class's own
    attributes) as a plain method:

        def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data):
            return status_stream(response, request_data)
    """
    return StatusStream(response, notice_for(request_data))


stream_with_status = status_stream        # earlier name, kept for the published tests
