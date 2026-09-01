# Parser threat model — embedded-claims phase 2 step 2 (before code)

**Status:** threat model + corpus spec, written BEFORE the parser (Codex's pressure:
don't wait, act — start from real documents and adversarial cases, not code). This
document records the Markdown ambiguities a conformant capsule/claim parser must
resolve, grounded in what the manifesto actually contains. The parser and the
capsule→records compiler come after this is agreed.

## 0. Evidence: real documents already carry real claims

Not synthetic. Settled with the existing `tools/settle_gate.py` against the live repo:

| Document | claims | settled true | REFUTED | note |
|---|---|---|---|---|
| `drafts/SSD-DEMO-0.1.md` | 11 | 7 | **4** | "white cone" generator output — fabricated counts caught |
| `drafts/SSD-DEMO-0.2.md` | 11 | 8 | **3** | corrected pass — still 3 wrong |
| `MISSION.md` | 3 | 3 | 0 | real `⟦cite:⟧` quotes; all reproduce verbatim |

A concrete predicate trap from real data: the claim `⟦count: /Теза/ in README.md = N⟧`.
The true substring count is **8**. SSD-0.1 claims 12 (wrong); SSD-0.2 claims 7 (also
wrong — 7 is the count of `^## Теза N:` *headings*, a different predicate). Two
documents, one string predicate, three different numbers, and the "corrected" one is
still wrong because it silently switched predicates. This is exactly the
`dependency_id` vs `evaluation_id` / predicate-identity distinction (P0-2) showing up
in the wild.

Consequence: settlement over real prose works. The open problem is not *whether* to
settle, it is *what the parser is even allowed to treat as a live claim* — because
the same repo is saturated with claims that are illustrations, not obligations.

## 1. T1 — Self-reference: illustration vs live claim (the central threat)

The manifesto is a repository ABOUT embedded claims. Tracked Markdown hits:

- `git grep -l '⟦[a-z]+:'` → 10+ documents (MISSION, EMBED-FORMAT-DESIGN,
  EMBEDDING-SETTLEMENT, ARCHITECTURE-0.1, SSD-DEMO-*, the PoC README, fixtures…).
- `git grep -l '```json (capsule|claim)'` → 20+ files (the architecture doc's §7.2
  example, this PoC's every fixture, the PoC README).

Most of these are the *format describing itself*: `EMBED-FORMAT-DESIGN.md` writes
`⟦arith: 74+1=75 ⊨ …⟧` as a design example; `ARCHITECTURE-0.1.md` shows a
`​```json claim` capsule as documentation; every fixture is a specimen. A regex sweep
cannot tell "this is a claim" from "this is a picture of a claim." `SSD-DEMO-*.md`
claims are meant to be settled; the architecture doc's identical-looking example is
NOT. They are byte-indistinguishable to a scanner.

**Design consequence (the load-bearing one): "live" must be explicit, never inferred.**
A parser must not auto-sweep a document, still less a repo, and treat every `⟦…⟧` or
`​```json capsule` as an obligation. Options to decide (§7): a per-document opt-in
marker (front-matter `settlement: active`), a live-region delimiter, or an inert form
for examples (examples fenced as ```` ```text ````, live claims only in prose). Until
one is chosen and enforced, running any parser over the manifesto would "find"
dozens of documentation specimens and either settle or refute them meaninglessly.

## 2. T2 — Multiple claims per document

`SSD-DEMO-0.1.md` carries 11 claims in a single paragraph. The current PoC
`verify.py`/`settle_core.py` finds only the FIRST claim (`CLAIM_RE.search`) and the
FIRST capsule (`CAPSULE.search`); `settle_gate.py` finds ALL (`CLAIM.sub`). A
conformant parser must return every claim, in document order, and a per-claim result
— not the first. Sub-threats: stable per-claim identity/ordinal; a binding
environment threaded left-to-right (settle_gate's `bindarith` already depends on
earlier `@name` binds), so order is semantically load-bearing, not cosmetic.

## 3. T3 — Claims inline in prose

Real claims sit mid-sentence: `…що разом дає ⟦arith: 3 + 6 = 9⟧ елементів…`. The glyph
delimiters make this tractable, but the payload grammar `[^⟧]+` must be tested against
adjacency to punctuation, and against a payload that itself wants a `⟧` (a `cite`
quote containing the character). See T7.

## 4. T4 — Fenced-capsule Markdown ambiguities

The capsule regex is `​```json capsule\n(.*?)\n``` `. Every one of these breaks or
mis-fires it:

- **Info-string drift:** `​```json capsule` (PoC) vs `​```json claim` (architecture
  doc) vs `​``` json capsule` (leading space) vs `​```JSON capsule` (case) vs
  `​```json capsule {profile}` (trailing tokens) vs `​```json  capsule` (two spaces).
- **Nested fences:** a capsule shown *inside* a wider fence (a doc teaching "write
  this capsule" wraps it in an outer ```` ``` ````). The non-greedy `.*?\n``` ` closes
  on the INNER ```` ``` ````, capturing a truncated body.
- **Unclosed fence:** `​```json capsule\n{…}` with no closing ```` ``` ```` — the regex
  simply fails to match and the block is silently dropped. Must be a typed error, not
  a silent skip.
- **Alternate fences / indentation:** `~~~` fences, 4-space indented code blocks,
  blockquoted (`>`) capsules, CRLF line endings.
- **Fence content that contains a fence:** a capsule JSON string value containing the
  literal ```` ``` ```` closes the block early for a naive scanner.

A regex cannot resolve these. The parser must consume real Markdown block structure
(a CommonMark-aware pass), not pattern-match text.

## 5. T5 — Glyph claims inside code fences (inert vs live)

`⟦arith: 3+6=9⟧` printed *inside* a ```` ```text ```` example block must NOT settle;
the same bytes in prose must. Fence context therefore changes meaning — a second
reason the parser needs Markdown structure, and it interacts with T1: an example is
usually (but not reliably) fenced, a live claim usually in prose. "Usually" is not a
contract; §7 must make it one.

## 6. T6/T7 — Unicode and delimiter injection

- **Normalization:** a payload with combining marks or NFC/NFD variance hashes
  differently pre/post normalization; the parser must fix a normalization form before
  any identity is computed. (The canonical layer already rejects lone surrogates; that
  is necessary, not sufficient.)
- **Homoglyphs / invisibles:** `⟦` is U+27E6; lookalike brackets, zero-width joiners,
  and RTL marks inside a payload must be handled deliberately (reject or normalize),
  not silently.
- **Delimiter injection (T7):** a payload that contains `⟧` (a `cite` quote), or a
  capsule JSON string containing ```` ``` ````, must not let the content terminate the
  container. Needs an escaping rule or a length-prefixed / structural parse.

## 7. T8 — Claim ↔ capsule association

The PoC assumes one claim + one capsule per file. Real documents (SSD-DEMO) have many
claims and zero capsules; a future document may have several of each. Which capsule
binds to which claim? Adjacency is fragile. The compiler needs an explicit association
rule (an `id` on the claim referenced by the capsule, or a strict one-capsule-per-claim
adjacency contract), decided before the capsule→records compiler is written.

## 8. Open decisions this model forces (operator / next reviewer)

1. **Live demarcation (T1) — the blocker.** Front-matter opt-in? live-region marker?
   inert-example convention? No parser should run over the manifesto until this is set.
2. **Info string (T4):** freeze exactly one (`json capsule`), reject all variants.
3. **Fence engine (T4/T5):** adopt a CommonMark parser vs a hardened bespoke block
   scanner. External dependency vs stdlib-only (the CI gate currently needs no package
   beyond the evaluator).
4. **Normalization form (T6):** NFC, fixed before identity.
5. **Escaping (T7):** how a payload carries `⟧` or a fence.
6. **Association (T8):** how a capsule names its claim.

## 9. The adversarial corpus (this step's deliverable)

`fixtures/adversarial/` holds one small Markdown file per threat, each paired with an
entry in `fixtures/adversarial/EXPECTED.md` stating what a conformant parser MUST do —
**a spec written before the parser, so the parser is measured against it, not the
reverse.** No parser is implemented in this step. When the parser is built (step 3),
these become its first failing tests, and each must pass with a typed reason, never a
silent skip.
