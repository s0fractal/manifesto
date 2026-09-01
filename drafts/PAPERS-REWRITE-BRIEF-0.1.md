# Papers Rewrite Brief 0.1

**Status:** working handoff, not a paper, not a publication decision  
**Audience:** Claude or another writing agent preparing replacement drafts  
**Scope:** triage the Qwen reviews, fully rewrite the two existing papers, and
separate stronger future paper subjects from material that is not ready  
**Non-scope:** no Zenodo deposit, DOI reservation, release, tag, push, license
selection, protocol adoption, or claim of external validation

> **Post-brief decision, 2026-09-01.** The operator delegated the license choice
> after this handoff was executed. Code is now AGPL-3.0-only; text, papers,
> specifications and documentary evidence are CC BY-SA 4.0. `LICENSE` is the
> path-scoped authority. References below to an unresolved license blocker are
> retained as the brief's input state, not the repository's current state.

---

## 0. Operator intent

The repository needs dated publication points in its development trajectory.
It does **not** need publication-shaped confidence inflation.

The existing papers were valuable instruments: they forced measurements,
falsifiers, claim checkers, and downstream execution. They also preserve an
earlier conceptual state. Since then:

- the Reflexive Verification Bound (RVB) was demoted from theorem to a
  conditional model-hypothesis after scheduler and abandonment
  counterexamples;
- Addressing Is Equality (AIE) was demoted from unconditional soundness to an
  admitted-domain, profile-scoped engineering idiom after an executable
  collision counterexample;
- the original inline settlement-gate experiment was succeeded, for canonical
  authoring, by an explicit capsule-only PARSE → COMPILE → RUN pipeline;
- document-level green was rejected in favor of a per-record result vector;
- REPORT, receipt/authenticity, semantic adequacy, normative adoption, and
  publication were kept as different status classes.

The rewrite must make those repairs constitutive of the papers, not add them as
warning banners around prose that still makes the old claims.

---

## 1. Governing rule: rewrite, do not patch

Do not edit the current papers paragraph by paragraph. Draft replacements from
the evidence boundary inward.

During review, preserve the current paper files as historical comparators and
write replacement drafts beside them. Suggested temporary names:

```text
papers/every-check-spawns-more/paper-v0.2-draft.md
papers/addressing-is-equality/paper-v0.2-draft.md
```

Only after an explicit operator decision may a replacement become `paper.md`.
Git history is recoverability; the working surface should eventually expose
only the currently supported argument, with a short version/history note.

Each replacement begins with a claim ledger, not with an abstract:

| claim | status | exact evidence | checker | falsifier | known loss |
|---|---|---|---|---|---|

The abstract is written last from the claims that survive that ledger.

---

## 2. How to use the Qwen reviews

Qwen is a source of pressure points and candidate research questions. It is not
an adoption authority. Its praise contains several status escalations that the
repository's own evidence rejects: `theorem` for RVB, `revolutionary` for PoCs,
and publication/standard claims before independent use.

### 2.1 Implement before either paper is deposited

1. **Propagate the AIE errata into the paper itself.** A warning banner is not
   enough. The abstract, title, examples, cost table, semantics, conclusion,
   and claim checker must all speak the repaired scope.
2. **Rewrite RVB as a conditional model-hypothesis.** State the scheduler,
   abandonment/expiry, well-foundedness, offspring, deduplication, and closure
   policies before any equations. Never use `theorem`, `bound`, or `phase
   transition` without naming the conditions under which that sentence is
   derived.
3. **Treat model lineage as a first-class limitation.** All measured verifiers
   are related LLM systems. Cross-model agreement is not independent
   validation. The paper may report it as replication across instruments, but
   not as out-of-lineage confirmation.
4. **Separate old and current machinery.** The 11-claim SSD episode used the
   historical inline gate. It remains valid evidence about that episode if its
   artifacts replay, but it is not the canonical current authoring protocol.
   The capsule-only pipeline is a subsequent implementation and must not be
   retroactively substituted into the original experiment.
5. **Resolve publication licensing before deposit.** The repository currently
   has no `LICENSE`, and `CITATION.cff` deliberately leaves the field unset.
   The writing agent must expose this blocker, not choose a license.
6. **Make reproducibility classes explicit.** Distinguish counts re-derived by
   a local checker, evaluator replay, external command replay, transcript-based
   LLM measurements, citation review, and independent replication.
