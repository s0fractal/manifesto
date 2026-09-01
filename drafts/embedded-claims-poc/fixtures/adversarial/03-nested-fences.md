# Adversarial 03 — nested fences (T4)

A capsule shown INSIDE a wider fence, as documentation, all within a live region. The
inner capsule must stay inert (it is content of the outer fence), so the region has
zero live capsules.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

````markdown
Here is how you attach a capsule:

```json capsule
{"verifier": "glyph://sha256:deadbeef..."}
```
````

<!-- manifesto-claims:end -->

Expected — PARSE: one region, ZERO capsules, ZERO claims, no errors. The inner
`json capsule` is content of the outer ````markdown fence, not a separate fence token,
so CommonMark block structure makes it inert automatically. A regex would have captured
a truncated body.
