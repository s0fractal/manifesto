# Adversarial review — manifesto papers v0.2 replacement drafts

**Reviewer:** Codex (OpenAI), 2026-09-01
**Disposition:** **BLOCKED for promotion and Zenodo deposit**; both drafts are materially better
than v0.1 and are repairable.
**Scope:** the two four-file v0.2 packages, their declared evidence, current checkers, the legacy
SSD/Warrant pack, and the exact Sigma-Glyph profile they cite. This review does **not** edit either
paper and does not review the embedded-claims implementation except where a paper borrows its
status vocabulary.

## 0. Bottom line

The rewrite succeeded at the most important ethical task: the old universal claims are no longer
quietly laundered through an errata banner. The drafts now expose failure boundaries, distinguish
permissive and admitted evaluation, keep semantic binding open, and refuse to turn local green into
document truth.

They are nevertheless not deposit-ready. Four blocker families are load-bearing:

1. Paper A's primary measurement corpus is not in the repository: the full acts, prompts,
   offspring texts, removal decisions, and dedup decisions remain in chat transcripts. The current
   checker finds summary **strings**, not the measurements.
2. Paper A's branching/queue contribution is still not a specified model. Its central paragraph
   changes the meaning of `g`, omits the stochastic process and proposition, and cannot be derived,
   simulated, or falsified as written.
3. Paper B repeatedly calls `church@v0` a **released** profile and writes as if the admitted-domain
   method exists for the motivating computation. The profile is instead a DRAFT, non-gated,
   blocked proposal 175 commits after `v0.6.7`, and it refuses that computation.
4. The current checkers do not decide the proposed ledgers: one searches for summary literals,
   another depends on an absolute sibling-checkout path, and neither deposit build targets v0.2.

The right response is **not** to implement the present checker gap-lists verbatim. First repair the
ledgers and paper claims below; then make the checkers decide those repaired ledgers.

## 1. Review binding and method

Repository base inspected: `d1d0a6cf5f4c11b185ac7a149ab293cac5a3c2b1` with the papers and
licensing work uncommitted. To make this review addressable despite that state, the reviewed files
are bound by content digest:

| package file | sha256 |
|---|---|
| `every-check-spawns-more/paper-v0.2-draft.md` | `570b0ff8a76df53932292970173ddbbcfbe5c3c5209d22295d7f9f3cafffec60` |
| `every-check-spawns-more/CLAIM-LEDGER.md` | `40ff6d5c7fcb2e5160d4cc4b9a5ace618f81ed58e064b3cb416119bd459bdf2c` |
| `every-check-spawns-more/MIGRATION-NOTES.md` | `fd55b08b35f834eab347a8096a1cde86df63618e573cd5fd4353c22a570eaa71` |
| `every-check-spawns-more/DEPOSIT-AND-AUDIT.md` | `8e95ff8c83e0f85fb9539e63004830db670178dd6098812d1a06950cac12f065` |
| `addressing-is-equality/paper-v0.2-draft.md` | `b4755d8eb13d045023538bf17fe359e6bba9b3d178af315aac10ff61b2eb5d2a` |
| `addressing-is-equality/CLAIM-LEDGER.md` | `049d78de378665bf4c2eaf528774c92b5de71638ac02d4e5b13007bd20e75cee` |
| `addressing-is-equality/MIGRATION-NOTES.md` | `f0a06d3cf3eab658606132da42c1c162bf33c45d2b62f5081bc1579ff438d9fe` |
| `addressing-is-equality/DEPOSIT-AND-AUDIT.md` | `fe4a433751c9f39ecbb84c5af7d9879ab3217eac6e50a82b64328bd7028ef975` |

Checks were run in a fresh temporary Python 3.14.7 venv containing the published
`sigma-glyph==0.6.7` wheel. I also inspected Sigma-Glyph
`196c45a2f9074a472b96af1a6bae2c67533edbb1` (`v0.6.7-175-g196c45a`) read-only and ran its
ADR-011 selftest and benchmark check.

