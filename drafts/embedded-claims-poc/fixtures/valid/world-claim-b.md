# Fixture: world claim B (predicate /^## Теза/)

Paired with world-claim-a.md. Different predicate over the same README bytes.
Same dependency_id, different claim_id and result_value_id. If these ever alias, P0-2
has regressed.

⟦count: /^## Теза/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "dep": {"path": "README.md", "sha256": "f1bb9ae17192e42624d527c7c37b472c5bf4720631f5036ebd35f81860d86cc7"}
}
```

Expected: execution=REPLAYED.
