# Fixture: lone surrogate is outside the closed profile (phase 2, P1)

`binding.target` contains a lone UTF-16 surrogate (`\ud800`). It parses as a Python
string but is not a Unicode scalar value and cannot encode to UTF-8. The closed
profile must reject it at parse time (CanonicalError) → CAPSULE_INVALID → UNVERIFIED,
not crash later with UnicodeEncodeError.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "binding": {"relation": "measures", "target": "\ud800"}
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about a lone surrogate.
