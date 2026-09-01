# Adversarial 14 — end marker without begin (region layer)

A stray `end` marker with no matching `begin` before it.

Some ordinary prose.

<!-- manifesto-claims:end -->

⟦arith: 3 + 6 = 9⟧

Expected: a typed `UNEXPECTED_END` failure — the `end` has no open region to close.
Fail closed; the glyph is never settled (it is not inside any region anyway).