Severity means:

- **P0** — promotion/deposit blocker or a claim whose present evidence/status is false;
- **P1** — material scientific, semantic, or reproducibility repair required before deposit;
- **P2** — publication-quality or clarity repair that does not change the central result.

Each finding names a target, reproducer/observation, why it matters, and a closure condition.

## 2. Cross-paper findings

### [P1-S1] Per-check Warrant replay and pack-level strict replay are different credits

**Targets:** Paper A §7 lines 238–241 and artifact map; Paper B §0, §7, abstract; Paper B ledger B7;
both deposit/audit files' Warrant classifications.

The narrow Paper B execution claim is live: using the current local Warrant implementation,
`warrant verify --settlement` reports 4 records, 0 errors, 0 warnings, and
`warrant check 0597575d…` re-executes the stored AIE check to `PASS` at 2,108 ATP. That credit should
be kept.

It is not the same as strict replay of the evidence pack. The current repository says in
`drafts/ssd-pack/STATUS.md` that the pack is historically sealed, recorded no dependency closure,
and strict pack replay is impossible.

**Reproducer:** with the published evaluator wheel:

```sh
python tools/replay_pack.py replay drafts/ssd-pack \
  --evaluator sigma_glyph-0.6.7-py3-none-any.whl
```

Observed:

```text
REPLAY: LEGACY_UNPINNED
exit 1
```

Thus a stored machine check inside the pack is locally replayable, while the complete historical
claim/dependency bundle is `LEGACY_UNPINNED`. Neither result cancels the other. The paper's own
current vocabulary makes that vector distinction constitutive.

**Required closure — choose one:**

1. say exactly that the named stored SKI checks re-execute under Warrant, while the pack as a whole
   is **historically sealed / `LEGACY_UNPINNED` and not strict-replayable**; and
2. if pack-level `MATCH` is desired, create a new, explicitly non-historical, dependency-closed
   pack. Do not mutate the old pack or reconstruct missing historical pins.

### [P0-S2] Current green checkers are stale-green with respect to the proposed ledgers

**Targets:** both `check_claims.py`; both deposit §A and acceptance self-checks; Paper A §9; Paper B
§9.

The green runs are real but decide much less than their final banners suggest.

- Paper A lines 98–104 check only that μ **literals occur somewhere** in
  `EXP-RVB-1-RESULTS.md`; they do not parse a row, recount an act, verify a denominator, or bind a
  number to a claim ID.
- Paper A's receipt loader discards `RECEIPT_SHA256` without verifying it.
- `SSD-INDEX-AUDIT.receipt.json` commits source digest `dad53f…`, while the current
  `SSD-INDEX-AUDIT.md` is `0a75d8…`; the checker combines the old receipt with current files and
  remains green.
- Paper B checks the two Warrant ATP values by reading `manifest.json`; it does not execute the
  checks. It prints that omission, but the paper still says “re-executes.”
- Paper B's ADR check is an absolute, author-machine path:
  `/Users/s0fractal/Projects/sigma-glyph/proposals/ADR-011-eq-by-normal-form-address.md`.
  A stranger's clean checkout cannot satisfy this path, and existence does not establish the
  proposal's digest, status, or implementation.
- Both final banners say they match `paper.md`, although the reviewed claim surfaces are the
  unpromoted v0.2 files.

This is the exact failure mode the embedded-claims work was built to prevent: a true local check
borrowing a broader claim.

**Required closure:** compile a closed ledger manifest into checks, bind each checked number to a
claim ID/profile/source row, verify receipt commitments before consuming bodies, and emit exact
`checked`, `excluded`, and `refused` sets. A missing raw record must be a typed refusal, not a
successful string-presence check. The deposit gate must invoke the v0.2 artifact it is depositing.

### [P1-S3] “Falsifier” currently mixes five different relations

**Targets:** Paper A §8 and C1–C8; Paper B §9 and B1–B8.

Several listed falsifiers cannot falsify their row:

