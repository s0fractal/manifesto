---
title: "Measuring Verifier-Reported Verification Load on a Single LLM Monologue Corpus: A Report with Termination Controls"
status: v0.2 replacement draft (rev after Codex adversarial review 2026-09-01) — NOT the canonical paper.md; not deposited; not peer-reviewed
supersedes: paper.md (v0.1, "Every Check Spawns More: A Reflexive Verification Model (Conjectural)")
date: draft
license: CC-BY-SA-4.0
---

> **Draft status.** A from-scratch replacement written from the evidence boundary inward (see
> `CLAIM-LEDGER.md`), revised against Codex's adversarial review (`reviews/2026-09-codex-papers-v0.2.md`).
> The v0.1 file is retained as a historical comparator; see `MIGRATION-NOTES.md`. CC BY-SA 4.0
> under the repository's path-scoped license; no deposit, DOI, or claim of external validation.
> **Deposit is BLOCKED until the frozen act corpus is exported (§10) and the checker decides the
> repaired ledger (`DEPOSIT-AND-AUDIT.md`).**

## Abstract

Automated verification of informal claims can spawn new checkable obligations faster than it
discharges them. We make this measurable — not as a law but as an operational quantity. Under a fixed
protocol P, one strict LLM verifier per claim emitted a verdict and new claims, *judged* which were
load-bearing, applied a removal test, and deduplicated its own output; we call the per-act result the
**verifier-reported offspring count ô**, with self-adjudication part of the construct. On **one**
named informal corpus — the repository's *Monday* notes, a single-model monologue — ô sat near
**2–3** through the sampled depths (to 4), over selected paths, **not** an asymptote. Termination controls bound one narrow alternative (that the prompt *always*
produces a list): well-founded claims read **≈0.14** and stopped unaided. §0 states what this does
not establish. All verifiers are one vendor's models — within-family replication on a single corpus,
not independent validation.

*(Full negative-space table in §0; the defect-family glossary intervention (ô 3.13→2.11), the
compiled-check separate axis, and the retired queue model are §6–§7.)*

## 0. What this paper does and does not establish

| It establishes (for the tested configurations) | It does NOT establish |
|---|---|
| Protocol P yields a **verifier-reported** offspring count ô, self-adjudicated. | An independently-adjudicated count, or a law of verification/cognition/truth. |
| ô ≈ 2–3 on the informal corpus over the sampled selected paths; ≈0.14 on termination controls. | An unconditional *theorem*, *bound*, or *phase transition* at μ=1. |
| ô stayed non-zero through the finite depths sampled (to depth 4). | Any asymptotic value; the round-1 geometric extrapolation was disconfirmed. |
| One prose claim compiled to a priced deterministic check has a **terminal execution sub-act with zero emitted prose obligations**. | That compilation lowers the *same* ô, or that the compiled artifact captures the claim's meaning. |
| An external reviewer's counterexamples break the v0.1 closed forms. | Any *specified* replacement queue model — §7 is an open problem, not a result. |
| ô is verifier-dependent; and over four paired crossed roots, negative verdicts replicated while positive ones did not. | A clean "Fable vs Sonnet" factor effect (the 2×2 confounds verifier with root assignment). |

Status vocabulary is fixed: **measurement** (a number from a stated protocol), **negative result**
(a bounding counterexample), **open** (named, not established). *Local CI, evaluator replay,
independent review, publication, and adoption are different statuses, never substituted.*

All verifiers are large language models from a single vendor lineage (Anthropic). Cross-model
agreement is **replication across instruments of one family**, never out-of-lineage confirmation.

## 1. Research question

Checking ends by decision, not by completion — that is old. This paper asks whether the *rate* at
which a verification act produces new checkable obligations is **operationally measurable**, what a
measured value would and would not imply, and how the measuring instrument depends on itself.

The measured quantity is **ô = the verifier-reported number of new, load-bearing, checkable,
deduplicated obligations per act, under protocol P** — where "load-bearing", "novel", and the verdict
are all decided by the same verifier that produced the offspring. Self-adjudication is therefore part
of the construct; we do not present ô as an independent count.

## 2. Measurement protocol P

A **verification act** takes one claim and produces (i) a verdict —
`VALID | INVALID | UNVERIFIABLE-AS-STATED`, backed by attempted proof, counterexample search, or
evidence assessment — and (ii) new claims. The verifier counts an offspring only if, **in its own
judgment**, it is *checkable* (has truth conditions), *load-bearing* (survives a removal test: if
false, the parent verdict falls), and *novel* (deduplicated against every claim already recorded in
that tree/chain). All four judgments are the verifier's.

