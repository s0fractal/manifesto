# Fixture: world claim A (predicate /^## Теза [0-9]+:/)

Paired with world-claim-b.md. Same file, same byte digest (dependency_id), but a
DIFFERENT predicate. Their claim_id and result_value_id must differ; only the
dependency_id is shared. This is the P0-2 fix: the input digest is not the claim
address.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:bf940e0a46eb384218e275ff50bdc0731c7a297a16ce13ff07d5a71e82d3f0cf",
  "dep": {"path": "README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=REPLAYED.
