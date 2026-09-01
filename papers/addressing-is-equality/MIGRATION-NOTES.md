# Migration notes — Addressing Is Equality → v0.2

The governing instruction here is stronger than for paper A: **do not publish the false v0.1 body
with only an errata banner.** The v0.1 `paper.md` is kept as a historical comparator; the
replacement is `paper-v0.2-draft.md`, rebuilt from the failure boundary inward. Promotion to
`paper.md` is an explicit operator decision.

## Cross-cutting repairs

1. **Genre = incident-and-repair note (Codex §7 / P0-B2).** The title must NOT imply the method is
   realized on an admitted domain. It becomes "Budgeted Equality by Normal-Form Address: A Cost Gap,
   an Executable Soundness Boundary, and a Blocked Admitted-Domain Contract"; "Addressing Is
   Equality" survives only as a subtitle/historical name. **No single deposited implementation both
   admits the motivating computation and emits the two-sided receipt** — this is stated as the
   paper's central, most trustworthy result, not hidden.
2. **`church@v0` is DRAFT, unreleased (Codex P0-B1).** Never "released profile". It is ADR-011 — a
   DRAFT / reference implementation at Sigma-Glyph commit `196c45a2…` (`v0.6.7-175-g196c45a`),
   non-normative, not gated, not adopted, and **not in the published `sigma-glyph==0.6.7` wheel**
   (`git ls-tree -r v0.6.7` has no ADR-011/`equality_profile.py`/`church@v0`). Split the evaluator
   wheel (0.6.7) from the unreleased profile implementation in every environment record. Its selftest
   (72/72) is strong implementation evidence, not a release fact.
3. **Two surfaces, always separated.** Every ATP figure is labeled *permissive harness*
   (`glyphlib.py`) or *`church@v0` DRAFT*. The 601-ATP idiom figure and the 260,780/26,212,480/50M
   predicate figures are **permissive**; `church@v0` refuses `PLUS 7 5`.
4. **Name the comparator correctly (Codex P1-B3).** The executed in-language predicate is
   `EQN(m,n)=AND(LEQ(m,n),LEQ(n,m))`, **not** `ISZERO∘SUB`; the one-sided form is only an order
   predicate. Bind every figure to the exact executed term hash. Ship one typed 4-column outcome
   table (evaluator exit / harness comparison / profile settlement / meaning) so `VIOLATION`
   (harness) is not conflated with `UNEQUAL` (profile) or with `FAULT`/`REFUSED`/`UNSETTLED`.
5. **Failure boundary first** (v0.2 §3) — the collision counterexample precedes the contract.
6. **Soundness/completeness are profile OBLIGATIONS, argued not proved (Codex P0-B2).** §4 states
   them as the contract a real admitted profile would discharge; B4/B5 are argued conjectures
   inheriting an unproved λ→SKI compiler, not established propositions. Name the equivalence `~`
   exactly.
7. **Warrant = conformance, one-sided, AND pack-level `LEGACY_UNPINNED` (Codex P1-S1).** Report both:
   `warrant check 0597575d…` re-executes one stored check to PASS 2,108 ATP, while
   `replay_pack.py replay drafts/ssd-pack → LEGACY_UNPINNED` (exit 1). Never adoption, a two-sided
   receipt, a strict pack replay, or a proof of the theorem.
8. **The Σ-lemma is renamed** *hash-relative observation identity* (a representation invariant under
   named assumptions); "unconditional" is dropped (Codex P1-B4).
9. **Novelty is OPEN** pending external prior-art review; each prior-art source supports only its
   exact adjacent relation; a search log is required (Codex P1-B5).

## Section-by-section

