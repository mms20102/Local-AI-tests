# Branch comparison

Checked on 2026-11-17 from the repository checkout.

| Ref | Reachable state | Decision |
|---|---|---|
| `main` / `origin/main` | Single checked-out repository state containing the current research checkpoint | Preserve |

No other local or remote branch was present in the checkout. The README links to
a historical Claude branch, but it is not a reachable ref in this clone and
must not be merged or deleted by inference. No unneeded branch was deleted.

## Integration rule

Future worker or review branches must be compared by commit and evidence
provenance before selective integration. Do not merge a branch merely because
its pass count is higher, and do not rewrite or reset the current evidence
history.
