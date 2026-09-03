# Fixture: wrong-shaped binding value fails closed (phase 2, P1)

`binding.relation` is an array, not a string. A membership test against the allowed
set would raise TypeError on an unhashable value; the schema must type-check first
and report a typed error, ending in CAPSULE_INVALID → UNVERIFIED.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "binding": {"relation": [], "target": "x"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about binding.relation.
