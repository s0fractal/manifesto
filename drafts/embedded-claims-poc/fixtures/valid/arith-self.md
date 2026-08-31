# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:bf940e0a46eb384218e275ff50bdc0731c7a297a16ce13ff07d5a71e82d3f0cf",
  "evaluation_id": "a1d63ffbb96aac8a20465c3d98d6f087617f2e7a9eefb318e425fc7dfc1e8372"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