- a future rerun outside Paper A's spread challenges replication/generalization; it does not erase
  the historical measured count;
- one corpus chain reaching zero would refute “no zero occurred” only if it were in the frozen
  sample, not in a later run;
- a glossary pass that monotonically reduces debt does not falsify the observed non-monotone
  episode;
- a future released profile with different costs does not falsify permissive-harness measurements;
- someone reading Warrant conformance as endorsement is misuse, not an empirical falsifier;
- an out-of-domain term is irrelevant to a domain-scoped semantic proposition unless the claim is
  about admission enforcement.

**Required closure:** replace the single column with typed relations:
`integrity_break`, `within-sample_counterexample`, `replication_failure`, `scope_boundary`,
`competitive_result`, `misuse_warning`, and `open_obligation`. Only call the first two a falsifier
of the claim as stated.

### [P1-S4] The publication package currently builds and cites the wrong surface

**Targets:** both build scripts, both v0.2 front matters, both bibliography audits.

- Both `build.sh` files build `paper.md`, not `paper-v0.2-draft.md`.
- Both abstracts are placed after the paper body. “Written last” is an authoring order, not a
  publication location.
- Neither v0.2 body contains a Pandoc/BibTeX citation key, while both bibliography audits mark
  references “in-text: yes.” `--citeproc` therefore has no citations to resolve.
- Author, exact date, keywords, bibliography metadata, artifact revision, and software/environment
  identifiers are absent or placeholders.

**Required closure:** make one candidate-build command take the exact reviewed draft (or promote
first), put abstract metadata/front matter at the front, add real citation keys, produce HTML/PDF in
a clean directory, and verify the rendered references and metadata. The deposit manifest must hash
the generated paper and every included artifact.

## 3. Paper A — Measuring Reflexive Verification Load

### [P0-A1] The primary measurement is not deposited and is not presently reproducible “in kind”

**Targets:** §2 lines 63–86, §3, §9 lines 267–280, ledger C1–C4/C8, deposit §§A/C/D/E.

`drafts/EXP-RVB-1-RESULTS.md` explicitly says the full JSON trees live in session transcripts and
can be exported “if needed.” They are needed for a paper whose central contribution is a measured
coefficient. The repository contains summary tables, not the observations from which an outsider
can reapply:

- the exact prompt and role instruction for each act;
- the model/API identity and available sampling settings;
- the exact root bytes and chosen child at every depth;
- each offspring text before and after deduplication;
- the removal-test decision and reason;
- every rejected duplicate/decorative candidate;
- the complete crossed and intervention acts.

The verifier currently generates the offspring, judges whether each one is load-bearing, applies
the removal test, and deduplicates its own output. That is a valid **verifier-reported operational
measure**, but without records or independent coding it is not an independently adjudicated count.
The phrase “same prompts” is also not actionable because those prompts are not in the deposit set.

**Required closure:** export a machine-readable, append-only act corpus with exact source/model/
prompt/selection provenance and an explicit adjudication field. Re-derive every table from it. If
independent coding is not performed, rename the quantity throughout to **verifier-reported
verification offspring under protocol P** and make self-adjudication part of the construct, not a
minor limitation.

### [P0-A2] The sampling statements and denominators are wrong or unsupported

**Targets:** §2 lines 78–81; §3.2 lines 97–110; ledger C1/C2; §6.1.

There are three distinct problems.

1. “The unbiased mean-offspring estimate does not depend on the expanded fraction” is false for
   this design. The source says depth-1 children were selected as **first + middle**, not randomly.
   Later-depth means are means over selected paths, not unbiased generation-wide offspring means.
   Global deduplication also makes node offspring dependent, violating the simple i.i.d.
   Galton–Watson reading.
2. Round 2 has 8 chains × 5 acts = **40 acts**, not 100. The number 100 is the cumulative Round
   1 + Round 2 total (60 + 40). Paper §3.2 and ledger C1 currently attach 100 acts to Round 2.
