# Fixture: world claim B (predicate /^## Теза/)

Paired with world-claim-a.md. Different predicate over the same README bytes.
Same dependency_id, different claim_id and result_value_id. If these ever alias, P0-2
has regressed.

⟦count: /^## Теза/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "dep": {"path": "README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=REPLAYED.
