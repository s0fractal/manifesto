# Adversarial 12 — unbalanced region markers (region layer)

A `begin` with no matching `end` (and, as a second case, a duplicate `begin`).

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦arith: 3 + 6 = 9⟧

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦arith: 74 + 1 = 75⟧

Expected: a typed failure. A duplicate `begin` before any `end` is `NESTED_OR_DUP_BEGIN`;
a region never closed by end-of-document is `MISSING_END`. Regions are balanced and
non-nested; either violation fails closed, and no claim inside an unbalanced region is
settled.
