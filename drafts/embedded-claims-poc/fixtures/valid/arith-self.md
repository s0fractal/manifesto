# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:7a678c25452c23f91f6193b68e78cca09faea917b0b2b433cd36ea0878a95c90",
  "evaluation_id": "dfa9ea0809c659092da7b3191300c0fe9d2956792e7587cc113279441b1596a3"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
