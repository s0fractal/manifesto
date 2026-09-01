# C2 crossed-design mapping discovery (DERIVED, non-crediting)

**Status: `DERIVED` working notes. This artifact grants NO credit.** It is the first reviewable
mapping-discovery pass approved by the Codex `4718a9f` review (PRE-GOVERNANCE SAFE). No admitted
authority, no pinned manifest, no `EXACT` mapping, no L4. Every claim below is a *proposal* to be
adversarially reviewed; the deposit gate keeps C2 `REFUSED` until a governance act.

## What C2 needs

C2 (verifier-dependence on the same root) requires **both verifiers' offspring on each of the four
crossed roots** — a proven unique bijection of 4 roots × 2 verifiers = 8 acts (Codex's highest-risk
claim). Discovery is by *observed model + root*, never by matching expected counts.

## The 8 chains (located, one per (root, verifier); disambiguation resolved by observed model)

Each is a depth-0→4 verification-chain subagent transcript in the quarantine, identified by its
first-user ROOT prompt (which quotes the exact Monday-corpus root) and its **observed model** (the
`model` field on the transcript's assistant events).

| root | paper label | observed model | agent transcript | blob sha256 (prefix) |
|---|---|---|---|---|
| 0030 monotonicity | "Fable" | **claude-opus-5** | agent-a1153e2189d4006c… | `7c002f72f968…` |
| 0030 monotonicity | "Sonnet" | claude-sonnet-5 | agent-a700944565f64aed… | `08694626479b…` |
| 0025 modal core (◇⁻/◇⁺) | "Fable" | **claude-opus-5** | agent-aac209dc4cdcafae… | `287d99a2c186…` |
| 0025 modal core | "Sonnet" | claude-sonnet-5 | agent-ab8454e235e42cc7… | `0d1ed0ab9405…` |
| FLOW §15 central thesis | "Fable" | **claude-opus-5** | agent-a0eda1deea730b87… | `99a2c169415b…` |
| FLOW §15 central thesis | "Sonnet" | claude-sonnet-5 | agent-a8b2b993190ea94a… | `edd7f7309ea6…` |
| FLOW §17 Player | "Fable" | **claude-opus-5** | agent-a38287b9dd6a4946… | `5784ffa1be7b…` |
| FLOW §17 Player | "Sonnet" | claude-sonnet-5 | agent-a3432dae9930a82b… | `34dda1d7d101…` |

Exactly one opus chain and one sonnet chain per root were located — a clean 4×2 bijection with **no
duplicate (root, model) runs** (so no `CONFLICTED` at this layer). The root prompts quote the exact
Monday files verbatim, so `root_digest` is directly evidenceable from each transcript's ROOT span.

## Finding F-C2-1 — the declared verifier does not match the observed model (paper-affecting)

**The paper calls the two verifiers "Fable 5" and "Sonnet 5" (`EXP-RVB-1-RESULTS.md`, paper §5). The
transcripts observe `claude-opus-5` and `claude-sonnet-5`.** The Sonnet side matches; the **"Fable"
side was observed as `claude-opus-5`, which is not `claude-fable-5`.**

This is exactly the `verifier_declared_identity` ≠ `verifier_observed_identity` split the corpus schema
anticipated, and it is now real and load-bearing:

- Paper A §5's contrast is stated as **"Fable ≈ 3.15 vs Sonnet ≈ 2.10"**; at the transcript level it is
  **Opus-5 vs Sonnet-5**. If "Fable" was a fast Opus variant at run time, the *label* is wrong but the
  measurement stands as an Opus/Sonnet contrast; if a distinct `claude-fable-5` was intended, the runs
  did not use it.
- This does **not** by itself invalidate the ô measurement, but it **does** mean the paper's verifier
  identity is mislabeled relative to the preserved evidence. Until resolved, the honest
  `verifier_observed_identity` for the "Fable" acts is **`claude-opus-5`**, and any C2 unit key must use
  the observed model, not the paper label.

**Operator decision required before any C2 governance act:** which is authoritative — the paper's
"Fable 5" label or the transcript's `claude-opus-5`? The paper text and the C2 unit definitions must be
reconciled to the observed model (or the label corrected with an explicit note) before an `EXACT`
mapping or a pinned C2 manifest can be honest.

## What is deliberately NOT done here

- No `EXACT` mapping, no adjudication, no evidence-record digests committed (that is a governed act).
- The 1b-original vs 1c-crossed provenance of each chain is **not** distinguished — the prompts are
  identical across the original and crossed runs, so "which run was the crossed one" is not recoverable
  from the prompt alone (only the (root, observed model) pair is). For the C2 *unit* (root × verifier)
  this suffices; for a claim that the contrast is specifically the *crossed* design, that provenance is
  an open `AMBIGUOUS` item.
- No required-unit manifest is pinned; C2 stays `REFUSED: MANIFEST_NOT_PINNED / AUTHORITY_NOT_ADMITTED`.

## Next (only after operator resolves F-C2-1)

Author the machine-readable DERIVED mapping table (per-chain evidence spans for experiment/root/verifier
from each transcript), keeping `mapping_status: DERIVED`; then, as a separate governance act, admit an
authority, pin the C2 manifest with the **observed-model** unit key, and promote reviewed rows to
`EXACT`.
