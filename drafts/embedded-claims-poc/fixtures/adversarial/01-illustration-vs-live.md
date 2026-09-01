# Adversarial 01 — illustration vs live claim (T1, the central threat)

This document contains TWO glyph claims that look identical byte-for-byte but must
be treated differently.

A live claim, in prose: the repo root holds ⟦arith: 3 + 6 = 9⟧ top-level entries.

An ILLUSTRATION of the format, fenced as an example:

```text
⟦arith: 2 + 2 = 5⟧
```

Expected: under the chosen live-demarcation rule (§7 of the threat model), the prose
claim is a live obligation and the fenced one is an illustration that MUST NOT be
settled or refuted. A parser that settles the `2+2=5` example is wrong even though it
is "false" — it was never a claim. If no demarcation rule is active, the parser must
REFUSE to run over this document rather than guess.