**Verifier setup.** One isolated agent per tree/chain, instructed to be strict and told the corpus
had never faced criticism. **Corpus** = the repository's *Monday* dialogue notes — a generator with
prior verification rate essentially zero.

**Sampling / depth (stated exactly, not as an unbiased estimator).** Round 1 expanded two offspring
at depth 0 and, at depth 1, the **first and middle** children — a *purposive*, non-random selection.
Round 2 expanded one offspring per act to depth 4. Because children are selected non-randomly and
deduplication is *global* (offspring depend on the whole tree), the depth-d means are
**selected-path descriptive means**, NOT unbiased generation-wide offspring means, and the process is
**not** an i.i.d. Galton–Watson branching process. Depth stops at 4; no asymptote is observed or
claimed.

**Provenance and reproducibility class.** Every ô is *transcript* evidence from a stochastic model.
**The full act corpus — exact prompts, model/API identity and sampling settings, root bytes, selected
child IDs at each depth, each offspring pre/post dedup, each removal-test decision, and every rejected
candidate — is NOT yet in the repository (§10).** Until it is exported, "same prompts" is not
actionable and no table is independently reproducible; the numbers below are the verifier's reported
measurements, deposited as a claim to be repaired, not as a finished reproducible artifact.

## 3. Measured results (raw before interpretation)

### 3.1 Round 1 — trees (Fable 5, 12 *Monday* roots, 60 acts)

Verifier-reported mean offspring by depth: **ô₀ = 5.42, ô₁ = 3.38, ô₂ = 2.50** (d0 spread 4–7,
sd ≈ 0.8). By claim type at d0: formal 5.50, empirical 5.50, conceptual 5.25 — no measurable type
effect. Verdicts: 0 VALID / 8 INVALID / 4 UNVERIFIABLE. Sixty acts reported 206 new load-bearing
assertions and 48 closed, a net backlog of +158. Depth-1 means are over the *first+middle* selected
children only.

### 3.2 Round 2 — chains, depth 4 (8 chains × 5 acts = **40 acts**)

