# Fixture: world claim A (predicate /^## Теза [0-9]+:/)

Paired with world-claim-b.md. Same file, same byte digest (dependency_id), but a
DIFFERENT predicate. Their claim_id and result_value_id must differ; only the
dependency_id is shared. This is the P0-2 fix: the input digest is not the claim
address.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "dep": {"path": "README.md", "sha256": "f1bb9ae17192e42624d527c7c37b472c5bf4720631f5036ebd35f81860d86cc7"}
}
```

Expected: execution=REPLAYED.