3. “Fable effect” and “Sonnet effect” need the paired crossed data. In the original 2×2 table,
   verifier is confounded with root assignment. EXP-RVB-1c supplies four paired roots and supports
   a small descriptive paired contrast; the paper instead reports the confounded means as though
   they were a clean factor effect.

The intervention denominator is also hidden: `3.33 → 2.11` compares the first three acts of each
pre-intervention chain (30/9) with the three observed post-intervention acts (19/9), not all five
acts of V1–V3 (47/15 = 3.13). Before the glossary, Round 1 + Round 2 + crossed corpus acts total
**120**, so “first across 100+ acts” can be made exact if that is the intended chronology.

**Required closure:** publish the sampling rule and selected child IDs; remove “unbiased”; call the
depth rows selected-path descriptive means; fix 40/100; report the four paired contrasts for the
verifier association; state the exact intervention window and denominator. Do not infer a
population offspring distribution from these paths.

### [P0-A3] The conditional branching–queue model still has no reviewable mathematical object

**Targets:** title, §0 line 23, §5 lines 139–174, ledger C6/C7, abstract lines 295–298.

The repair demotes the old theorem but does not specify its replacement. In §5, `g` is called a
“closure fraction”; in the source model and in the numerical counterexample, `g = λ_G/λ_V` is
generative load. The paragraph names a size-blind scheduler, no expiry, deduplication, and an
anchor, then jumps to the threshold `λ_G < (1−μ)λ_V` without defining:

- queue state and arrival process;
- whether offspring join the same queue and when;
- service times and work-conservation;
- what “closure fraction” means;
- the scheduler's observability and tie-breaking;
- whether offspring are i.i.d., depth-dependent, or verifier/claim dependent;
- the precise stability/throughput proposition;
- the domain where `μ ≥ 1` is interpreted when closure sizes have infinite expectation.

The two executable counterexamples requested in the deposit plan can prevent the **old** theorem
from returning, but cannot validate an unspecified repaired model. The expiry equilibrium also
needs a reflected/non-negative queue (`max(0, …)` or an explicitly fluid regime); the printed
formula can be negative.

**Required closure — choose one:**

1. write a minimal formal model with a single unambiguous symbol table, proposition, assumptions,
   derivation, and executable simulation/property tests; calibrate only what the selected-path data
   support; or
2. remove “branching–queue model” from title/abstract and present §5 as a heuristic design map and
   open probability/queueing problem.

“Not a theorem” does not by itself make an undefined derivation scientifically safe.

### [P1-A4] The controls bound one narrow alternative; they do not validate the instrument

**Targets:** §4.1 title and lines 121–137; abstract “Two controls locate the effect”; ledger C4.

The controls differ from the corpus in more than grounding: length, domain, familiarity, access to
an external specification, proof depth, empirical context, and statement complexity. “Water boils
at 100°C / 1 atm,” a current Git digest, an analytic sentence, and a PA derivation are not exchangeable
instances of one well-founded class. The style control itself shows that adding rhetoric can add
substantive quantifiers and new obligations.

The observed contrast is useful: it rejects the narrow hypothesis that the prompt *always* forces
2–7 offspring regardless of input. It does not establish construct validity, and it does not
separate groundedness from complexity/familiarity/domain.

**Required closure:** rename §4.1 “termination controls” and abstract wording to “bound a
prompt-always-produces-a-list alternative.” Add matched controls or leave broader instrument
validity open. Report each control, not only the pooled 0.14.

### [P1-A5] `μ=0` for COMPILE-0030 is a local protocol projection, not the same measurement class

**Targets:** §6.2, ledger C5, abstract.

The LLM acts are allowed to emit new obligations; the compiled act is defined as “run script,
compare bytes, stop.” A deterministic program cannot emit prose obligations unless the surrounding
review process asks for them. The many closure, binding, dependency, and receipt obligations found
later in this repository demonstrate that the surrounding verification process did not become
zero-offspring merely because one execution was terminal.

