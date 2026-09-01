# Fixture: malformed capsule JSON fails closed (phase 2, P1)

The capsule body is not valid JSON (trailing comma, unquoted token). The parser
must turn this into CAPSULE_INVALID → UNVERIFIED, never a traceback that aborts
verification.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  oops not json,
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID.
