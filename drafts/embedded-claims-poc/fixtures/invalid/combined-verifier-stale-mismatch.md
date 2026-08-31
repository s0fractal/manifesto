# Fixture: three faults at once — nothing hidden by if-order (P1-4)

A claim can be wrong in several ways simultaneously: wrong verifier pin, stale
dependency, AND a false count. The report must surface ALL of them as independent
facts, not collapse to whichever `if` fired first. The summary is UNVERIFIED
(fail-closed, highest severity), but the facts list keeps every fault visible.

⟦count: /^## Теза [0-9]+:/ in README.md = 99⟧

```json capsule
{
  "verifier": "settle-gate://sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
  "dep": {"path": "README.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
```

Expected: execution=UNVERIFIED; execution_facts contains VERIFIER_MISMATCH,
DEPENDENCY_STALE, and RESULT_MISMATCH.
