# Fixture: world claim B (predicate /^## Теза/)

Paired with world-claim-a.md. Different predicate over the same README bytes.
Same dependency_id, different claim_id and result_value_id. If these ever alias, P0-2
has regressed.

⟦count: /^## Теза/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  "dep": {"path": "README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=REPLAYED.
