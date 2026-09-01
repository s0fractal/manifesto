# Fixture: wrong-shaped binding value fails closed (phase 2, P1)

`binding.relation` is an array, not a string. A membership test against the allowed
set would raise TypeError on an unhashable value; the schema must type-check first
and report a typed error, ending in CAPSULE_INVALID → UNVERIFIED.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "binding": {"relation": [], "target": "x"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about binding.relation.
