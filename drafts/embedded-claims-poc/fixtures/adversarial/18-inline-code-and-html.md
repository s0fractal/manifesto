# Adversarial 18 — glyphs in inline code / inline HTML are inert (T5, Codex P1)

CommonMark inline structure must be respected: a glyph inside an inline code span or an
inline HTML comment is NOT a live claim, and a literal `⟧` inside code is NOT a
delimiter error. Only real prose text is live.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

Glyph in an inline code span: `⟦arith: 2 + 2 = 5⟧` — inert.

Glyph in an inline HTML comment: <!-- ⟦arith: 9 + 9 = 1⟧ --> — inert.

A literal close glyph inside code: `a ⟧ b` — must NOT trigger a delimiter error.

A real claim in prose: ⟦arith: 3 + 6 = 9⟧.

<!-- manifesto-claims:end -->

Expected — PARSE: status VALID, exactly ONE live claim (`3 + 6 = 9`), no errors. The
code-span and HTML-comment glyphs are excluded because claims come from CommonMark TEXT
nodes only; the code-span `⟧` is likewise not seen.
