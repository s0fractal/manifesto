# Adversarial 05 — unclosed capsule fence (T4)

A capsule fence opened inside a region but never closed. Per CommonMark the fence runs
to end-of-document, which also swallows the region's `end` marker.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"verifier": "glyph://sha256:deadbeef...", "note": "no closing fence follows"}

<!-- manifesto-claims:end -->

Expected — PARSE: `UNCLOSED_FENCE` (the exact opener is never closed). Because the
unclosed fence eats everything after it — including the `end` marker — the region is
also reported `MISSING_END`. The one forbidden outcome is silence: the current regex
would drop the block with no error. Both are typed.