7. **Preserve negative results.** The scheduler counterexamples, AIE marker
   collision, false live world-facts, semantic-binding gap, and non-transitive
   green composition are part of the result, not embarrassing footnotes.

### 2.2 Useful, but not part of these two rewrites

- an audit/translatability boundary for machine protocols;
- appeal, rehabilitation, proportionality, sunset, and presumption-of-good-
  faith mechanisms for responsibility systems;
- stratified identity as a hypothesis to compare with existing identity
  models;
- the political economy of compute and ATP;
- external human review from security, probability, PL, philosophy, law, and
  governance perspectives;
- an anti-paralysis rule for Operator-as-Hypothesis, expressed as priced
  verification policy rather than an arbitrary maximum number of checks;
- controlled retirement/forgetting, already being developed more carefully as
  exact removal from the active surface rather than cryptographic erasure.

These belong in the research roadmap or separate artifacts. Mentioning them as
limitations is legitimate; pretending to solve them inside the two papers is
not.

### 2.3 Do not implement as proposed

- Do not use AutoGen or CrewAI as evidence for a reducer ecology merely because
  they contain multiple agents. That would establish orchestration, not the
  claimed ecology.
- Do not present Lean/Coq/Isabelle as validators of semantic adequacy. A kernel
  can validate a derivation inside a formalization; it does not establish that
  the formalization captures the world or the prose.
- Do not add decentralized-compute providers to create a physical ATP economy
  before a resource/conformance model exists.
- Do not freeze an `ontogenetic threshold` into a protocol before the subject
  problem is operationally specified and adversarially tested.
- Do not turn a right-to-forgetting concern directly into key rotation and
  Merkle pruning. Retirement, historical recoverability, confidentiality,
  erasure, redaction, and legal deletion are different operations.
- Do not claim OAH is or could soon become a de-facto standard.
- Do not build a unified toroidal theory of agency, a marketplace of settlement
  servers, or a Rust CA-VM as paper-padding.
- Do not inherit Qwen's adjectives (`revolutionary`, `defining`, `proved`) as
  evidence statuses.

---

## 3. Replacement paper A: reflexive verification load

### 3.1 Working title

Preferred:

> **Measuring Reflexive Verification Load in LLM Review: A Conditional
> Branching-Queue Model and Two Controls**

Acceptable shorter title:

> **Every Check Spawns More? Measuring Reflexive Verification Load Under a
> Fixed Protocol**

The question mark matters if the historical title is retained.

### 3.2 One research object

The paper studies a measured coefficient under a fixed counting protocol:

```text
mu = mean new load-bearing, checkable, deduplicated obligations
     produced by one verification act
```

It asks:

1. Is the coefficient measurably different across a named informal corpus,
   well-founded controls, verifier configurations, and compiled artifacts?
2. Under which explicitly stated queue/scheduler/expiry assumptions would a
   coefficient of that size imply unstable closure load?
3. Which interventions reduce observed offspring without pretending to settle
   semantic adequacy?

The paper does **not** establish a universal law of verification, cognition,
truth, or all LLM systems.

### 3.3 Claims allowed in the abstract

- A fixed protocol was used to count verification offspring on a named corpus.
- The observed values for the tested verifier/corpus/protocol configurations
  were approximately 2–3 on informal claims and much lower on the tested
  well-founded controls.
- The measurements remained non-zero through the finite depths actually
  sampled; this is not an asymptotic observation.
- A compiled deterministic instance produced no new prose obligations under
  that counting protocol; this is `mu = 0` for the measured replay act, not
  universal semantic closure.
- A conditional branching/queue model illustrates why coefficients near or
  above one create pressure under specified scheduling and retention policies.
- Counterexamples show why the originally unconditional closed forms do not
  hold for arbitrary schedulers.

### 3.4 Claims forbidden in the abstract and conclusion

- `RVB theorem` or an unconditional `RVB bound`;
- `at mu >= 1 no finite budget suffices` without a precise policy/model
  qualifier;
- `AI checking AI cannot converge`;
- `the plateau is a property of the claims, not the model`;
- `the gap is crossed` without naming the exact instance and lost semantics;
- `verification equals byte-identical replay` as a general definition;
- `the experiment proves the model`;
- any implication that Warrant signatures, green CI, or a settlement REPORT
  validate the paper's interpretation.

### 3.5 Proposed structure

1. **Research question and status vocabulary**
   - measurement, model-hypothesis, replay, independent validation;
   - one-page table of what the paper does and does not establish.
