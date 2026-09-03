# Fixture: world claim without a dependency pin (P0, rev 3)

The count is correct and the verifier is correctly pinned — but the author pinned
NO dependency. A world-dependent claim that does not commit to the exact bytes it
read cannot earn replay credit: it would go green against any future README.
Fail-closed.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0"
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_MISSING).
