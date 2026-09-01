# Adversarial 08 — Unicode normalization & invisibles (T6)

Payloads that are visually equal but byte-unequal, or carry invisible characters.

A cite whose quoted phrase can be written NFC or NFD (é as U+00E9 vs e + U+0301):
⟦cite: "café" in NOTES.md⟧

A payload with a zero-width joiner or non-breaking space hidden in it (invisible here
but present in bytes) would hash differently from its clean form.

A homoglyph risk: the opening glyph is U+27E6 `⟦`; lookalike bracket characters must
not be accepted as the delimiter.

Expected: the parser fixes a normalization form (NFC) BEFORE any identity or digest is
computed, so NFC and NFD spellings of the same quote settle to the same claim_id.
Invisible/format characters in a payload are rejected or normalized deliberately, never
silently carried into a hash. The canonical layer already rejects lone surrogates; that
is necessary but not sufficient — normalization lives at the parser boundary.
