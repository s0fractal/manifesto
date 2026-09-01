# Fixture: wrong-shaped binding value fails closed (phase 2, P1)

`binding.relation` is an array, not a string. A membership test against the allowed
set would raise TypeError on an unhashable value; the schema must type-check first
and report a typed error, ending in CAPSULE_INVALID → UNVERIFIED.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "binding": {"relation": [], "target": "x"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about binding.relation.
