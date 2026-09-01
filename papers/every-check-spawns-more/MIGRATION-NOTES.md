# Migration notes — Every Check Spawns More → v0.2

Maps each v0.1 (`paper.md`) section to **keep / rewrite / retire / relocate** and why. The
governing rule (brief §1) is *rewrite, do not patch*: `paper.md` is untouched and preserved as
a historical comparator; `paper-v0.2-draft.md` is the replacement. Only an explicit operator
decision may promote the draft to `paper.md`.

## Cross-cutting repairs (apply throughout)

1. **Retire residual theorem language AND the model itself (Codex P0-A3).** v0.1 labels itself
   "Conjectural" in the title and §2.2, yet the abstract still says "the **theorem's** only
   asymptotic escape", §2.3 says "the theorem's escape hatch", and §1 lists deliverable 1 as
   "**State the bound** … a **phase transition** at μ=1". v0.2 removes *theorem / bound / phase
   transition* as claims everywhere. It goes further than "keep the model, drop the theorem": the
   branching–queue **model is removed from the title and abstract** and demoted to an **open
   queueing problem** (§7) — the paper defines no queue state, arrival process, service discipline,
   scheduler observability, or stability proposition, so it claims *no* model, conditional or
   otherwise. The refuted unconditional forms survive only as the negative result (C6) that retired
   them.
1a. **Rename the measured quantity to ô — the verifier-reported offspring count.** The same verifier
   that emits offspring also judges load-bearingness, applies the removal test, and deduplicates;
   self-adjudication is constitutive and is stated wherever a number appears.
2. **Single-vendor lineage is first-class**, stated in the abstract and §0/§8, not buried.
3. **Finite-depth wording everywhere**; μ_∞ is never asserted; the round-1 geometric
   extrapolation is explicitly marked disconfirmed.
4. **Reproducibility classes are explicit** (checker / replay / command / transcript / manual);
   offspring counts are transcript, not byte-reproducible.
5. **Legacy vs current machinery separated**: the SSD gate is the *legacy inline* gate; the
   capsule pipeline is subsequent work and is not substituted into the experiment.

## Section-by-section

| v0.1 section | disposition | why / how |
|---|---|---|
| Title "A Reflexive Verification Model (Conjectural)" | **rewrite** | Measurement-first and **scoped to the single Monday corpus** (Fable §2.4): "…on a Single LLM Monologue Corpus". No "LLM review" generalization and no "Open Queueing Problem" in the title (the queue likely reduces to a known branching-service form, §7). |
| Abstract | **rewrite, ≤150 words, front-loaded** | Rebuilt from the ledger; drop "theorem's escape", "at μ≥1 no finite budget suffices" (unqualified), "do not converge"; the long negative-space table lives in §0, not the abstract (Fable §2.1 — the abstract was over-hedged and is now tightened to number + control + scope caveat). |
| §1 "State the bound / phase transition at μ=1" | **rewrite** | Becomes the research question (v0.2 §1); "bound/phase transition" removed as deliverables. |
| §2 the model, §2.1–§2.3 | **retire → v0.2 §7 (open problem)** | Not "conditional model" — the queueing question is stated as OPEN with the counterexamples (C6) that refuted the closed forms adjacent; the paper commits to no queue model. §2.2 status box content becomes constitutive. §2.3 "escape hatch" reframed as a measured intervention (§6.1), no "theorem". |
| §3.1 protocol | **keep → v0.2 §2** | Removal test / dedup / depth policy preserved verbatim in substance; add reproducibility class. |
| §3.2–§3.3 results | **rewrite → v0.2 §3–§4** | Raw counts before interpretation; round 2 is **40 acts (8 chains × 5 depths)**, not 100; depth-1 means are **selected-path** (first+middle roots, non-random) and are not unbiased estimates; the Fable/Sonnet split is reported **confounded**; controls (§4) explain which control isolates which alternative. |
| §3.4 amortization | **rewrite → v0.2 §6.1** | Add the **non-monotone** debt curves explicitly (G5 6→3→3→7; G6 6→3→3→7→4→8) — v0.1 compressed these. |
| §3.5 threats | **rewrite → v0.2 §8** | Expanded: lineage, protocol/adjudicator sensitivity, scheduler sensitivity, transcript class; falsifiers F1–F6. |
| §4 COMPILE-0030 | **rewrite → v0.2 §6.2** | Keep the settlement ATP numbers; frame as a **terminal execution sub-act with zero emitted prose obligations on a separate axis from ô**, not "compilation lowers μ"; the surrounding review's closure/binding/dependency obligations are *excluded operands*; keep "`return true` also terminates"; state semantic binding OPEN; never say "the gap is crossed". |
| §5 SSD episode, §5.1–§5.3 | **rewrite → v0.2 §7** | Relabel *legacy inline gate*; keep 4/11 and the index audit (30/2/10/18); **add** the boundary that 11/11 badges a false marked operand and the live re-run drifts to 10/1; state the capsule pipeline is subsequent work. Guessed counts "42/37/8/12" are NOT reproduced (transcript-only); only the measured set {7,12,12,67} is used. |
| §6 AIE numbers | **relocate → Paper B** | Detailed AIE cost argument leaves this paper; retain at most one sentence identifying AIE as a companion engineering technique. Removes the 260,780 / 26,212,480 / 601-ATP table from paper A. |
| §7 related work | **keep, trim** | Keep load-bearing citations (`cacm-verification-debt`, `luu2015demystifying`, `barendregt2005challenge`, `sigma-glyph`, `warrant`); amplification/debate/logical-induction remain contrast, not claims. See `DEPOSIT-AND-AUDIT.md` bibliography audit. |
| §8 conclusion | **rewrite** | Keep "checking ends by decision … what is new is a number"; **drop** "do not converge on their own, at any budget" and "does not fall below 1 within measurable depth" as a universal statement — replace with the scoped finite-depth finding. |
| Provenance | **keep** | Model identity + date retained; byte reproducibility not claimed where the provider cannot supply it. |

## Retired sentences (must not survive outside history/counterexample)

- "State the bound … a phase transition at μ = 1."
- "the theorem's only asymptotic escape."
- "chains of 'AI checks AI' do not converge on their own, at any budget."
- "does not fall below 1 within measurable depth" *as a claim about all such chains* (kept only
  as the finite-depth observation it actually is).
- any use of "RVB theorem".
- "100 acts" for round 2 (it is 40); "an unbiased estimate" of any depth mean (selection is
  first+middle, non-random); "compilation lowers μ" (the compiled terminal sub-act is a *separate
  axis* from ô, §6.2); "Fable-vs-Sonnet factor effect" stated as clean (it is confounded).

## What history/comparator retains

`paper.md` (v0.1) stays in the tree as the historical comparator. When (and only when) the
operator promotes v0.2, the working surface should expose the supported argument with a short
version/history note pointing back to v0.1 via git history — not two live papers making
different claims.
