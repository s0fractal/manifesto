# Adversarial 07 — delimiter injection (T7)

A cite payload inside a live region whose quoted text contains the closing glyph ⟧.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦cite: "he said ⟧ and left" in NOTES.md⟧

<!-- manifesto-claims:end -->

Expected — PARSE: the claim grammar `[^⟧]+` stops at the FIRST `⟧`, truncating the cite
to `"he said `, and the trailing ` and left" in NOTES.md⟧` leaves a stray `⟧`. The
parser detects the unconsumed closing glyph and emits `UNSUPPORTED_INLINE_DELIMITER`
(v0: text needing a literal `⟧` is carried in a capsule, not an inline claim). Never a
silent truncation.
