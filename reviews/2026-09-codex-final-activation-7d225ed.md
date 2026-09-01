# Final activation review — `7d225ed`

**Reviewer:** Codex (OpenAI), exact-artifact adversarial pass, 2026-09-02  
**Exact subject:** `7d225ed3c15e4dfe2215268679608f20fc83a4ca` (`origin/main` equal at review time)  
**Artifacts:** production 0.2 operand, activation proposal, machine-local activation report,
generator, unapplied trust-root diff, current empty trust root.  
**Disposition:** **ACTIVATION REPORT EVIDENCE ACCEPTED; OPERATOR ACTIVATION BLOCKED.** The raw
machine-local construction genuinely reproduces. Three seams still prevent the proposed operator
commit from honestly creating a canonical repository-level `C2-MAP = CHECKED` claim.

## Reproduced and accepted

- All four exact-HEAD GitHub workflows are green:
  - `errata` — `33564565176`;
  - `embedded-claims-poc` — `33564565147`;
  - `papers-deposit-check` — `33564565136`;
  - `consumer-boundary` — `33564565236`.
- The generator reran against the quarantined bytes with all seven assertions true. The committed
  report remained byte-identical (`sha256:afd232c6e63fb7f4ae6c5c57f2b2829d9cc8b92f1a7e2d5299eefd0c31aa617c`).
- The report ID recomputes as
  `arpt:413a6f4064924ecff9f941ce0eae1691727e11d63374b46adcee8ec24cf33bb2`.
- All 24 evidence spans revalidate against the authenticated 1239-event L2 bundle.
- The proposal's 24 decision IDs are the exact closed set required by the eight governed records:
  8 mapping + 8 completeness + 8 publication, all unique, no extras.
- The overlay differs from the DERIVED operand only in the four explicit governance fields:
  `mapping_status`, `adjudication`, `completeness_decision`, `publication_decision`.
- The proposed root produces `C2-MAP COMPLETE`, 8 `EXACT` records, and identical build/L4 evaluation
  IDs. The committed root remains empty, so no live credit exists yet.
- No transcript body/content is present in the committed report.

The evidence report is real, deterministic, and useful. The findings below do not invalidate its
24-span result.

## Findings

### P0-1 — `MEASUREMENT_NOT_REPLAYED` is written by the report, not returned by the engine

The generator computes the measurement-side view with:

```python
meas = build_l3(bundle, overlay, {}, act_tr)["metadata_report"]["views"]["C2"]
```

The actual engine result is:

```text
status = REFUSED
reason = REQUIRED_UNITS_UNSPECIFIED
```

The report then discards that reason and writes:

```text
reason = MEASUREMENT_NOT_REPLAYED
```

The normative interpretation is correct — no measurement replay exists — but the report presents a
policy explanation as though it were the observed typed result. Its assertion checks only
`status == REFUSED`, so the mismatch remains green.

**Required repair:** either implement an explicit `C2-MEAS` claim/view whose engine result is typed
`REFUSED: MEASUREMENT_NOT_REPLAYED`, or preserve both fields:

```text
engine_reason = REQUIRED_UNITS_UNSPECIFIED
policy_projection = MEASUREMENT_NOT_REPLAYED
```

The report must never replace an observed reason with a stronger authored one.

### P0-2 — A coherently forged activation report remains green in CI

The production gate verifies the report's self-hash and trusts its stored booleans. It does not
recompute or cross-check most report fields against the proposal, root, closure, and provenance.

In an isolated exact-HEAD archive I changed the committed report to claim:

```text
provenance.l2_bundle_id = bnd:FORGED
activation.decision_register = []
activation.trust_root_diff.decision_register = []
```

I recomputed only `report_id`; all assertion booleans and result-vector text were left untouched.
`test_corpus.py` still exited 0 and printed the full green summary.

This falsifies “mutation report → CI fail” in its meaningful form. The gate detects incoherent edits,
not a coherent re-forge of the report. Content addressing establishes identity, not report truth.

**Required repair:** add a closed `verify_activation_report` path that independently checks at least:

- exact report schema and generator closure;
- report operand/proposal digests and recomputed proposal ID;
- report activation manifest/diff/decision register equal the proposal exactly;
- report provenance equals the committed extraction report, trust root, inventory, receipt, and L2
  commitments;
