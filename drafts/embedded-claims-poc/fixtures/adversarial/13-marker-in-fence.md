# Adversarial 13 — region marker inside a code fence / blockquote (region layer)

The begin/end markers appear only inside a code fence and a blockquote — documentation
of the marker syntax, not an actual region.

````markdown
<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->
⟦arith: 2 + 2 = 5⟧
<!-- manifesto-claims:end -->
````

> <!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->
> quoted, not live

Expected: neither marker activates a region — a marker inside a code fence or a
blockquote is inert (it is someone documenting the syntax). The document has NO live
region, so the result is `NO_LIVE_REGION`; the `2+2=5` glyph is never settled. This is
how a document can explain the format without accidentally arming it.