The draft already contains the crucial honesty — weaker stipulation, `return true` also terminates,
semantic binding open. Carry that one step further: this is not evidence that compilation lowers the
same μ. It is evidence that a **closed execution sub-act** has zero emitted prose obligations under
a policy that treats its verifier/environment/binding as external operands.

**Required closure:** classify C5 separately from the transcript coefficient; name the excluded
closure and binding obligations; do not place 0 on the same quantitative axis without an explicit
mapping. If you want a comparable intervention, run the same review protocol over the compiled
bundle and count what it spawns.

### [P1-A6] Crossed-verdict reporting needs the actual four-root table

**Targets:** §5.1 lines 176–185; ledger/abstract language about negative and positive replication.

The two positive Sonnet verdicts fail to replicate under Fable (0030, 0025). The two negative
Fable verdicts that replicate under Sonnet are different roots (FLOW §15, §17). The current prose
puts “negative 2/2, positive 0/2” immediately before only the two positive-root flips, making the
denominator hard to reconstruct and encouraging a same-root reading.

**Required closure:** include the four-row crossed table, exact verdicts, and an `n=2 per direction`
warning. “Replication” here is within one vendor lineage and for four purposively selected roots.

## 4. Paper B — Budgeted Equality by Normal-Form Address

### [P0-B1] `church@v0` is not a released profile

**Targets:** §0 lines 27–32; §1 lines 49–50; §2 lines 68–75; §7; abstract; ledger preamble/B4;
migration notes; deposit reproduction/manifest.

The exact upstream state says:

```text
sigma-glyph HEAD: 196c45a2f9074a472b96af1a6bae2c67533edbb1
describe:          v0.6.7-175-g196c45a
ADR-011 status:    DRAFT — non-normative, not gated, not adopted
                   BLOCKED on PLUS 7 5
```

`git ls-tree -r --name-only v0.6.7` contains no ADR-011, `equality_profile.py`, or `church@v0`.
The `sigma-glyph==0.6.7` wheel used by the paper checkers therefore cannot exercise the profile.
The profile exists as a current proposal/reference implementation, and its current selftest is
strong (`ADR-011-SELFTEST: ALL PASS (72/72)`); that is valuable, but it is not a release fact.

**Required closure:** replace every “released profile” with **DRAFT proposal/reference
implementation at exact commit 196c45a…** (or a later exact reviewed commit). Pin or vendor the
proposal files and their license into the deposit. If it later becomes a release, cite that new
release; do not backdate release credit. Split the evaluator wheel (`0.6.7`) from the unreleased
profile implementation in every environment record.

### [P0-B2] No single admitted implementation currently carries the motivating result

**Targets:** title/§0 table, §1, §2, §4, abstract, ledger B2/B4/B5/B8.

The permissive harness can run `PLUS 7 5` and yields the cost result, but has no admitted domain,
profile commitment, or receipt composition. `church@v0` has the safety machinery, but refuses
`PLUS 7 5`. Thus there is currently no one implementation/profile that both:

1. admits the computed expression family central to the paper; and
2. establishes/refines reflection and preservation for that family; and
3. emits the claimed two-sided budgeted receipt.

Moreover, §0 says the paper “establishes” domain soundness/completeness while §4 correctly says
they are argued, not proved, and inherit an unproved λ→SKI compiler. Testing written numerals 0–8
is implementation evidence, not a domain-wide proof. The equivalence relation `~` also needs to be
named exactly in the paper rather than left schematic.

**Required closure — choose the paper's actual genre:**

- **current evidence:** frame it as an incident report + executable failure boundary + requirements
  for a future admitted equality settlement; title/abstract must not imply the motivating method is
  realized on an admitted domain; or
- **stronger method paper:** implement the preregistered computed-expression profile, prove or
  sharply classify reflection/preservation, and generate a two-sided receipt on the motivating
  case.

Until then B4/B5 are **profile obligations / argued conjectures**, not established propositions.