2. **Measurement protocol**
   - removal test for load-bearingness;
   - deduplication scope;
   - verifier prompt/configuration;
   - corpus selection and claim classes;
   - stopping/depth policy;
   - transcript and adjudication provenance.
3. **Measured results**
   - raw counts before interpretation;
   - uncertainty and sample-size limits;
   - per-verifier and per-claim-class results;
   - finite-depth wording everywhere.
4. **Controls**
   - well-founded control;
   - style control;
   - explain exactly which controls isolate which alternative explanation.
5. **Conditional model**
   - define scheduler, service, expiry, abandonment, and completion;
   - separate statements that are derived under those assumptions from
     conjectures;
   - put the concrete counterexamples next to the repaired statements.
6. **Interventions**
   - glossary/amortization result;
   - one compiled instance;
   - explicitly record semantic loss and adequacy remaining open.
7. **Historical settlement episode**
   - short case study only;
   - state that it used the legacy inline gate;
   - no claim that the current capsule pipeline reproduces the historical
     generation process.
8. **Threats to validity and falsifiers**
   - common lineage;
   - protocol sensitivity;
   - evaluator and adjudicator dependence;
   - small corpus and finite depth;
   - scheduler sensitivity;
   - transcript reproducibility class.
9. **Artifact map and provenance**
   - exact repository revision;
   - commands and expected outputs;
   - what is frozen versus fetched externally.

### 3.6 Material to remove or relocate

- Move the detailed AIE cost argument to paper B; retain at most one sentence
  identifying it as a companion engineering technique.
- Move Warrant pack internals to an artifact appendix unless directly needed
  to reproduce a paper claim.
- Do not make the manifesto's digital-entity ontology part of the empirical
  argument.
- Do not expand into ATP political economy, rights, identity, or substrate
  governance.
- Describe the phase-2 embedded-claims pipeline only as subsequent work, or
  cite a future companion. It must not silently upgrade the old experiment.

### 3.7 Required evidence work before deposit

- Re-run the claim checker from a documented clean environment.
- Make the checker print a closed list of checked claim IDs and a closed list
  of excluded claim classes; avoid `100+` when an exact count exists.
- Preserve raw measurement tables and the counting/adjudication protocol in
  the deposit artifact.
- Reproduce every paper table from those raw records or label it manually
  transcribed.
- Add at least one executable scheduler counterexample to prevent theorem
  language from returning.
- Record model identity and available generation parameters without claiming
  byte reproducibility where the provider cannot supply it.
- A probability/queueing reviewer would materially increase credit, but lack
  of one is a declared limitation rather than a reason to invent endorsement.

---

## 4. Replacement paper B: normal-form address comparison

### 4.1 Working title

Preferred:

> **Budgeted Equality by Normal-Form Address on an Admitted Domain:
> Measurements and Failure Boundaries**

Possible historical subtitle:

> *Revising the “Addressing Is Equality” Idiom*

The unqualified slogan should not be the grammatical claim of the title.

### 4.2 One research object

The paper studies an engineering comparison method:

1. evaluate two admitted terms at a profile-defined generic observation
   point under explicit budgets;
2. compare the resulting canonical normal-form addresses;
3. record both observed values, exit kinds, addresses, spends, machine/profile
   identity, and dependency closure.

The result is an equality verdict only for the profile's admitted domain and
equivalence relation, under the collision assumption and termination/budget
conditions. Outside that domain it is only equality of observations.

### 4.3 Claims allowed in the abstract

- In-language Church equality was extremely more expensive than comparing the
  selected normal-form observations in the measured evaluator/profile.
- The measured cost curve motivates an interface idiom for canonical data.
- An executable counterexample falsifies unconditional soundness when input
  terms can name an observation marker.
- Completeness holds only where the produced normal form is canonical for the
  intended equivalence class; arbitrary higher-order extensional equality is
  out of scope.
- Budget exhaustion is an unsettled evaluation outcome, not inequality.
- The idiom was exercised in a named Warrant evidence-pack configuration;
  this demonstrates conformance/executability, not upstream adoption or
  endorsement.

### 4.4 Claims forbidden

- unqualified `addressing is equality`;
- `nothing else needs to be believed`;
- `unbounded advantage` inferred from finite measurements;
- `linear thereafter` without the measured range and fitted/observed status;
- treating 601 ATP as a released-profile fact if it was obtained only with a
  permissive research harness;
