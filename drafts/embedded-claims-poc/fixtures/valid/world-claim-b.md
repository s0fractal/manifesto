# Fixture: world claim B (predicate /^## Теза/)

Paired with world-claim-a.md. Different predicate over the same README bytes.
Same dependency_id, different claim_id and result_value_id. If these ever alias, P0-2
has regressed.

⟦count: /^## Теза/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  "dep": {"path": "README.md", "sha256": "3a6edc622b3dbca9e71885eed8b51a52d4aedd76f1db9f740ab28c4a141b5e52"}
}
```

Expected: execution=REPLAYED.
