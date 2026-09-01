# Claim ledger — verifier-reported verification load (paper A, v0.2 draft, rev after Codex review)

Every abstract claim is a row. Status: **MEASUREMENT** (a number from stated protocol P),
**NEGATIVE RESULT** (a bounding counterexample), **OPEN** (named, not established). The measured
quantity is **ô** — the *verifier-reported* offspring count per act; the same verifier that produces
offspring also judges load-bearingness, applies the removal test, and deduplicates. Self-adjudication
is part of the construct.

Reproducibility: `checker` (re-derived locally), `replay` (byte-identical evaluator replay),
`command` (external command), `transcript` (LLM measurement, re-runnable in kind only), `manual`.

**Falsifier is typed** (Codex S3): only `integrity_break` (a number fails to re-derive from the frozen
act corpus) and `within-sample_counterexample` (a chain in the *frozen sample* reaches 0 at depth ≤4)
falsify the claim as stated. `replication_failure`, `scope_boundary`, `competitive_result`,
`misuse_warning`, and `open_obligation` do not.

| # | claim | status | evidence | repro | falsifier (typed) | known loss |
|---|---|---|---|---|---|---|
| C1 | Under protocol P the verifier reported ô₀/ô₁/ô₂ = 5.42/3.38/2.50 (round 1, **Opus 5** — observed `claude-opus-5`, formerly mislabeled "Fable 5", 12 roots, 60 acts) and 3.50/2.75/2.50/2.13/2.25 at depths 0–4 (round 2, **8 chains × 5 = 40 acts**). | MEASUREMENT | EXP-RVB-1-RESULTS.md §1–§2 | transcript | `integrity_break` | **frozen act corpus not yet exported** (§10); self-adjudicated; single lineage; depth-1 selection is first+middle (selected-path means) |
| C2 | ô sat near 2–3 on informal claims and much lower on termination controls. The Opus-5≈3.15 / Sonnet≈2.10 split is **confounded** (2×2 assigns roots to verifiers); the only paired verifier contrast is the four crossed roots (n=2/direction). **Verifier identity is the OBSERVED model** (`claude-opus-5` / `claude-sonnet-5`; the "Fable 5" label was wrong — `CORPUS-C2-DISCOVERY-0.1.md` F-C2-1); the C2 unit key uses the observed model. **Corpus-activation scope (operator 2026-09-02): C2 is the OBSERVED-MODEL 4×2 unit** — the three evidence-gated components are `root_digest` (the ROOT-file token, not the verbatim claim), `verifier_identity` (observed model), `agent_run_occurrence` (transcript agentId); `experiment_id` (EXP-RVB-1c) is **asserted, not evidenced** (1b/1c provenance AMBIGUOUS). The `CORPUS-C2-MAPPING-0.2.json` operand carries all three spans and is activation-ready (a governance act promotes it to EXACT — proven by simulation), while the committed trust root stays empty → C2 REFUSED. | MEASUREMENT | EXP-RVB-1b; §5 crossed table; 8-chain bijection in CORPUS-C2-DISCOVERY-0.1.md | transcript | `integrity_break` | not a clean factor effect; small n; **the crossed-root ô-profiles replicate per verifier (Opus-5≈3.2, Sonnet≈2.1) while verdicts flip on the same roots — consistent with ô being a property of the verifier's generative distribution, not of the claim's obligations** (Kimi 2026-09-01, Task 1.1); the offspring-overlap test that would settle this is blocked on the frozen corpus |
| C3 | ô stayed non-zero through the finite depths sampled (to depth 4); across the 40 round-2 acts no act reported zero. Finite-depth, not asymptotic. | MEASUREMENT | EXP-RVB-1b | transcript | `within-sample_counterexample` | μ_∞ NOT observed; round-1 geometric extrapolation disconfirmed; **the depth-3–4 plateau survives as a count, but the non-monotone tail (2.13→2.25) is what soft-dedup paraphrase leakage would produce — so its interpretation as _genuine new_ obligations is un-audited** (Kimi 2026-09-01, Task 1.2), pending the corpus |
| C4 | Termination controls reported ô ≈ 0.14 (pooled) and terminated unaided; a style control ≈1.25. This bounds one alternative (the prompt *always* produces a list), NOT construct validity. | MEASUREMENT | EXP-RVB-1-NC (T1–T6); EXP-RVB-NC2 (S1–S4) | transcript | `within-sample_counterexample` (a control reads ≥2 in-sample) | controls differ in length/domain/familiarity/complexity; Pythagorean control did not terminate |
| C5 | The compiled 0030 check has a **terminal execution sub-act with zero emitted prose obligations** (settlement 4,151,277 / 554,678 / 25 ATP). This is on a **separate axis** from ô, not "compilation lowers μ". | MEASUREMENT (distinct axis) | COMPILE-0030; `conf_mono_settle.py` | replay + checker | `integrity_break` (ATP/verdict mismatch) | weaker stipulation; `return true` also terminates; semantic binding OPEN; the surrounding review's closure/binding/dependency obligations are excluded operands |
| C6 | An external reviewer's counterexamples break the v0.1 closed forms: μ=0.5 short-closure-first closes 75% (vs a ≥37.5%-unclosed bound); μ=1.2 closes 40% on the first act (so "throughput→0" fails); the anchor needs well-foundedness, not acyclicity. | NEGATIVE RESULT | paper §7; reviewer (Codex 2026-08) | executable (scheduler counterexample to ship) | — (it *is* the falsifier of the theorem) | retires the theorem; does **not** validate any replacement |
| C7 | A glossary closing defect families cut ô from **3.13 → 2.11** over an exact window (47/15 pre → 19/9 post) and produced the first unaided terminations on corpus material across the **120** prior corpus acts; the reduction is non-monotone (6→3→3→7→4→8). | MEASUREMENT (intervention) | EXP-RVB-2; G4/G5/G6 | transcript | `integrity_break` | debt migrates to the glossary; adequacy OPEN |
| C8 | The **legacy inline gate** caught 4 of 11 world-fact claims (all `count`-class) in one generated summary, reached 11/11 on correction, yet badges a *false* marked operand (`3+6=9` over 8+8) and drifts to 10/1 on re-run. | MEASUREMENT (legacy tool) + NEGATIVE RESULT | SSD-DEMO-0.1/0.2; SSD-INDEX-AUDIT; check_claims | checker | `integrity_break` | legacy inline gate, **not** the capsule pipeline; per-claim gate blind to inheritance |

