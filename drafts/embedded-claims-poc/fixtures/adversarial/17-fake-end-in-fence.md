# Adversarial 17 — fake end inside a fence, then real end (region state)

A real region that contains a fenced block which itself contains an `end` marker as
example text. The fenced `end` must NOT close the region; the real top-level `end`
does. This tests that the region scanner tracks fence state, not raw text matches.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

First live claim: ⟦arith: 3 + 6 = 9⟧.

An example of how a region ends, shown inside a fence:

```text
<!-- manifesto-claims:end -->
```

Still inside the region (the fenced marker was inert): ⟦arith: 74 + 1 = 75⟧.

<!-- manifesto-claims:end -->

Expected: the fenced `end` is inert; the region spans BOTH claims; two live claims are
found. A scanner that matched the marker by raw text would close the region early and
miss the second claim. Region membership is computed over CommonMark block state.
