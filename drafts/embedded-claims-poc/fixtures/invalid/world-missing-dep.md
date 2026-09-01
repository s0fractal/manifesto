# Fixture: world claim without a dependency pin (P0, rev 3)

The count is correct and the verifier is correctly pinned — but the author pinned
NO dependency. A world-dependent claim that does not commit to the exact bytes it
read cannot earn replay credit: it would go green against any future README.
Fail-closed.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e"
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_MISSING).
