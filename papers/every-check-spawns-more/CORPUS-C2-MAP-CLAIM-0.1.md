# C2-MAP / C2-MEAS — closed claim definitions (v0.1)

Two **separate** addressable claims split out of the paper's measurement claim `C2`
(Codex governance-activation review, ecda7f0). They must never be merged: `C2-MAP` can
become `CHECKED`; `C2-MEAS` is permanently `REFUSED` until real measurement replay.
`C2` (the paper's prose measurement claim) is unchanged and stays refused on the
`FROZEN_CORPUS_NOT_DEPOSITED` axis.

---

## C2-MAP — cohort addressability (address map)

**Exact body.** The eight crossed transcripts of the observed-model experiment form an
**addressable 4×2 cohort**. The unit key is `(root_digest, verifier_identity)` with
`verifier_identity ∈ {claude-opus-5, claude-sonnet-5}` (the OBSERVED model; the "Fable 5"
label was the mislabel corrected in `CORPUS-C2-DISCOVERY-0.1.md` F-C2-1). The four roots
are the crossed roots
`61a110be…`, `74e53505…`, `e43b2b86…`, `ed8719cd…`. For every one of the eight
`(root, model)` units there is exactly one act, byte-mapped to the frozen corpus through
three evidence-gated spans: `root_digest` (the ROOT-file token, hashed to the unit root
digest), `verifier_identity` (the observed model string), and `agent_run_occurrence` (the
transcript agentId). The cohort is an exact bijection onto the 4×2 grid.

**Scope — what CHECKED means.** Only that these specific acts are the contestable objects
the C2 discussion ranges over, and that each is content-addressed to preserved bytes under
a pinned extractor/mapper closure and an admitted governance authority. It is a statement
about *addressing*, not about any measured quantity.

**Evidence class.** `address_map`. Recomputable relations (ids, commitments, manifest pin,
decision register, proposal identity, provenance) are re-derived in CI by
`verify_activation_report`; the **raw-byte span truth** is revalidated **machine-locally**
against the quarantine by `corpus_activation_report.generate()` and is *not* re-executed in
CI. A CI `CHECKED` therefore attests: every recomputable relation holds **and** the live
trust root applies the governance diff — not a CI re-run of the raw bytes.

**Exclusions (NOT claimed by C2-MAP).**
- any offspring count, dedup decision, or ô value (that is C2-MEAS);
- `experiment_id` (EXP-RVB-1c) provenance — it is **asserted, not evidenced** (1b/1c
  ambiguous), part of the mapping subject, not an evidence-gated component;
- the paper's declared verifier label "Fable 5" — the map binds the **observed** model;
- any causal or factor-effect reading of the Opus-5 / Sonnet-5 ô split.

**Falsifier (typed).**
- `integrity_break` — any span, id, commitment, or relation fails to re-derive from the
  frozen corpus / pinned closures; or the committed trust root does not actually pin the
  manifest, mapper, register, and authorities of the proposal.
- `bijection_break` — the eight acts do not exactly cover the 4×2 `(root, model)` grid
  (a missing unit, a duplicate run across units, or an unexpected unit).

**Lifecycle.** `REFUSED: ACTIVATION_NOT_APPLIED` while `CORPUS-TRUST-ROOT.json` is empty;
`CHECKED` only after the operator applies the pinned `trust_root_diff`
(`CORPUS-C2-MAP-ACTIVATION-0.1.json`) as a path-limited governance commit and records the
readback (`CORPUS-OPERATOR-ACT.md`). The transition is addressable and reversible: reverting
the trust root returns the claim to `REFUSED`.

---

## C2-MEAS — the measurement (permanently refused here)

**Exact body.** The measurement of C2 — ô (offspring before dedup), the dedup removal
decisions, and the resulting per-act ô — over the same cohort.

**Status.** `REFUSED: MEASUREMENT_NOT_REPLAYED`, permanently, on this path. offspring,
dedup, and ô are **neither extracted (L2) nor derived (L3)** by the address-map apparatus.
C2-MAP addressability grants C2-MEAS nothing; deriving a measurement verdict from the map
would be **composition laundering**. C2-MEAS leaves `REFUSED` only when measurement evidence
is itself extracted, mapped, adjudicated, and governed under its own manifest — a separate
future act, not a projection of this one.

**Engine vs policy.** The corpus engine's actual typed result for the unclaimed measurement
view is `REQUIRED_UNITS_UNSPECIFIED` (no C2-MEAS manifest exists). The activation report
records that engine reason verbatim under `engine_reason` and keeps the normative
`MEASUREMENT_NOT_REPLAYED` reading in a **separate** `policy_projection` field — the report
never overwrites an observed engine reason with a stronger authored one.
