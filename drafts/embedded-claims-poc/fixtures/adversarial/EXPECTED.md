# Adversarial corpus — expected parser behavior (capsule-only)

What a CONFORMANT parser must do for each specimen. Executable in `test_parser.py`
(13 specimens + 2 invariants, run by the CI gate).

**The pivot (operator + Codex).** The canonical pipeline grants machine credit ONLY to
an explicit `json capsule` inside a live region. The parser never scans prose for inline
claims — prose stays prose. The capsule CONTAINS the claim (class, payload, plus
verifier/dep/binding), so claim↔capsule association is structural containment; the whole
inline-glyph / `⟧`-escaping / `claim_ref` / `{#local_id}` / multiple-inline apparatus is
retired from the normative parser (it survives only as LEGACY `settle_gate` authoring).

**Report status (fail-closed).** `status ∈ {VALID, INVALID, INERT}`: any fatal parse
error ⇒ INVALID; no live region ⇒ INERT; live region with no fatal error ⇒ VALID. The
compiler precondition is `status == VALID`. Layers stay separated: PARSE = region + block
structure + capsule extraction (byte spans); COMPILE (3c) = schema validation of the v2
capsule + settlement of the contained claim.

## Region layer

| Specimen | Expected |
|---|---|
| `10-no-live-region.md` | INERT, `NO_LIVE_REGION` — explicit, not a silent skip. |
| `11-unknown-profile.md` | INVALID, `UNKNOWN_PROFILE` — no fallback profile. |
| `12-unbalanced-region.md` | INVALID, `NESTED_OR_DUP_BEGIN` + `MISSING_END`. |
| `13-marker-in-fence.md` | INERT, `NO_LIVE_REGION` — markers inside a fence/blockquote are inert. |
| `14-unexpected-end.md` | INVALID, `UNEXPECTED_END` — an `end` with no open region. |
| `17-fake-end-in-fence.md` | VALID, 0 capsules — a fenced `end` is inert; the region spans past it (region state over CommonMark block state, not raw text). |

## Capsule extraction

| Specimen | Expected |
|---|---|
| `01-illustration-vs-live.md` | VALID, 1 capsule — the illustration inside an outer fence is inert; only the in-region capsule is live. |
| `02-multiple-claims.md` | VALID, 2 capsules in order (local_ids A, B); surrounding prose inert. |
| `03-nested-fences.md` | VALID, 0 capsules — a capsule inside an outer fence is inert (CommonMark block structure). |
| `04-info-string-variants.md` | VALID, 1 capsule — only the exact raw opener ` ```json capsule` counts; leading-space (CommonMark trims `info`), uppercase, `json claim`, and `{profile}` variants are ordinary code. |
| `05-unclosed-fence.md` | INVALID, `UNCLOSED_FENCE` (+`MISSING_END`, since the unclosed fence eats the region end). |
| `09-claim-inside-capsule.md` | VALID, 1 capsule whose raw body contains the full v2 claim object; association is containment. |
| `20-noncloser-line.md` | INVALID, `UNCLOSED_FENCE` (+`MISSING_END`) — ```` ```not-a-closer ```` is not a valid closing fence. |

## Invariants (across the corpus)

1. **No silent skip.** Every malformed/ambiguous construct is a typed, enumerable outcome.
2. **No guessing liveness.** Liveness is an explicit region, or `NO_LIVE_REGION`.
3. **Structure, then protocol.** Pinned CommonMark for block/nesting/inertness; a protocol
   profile over raw spans for exact opener/closer and exact markers.
4. **Byte spans.** Every capsule carries a raw `[start,end]` byte span; the body is the raw
   source slice (the source occurrence the compiler needs), and the span slices back to it.
5. **parser_id binds the runtime.** The identity closes over parser.py + the lock + the
   installed bytes/versions of markdown_it and mdurl; path-independent, checked cross-venv.
6. **Line-ending ingress.** Files are read as bytes; uniform LF and uniform CRLF parse
   identically with byte-faithful spans; mixed or lone-CR endings are a typed
   `UNSUPPORTED_LINE_ENDING`, never a silent `NO_LIVE_REGION`.

## Compile layer (3c — structural, `compiler.py`)

`VALID ParseReport → strict JSON → capsule.v2 → canonical records/IDs`. STRUCTURAL only:
no settlement is run (that is 3d; `COMPILED` ≠ `REPLAYED`). The precondition is
`parser.status == VALID`; a non-VALID report is REFUSED as a whole (zero records), even
if it diagnostically carried a candidate capsule. An INVALID compile emits no records
either — records are handed forward only from a `COMPILED` report.

| Specimen | Compile expected |
|---|---|
| `01`, `02`, `09`, `03`, `17` | COMPILED — records with content-addressed `claim_id`/`plan_id`/`dependency_id`/`capsule_id` + source occurrence span (0 records for the empty regions 03/17). |
| `05`, `10`, `11`, `13`, `14` | REFUSED, `PRECONDITION_NOT_VALID` — parser status was INVALID/INERT. |
| `21-capsule-bad-json.md` | INVALID, `CAPSULE_NOT_STRICT_JSON`. |
| `22-capsule-schema-invalid.md` | INVALID, `CAPSULE_SCHEMA_INVALID` (unknown claim.class). |
| `23-duplicate-local-id.md` | INVALID, `DUPLICATE_LOCAL_ID`. |

## Status

PARSE (`parser.py`, pinned markdown-it-py==4.2.0) and COMPILE (`compiler.py`, structural)
are implemented and green. **Settlement of the contained claim + the two-axis REPORT is
3d** — not yet built; `COMPILED` is not `REPLAYED`. The old inline `settle_gate` form and
the SSD demos remain legacy authoring, not auto-migrated.