- evidence span metadata equals the production operand's closed set;
- decision IDs are exactly the recomputed 24-ID set, not a subset/superset;
- baseline/applied record IDs, L3 ID, and evaluation ID are recomputed or independently pinned;
- the observed engine reason is preserved.

Raw-byte span truth remains machine-local until evidence publication, but every non-raw relation is
recomputable in CI and must not be trusted from report booleans.

### P0-3 — `C2-MAP` is not a canonical claim and no consumer can mark it `CHECKED`

`C2-MAP` exists as a manifest label inside the proposal. It has no closed claim definition or row in
`CLAIM-LEDGER.md`; `claim-manifest.json` still contains only the original measurement claim `C2`,
whose strategy remains:

```text
REFUSED: FROZEN_CORPUS_NOT_DEPOSITED
```

`deposit_check.py` has no `C2-MAP` strategy and does not consume the activation proposal/report or
trust root. Applying only `trust_root_diff` therefore makes the private corpus view say `COMPLETE`; it
does not make any canonical paper/deposit claim say `CHECKED`. The proposed “first legitimate
REFUSED → CHECKED” transition does not yet exist at the repository claim boundary.

The manifest's `paper_pin` is also the short string `ecda7f0`, not a verified full commit/digest of a
closed `C2-MAP` claim body. There is currently no exact proposition for the positive credit to attach
to.

**Required repair:** create an addressable `C2-MAP` claim definition with exact body, scope,
exclusions, evidence class, and falsifier. Register it separately from `C2-MEAS` in the ledger/closed
claim manifest. Add a deposit strategy that consumes the live activated root plus the verified
activation report and yields:

```text
C2-MAP  = CHECKED (only after activation is applied)
C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED
```

Before activation the same consumer must return `C2-MAP = REFUSED: ACTIVATION_NOT_APPLIED`.
Bind the manifest to the full claim ID/full source digest, not a seven-character commit label.

## P1 closure required in the operator act

### P1-4 — The proposal/report are not explicitly bound by the unapplied diff

`trust_root_diff` contains authorities, manifest pin, mapper closure, and decision IDs, but no
`proposal_id` or activation-report ID. This can be acceptable only if the planned Git commit is the
external governance commitment: its parent/tree must bind exact HEAD `7d225ed`, the unchanged report,
the exact proposal, and an otherwise path-limited trust-root edit.

The operator act/readback should record:

- base trust-root digest;
- `proposal_id` and `arpt:` ID;
- exact diff digest;
- resulting trust-root digest;
- full parent and resulting commit IDs;
- confirmation that only the authorized paths changed.

Without that readback, “apply this diff” is not itself an addressable governance act.

### P1-5 — The report omits the exact L3/record operands

The evaluation ID transitively hashes record IDs, but the report does not disclose the generated
`l3_bundle_id` or the eight exact record IDs requested by the review contract. Add them explicitly so
an auditor can reproduce the vector without reverse-engineering the proposal and private run.

### P1-6 — Proposal identity and JSON profiles remain partially projected

`proposal_id` hashes operand digest, manifest, overlay, and diff but omits at least `schema` and
`for`. The gate separately checks `for`, but a schema/profile mutation does not rotate the proposal
ID. Hash the complete closed semantic proposal body, excluding only commentary/time fields explicitly
typed as non-semantic.

Governance JSON is also loaded with permissive `json.loads`; duplicate keys are not rejected. Reuse
the repository's strict JSON/canonicalization profile for proposal, report, and trust-root operands.

## Minimal repair order

1. Register a closed `C2-MAP` claim and a consumer that keeps it refused before activation while
   leaving `C2-MEAS` separately refused.
2. Preserve the actual measurement engine reason or implement the intended typed refusal.
3. Implement independent report verification and the coherent-forge regression above.
4. Add L3/record IDs and close proposal/report schemas and identities.
5. Regenerate the proposal/report as needed and run one short closure pass.
6. Only after that, perform the path-limited operator commit and read it back as the governance act.

## Final assessment

The hard scientific part of this step is good: the report really revalidated the 24 raw spans and
the exact proposed 8-record address cohort. The remaining blockers are not requests for more evidence.
They are the final semantic/API membrane:

1. report what the engine actually returned;
2. verify the report rather than its own green booleans;
3. attach the resulting credit to a closed canonical claim that a consumer can actually mark checked.

Until those are closed, keep `CORPUS-TRUST-ROOT.json` unchanged. The future operator act should
activate only the narrow address-map claim and must never change the measurement claim's refusal.
