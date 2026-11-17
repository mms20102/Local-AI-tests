"""Fixture-only candidate wiring: teach revision 18 hook + status adapter on ONE registered leaf class.

This file exists only in the scratch test. It is the piece that would have to be written for a real
integration; nothing here is loaded by the laptop's gateway.
"""
from __future__ import annotations

import os

import teach_status_adapter as adapter
from teach_hook import TeachHook, inject_with_status, safe_log

LOCALE = os.environ.get("SCRATCH_STATUS_LOCALE", "en")
STREAMS: list = []          # fixture-only: lets the test read each stream's cleanup state
DECISIONS: list = []        # fixture-only: (used, fingerprint, status) per pre-call


class TeachWithStatus(TeachHook):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if call_type not in ("completion", "acompletion"):
            return data
        changed, used, fingerprint, status = inject_with_status(
            data, self.limits, count_tokens=getattr(self, "count_tokens", None))
        safe_log(used, fingerprint, status)
        DECISIONS.append((list(used), fingerprint, dict(status)))
        return adapter.attach(changed, adapter.decision_from_hook(used, fingerprint, status), LOCALE)

    def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data):
        stream = adapter.status_stream(response, request_data)
        STREAMS.append(stream)
        return stream


teach = TeachWithStatus()
