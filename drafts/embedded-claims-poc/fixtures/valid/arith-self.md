# Fixture: self-contained arithmetic claim (D1)

The most aligned case: the claim carries its own settlement. A reader recomputes
both sides on the Σ-GLYPH machine and compares. No CAS, no receipt store, no
network. The capsule pins the verifier that must have run and the evaluation_id the
author bets on.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  "evaluation_id": "35d9e88d7f590e2e7a233b18a1d4d520b3284c475353d056d221523185dd3642"
}
```

Expected: execution=REPLAYED, binding=UNTIED. Verifier pin confirmed, evaluation_id
reproduces.
