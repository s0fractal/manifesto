# Fixture: world claim A (predicate /^## Теза [0-9]+:/)

Paired with world-claim-b.md. Same file, same byte digest (dependency_id), but a
DIFFERENT predicate. Their claim_id and result_value_id must differ; only the
dependency_id is shared. This is the P0-2 fix: the input digest is not the claim
address.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  "dep": {"path": "README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=REPLAYED.
