# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "evaluation_id": "0624034f62ed5f1ada529e49146cc4d9beb97d85c9756a542e4b4eb234579a92"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
