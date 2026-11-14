# Teaching-status display contract — draft

2026-11-14. **Pinned-source design; no UI/gateway code installed or changed.** Claude reports Open WebUI 0.13.3 / LiteLLM 1.108.5, a plain provider connection, Functions disabled and no response hook. This document is not a verified adapter or runtime clearance.

## User-visible outcome

If saved notes are left out, Mohamed receives the answer and a short truthful notice attached to that answer. Keep model-produced code, JSON and text unchanged. Do not ask the model to generate the notice or make another model request.

Admission failures and successful answers with omitted notes are different paths. The reviewed `ProxyException` reason types classify refusals; they do not themselves display teaching status on successful answers.

## Evidence contract

Use the final teaching decision already captured for the request. Entries, fingerprint and diagnostics must describe one immutable store snapshot; do not reread the store or scrape “the latest” log line for display.

Correlate evidence to the actual message/request and attempt that produced the answer. The eventual adapter must show how those identifiers survive its installed request/response path; no global last-status variable. A retry or parallel chat must not borrow another attempt’s status.

Carry only bounded, typed status/counts through the trusted adapter. No note text, credentials, file paths or raw exception strings. Suggested conceptual fields, not an approved wire format:

- store availability: available / unavailable / unknown;
- relevant valid-note count, applied count, and omission counts by cap / no room / uncounted;
- invalid-entry count separately;
- count evidence: successfully counted / byte fallback / unavailable;
- request/message/attempt correlation and source-evidence reference, retained locally as needed.

For a known relevant set, applied + cap omissions + no-room omissions + uncounted omissions should account for it without double counting. `byte_only` is a subset of applied notes, not an additional note count. Unreadable-store/unknown evidence must not become “no relevant notes” merely because numeric fields are zero.

## Plain display mapping

Use the UI’s locale, with fixed strings. These are proposed texts, not deployed messages.

| Actual final outcome | English | Arabic |
|---|---|---|
| Some relevant notes omitted for cap/room | Some saved notes weren’t used for this answer. | بعض الملاحظات المحفوظة لم تُستخدم في هذه الإجابة. |
| Notes omitted because counting was unavailable/failed | Saved notes couldn’t be checked and were left out of this answer. | تعذّر التحقق من الملاحظات المحفوظة، فلم تُستخدم في هذه الإجابة. |
| Store unavailable | Saved notes weren’t available for this answer. | تعذّر الوصول إلى الملاحظات المحفوظة لهذه الإجابة. |
| Invalid entries skipped | Some saved notes couldn’t be read. | تعذّر قراءة بعض الملاحظات المحفوظة. |
| No relevant notes, or all applied normally | No omission notice is needed. | لا يلزم إشعار باستبعاد ملاحظات. |

Choose one concise message per answer; do not emit one per token or per note. Partial application must not say every note was omitted. `kept-byte-rule-only` means notes were applied, so it must not be rendered as omission or verified token admission. Claude now relays Mohamed retaining absent-counter byte-only notes as a stated limitation; any fallback-specific display should describe applied notes honestly. That policy report and UI labeling do not prove a native-token bound.

## Pinned streaming candidate

The source review identified a provider-stream event path **separate from enabling Functions**. The Function-event route remains unavailable under the reported flags; that does not rule out the ordinary provider-stream path below.

| Stage | Tagged-source evidence |
|---|---|
| Provider SSE | [Open WebUI router](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/backend/open_webui/routers/openai.py#L1595) forwards successful event streams. |
| Event dispatch | [Middleware](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/backend/open_webui/utils/middleware.py#L4971) parses provider JSON and forwards its `event` outside the filter branch, when `request.state.direct` is false. A choice-free status need not become assistant content. |
| Message association | [Socket emitter](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/backend/open_webui/socket/main.py#L1633) supplies chat/message context. [Chat handling](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/src/lib/components/chat/Chat.svelte#L1630) records status history. |
| Display gate | [ResponseMessage](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/src/lib/components/chat/Messages/ResponseMessage.svelte#L740) renders status history if the model's `status_updates` capability is enabled, default true. Actual runtime capability/path/visibility remain unverified. |
| Gateway response hook | [LiteLLM CustomLogger](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/integrations/custom_logger.py#L526) exposes a response-iterator hook with request data; [proxy dispatch](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L10040) invokes it. |

Pinned sources: Open WebUI v0.13.3 → `b0e6098e940942281d9c83f3529ea117287a3a22`; LiteLLM v1.108.5 → `2a61f2114d45016bae77930903e65172cd8e762c`. These source identities are not installed-package verification.

A minimal candidate is a request-scoped iterator hook emitting **one fixed allowlisted status event** from the final pre-call evidence, then forwarding model chunks unchanged. Do not pass arbitrary provider-controlled event types through this adapter. The carrier from pre-call evidence to response iterator still needs proof of correct association and exclusion from the upstream engine body.

**Framing matters:** the [proxy formatter](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L9797) interpolates a bare dictionary instead of JSON-encoding it. For the ordinary structured stream, a candidate should yield a serialized JSON string without the `data:` prefix, subject to verifying the [actual iterator serialization path](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L10154). Mixed string/model chunks also need output-accounting/cancellation checks; no live compatibility is claimed.

[Handwritten wire fixture](fixtures/teach-status-stream.sse): one completed visible status, followed by model content exactly `{"ok":true}`, stop and DONE. The [fixture-only check](experiments/2026-11-14-teach-status-fixture-check.json) checks its framing/values, not a vendor pipeline. `done:true` controls status presentation, not delivery acknowledgment.

## Nonstream and diagnostic limits

No corresponding provider-event dispatch was found in the [nonstream handler](https://github.com/open-webui/open-webui/blob/b0e6098e940942281d9c83f3529ea117287a3a22/backend/open_webui/utils/middleware.py#L4060). A custom JSON property or header alone does not establish display. A nonstream adapter or explicit streaming-only disclosure scope needs a separate reviewed decision; do not silently assume both paths work.

A manually consulted status command/page is a diagnostic candidate, not demonstrated automatic per-answer disclosure. Do not scrape global latest logs for the notice. No extra endpoint, Function enablement, package update or UI configuration change is selected by this document.

## Acceptance before claiming disclosure works

Use handwritten synthetic evidence and a fake/non-generating response path first:

1. Nonstream and streaming answers preserve model content exactly; one final notice corresponds to the final notes actually sent/omitted.
2. Cap, room, uncounted, store-unavailable, invalid-entry, partial and empty-store cases display the right meaning.
3. Two chats, retry, cancellation and a mid-request store replacement retain correct request/snapshot association.
4. Missing emitter/status transport fails without claiming a notice was shown or corrupting the answer; no indefinite UI loading indicator.
5. Real browser observation confirms visibility on the installed version. Logs, headers, a backend event or `done=true` alone are insufficient.
6. No note text/secret/exception detail is exposed and no model call or candidate execution is added.

The request-scoped adapter, pinned synthetic pipeline test and real browser observation remain to be prepared. Loading and other profile/counter/margin/isolation gates remain unchanged.
