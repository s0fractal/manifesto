# Fixture: malformed capsule JSON fails closed (phase 2, P1)

The capsule body is not valid JSON (trailing comma, unquoted token). The parser
must turn this into CAPSULE_INVALID → UNVERIFIED, never a traceback that aborts
verification.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  oops not json,
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID.