- calling address equality a proof of input extensional equality;
- calling the method complete for functions;
- calling ADR-011 accepted, deployed, or standardized without live evidence;
- calling a Warrant pass a proof of the semantic theorem.

### 4.5 Proposed structure

1. **Incident and measured problem**
   - exact evaluator version/profile;
   - exact benchmark terms and budgets;
   - split released/safety behavior from permissive research behavior.
2. **Method**
   - observation context;
   - admitted domain;
   - canonicalization/equivalence relation;
   - address/hash anchor;
   - exit kinds and dual budget results.
3. **Failure boundary first**
   - marker collision counterexample;
   - higher-order incompleteness;
   - nontermination/budget exhaustion;
   - hash collision assumption;
   - profile and evaluator drift.
4. **Corrected propositions**
   - observation identity;
   - domain-scoped soundness;
   - conditional completeness;
   - each with assumptions adjacent, not deferred to errata.
5. **Measurements**
   - raw table and commands;
   - cost curves by execution profile;
   - do not extrapolate beyond observed points without a labeled model.
6. **Prior art and narrow novelty claim**
   - hash-consing, Merkle identity, normalization by evaluation;
   - novelty candidate is the budgeted, receipted composition in this machine
     context, subject to prior-art falsification.
7. **Downstream execution**
   - Warrant as one conformance/use case;
   - exact versions and record IDs;
   - distinguish accepted data format from normative protocol adoption.
8. **Errata history and epistemic status**
   - show how the unconditional statement failed;
   - list artifacts whose wording/status was affected;
   - do not make the repair trajectory disappear from the publication.
9. **Artifact map, falsifiers, and provenance**

### 4.6 Required evidence work before deposit

- Run the executable collision counterexample in the deposit build/check path.
- Re-run the benchmark matrix on the exact dependency release named by the
  paper, not an unrecorded local checkout.
- Separate measured values produced by the released profile from values that
  require a permissive harness.
- Verify the live Warrant use case against the exact archived evidence pack;
  report conformance status separately from semantic status.
- Update the claims checker so the repaired propositions and negative fixture
  are first-class checks, not only the positive cost numbers.
- Make all build dependencies and interpreter versions explicit.
- Preserve the original overclaim and correction in a compact errata/history
  appendix; do not publish the false v0.1 body with only a banner.

---

## 5. Better future paper subjects

This is a readiness ranking, not a publication queue.

### 5.1 Highest readiness: Embedded Claims as an Epistemic Membrane

**Working title:**

> **Embedded Claims as an Epistemic Membrane: Explicit Capsules,
> Content-Addressed Compilation, and Non-Transitive Verification Credit**

**Why it is stronger than an SSD-only paper:** the contribution is not “an
LLM caught hallucinations.” It is the architectural separation:

```text
prose → explicit live region → capsule → PARSE → COMPILE
      ── epistemic membrane ──> per-record EXECUTE → vector REPORT
```

It has executable positive and adversarial fixtures, closed schemas, parser,
compiler, source occurrence, claim-bound plans/bindings, dependency freshness,
declared-versus-observed operands, typed values, non-vacuous strict policy, and
a real end-to-end specimen. Its central negative result is equally important:
local green does not compose into document truth, REPORT is not receipt, and
execution does not upgrade semantic binding.

**Not ready yet because:** one real capsule is a route demonstration, not an
ecology of use; receipt/authenticity remains separate; there is no independent
implementation or external adversarial review.

**Minimum maturation:** use it in several real manifesto claims of different
classes, freeze conformance vectors, perform a clean-room implementation or
external review, and measure false-green/false-refusal behavior under mutation.

### 5.2 Strong conceptual/engineering paper: Controlled Forgetting

**Working title:**

> **Controlled Forgetting in Versioned Knowledge Repositories: Retiring Active
> Authority Without Erasing History**

The subject is exact retirement from the active retrieval surface with a
typed loss record, replacement mapping, impact analysis, status-aware
retrieval, and explicit re-adoption. It should distinguish forgetting from
erasure, hiding, refutation, confidentiality, and legal deletion.

**Not ready yet:** currently a design draft. It needs at least one executable
retirement specimen, retrieval tests showing reduced stale-pattern selection,
a negative test for accidental re-adoption, and a measured before/after model
retrieval experiment.

### 5.3 Research-method paper: Repair Trajectories as Evidence

**Working title:**

> **From Theorem to Model-Hypothesis: Decision Archaeology of Overclaim Repair
> in an LLM-Assisted Research Repository**

