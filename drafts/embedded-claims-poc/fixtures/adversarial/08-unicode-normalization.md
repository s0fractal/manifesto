# Adversarial 08 — Unicode normalization & invisibles (T6)

A cite payload in a live region whose quoted phrase can be written NFC or NFD.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦cite: "café" in NOTES.md⟧

<!-- manifesto-claims:end -->

Expected — PARSE (partial): the parser structurally extracts ONE cite claim with the
EXACT bytes as written (default = exact Unicode scalar values; no global NFC — that
would alias NFC/NFD predicates, Codex P0). Normalization is a later ID-layer concern
and only under a field's verifier profile; the raw source occurrence is committed
separately. So at PARSE this specimen yields one claim and no error; the NFC/NFD
equivalence question is deferred, not decided here.
