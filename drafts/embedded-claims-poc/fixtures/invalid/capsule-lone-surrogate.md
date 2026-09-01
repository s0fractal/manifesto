# Fixture: lone surrogate is outside the closed profile (phase 2, P1)

`binding.target` contains a lone UTF-16 surrogate (`\ud800`). It parses as a Python
string but is not a Unicode scalar value and cannot encode to UTF-8. The closed
profile must reject it at parse time (CanonicalError) → CAPSULE_INVALID → UNVERIFIED,
not crash later with UnicodeEncodeError.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "binding": {"relation": "measures", "target": "\ud800"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about a lone surrogate.
