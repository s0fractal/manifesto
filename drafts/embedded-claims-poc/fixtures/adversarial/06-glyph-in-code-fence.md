# Adversarial 06 — glyph claim inside a code fence (T5)

The same claim bytes appear once in prose (live) and once inside a code fence (inert).

Live, in prose: the root holds ⟦arith: 3 + 6 = 9⟧ entries.

Shown as literal example output:

```text
$ settle README
⟦arith: 3 + 6 = 9⟧ → PASS
```

Expected: the prose claim is live; the identical glyph inside the ```` ```text ````
block is inert and must not be settled. Fence context changes meaning, so a raw
whole-document regex over glyphs is wrong. This interacts with T1: fencing is the
usual (but not guaranteed) marker of illustration.
