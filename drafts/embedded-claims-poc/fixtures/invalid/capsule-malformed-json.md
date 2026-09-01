# Fixture: malformed capsule JSON fails closed (phase 2, P1)

The capsule body is not valid JSON (trailing comma, unquoted token). The parser
must turn this into CAPSULE_INVALID → UNVERIFIED, never a traceback that aborts
verification.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  oops not json,
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID.
