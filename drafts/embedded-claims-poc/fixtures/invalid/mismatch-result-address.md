# Fixture: evaluation_id that does not reproduce (P0-2, P2-6)

The arithmetic is true and the verifier is correct — but the author pinned a
evaluation_id that does not recompute. This is the raw→MISMATCH transition on the
address itself: the author bet on an address the computation refuses. Because the
evaluation_id binds the verdict and BOTH normal forms (not just the left one), a false
claim can no longer borrow a true claim's address.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "evaluation_id": "deadbeef00000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=MISMATCH (facts include ADDRESS_MISMATCH).