### [P1-B3] The object-language comparator is described incorrectly and exit vocabularies are mixed

**Targets:** §1 line 37; ledger B1; §2 lines 64–65; §3; all benchmark labels.

The executed comparator is not `EQN = ISZERO ∘ SUB`. In `tools/glyphlib.py`:

```text
LEQ(m,n) = ISZERO(SUB(m,n))
EQN(m,n) = AND(LEQ(m,n), LEQ(n,m))
```

With truncated Church subtraction, the one-sided expression is an order predicate, not equality.
The cost claim must name the exact executed term.

The paper also lists `VIOLATION` as “addresses differ / determinism.” In the permissive harness,
`VIOLATION` is the ordinary result for unequal observed addresses; in ADR-011 the semantic verdict
is `UNEQUAL`, while `FAULT`, `REFUSED`, and `UNSETTLED` are non-verdict outcomes. Mixing harness
labels, profile settlement labels, evaluator exits, and invariant failures makes the receipt schema
ambiguous.

**Required closure:** include one typed table with four columns:
`evaluator exit`, `harness comparison`, `profile settlement`, `meaning/credit`. Correct the EQN
definition everywhere and bind measurements to the exact AST/term hash.

### [P1-B4] “The only unconditional statement” still contains assumptions and overnames its credit

**Targets:** §4 lines 111–113; abstract lines 202–203; ledger B8.

“Modulo SHA-256 and implementation correctness” is not unconditional. The surviving Σ statement
is a representation/evaluator invariant: two successful runs reported the same result hash under
one hash and result-encoding regime. It does not independently establish that the result is the
correct normal form, that two implementations agree, or that the address is collision-free.

**Required closure:** call it **hash-relative observation identity** or **kernel representation
invariant under named assumptions**. Record the canonicalization/profile/evaluator identity next
to it. Reserve “unconditional” for a syntactic tautology inside a fixed formal model.

### [P1-B5] The novelty sentence outruns the deposited artifact and its citations

**Targets:** §6, abstract's “budgeted, receipted equality settlement,” deposit manifest, bibliography
audit.

The narrow novelty candidate is defensible as a **design candidate**, but the included Warrant pack
is explicitly one-sided and legacy-unpinned, while the two-sided implementation lives only in an
external DRAFT Sigma-Glyph proposal that the manifest neither vendors nor pins by full content
closure. The deposit therefore would not contain the composition whose novelty it asks readers to
assess.

The bibliography audit also overstates support:

- Berger–Schwichtenberg 1991 supports normalization by evaluation (evaluation plus readback), but
  the current citation does not by itself establish that this exact untyped Church-numeral `F,X`
  probe is “the” NbE observation trick.
- Merkle 1987 is a hash-based digital-signature construction; it is not a direct authority for the
  full content-addressed result-identity claim as phrased.
- Filliâtre–Conchon directly supports hash-consing/structural equality and should be used for that
  narrower relation.
- None of these sources is actually connected to the v0.2 body through citation keys today.

Primary sources checked:

- Berger & Schwichtenberg, *An inverse of the evaluation functional for typed λ-calculus*:
  <https://www.mathematik.uni-muenchen.de/~schwicht/papers/lics91/paper.pdf>
- Filliâtre & Conchon, *Type-Safe Modular Hash-Consing*:
  <https://gallium.inria.fr/ml2006/accepted/5.html>
- Ershov, *On Programming of Arithmetic Operations*:
  <https://doi.org/10.1145/368892.368907>
- Merkle, *A Digital Signature Based on a Conventional Encryption Function*:
  <https://people.eecs.berkeley.edu/~raluca/cs261-f15/readings/merkle.pdf>

**Required closure:** include an exact, licensed snapshot of the two-sided proposal implementation
and receipt fixture—or narrow “novelty” to a specification pattern not yet demonstrated end to end.
Rewrite prior-art sentences so each source supports the exact adjacent relation; add a search log
and treat novelty as OPEN until external prior-art review.

## 5. What survived adversarial replay