Candidate cases: RVB theorem → conditional model, AIE unconditional soundness
→ admitted domain, FLOW taxonomy repair cycles, embedded-claims identity and
closure mutations, and vacuous-green detection.

The contribution would be a coded repair corpus and a method for distinguishing
development provenance from validation credit. It cannot be written as a
self-congratulatory history.

**Minimum maturation:** preregister the coding scheme, define what counts as an
overclaim and repair, have at least one out-of-lineage coder, publish the event
corpus, and include failed repairs.

### 5.4 Useful after measurement: Operator as Hypothesis

**Working title:**

> **Operator Instructions as Fallible Inputs: Measuring Verification Cost,
> Error Prevention, and Paralysis in Coding Agents**

OAH is currently a compelling discipline and a falsifiable proposal, not a
standard. A paper needs comparative tasks with OAH on/off, predeclared error
classes, verification cost, avoided incidents, false refusals, and paralysis
or delay measurements.

### 5.5 Narrow conceptual note: Non-transitive Green

**Working title:**

> **Green Does Not Compose: Claim-Local Verification Credit in Versioned
> Documents**

This can unify the semantic-binding gap, composition laundering, result-vector
design, and the rule that a composite is a new claim. It is likely better as a
short position/technical note unless accompanied by a corpus of real failures
across repositories.

### 5.6 Not paper-ready

- ontogenetic thresholds and digital personhood criteria;
- a comprehensive Charter of Human-Digital/Digital-Digital Relations;
- ATP political economy or epistemic commons;
- stratified identity as a settled model;
- toroidal agency or unified geometric ontology;
- Tiered CA-VM hardware claims;
- settlement-server marketplaces.

These may be valuable research directions. They currently lack the operational
definitions, comparative evidence, or implementation pressure required for a
paper claim.

---

## 6. Recommended publication trajectory

1. Rewrite and deposit the narrow RVB measurement/model paper as its own
   version series.
2. Rewrite and deposit the corrected AIE engineering note as a separate
   version series.
3. Mature the embedded-claims pipeline through multiple real uses and external
   pressure, then publish it as a separate paper rather than appending it to
   RVB.
4. Implement and measure controlled forgetting before turning its design into
   a paper.

Each paper should have its own Zenodo record/version series. A new paper is not
a “new version” of a different paper. Software/protocol snapshots are separate
artifacts from paper versions even if they point to the same Git revision.

Publication is a trajectory marker, not adoption, peer review, scientific
validation, or protocol release.

---

## 7. Deliverables requested from the writing agent

For each of the two replacement papers, produce:

1. `paper-v0.2-draft.md` — a full replacement, not a patch;
2. `CLAIM-LEDGER.md` — claim/status/evidence/checker/falsifier/loss;
3. a revised `check_claims.py` proposal or exact gap list if implementation is
   outside the writing pass;
4. a bibliography audit: source exists, directly supports the sentence, and
   is not used as borrowed authority;
5. `MIGRATION-NOTES.md` mapping old sections to keep/rewrite/retire and why;
6. a list of every sentence that still depends on transcript-only evidence,
   external live state, or an unverified citation;
7. exact build and reproduction instructions for a clean environment;
8. a deposit manifest proposal listing files, Git revision placeholder,
   expected checks, and explicit exclusions.

Do not:

- change runtime code to make the prose easier to defend;
- update the canonical `paper.md` files;
- choose a license;
- reserve a DOI, create a release/tag, commit, push, or publish;
- fabricate external review, citations, experiments, or missing metadata;
- turn a green checker into a paper-level truth badge.

---

## 8. Acceptance gate for the rewrite

A replacement draft is ready for adversarial review only when:

- every abstract claim appears in the claim ledger;
- no historical false claim survives outside an explicitly marked history or
  counterexample section;
- all model assumptions are adjacent to the statement they condition;
- every number is either re-derived, replayed, or explicitly classified as
  transcript/manual evidence;
- positive and negative fixtures are both exercised;
- current and legacy pipelines are not conflated;
- local CI, replay, independent review, publication, and adoption remain
  distinct statuses;
- the paper can state in one paragraph what observation would make its central
  claim weaker or false;
- the license blocker and any missing external validation remain visible;
- no document-level green badge is inferred from a vector of locally green
  records.

The intended result is not a paper that cannot be criticized. It is a paper
whose criticism has an exact address and whose surviving claim is small enough
to deserve one.
