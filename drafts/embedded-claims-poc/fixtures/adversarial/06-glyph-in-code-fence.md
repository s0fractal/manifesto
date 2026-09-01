# Adversarial 06 — glyph claim inside a code fence (T5)

The same claim bytes appear once in prose (live) and once inside a code fence (inert),
both within the live region — the fence wins.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

Live, in prose: the root holds ⟦arith: 3 + 6 = 9⟧ entries.

Shown as literal example output:

```text
$ settle README
⟦arith: 3 + 6 = 9⟧ → PASS
```

<!-- manifesto-claims:end -->

Expected: the prose claim is live; the identical glyph inside the ```` ```text ````
block is inert even though both are inside the region. Fence context changes meaning,
so a raw whole-document regex over glyphs is wrong. Interacts with T1: fencing is a
reliable inert-marker; region membership alone does not make fenced content live.
