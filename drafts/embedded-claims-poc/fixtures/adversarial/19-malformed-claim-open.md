# Adversarial 19 — unclosed opening glyph (Codex P1)

An opening `⟦` with no closing `⟧` must be a typed error, not a silent disappearance.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

An unclosed claim: ⟦arith: 1 + 1 = 2

<!-- manifesto-claims:end -->

Expected — PARSE: status INVALID, `MALFORMED_CLAIM_OPEN`. The old raw-line regex would
have found no match and dropped the fragment with no error; the hardened parser counts
an unmatched `⟦` in the text nodes and fails closed.
