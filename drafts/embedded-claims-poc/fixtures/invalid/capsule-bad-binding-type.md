# Fixture: wrong-shaped binding value fails closed (phase 2, P1)

`binding.relation` is an array, not a string. A membership test against the allowed
set would raise TypeError on an unhashable value; the schema must type-check first
and report a typed error, ending in CAPSULE_INVALID → UNVERIFIED.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "binding": {"relation": [], "target": "x"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about binding.relation.
