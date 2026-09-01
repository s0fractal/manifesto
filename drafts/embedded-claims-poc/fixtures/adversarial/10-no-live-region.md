# Adversarial 10 — no live region (T1 / region layer)

A document that contains claim-shaped text but declares NO live region.

The repo root holds ⟦arith: 3 + 6 = 9⟧ entries, and Monday has ⟦arith: 74 + 1 = 75⟧
notes.

Expected: the parser returns an explicit `NO_LIVE_REGION` result — NOT a silent skip,
and NOT settlement of the glyphs. Absence of a region is a stated outcome, not silence.
This is the default state of almost every existing manifesto document.