These should be preserved rather than rewritten away:

1. In a clean venv with the published `sigma-glyph==0.6.7`, the permissive harness reproduced:
   `601`, `1,997`, `9,997`, `19,997`, `2,213`, `21,453`, `260,780`, `26,212,480`, and
   `ATP_EXHAUSTED` above 50M exactly as checked.
2. The marker counterexample reproduced: Church zero and `λf.λx.X` returned `PASS` at 27 ATP with
   equal `8785b7dd…` observations; M1, M2, and M3 flipped their intended controls.
3. COMPILE-0030 reproduced the three stated ATP spends and `[PASS, VIOLATION, PASS]` in the clean
   venv.
4. The current unreleased ADR-011 reference implementation passed 72/72 selftests, including
   admission, per-side budget, profile commitment, anchor, malformed-shape, and mutation controls;
   its benchmark receipt check also passed.
5. The drafts consistently state that semantic binding remains open, that `COMPILED ≠ REPLAYED`,
   that Warrant conformance is not endorsement, and that local claim success is not document truth.
6. Licensing is visible and path-scoped in the draft packages; no DOI, tag, or external validation
   is falsely claimed.

That is a substantial surviving core. The problem is not absence of evidence; it is address and
credit: some strong evidence is attached to a wider or newer claim than it actually settles.

## 6. Minimum closure gate before promotion

Promotion from `paper-v0.2-draft.md` to `paper.md` should require all of the following:

1. **P0-A1:** frozen act-level corpus exported; exact prompts/model/source/selection/adjudication
   recorded; every Paper A table regenerated from it.
2. **P0-A2:** denominators and sampling language repaired; Round 2 = 40 acts; selected-path and
   paired-cross results labeled honestly.
3. **P0-A3:** one actual queue model/proposition exists, or the model is removed from title/abstract.
4. **P0-B1:** `church@v0` is called DRAFT/unreleased and bound to an exact commit/content package.
5. **P0-B2:** Paper B is explicitly a failure-boundary/specification note, or an admitted computed
   profile plus two-sided receipt exists.
6. **P1-S1:** stored-check `PASS` and pack-level `LEGACY_UNPINNED` are both reported; any new
   dependency-closed pack is a new artifact rather than repaired history.
7. **P0-S2:** checkers consume closed claim manifests and raw records, not summary literals or
   author-machine paths; source/receipt commitments are verified.
8. Build exact candidate papers in a clean environment; abstracts front-loaded; real citations,
   author/date/version/revision metadata; rendered HTML/PDF inspected; deposit files hashed.
9. Re-run this review's positive and negative commands. Record failures as typed statuses, not
   prose exceptions.
10. Obtain the planned out-of-lineage adversarial pass. Call it review, not independent validation
    of the scientific claims unless it independently redoes the measurements/proofs.

## 7. Recommended rewrite direction

**Paper A's strongest honest paper is narrower and better:** an exploratory methods/report paper
about a verifier-reported obligation count, with a frozen act corpus, selected-path statistics,
termination controls, and one explicitly separate heuristic queue model. Its unusual contribution
is not “μ≈2 therefore supercritical”; it is that the operationalization exposes how checking
creates inspectable obligations, and that the instrument's own dependence can be measured and
attacked.

**Paper B's strongest honest paper today is an incident-and-repair note:** a large reproducible
cost gap in a permissive harness; an executable soundness counterexample; the derivation of an
admitted-profile contract; and the discovery that the safe profile refuses the motivating case.
That last failure is not embarrassment—it is the paper's most trustworthy result. Publishing it as
“the method works on an admitted domain” weakens it; publishing it as “the failure boundary forced
the admitted-domain contract, which remains blocked on computed terms” is both accurate and novel
enough to mark the trajectory.

**Final disposition:** do not deposit either current draft. Repair the ledgers first, then the prose,
then implement the checker additions against the repaired claims. After those changes, request a
short Codex closure pass and the planned Kimi/Qwen adversarial pass.
