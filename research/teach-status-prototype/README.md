# Offline teaching-status core prototype

**Not loaded, not registered and not a working gateway adapter.** This branch contains a small pure-Python status core and authored synthetic tests for review. No live gateway/teach file or configuration is changed.

## What is implemented

- Frozen, strictly typed counts from an explicitly supplied final decision; partial application and byte-only application are distinct from omission.
- Fixed English/Arabic status strings and JSON event encoding, without SSE framing or assistant-content modification.
- One emitter per response attempt, with at-most-once local consumption and no global last-status map.
- No store, request-body, log, environment or network access by the core.

The `1024` count cap is a prototype input guard, not a claim about a production note quota.

## Verification status

There are **21 authored unittest methods; they have not been executed in this session**. The cloud shell returned "No usable execution environment is available." Source review and JavaScript checks of a separate handwritten SSE fixture do not validate these Python files.

A test-capable isolated cloud worker can run:

```sh
python -m unittest discover -s research/teach-status-prototype -p 'test_*.py' -v
```

Tests use synthetic values only. They do not import LiteLLM/Open WebUI, start services, execute model output, read user stores or contact the laptop. Do not replace the unexecuted status with a pass until the exact published files are tested.

## Framework seam still to implement and verify

The pinned source supports an explicit server-created request-data carrier rather than client call IDs, object-identity maps or ContextVar-only correlation. A candidate name is `_litellm_teach_status_v1`, carrying bounded validated status primitives:

- [Normal response data propagation](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L3100) to the streaming generator and [iterator callback](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L10028).
- [Internal-key prefix](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/constants.py#L1705), [owned-parameter classification](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/types/utils.py#L4239) and [normal provider-kwargs filtering](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/utils.py#L4547).
- [Leaf-class callback detection](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L3406): the iterator override should be defined on the registered leaf class rather than assumed detected through inheritance.

This is tagged normal-path evidence, not proof about all routes or the installed wheel. The separate fake-upstream fixture must establish carrier survival/exclusion, exact outbound content, concurrent attempt isolation and real error serialization. The core above does not supply that carrier or a stream wrapper, and its Python objects must not be inserted into an engine request.

Future integration must preserve responsibility for closing the model iterator on cancellation and failure, and verify LiteLLM output accounting. Do not add an untested asynchronous wrapper that leaks its source or claims bounded cleanup.

No nonstream display path is implemented. See the [pinned display contract](../teach-status-display-contract.md) and [final-payload plan](../context-preflight/final-payload-evidence-plan.md). This prototype does not change the accepted operating limitations or authorize runtime work.
