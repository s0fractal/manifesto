# Fixture: wrong verifier identity — no replay credit (D3, P0-1)

The arithmetic is true, but the capsule pins a verifier that is NOT the actual
evaluator closure. A result is only as trustworthy as the named verifier: a
mismatched verifier identity earns no REPLAY credit, even when the computation is
correct.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
}
```

Expected: execution=UNVERIFIED (facts include VERIFIER_MISMATCH).
