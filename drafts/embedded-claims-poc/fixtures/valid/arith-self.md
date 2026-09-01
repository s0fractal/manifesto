# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "evaluation_id": "ba68bf2096a58694dd8064c321cd56441574d8efdf58d3e478b8099bb7417ce0"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
