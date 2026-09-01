# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "evaluation_id": "47fde598e45d1b0b5aad75dd24207b06236c65c99c8dcb387531751e8ed4bbfa"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
