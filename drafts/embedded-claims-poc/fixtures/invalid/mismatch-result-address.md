# Fixture: evaluation_id that does not reproduce (P0-2, P2-6)

The arithmetic is true and the verifier is correct — but the author pinned a
evaluation_id that does not recompute. This is the raw→MISMATCH transition on the
address itself: the author bet on an address the computation refuses. Because the
evaluation_id binds the verdict and BOTH normal forms (not just the left one), a false
claim can no longer borrow a true claim's address.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "evaluation_id": "deadbeef00000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=MISMATCH (facts include ADDRESS_MISMATCH).
