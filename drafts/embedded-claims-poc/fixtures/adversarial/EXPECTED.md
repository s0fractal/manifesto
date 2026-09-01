# Adversarial corpus — expected parser behavior (spec before code)

What a CONFORMANT parser/compiler must do for each specimen. Written BEFORE the parser
exists (Codex's pressure: record the ambiguities first). Each row becomes a test when
the parser is built (phase 2 step 3) — passing with a TYPED reason, never a silent skip.

**Layers are separated (Codex P1).** PARSE = region + block structure + claim/capsule
recognition. COMPILE = closed-schema validation + claim↔capsule association + identity.
A specimen that tests COMPILE uses schema-valid capsules so it actually reaches that
layer instead of being rejected at schema first. A specimen that tests PARSE says so and
its placeholder bodies are irrelevant to the parse verdict.

The specimens are themselves format-shaped text, so they also belong to the T1
illustration corpus: they live under `fixtures/adversarial/` precisely so no repo sweep
mistakes them for claims. Live specimens carry explicit `manifesto-claims` regions.

## Region layer (the decided §8.1 rule)

| Specimen | Layer | Expected |
|---|---|---|
| `10-no-live-region.md` | PARSE | `NO_LIVE_REGION` — explicit, not a silent skip; glyphs never settled. |
| `11-unknown-profile.md` | PARSE | `UNKNOWN_PROFILE` typed failure; no fallback profile. |
| `12-unbalanced-region.md` | PARSE | `NESTED_OR_DUP_BEGIN` / `MISSING_END`; nothing inside settled. |
| `13-marker-in-fence.md` | PARSE | Markers inside a fence/blockquote are inert ⇒ `NO_LIVE_REGION`. |
| `14-unexpected-end.md` | PARSE | `UNEXPECTED_END` — an `end` with no open region; fail closed. |
| `17-fake-end-in-fence.md` | PARSE | A fenced `end` is inert; the region spans both claims ⇒ TWO live claims. Region state is over CommonMark block state, not raw text. |

## Claim / capsule sub-parsing (assumed inside a live region)

| Specimen | Threat | Layer | Expected |
|---|---|---|---|
| `01-illustration-vs-live.md` | T1 | PARSE | Exactly one live claim (`3+6=9`); the fenced `2+2=5` (fence wins inside region) and the out-of-region `1+1=3` are inert. |
| `02-multiple-claims.md` | T2 | PARSE | All THREE claims, in document order, each its own result. Never just the first. |
| `03-nested-fences.md` | T4 | PARSE | The `json capsule` inside an outer fence is inert; NO live capsule found. |
| `04-info-string-variants.md` | T4 | PARSE | Only the exact `json capsule` opener is a candidate; the leading-space variant (CommonMark trims it) and the others are rejected at the RAW opener-line level. |
| `05-unclosed-fence.md` | T4 | PARSE | `UNCLOSED_FENCE` typed error (CommonMark would run it to EOF); fail closed, never silent-drop. |
| `06-glyph-in-code-fence.md` | T5 | PARSE | Prose glyph live; identical glyph inside ```` ```text ```` inert. |
| `07-delimiter-injection.md` | T7 | PARSE | No truncation at an embedded `⟧`; a capsule string's ```` ``` ```` does not close the fence. Absent an escaping rule, a typed error — never silent truncation. |
| `08-unicode-normalization.md` | T6 | PARSE→ID | Default EXACT scalars; normalize a field only under its verifier profile; commit raw source occurrence separately; accept only U+27E6/U+27E7 delimiters. Global NFC is forbidden (it would alias distinct predicates). |
| `09-claim-capsule-association.md` | T8 | COMPILE | Capsules bind by `claim_ref` (out-of-order on purpose), not adjacency; bodies are schema-valid (`manifesto.capsule.v1`) so association is actually reached; both capsules validate and carry claim_ref A/B (this is now an executable suite invariant). |
| `15-dangling-claim-ref.md` | T8 | COMPILE | Capsule is schema-valid, then `DANGLING_CLAIM_REF` — `claim_ref` names no existing claim. |
| `16-duplicate-local-id.md` | T8 | COMPILE | Two schema-valid capsules bind one local_id ⇒ `DUPLICATE_CLAIM_REF`; a claim owns at most one capsule. |

## Invariants across the whole corpus

1. **No silent skip.** Every malformed/ambiguous construct produces a typed, enumerable
   outcome. Silence is the one forbidden result.
2. **No guessing liveness.** Liveness is declared by an explicit region, or the parser
   returns `NO_LIVE_REGION`. It is never inferred.
3. **Structure, then protocol.** A pinned CommonMark pass gives block/nesting/inertness;
   a protocol profile over the raw source spans adds exact-opener and explicit-closing
   requirements CommonMark cannot express.
4. **Identity after (field-scoped) normalization, with raw occurrence kept.** No digest
   over globally-normalized text; the raw source occurrence is committed alongside the
   semantic `claim_id`.

## Not in this step

No parser, no compiler. These specimens are the pressure the parser will be built
against. Building the parser before this corpus is agreed would fit the spec to the code
instead of the code to the spec.
