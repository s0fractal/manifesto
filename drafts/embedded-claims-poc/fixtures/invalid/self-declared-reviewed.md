# Fixture: author self-declares REVIEWED — must be clamped (P1-4)

Execution and verifier are fine. But the author writes `status: "REVIEWED"` in the
raw capsule, trying to make the renderer show an independent review that never
happened. A raw capsule may only ASSERT; REVIEWED/CONTESTED require a separate,
attributable review record. The tool clamps it back to ASSERTED and says so.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "binding": {
    "relation": "measures",
    "target": "This identity has been peer-reviewed",
    "status": "REVIEWED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (clamped), with a note that
REVIEWED requires a review record.
