# Fixture: malformed capsule JSON fails closed (phase 2, P1)

The capsule body is not valid JSON (trailing comma, unquoted token). The parser
must turn this into CAPSULE_INVALID → UNVERIFIED, never a traceback that aborts
verification.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  oops not json,
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID.
