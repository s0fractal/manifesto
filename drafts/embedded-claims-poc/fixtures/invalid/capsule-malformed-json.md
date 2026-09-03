# Fixture: malformed capsule JSON fails closed (phase 2, P1)

The capsule body is not valid JSON (trailing comma, unquoted token). The parser
must turn this into CAPSULE_INVALID → UNVERIFIED, never a traceback that aborts
verification.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  oops not json,
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID.
