# Parser threat model — embedded-claims phase 2 step 2 (before code)

> **PIVOT (after step 3b, operator + Codex): the canonical pipeline is CAPSULE-ONLY.**
> The parser no longer scans prose for inline `⟦…⟧` claims. Machine credit is granted
> only to an explicit `json capsule` inside a live region, and the capsule CONTAINS its
> claim, so claim↔capsule association is structural containment. This RETIRES threats
> T2 (multiple inline claims), T3 (inline-in-prose), T5 (glyph-in-fence at the inline
> level), and T7 (inline delimiter injection) from the normative parser, along with the
> `{#local_id}` suffix and `claim_ref`. What STAYS load-bearing: T1 (live vs
> illustration — solved by regions), T4 (fenced-capsule Markdown ambiguities), T6
> (Unicode, now a compile/ID concern on capsule bodies), T8 (dissolved by containment),
> plus the installed-dependency closure, exact markers/opener/closer, byte spans, and
> report-level fail-closed. The inline sections below are kept for provenance; read them
> as the history that led to the pivot, not as current parser requirements. The old
> inline `settle_gate` form and the SSD demos remain LEGACY authoring, not auto-migrated.


**Status:** threat model + corpus spec, written BEFORE the parser (Codex's pressure:
don't wait, act — start from real documents and adversarial cases, not code). Records
the Markdown ambiguities a conformant capsule/claim parser must resolve, grounded in
what the manifesto actually contains. Updated after a Codex review pass: the
live-demarcation blocker is now DECIDED (explicit live regions, §1/§8), and four
findings are folded in — global-NFC aliasing (P0), CommonMark-vs-protocol layering
(P1), parser-vs-schema expectation split in the corpus (P1), and source-occurrence
identity (P2). The parser and the capsule→records compiler come after this is agreed.

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
`​```json capsule` as an obligation.

**DECIDED (§8.1 resolution): explicit live regions.** Live claims and capsules are
recognized only inside an explicitly delimited region:

```md
<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

…live claims and capsules…

<!-- manifesto-claims:end -->
```

Rules (all typed-failure on violation, never silent):
- the marker is an exact ASCII top-level HTML comment (fixed spelling);
- regions are balanced and NOT nested;
- a marker inside a code fence or blockquote activates nothing;
- unknown `profile`, a duplicate `begin`, or a missing `end` is a typed failure;
- a document with no region yields an explicit `NO_LIVE_REGION`, never a silent skip;
- the parser runs only on files passed explicitly — never an automatic repo sweep.

This lets one document hold both live obligations and illustrations of the format
(the illustrations simply live outside any region), and supports gradual adoption of
manifesto documents one region at a time. Everything outside a region — every design
example, every fixture specimen, the architecture doc's capsule — is inert by
construction, which dissolves T1 rather than heuristically guessing at it.

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

**CommonMark alone is necessary but NOT sufficient** (Codex P1, per
[CommonMark 0.31.2 §fenced-code-blocks](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)):
- it TRIMS leading/trailing info-string whitespace, so ```` ``` json capsule ```` and
  ```` ```json capsule ```` share one structural info string — the leading-space
  variant cannot be rejected at the AST level;
- an unclosed fence legally runs to end-of-document — CommonMark will not flag it;
- a ```` ``` ```` inside a JSON string does not close the fence unless it stands as a
  valid closing-fence line on its own.

Therefore the parser is a **pinned CommonMark pass + a strict protocol profile over
the raw source spans**: CommonMark gives correct block/nesting/inertness; the protocol
profile, working on the raw bytes of the opener line and the block, additionally
requires the EXACT opener spelling (`json capsule`, no leading space, case-sensitive,
no trailing tokens) and an EXPLICIT closing fence (unclosed ⇒ typed `UNCLOSED_FENCE`).
The constraints that look like "CommonMark violations" are really protocol-profile
requirements layered on top of a conformant CommonMark parse.

## 5. T5 — Glyph claims inside code fences (inert vs live)

`⟦arith: 3+6=9⟧` printed *inside* a ```` ```text ```` example block must NOT settle;
the same bytes in prose must. Fence context therefore changes meaning — a second
reason the parser needs Markdown structure, and it interacts with T1: an example is
usually (but not reliably) fenced, a live claim usually in prose. "Usually" is not a
contract; §7 must make it one.

## 6. T6/T7 — Unicode and delimiter injection

- **Normalization (Codex P0 — global NFC is WRONG):** a blanket "normalize to NFC
  before identity" creates a semantic alias. `count: /é/` or an exact `cite` operate on
  the file's actual bytes; if the parser gives an NFC and an NFD spelling the same
  `claim_id` but the evaluator/dependency compares un-normalized bytes, two *different*
  predicates collapse to one identity. So: **the default is exact Unicode scalar values
  (no normalization)**; a field is normalized ONLY when its verifier profile explicitly
  defines an equivalent normalization for that field, and then evaluator and parser must
  use the SAME profile. Independently, the raw source occurrence (the exact bytes as
  written) is committed separately from the semantic `claim_id`, so the two never fuse.
  (The canonical layer already rejects lone surrogates; that is necessary, not
  sufficient.)
- **Homoglyphs / invisibles:** `⟦` is U+27E6; lookalike brackets, zero-width joiners,
  and RTL marks inside a payload must be handled deliberately (reject or normalize),
  not silently.
- **Delimiter injection (T7):** a payload that contains `⟧` (a `cite` quote), or a
  capsule JSON string containing ```` ``` ````, must not let the content terminate the
  container. Needs an escaping rule or a length-prefixed / structural parse.

## 7. T8 — Claim ↔ capsule association

The PoC assumes one claim + one capsule per file. Real documents (SSD-DEMO) have many
claims and zero capsules; a future document may have several of each. Which capsule
binds to which claim?

**Association is by explicit reference, not adjacency (Codex).** The claim carries a
`local_id` (already in the architecture capsule shape) and the capsule names it via
`claim_ref`. Adjacency ("nearest preceding claim") is fragile — an inserted paragraph
silently re-binds a capsule — so it is rejected. A capsule whose `claim_ref` matches no
claim, or two capsules claiming one `local_id`, is a typed error.

**Source-occurrence identity (Codex P2), separate from `claim_id`.** `claim_id` aliases
semantic content — and correctly so: the same predicate written twice has one
`claim_id`. But an identical normalized claim can occur twice in a document, and a
capsule must address a SPECIFIC occurrence. So the compiler also commits a source
occurrence — `(revision, path, byte-span)` or an equivalent source commitment —
distinct from `claim_id`. `claim_id` says *what* is claimed; the occurrence says *where
it was written*. The capsule binds a `(claim_id, occurrence)` pair, so two identical
claims in one file remain individually addressable.

## 8. Decisions this model forces

**DECIDED:**
1. **Live demarcation (T1)** — explicit live regions via the `manifesto-claims:begin/end`
   markers above (§1). No repo sweep; explicit files only; no region ⇒ `NO_LIVE_REGION`.
4. **Normalization (T6)** — default exact Unicode scalar values; per-field normalization
   only where a verifier profile defines it, shared by parser and evaluator; raw source
   occurrence committed separately.
6. **Association (T8)** — explicit `local_id` on the claim + `claim_ref` on the capsule;
   never adjacency. Capsule binds a `(claim_id, source-occurrence)` pair.

2. **Info string (T4)** — DECIDED: the exact raw opener is ` ```json capsule` (case
   sensitive, no leading space, no trailing tokens), enforced by the protocol profile
   over raw spans (CommonMark can't — it trims whitespace).
3. **Fence engine (T4/T5)** — DECIDED: `markdown-it-py==4.2.0`, preset `commonmark`,
   no plugins, for block/nesting/inertness and token line-maps; the raw opener/closer
   is enforced by our protocol layer over the source spans. The version and its
   artifact/closure must be PINNED (as the evaluator is), and the CI gate installs it
   explicitly. This ends the stdlib-only property — a deliberate, pinned trade.
5. **Escaping (T7)** — DECIDED v0: an inline claim containing a literal `⟧` is a typed
   `UNSUPPORTED_INLINE_DELIMITER`; text that needs the character is carried in a JSON
   capsule instead. No escape language is invented now.

**Local_id syntax — FROZEN:** inline `⟦<class>: <payload>⟧{#<id>}` — the `{#id}` suffix
follows the closing `⟧`, so the payload handed to the evaluator stays clean; `<id>` ∈
`[A-Za-z0-9_-]{1,64}`; the capsule's `claim_ref` carries the bare `<id>`. Added to the
closed schema as `manifesto.capsule.v1`.

## 9. The adversarial corpus (this step's deliverable)

`fixtures/adversarial/` holds one small Markdown file per threat (01–09 for
claim/capsule sub-parsing, 10–13 for the region layer), each paired with an entry in
`fixtures/adversarial/EXPECTED.md` stating what a conformant parser MUST do —
**a spec written before the parser, so the parser is measured against it, not the
reverse.** EXPECTED separates PARSE-layer from COMPILE-layer expectations (Codex P1),
so a specimen that tests association carries schema-valid capsules and actually reaches
the compiler instead of being rejected at schema first. Live specimens carry explicit
`manifesto-claims` regions. No parser is implemented in this step; when it is built
(step 3), each row becomes a test that must pass with a typed reason, never a silent
skip.
