# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:b4f33ca1ba18b005de4eeba34a550cd65e4481e54a3ce5885831cd6d239636cd",
  "evaluation_id": "7ffe9d84491b5e994e9062e20a116bdc20da518a16f3a5b9fa5fce7bc2dd021c"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
