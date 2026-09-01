# Fixture: evaluation_id that does not reproduce (P0-2, P2-6)

The arithmetic is true and the verifier is correct — but the author pinned a
evaluation_id that does not recompute. This is the raw→MISMATCH transition on the
address itself: the author bet on an address the computation refuses. Because the
evaluation_id binds the verdict and BOTH normal forms (not just the left one), a false
claim can no longer borrow a true claim's address.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  "evaluation_id": "deadbeef00000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=MISMATCH (facts include ADDRESS_MISMATCH).
