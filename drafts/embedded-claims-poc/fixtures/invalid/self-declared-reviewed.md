# Fixture: author self-declares REVIEWED — must be clamped (P1-4)

Execution and verifier are fine. But the author writes `status: "REVIEWED"` in the
raw capsule, trying to make the renderer show an independent review that never
happened. A raw capsule may only ASSERT; REVIEWED/CONTESTED require a separate,
attributable review record. The tool clamps it back to ASSERTED and says so.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  "binding": {
    "relation": "measures",
    "target": "This identity has been peer-reviewed",
    "status": "REVIEWED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (clamped), with a note that
REVIEWED requires a review record.
