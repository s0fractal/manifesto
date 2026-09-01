# Adversarial 01 — illustration vs live claim (T1, the central threat)

Two glyph claims that look identical byte-for-byte, disambiguated by the live-region
rule and by fence context — not by guessing.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

A live claim, in prose inside the region: the repo root holds ⟦arith: 3 + 6 = 9⟧
top-level entries.

An illustration, fenced even though it is inside the region — the fence makes it inert:

```text
⟦arith: 2 + 2 = 5⟧
```

<!-- manifesto-claims:end -->

And a claim OUTSIDE any region, which is inert by construction: ⟦arith: 1 + 1 = 3⟧.

Expected: exactly ONE live claim (`3+6=9`). The fenced `2+2=5` is inert (fence wins,
even inside a region); the `1+1=3` outside the region is inert (no region). A parser
that settles or refutes either non-live claim is wrong even though both are "false" —
they were never claims.