| v0.1 element | disposition | why / how |
|---|---|---|
| Errata banner over the old body | **retire the banner-approach** | Replace with a rewritten body that speaks the repaired scope throughout; keep the errata *history* as v0.2 §8. |
| Title "Addressing Is Equality" | **rewrite** | Incident-and-repair title (cost gap / soundness boundary / blocked contract); slogan demoted to subtitle; NOT "on an admitted domain". |
| Abstract | **rewrite, FRONT-LOADED** | Placed at the front of the body (Codex P1-S4), from the ledger; drop "unconditional", "nothing else needs to be believed", "linear thereafter" (unqualified); label 601 ATP permissive; state no single impl carries the result. |
| §1 incident / cost table | **rewrite → v0.2 §1** | Keep the exact ATP figures but label the surface; name the predicate `AND(LEQ,LEQ)`; state the gap is engineering motivation, not a complexity theorem. |
| §3.1 admitted domain / EqualityProfile | **rewrite → v0.2 §2** | Full `church@v0` grammar/arity/binder/freshness at commit `196c45a`; **state it refuses `PLUS 7 5`** and cannot settle the motivating case (admission gap, EXP-ADR011-01); DRAFT/unreleased, selftest 72/72 ≠ release. |
| Soundness "equal addresses ⇒ equal values (unconditional)" | **retire → replaced by v0.2 §3.1 + §4 contract** | Executable marker collision first; then reflection/preservation as **profile obligations, argued not proved**; `~` named exactly. |
| Completeness | **rewrite → v0.2 §3.2/§4** | Canonical only for first-order data at a generic point; higher-order out of scope. |
| Termination / exit kinds | **keep → v0.2 §2/§3.3** | `ATP_EXHAUSTED` = UNSETTLED; both exit kinds in the receipt; full budget per side; `DISSONANCE` collision hazard explicit. |
| "601 ATP … linear … ~50 ATP/unit … nothing else needs to be believed" | **rewrite → v0.2 §5** | Observed points over a measured range on the permissive harness; `church@v0` ≈37 ATP/unit; remove "nothing else needs to be believed"; no general "linear" law. |
| §5 Warrant use case | **rewrite → v0.2 §7** | Report BOTH the per-check re-execution (PASS 2,108 ATP) AND pack-level `LEGACY_UNPINNED`; one-sided against a constant, not a two-sided receipt; ADR-011 DRAFT/blocked; a new dependency-closed pack must be a new artifact, not repaired history. |
| §6 consequences (semantic mass, gates, speculative) | **trim** | Keep only what a measurement supports; the "internal equality predicates are a smell" line stays flagged speculative, "not defended beyond the measurements". |
| Prior art (hash-consing/Merkle/NbE) | **rewrite → v0.2 §6, novelty OPEN** | Each source supports only its exact adjacent relation (Filliâtre–Conchon=hash-consing; Berger–Schwichtenberg=NbE, not "the" probe; Merkle=signature lineage, not result-identity authority); novelty candidate = budgeted receipted composition, treated as **OPEN** pending external review + search log; the deposit does not yet contain the two-sided composition end-to-end. |
| Falsifiers F1–F4 | **rewrite typed → v0.2 §9** | Typed relations; only `integrity_break`/`within-sample_counterexample` falsify; F1 novelty = `open_obligation`, F3 = `competitive_result`, F4 = `misuse_warning`, F5 = `scope_boundary`, F6/F7 = `integrity_break`. |
| Errata history | **elevate → v0.2 §8** | The repair trajectory is part of the publication; C1–C11 split stated (4 executable, 7 documentation-only). |

## Retired sentences (must not survive outside history/counterexample)

- "equal addresses ⟹ equal values" (unconditional).
- "nothing else needs to be believed."
- "601 ATP" presented as the cost of the idiom **without** the permissive-harness label.
- "linear thereafter" as a general complexity property.
- any wording that reads the Warrant pass as a proof of the semantic claim or as adoption.
- `church@v0` as a "released profile" (it is DRAFT @196c45a, unreleased).
- `EQN = ISZERO∘SUB` (the executed term is `AND(LEQ,LEQ)`).
- "the Σ-lemma is unconditional" (it is a hash-relative representation invariant).
- soundness/completeness stated as proved (they are argued profile obligations).
- novelty stated as established (it is OPEN pending external review).

## Comparator

`paper.md` (v0.1, with its errata) remains as history. On promotion, the working surface exposes
the supported argument with a version/history note; the false v0.1 claims live only in the git
history and in v0.2 §8's explicit errata section.
