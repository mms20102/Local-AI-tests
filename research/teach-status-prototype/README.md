# Offline teaching-status core prototype

**Not loaded, not registered and not a working gateway adapter.** This branch contains a small pure-Python status core and authored synthetic tests for review. No live gateway/teach file or configuration is changed.

## What is implemented

- Frozen, strictly typed counts from an explicitly supplied final decision; partial application and byte-only application are distinct from omission.
- Fixed English/Arabic status strings and JSON event encoding, without SSE framing or assistant-content modification.
- One emitter per response attempt, with at-most-once local consumption and no global last-status map.
- No store, request-body, log, environment or network access by the core.

The `1024` count cap is a prototype input guard, not a claim about a production note quota.

## Verification status

There are **21 authored unittest methods**. Claude reports **21 passed / 0 skipped** on Windows Python 3.14.5 and again on the project's CPython 3.12.16, using isolated scratch copies of the exact two published blobs. This is Claude's execution report, not independent review or framework validation. This repository session still has no usable shell and did not rerun them.

Reproduction command for an isolated test environment:

```sh
python -m unittest discover -s research/teach-status-prototype -p 'test_*.py' -v
```

Tests use synthetic values only. They do not import LiteLLM/Open WebUI, start services, execute model output, read user stores or contact the laptop. The reported source blobs are core c07df5220f2064163ed5d11d035f6382fc4a9191 and tests ec60cd821b1ec593e9906d67b6cc1a925e1f24b4. No framework/PC operation follows from this core test result.

## Framework seam still to implement and verify

The pinned source supports an explicit server-created request-data carrier rather than client call IDs, object-identity maps or ContextVar-only correlation. A candidate name is `_litellm_teach_status_v1`, carrying bounded validated status primitives:

- [Normal response data propagation](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L3100) to the streaming generator and [iterator callback](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L10028).
- [Internal-key prefix](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/constants.py#L1705), [owned-parameter classification](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/types/utils.py#L4239) and [normal provider-kwargs filtering](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/utils.py#L4547).
- [Leaf-class callback detection](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L3406): the iterator override should be defined on the registered leaf class rather than assumed detected through inheritance.

This is tagged normal-path evidence, not proof about all routes or the installed wheel. The separate fake-upstream fixture must establish carrier survival/exclusion, exact outbound content, concurrent attempt isolation and real error serialization. The core above does not supply that carrier or a stream wrapper, and its Python objects must not be inserted into an engine request.

Future integration must preserve responsibility for closing the model iterator on cancellation and failure, and verify LiteLLM output accounting. Do not add an untested asynchronous wrapper that leaks its source or claims bounded cleanup.

No nonstream display path is implemented. See the [pinned display contract](../teach-status-display-contract.md) and [final-payload plan](../context-preflight/final-payload-evidence-plan.md). This prototype does not change the accepted operating limitations or authorize runtime work.

## Claude's rev18 mapping proposal

Claude's [test/mapping reply](https://github.com/mms20102/Local-AI-tests/blob/b5010ee2ec77f1b3394013150a0cffe1fd8d5a62/research/co-chat.md) maps `omitted_cap` to `note_cap`, `omitted_no_room` to `no_room`, `omitted_uncounted` to `uncounted`, and `invalid`/`byte_only` unchanged; `applied = len(used)`; `relevant = applied + cap + no_room + uncounted`. This is a proposed integration mapping, not an implemented/tested bridge.

Fingerprint `none` or a 12-hex value maps to available, `unknown` to unavailable; `not-read` represents an ineligible request and should bypass the notice rather than become a false "could not verify" warning. The real adapter must use the same final snapshot, not reread the store.

The core requires an explicit `en` or `ar` locale. The original request has no language setting. A latest-message script heuristic was suggested by Claude but is not adopted here; synthetic tests should use an explicit locale, with any eventual configured default/UI locale behavior stated separately.
