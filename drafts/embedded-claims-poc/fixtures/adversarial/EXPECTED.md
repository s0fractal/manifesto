# Adversarial corpus — expected parser behavior (spec before code)

This manifest states what a CONFORMANT parser must do for each specimen in this
directory. It is written BEFORE the parser exists (Codex's pressure: record the
ambiguities first). When the parser is built (phase 2 step 3), each row becomes a test
that must pass with a TYPED reason — never a silent skip, never a guess.

The specimens are themselves format-shaped text, so they also belong to the T1
illustration corpus: they are specimens, not live obligations, and live here under
`fixtures/adversarial/` precisely so no repo sweep mistakes them for claims.

| Specimen | Threat | A conformant parser MUST |
|---|---|---|
| `01-illustration-vs-live.md` | T1 | Treat the prose `3+6=9` as live; treat the fenced `2+2=5` as an illustration (never settle/refute it). With no active live-demarcation rule, REFUSE to run rather than guess. |
| `02-multiple-claims.md` | T2 | Return all THREE claims in document order, each with its own result. Never just the first. |
| `03-nested-fences.md` | T4 | Recognize the `json capsule` block is INSIDE an outer fence → inert. Find NO live capsule. (Regex would capture a truncated body.) |
| `04-info-string-variants.md` | T4 | Accept only the exact frozen info string (`json capsule`) as a candidate; treat `json claim`, ` json capsule`, `JSON capsule`, `json capsule {profile}` as ordinary code. |
| `05-unclosed-fence.md` | T4 | Emit a typed UNCLOSED_FENCE error and fail closed. Never silently drop the opened capsule. |
| `06-glyph-in-code-fence.md` | T5 | Settle the prose glyph; treat the identical glyph inside ```` ```text ```` as inert. |
| `07-delimiter-injection.md` | T7 | Not truncate a `cite` payload at an embedded `⟧`, nor let a capsule string's ```` ``` ```` close the fence. Absent an escaping rule, emit a typed error — never a silent truncation. |
| `08-unicode-normalization.md` | T6 | Normalize to NFC before computing any identity, so NFC/NFD spellings share a claim_id; reject/normalize invisibles; accept only U+27E6/U+27E7 as the glyph delimiters. |
| `09-claim-capsule-association.md` | T8 | Require an explicit claim↔capsule association (id reference or strict adjacency contract); flag ambiguous/crossed association as a typed error. |

## Invariants across the whole corpus

1. **No silent skip.** Every malformed or ambiguous construct produces a typed,
   enumerable outcome. Silence is the one forbidden result.
2. **No guessing liveness.** A parser never infers that an illustration is a claim.
   Liveness is declared (§7/§8.1 of the threat model), or the parser refuses.
3. **Structure, not regex.** Fence context, nesting, and info strings are resolved by
   CommonMark block structure, not text patterns.
4. **Identity after normalization.** No digest is computed over un-normalized text.

## Not in this step

No parser, no compiler. These specimens are the pressure the parser will be built
against. Building the parser before this corpus is agreed would be fitting the spec to
the code instead of the code to the spec.