## No queue model is claimed (Codex P0-A3)

§7 is an **open probability/queueing problem**, not a conditional model-hypothesis. The paper defines
none of: queue state, arrival process, offspring-join timing, service/work-conservation, scheduler
observability/tie-breaking, offspring dependence, the stability proposition, or the μ≥1 interpretation
under infinite-expectation closures. "Branching–queue model" is removed from the title and abstract.

## Forbidden claim TYPES (not verbatim strings — resurrection-channel control, §13.11)

Listed as *types*, deliberately not as the retired catch-phrases: quoting the old sentences here
would re-index them (the CONTROLLED-FORGETTING tombstone test — a typed blocklist must suffice).

- a reflexive-verification **theorem / bound / phase-transition asserted as a claim** (the
  branching-queue model is retired, not held);
- any **unconditional budget-insufficiency** statement at μ≥1, under any qualifier;
- any **universal "AI cannot verify/converge on AI"**;
- attributing the plateau to the **claims** rather than to the **instrument** (ô is verifier-reported);
- any **"the verification gap is crossed / closed"** claim;
- **"verification = byte-identical replay"** as a general definition;
- **"the experiment proves the model"**;
- any implication that a **Warrant pass, a green checker, or a settlement REPORT validates the
  interpretation**;
- a **clean single-factor verifier effect** (the 2×2 confounds verifier with root assignment);
- any **round-2 act count other than 40**, or a per-depth mean presented as **unbiased**;
- any **generalization beyond the single Monday corpus** stated as established.

## Open (named, not established)

- the frozen act corpus and independent (out-of-lineage) re-derivation of ô;
- any asymptotic value; any *specified* queue model (§7 likely reduces to a standard
  branching-service queue — Crump–Mode–Jagers / Bellman–Harris — under stated assumptions; a
  queueing-theory reviewer should confirm which citation settles it);
- construct validity separating groundedness from complexity/familiarity/domain;
- semantic adequacy of any compiled artifact;
- **generalization beyond the single Monday corpus** — the title and claims are scoped to it; a
  second-genre corpus (8–10 roots from arXiv abstracts / a technical spec / a real README under the
  same protocol P) and a **human baseline** (protocol P run by a person on ≥5 roots) are named future
  strengthening, deliberately not fabricated here (Fable 2026-09-01 §2.4–2.5);
- **two cheap construct-validity tests from the existing transcripts, not yet run** (Fable §2.2–2.3):
  offspring-set overlap (Jaccard / semantic) between verifiers on the four crossed roots — low overlap
  would mean ô measures the verifier, not the claim; and a manual paraphrase-leak audit of depth-3–4
  offspring — a notable paraphrase fraction would mean the ≈2.1–2.25 depth-3–4 figures are inflated by
  soft-dedup leakage. Both are blocked on exporting the frozen corpus.
