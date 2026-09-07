# Fixture: world claim A (predicate /^## Теза [0-9]+:/)

Paired with world-claim-b.md. Same file, same byte digest (dependency_id), but a
DIFFERENT predicate. Their claim_id and result_value_id must differ; only the
dependency_id is shared. This is the P0-2 fix: the input digest is not the claim
address.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  "dep": {"path": "README.md", "sha256": "3a6edc622b3dbca9e71885eed8b51a52d4aedd76f1db9f740ab28c4a141b5e52"}
}
```

Expected: execution=REPLAYED.