Selected-path mean offspring by depth (over the 8 chains' single expanded paths):

| depth | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| ô_d | 3.50 | 2.75 | 2.50 | 2.13 | 2.25 |

The curve flattens near 2 and does not cross 1 within the sampled depth; the geometric decay
suggested by round 1 is **disconfirmed**. Across the **40** round-2 acts, no act reported zero
offspring (minimum 1, once). *(The number 100 in v0.1 was the cumulative Round 1 + Round 2 total,
60 + 40; it is not a Round 2 act count.)*

**Verifier and counting-instruction contrasts — reported as confounded, not as clean factors.** The
2×2 layout assigns different roots to different verifiers, so the raw Fable ≈3.15 / Sonnet ≈2.10 and
standard 2.80 / anti-quantization 2.45 means confound verifier with root assignment. The only
*paired* verifier contrast is the four crossed roots of §5.1 (n=2 per direction) — a small descriptive
paired difference, not an established factor effect. A verbatim-vs-paraphrased control lowered Fable's
reported ô₀ from 5.42 to 4.25 (~20% extraction inflation in round 1).

### 3.3 Uncertainty and sample size

Samples are small (12 + 8 + 6 + 3 roots). No significance test is claimed beyond direction and rough
magnitude. The counting-quantization prior is not excludable; an explicit anti-quantization
instruction moved the reported count only ~0.35 in the confounded layout.

## 4. Termination controls

Six roots where verification should terminate — `2+2=4` in PA (full derivation in-act), infinitude of
primes, SHA-256 digest width, water's boiling point at 1 atm, "all bachelors are unmarried", the
40-hex Git SHA-1 (recomputed by hand) — reported **ô ≈ 0.14 pooled** (one offspring across seven
acts), chains terminating unaided. Per-control: five reported 0; the primes chain reported 1 → 0.

**What this control does and does not do.** It **rejects one narrow alternative** — that the prompt
*always* forces a 2–7 offspring list regardless of input. It does **not** establish construct
validity: the controls differ from the corpus in length, domain, familiarity, access to an external
specification, proof depth, and statement complexity, so they do not isolate *groundedness* from
complexity/familiarity/domain. A style control (well-founded claims dressed in corpus rhetoric)
reported **ô₀ = 1.25**, with the Pythagorean-theorem chain *not* terminating (3,3,3,2,2) — evidence
that "well-founded" does not entail "self-discharging", and that rhetoric can add real quantifiers.

## 5. Verifier-relativity of the verdict (the four crossed roots)

Crossing four purposively-selected roots across verifiers (n = 2 per direction, one vendor lineage):

| root | Fable verdict | Sonnet verdict | agreement |
|---|---|---|---|
| 0030 confidence monotonicity | INVALID | VALID | **flip** |
| 0025 modal core (◇⁻/◇⁺) | UNVERIFIABLE | VALID | **flip** |
| FLOW §15 central thesis | UNVERIFIABLE | UNVERIFIABLE | agree (negative) |
| FLOW §17 "Player" | UNVERIFIABLE | UNVERIFIABLE | agree (negative) |

The two **positive** Sonnet verdicts (0030, 0025) fail to replicate under Fable; the two verdicts
that **agree** are *different* roots (FLOW §15, §17), both non-positive. So "negative replicated,
positive did not" is a statement about **two roots per direction**, not a matched 2/2-vs-0/2 on one
root set. After crossing, no informal corpus claim was VALID under both verifiers. Two counterexamples
explain the positive flips: a valid evidence-free inference can raise certainty
(P(A∨B) > max(P(A),P(B)) refutes monotonicity as a law), and budget-bounded reachability is
non-transitive (a three-node construction breaks the modal core's implicit transitivity).

## 6. Interventions

### 6.1 Amortization by a defect-family glossary (exact window)

A glossary closing *families* of defects was measured against three round-2 roots over an **exact
window**: the reported mean fell from **3.13** (all five pre-intervention acts of V1–V3, 47 offspring
/ 15 acts) to **2.11** (the three observed post-intervention acts, 19/9). Two of three chains reached
unaided termination — the **first such terminations on corpus material across the 120 corpus acts
prior to the glossary** (Round 1 + Round 2 + crossed = 60 + 40 + 20). The reduction is **non-monotone**:
a hasty repair drove one debt count 6→3→3→**7**, and over six iterations the count traced
6→3→3→7→4→8. The debt did not vanish; it migrated into the glossary and was ledgered there.
*(The v0.1 "3.33 → 2.11" compared the first three pre-acts (30/9) with the three post-acts (19/9); the
window is stated here explicitly.)*

### 6.2 One compiled instance — a terminal sub-act, on a separate axis

The claim 0030 was compiled to a deterministic, integer-only, priced Σ-GLYPH check over confidence
traces. A *closed execution sub-act* defined as "run the script, compare receipt bytes, stop" emits
**zero prose obligations**; settlement cost 4,151,277 / 554,678 / 25 ATP (clean / laundering /
evidence-licensed).

This is **not** on the same axis as ô and is not "compilation lowers μ". The surrounding verification
process did **not** become zero-offspring: this repository's own later closure, binding, dependency,
and receipt obligations are exactly the offspring a *review* of the compiled bundle would spawn. The
compiled number is zero only under a policy that treats the verifier, environment, and semantic
binding as **external operands**. Three constitutive losses: the artifact is a **weaker stipulation**;
**termination is not adequacy** (`return true` also terminates); **semantic binding is open** — the
gap is named, not crossed. A comparable intervention would run protocol P over the compiled bundle and
count what *that* review spawns; we have not done so.

## 7. A heuristic closure map and an open queueing problem (NOT a model result)

The v0.1 draft stated a branching/queue theorem; the repair does **not** silently replace it with an
unspecified one. §7 is a **heuristic map and an open problem**, removed from the title and abstract as
a result.

An honest queue model of this process would have to fix, and this paper does **not**: the queue state
and arrival process; whether and when offspring join the queue; service times and work-conservation;
the scheduler's observability and tie-breaking; whether offspring are i.i.d., depth-dependent, or
verifier/claim-dependent; the exact stability/throughput proposition; and the interpretation of μ ≥ 1
when closure sizes have infinite expectation. Note also that v0.1 used the symbol `g` inconsistently
(a "closure fraction" in prose, but `g = λ_G/λ_V` generative load in the numeric counterexample).

What is **established** here is only the *negative* result — an external reviewer's counterexamples
break the v0.1 closed forms for other schedulers:

- A short-closure-first scheduler with P(N=0)=¾, P(N=2)=¼ (μ=0.5), g=0.8 closes 75% immediately,
  while the v0.1 bound demanded ≥37.5% unclosed — violated.
- With P(N=0)=0.4, P(N=2)=0.6 (μ=1.2), 40% close on the first act, so "throughput → 0" fails.
- The anchor leg needs **well-foundedness**, not mere acyclicity.
- An expiry equilibrium would require a **reflected, non-negative** queue (`max(0, (λ_G−(1−μ)λ_V)/δ)`);
  the v0.1 formula can go negative.

These counterexamples suffice to retire the theorem; they do **not** validate any replacement. The
replacement is left to a reviewer with the relevant expertise, and "open" here means *open to us*,
**not** claimed novel: under one natural set of assumptions — a work-conserving FIFO server, no
abandonment, and each root closing as a Galton–Watson tree with mean total progeny 1/(1−μ) — this is
a queue with branching-type service, and a stability result of the form "closes iff λ_G < (1−μ)λ_V"
is likely already **standard** in the branching-process / general-branching literature
(Crump–Mode–Jagers, Bellman–Harris). The honest framing is therefore "reduces to a known form under
assumptions A, and the counterexamples above show it fails under B", not "a new open problem". We do
not assert which citation settles it — that is exactly the one-hour check for a queueing-theory
reviewer. A minimal executable simulation of the two counterexamples ships with the artifact so the
retired theorem cannot return (`DEPOSIT-AND-AUDIT.md`).

## 8. Historical settlement episode (legacy inline gate)

One generated repository summary (a model forbidden to verify) produced **11 embedded claims**. The
**legacy inline settlement gate** settled 7 and refuted 4 (5,638 ATP); all four refutations were
world-fact `count`-class memory guesses; internal arithmetic survived; a corrected pass reached 11/11.

Two boundaries, filed as results: the same 11/11 case **badges a false marked operand**
(`⟦arith: 3+6=9⟧` green over a tree with 8 files and 8 directories — the gate binds marked operands,
not the sets they count), and a live re-run drifts to 10/1 as a `count` value changes; a companion
index audit filed 30 citation predictions of which **2 held verbatim, 10 failed on capitalization,
18 were absent**. **This used the legacy inline gate.** The capsule-only PARSE→COMPILE→RUN pipeline is
subsequent work and is not substituted into this experiment; the inline artifacts remain evidence
about this episode insofar as their receipts replay.

## 9. Threats to validity and typed falsifiers

**Threats.** Self-adjudicated construct (the verifier judges its own offspring); common single-vendor
lineage; purposive non-random child selection and global dedup (selected-path, not population, means);
small corpus, finite depth; the queue model is unspecified; all ô are transcript evidence, and the
underlying act corpus is not yet deposited (§10).

**Typed relations (not all falsifiers).** A single "falsifier" column conflated distinct relations; we
type them:

| observation | relation | falsifies the stated claim? |
|---|---|---|
| A number fails to re-derive from the frozen act corpus | `integrity_break` | **yes** |
| A chain in the *frozen sample* is found to reach 0 at depth ≤4 | `within-sample_counterexample` | **yes** |
| A later re-run reports counts outside the spread | `replication_failure` | no — challenges generalization, not the historical count |
| A future *released* profile or different corpus reads differently | `competitive_result` | no |
| A glossary pass elsewhere reduces debt monotonically | `scope_boundary` | no — the observed episode was non-monotone |
| Someone reads Warrant conformance as endorsement | `misuse_warning` | no |
| An out-of-domain term behaves differently | `open_obligation` | no, unless the claim is about admission enforcement |

## 10. Artifact map, provenance, and the deposit blocker

- **Model / date.** Anthropic "Fable 5"; date on file. Byte reproducibility not claimed for LLM counts.
- **Summary records (present).** `drafts/EXP-RVB-1-RESULTS.md`, `drafts/RVB-0.1-REFLEXIVE-VERIFICATION-BOUND.md`.
- **Frozen act corpus (REQUIRED, not yet present — deposit blocker).** A machine-readable, append-only
  export with exact source/model/prompt/selected-child/pre-and-post-dedup/removal-decision/rejected-candidate
  fields, from which every table regenerates. Until then ô is a verifier-reported quantity awaiting an
  independent re-derivation.
- **Compiled instance.** `tools/conf_mono_settle.py` (verdicts/ATP replay live).
- **Legacy episode.** SSD-DEMO receipts, index audit. **Warrant pack:** the named stored SKI checks
  re-execute under Warrant (e.g. the AIE check at 2,108 ATP), while the pack *as a whole* is
  historically sealed / `LEGACY_UNPINNED` and is **not** strict-replayable (`drafts/ssd-pack/STATUS.md`).
  Both facts are reported; neither cancels the other.
- **Checker.** The current `check_claims.py` is **stale-green w.r.t. this ledger** — it finds summary
  literals, not re-derived acts. `DEPOSIT-AND-AUDIT.md §A` specifies the closed-manifest checker that
  must replace it before deposit.
- **Licensing.** Paper + documentary artifacts CC BY-SA 4.0; executable deposit software AGPL-3.0-only;
  `LICENSE` is the scope authority. No DOI/tag/deposit here.
