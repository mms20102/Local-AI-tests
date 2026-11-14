"""Offline teaching-status core. Not registered with LiteLLM or Open WebUI.

The caller must create one emitter per response attempt from the final teaching
decision. This module does not read stores, request bodies, logs or environment
variables. Framework association, upstream stripping and browser visibility are
separate integration tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from threading import Lock
from typing import Literal

_MAX_COUNT = 1024
StoreState = Literal["available", "unavailable", "unknown"]
Locale = Literal["en", "ar"]

_TEXT = {
    "omitted": {
        "en": "Some saved notes were not used for this answer.",
        "ar": "بعض الملاحظات المحفوظة لم تُستخدم في هذه الإجابة.",
    },
    "uncounted": {
        "en": "Some saved notes could not be checked and were not used for this answer.",
        "ar": "تعذّر التحقق من بعض الملاحظات المحفوظة، فلم تُستخدم في هذه الإجابة.",
    },
    "unavailable": {
        "en": "Saved notes were not available for this answer.",
        "ar": "تعذّر الوصول إلى الملاحظات المحفوظة لهذه الإجابة.",
    },
    "invalid": {
        "en": "Some saved notes could not be read.",
        "ar": "تعذّر قراءة بعض الملاحظات المحفوظة.",
    },
    "unknown": {
        "en": "Whether saved notes were used could not be verified for this answer.",
        "ar": "تعذّر التحقق من استخدام الملاحظات المحفوظة في هذه الإجابة.",
    },
}


def _count(name: str, value: object) -> None:
    # bool is deliberately excluded. Never stringify untrusted values.
    if type(value) is not int or not 0 <= value <= _MAX_COUNT:
        raise ValueError("Invalid teaching count: " + name)


@dataclass(frozen=True, slots=True)
class TeachingDecision:
    """Final same-snapshot counts, supplied explicitly by a trusted adapter.

    byte_only counts applied notes; it is a subset of applied, not an omission.
    relevant=None means unknown and must not be silently interpreted as zero.
    """

    store: StoreState
    relevant: int | None = None
    applied: int = 0
    omitted_cap: int = 0
    omitted_no_room: int = 0
    omitted_uncounted: int = 0
    invalid: int = 0
    byte_only: int = 0

    def __post_init__(self) -> None:
        if type(self.store) is not str or self.store not in (
            "available", "unavailable", "unknown"
        ):
            raise ValueError("Invalid teaching store state")
        for name in (
            "applied", "omitted_cap", "omitted_no_room",
            "omitted_uncounted", "invalid", "byte_only"
        ):
            _count(name, getattr(self, name))
        if self.relevant is not None:
            _count("relevant", self.relevant)
        total = (
            self.applied + self.omitted_cap
            + self.omitted_no_room + self.omitted_uncounted
        )
        if total > _MAX_COUNT:
            raise ValueError("Teaching total exceeds limit")
        if self.byte_only > self.applied:
            raise ValueError("Byte-only count exceeds applied count")
        if self.store != "available":
            if self.relevant is not None or total or self.byte_only:
                raise ValueError("Unavailable teaching cannot have known decisions")
        elif self.relevant is not None and self.relevant != total:
            raise ValueError("Teaching counts do not account for relevant notes")

    def notice_kind(self) -> str | None:
        if self.store == "unavailable":
            return "unavailable"
        if self.store == "unknown" or self.relevant is None:
            return "unknown"
        if self.omitted_uncounted:
            return "uncounted"
        if self.omitted_cap or self.omitted_no_room:
            return "omitted"
        if self.invalid:
            return "invalid"
        return None


def encode_status(decision: TeachingDecision, locale: Locale = "en") -> str | None:
    """Return JSON text, without SSE framing; never return model answer text.

    Only fixed local strings enter the event. Counts, note IDs/text, exception
    text, paths, request IDs and fingerprints are deliberately not serialized.
    Invalid input raises a constant-message validation error; a framework adapter
    must handle that separately without claiming a notice was displayed.
    """
    if type(decision) is not TeachingDecision:
        raise ValueError("Invalid teaching decision")
    if type(locale) is not str or locale not in ("en", "ar"):
        raise ValueError("Unsupported teaching notice locale")
    kind = decision.notice_kind()
    if kind is None:
        return None
    return json.dumps(
        {"event": {"type": "status", "data": {
            "description": _TEXT[kind][locale], "done": True, "hidden": False
        }}},
        ensure_ascii=False, separators=(",", ":"),
    )


class AttemptNotice:
    """One immutable decision, one locale, at most one emitted event.

    This is explicit local state, not a global last-status registry or an engine
    request field. A retry needs a NEW instance. The caller/framework retains
    responsibility for associating it with the right response iterator.
    """

    def __init__(self, decision: TeachingDecision, locale: Locale = "en") -> None:
        self._event = encode_status(decision, locale)
        self._taken = False
        self._lock = Lock()

    def take(self) -> str | None:
        with self._lock:
            if self._taken:
                return None
            self._taken = True
            return self._event
