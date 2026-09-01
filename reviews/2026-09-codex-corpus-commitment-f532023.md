# Codex exact-HEAD closure review — corpus commitment at `f532023`

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `f532023d61b3d6d377db6bd38912d66675510553` (`origin/main`)  
**Disposition:** **BLOCKED before canonical `EXACT` mappings, pinned manifests, L4 credit, or an
auto-proposer.**

This repair closes another substantial layer. The real extraction now publishes a 1239-event
commitment; membership, stale body IDs, duplicate events, impossible spans, gaps, decision-field
identity, exact evidence-span commitments, and final mapping status all have executable checks.

The word `source-bound` is accurate **relative to the supplied report**. The remaining gap is that the
report/commitment is not itself an authenticated trust root, bundle verification does not bind all
credit-affecting bundle state, and the newly addressed decisions/manifests are content-addressed but
not authorized. Content addressing makes a decision distinguishable; it does not establish who had
the right to make it.

## Exact state and positive evidence

- `HEAD == origin/main == f532023d61b3d6d377db6bd38912d66675510553`;
- all four GitHub workflows are green at that exact SHA;
- `python3 papers/corpus/test_corpus.py` passes;
- live extraction is `CLEAN`, `55/55`, `1239 events`;
- committed and live extraction reports are JSON-equal;
- committed event manifest has exactly 1239 entries and no event content;
- a full real L2 bundle mints `CLEAN` with 1239 events and `verify_bundle()` succeeds;
- H1–H10-style mutations in the current suite pass;
- deposit state remains unchanged; no corpus claim is `CHECKED`.

The preservation and real extraction results stand. Findings below concern general trust and credit.

## Findings

### P0-1 — The extraction report is a caller-supplied trust root with no external pin

`mint_l2_bundle()` trusts `extraction_closure`, `corpus_commitment`, and `event_manifest` from any
dictionary. It does not recompute the commitment from a closed report body, require `set_status=CLEAN`,
verify a report ID/digest, or compare with a separately pinned expected commitment. `build_l3()` then
accepts the same caller-supplied commitment as its oracle.

I constructed an invented but coherent report, event manifest, L2 body, candidate, decisions, and
one-unit manifest. The complete path returned:

```text
mint_l2_bundle  -> CLEAN
verify_bundle   -> (True, None)
mapping         -> EXACT
view            -> COMPLETE
```

The current H1 test removes an event from a report while retaining that report as the trust root. It
correctly proves membership enforcement, but it does not test replacement of the trust root itself.

**Required repair:** define a canonical extraction-report artifact `{id, body}` and validate it
independently. Its ID must bind set status/faults, inventory and quarantine-receipt commitments,
extraction closure, closed source set, and exact event manifest. The mapping run must receive a pinned
expected report ID/corpus commitment from outside the submitted report—eventually from the reviewed
claim manifest/deposit record. A report with anything other than `CLEAN` must not mint a creditable L2.

### P0-2 — `bundle_id` does not bind the verified bundle state or the index address

The bundle ID hashes commitment, expected closure, and `events`. It omits `status`, `faults`, and the
index metadata consumed by mapping. `verify_bundle()` checks index body digests, but not equality of
index keys/addresses with committed event records.

Two executable mutations succeeded:

```text
L2_REFUSED bundle; change only status to CLEAN
bundle_id unchanged          True
verify_bundle                (True, None)

change index byte_start/end, retain events and body
bundle_id unchanged          True
verify_bundle                (True, None)
mapping with forged address  EXACT -> COMPLETE
```

Missing index entries are likewise not compared against the committed event set.

**Required repair:** the canonical bundle body must bind status/fault state and one exact ordered event
record per index entry, including event ID, blob, event index, span, body digest, and expected closure.
Verification must enforce exact events↔index equality and reconstruct the index from the committed body
rather than accept a second mutable representation. A refused bundle should have a refusal report, not
an ID that becomes clean when a flag is changed.

### P0-3 — Event-manifest membership is not closed-set equality

`mint_l2_bundle()` requires every submitted event to be present in the extraction manifest, but does
not require every committed event to be present in the bundle. A one-event private L2 minted `CLEAN`
against a two-event committed manifest and verified successfully:

```text
subset_of_closed_manifest -> CLEAN, 1 of 2, verify=True
```

This may be a useful *projection*, but then it is not the closed L2 bundle of the frozen extraction.

**Required repair:** choose and name one of two contracts:

1. full L2 bundle: exact set equality with the report event manifest; or
2. L2 projection: explicit content-addressed selection manifest, parent corpus commitment, selection
   rule, omitted-set/loss report, and no completeness credit beyond the declared projection.

Do not let an implicit subset inherit the full corpus commitment's completeness semantics.

### P0-4 — Decision and manifest identities establish distinction, not authority

`record_id` now rotates when completeness/publication decisions change, which closes undetected credit
flips. But `_decision_ok()` accepts any truthy `adjudicator_identity` and `authority`. The same applies
to mapping adjudication. No authority registry/policy, subject binding, evidence commitment,
signature/receipt, or expected decision ID is checked.

My invented record used:

```json
{"adjudicator_identity":"attacker","authority":"self","decision":"COMPLETE"}
{"adjudicator_identity":"attacker","authority":"self","decision":"CLEARED_FOR_PUBLICATION"}
```

It received `EXACT` and `COMPLETE`. The IDs honestly address those assertions, but the assertions
remain self-issued.

Similarly, a one-unit replacement manifest is accepted and produces `COMPLETE`; it merely has a new
`manifest_id`. The current test asserts only that the ID changes. Nothing compares it with the pinned
expected manifest ID, and `paper_pin` is an unchecked string.

**Required repair:** keep identities, but add validation credit separately. Pin allowed authority
profiles and exact expected manifest IDs/paper digests. Decision records must bind subject record,
decision kind, evidence, authority profile, and temporal provenance. Until an authorized external
commitment exists, status should be `ASSERTED`/`UNREVIEWED`, never publication clearance or complete
claim credit.

### P1-5 — Full ActRecords still do not leave the function as a replayable L3 bundle

`_actrecord()` constructs a useful body and record ID internally. `build_l3()` returns only seven
metadata fields per act:

```text
act_id, experiment_id, faults, local_ref, mapping_id, record_id, status
```

The record bodies, exact evidence records, completeness/publication decision bodies, and topology are
discarded. Thus “serialized L3 only, source table removed → L4 re-derives” is still impossible. The
note calls full bodies “private L3,” but no private L3 artifact is returned or validated.

Return separate `{private_l3_bundle, metadata_report}` outputs. The L3 bundle needs its own ID and exact
closed records, so L4 can operate solely on serialized L3 without the original candidate table.

### P1-6 — `record_id` is minted before graph finalization

The ActRecord body contains provisional mapping status. Later graph processing can change it to
`AMBIGUOUS` or `CONFLICTED` and add graph faults. `mapping_id` correctly uses the final status, but the
existing record ID/body still describes the pre-final status and does not bind the final faults or
resolved topology.

Finalize graph relations first; resolve parent/child local references to record IDs; then mint the
final ActRecord body and ID. Otherwise the full record and metadata report disagree about status.

### P1-7 — The evaluation identity omits the evaluator/mapper closure

`evaluation_id` binds manifest, L2 bundle, corpus commitment, and record IDs, but not
`mapper_closure_id`. Record IDs are hashes of output bodies and likewise omit the mapper closure. A
validator/schema change that preserves the same bodies can therefore retain the same evaluation ID.

Bind the mapper/compiler/profile closure—or an explicit evaluation plan ID—into the evaluation body.
Keep value identity separate if stable semantic values across verifier versions are desired.

### P1-8 — Remaining structural regressions are not yet covered

Add executable checks for:

- coherent replacement of the entire report/commitment;
- extraction report with `set_status=FAIL` attempting to mint a bundle;
- strict full-set equality or an explicit projection loss contract;
- index span/blob/event-index mutation with unchanged body;
- removal of an index entry;
- `L2_REFUSED -> CLEAN` status flip without ID rotation;
- self-issued decision authorities and unpinned one-unit manifest;
- final graph-status mutation rotating the final record ID;
- serialized L3-only L4 replay;
- mapper-closure mutation rotating the evaluation/plan identity.

## What is genuinely closed at `f532023`

- real extraction emits a reproducible event manifest and corpus commitment;
- events not present in the supplied manifest are refused;
- stale event/body identities, duplicate IDs, impossible lengths, and index gaps are detected during
  minting in the tested cases;
- exact occurrence addresses are checked against the current index;
- completeness/publication changes rotate provisional record IDs;
- exact evidence spans are committed by mapping adjudication;
- empty/unknown-field/claim-mismatched manifests receive typed handling;
- final mapping IDs bind final `CONFLICTED` status;
- actual schema bytes participate in extraction closure;
- the current real 1239-event path is clean and unchanged.

This is strong progress. The remaining problem is no longer hashing—it is selection of the trust root
and authorization to issue credit.

## Minimal repair order

1. Canonicalize and externally pin the extraction-report trust root; refuse non-clean reports.
2. Make the bundle one canonical representation binding state + exact index/event metadata; decide
   full bundle versus explicit projection.
3. Introduce authority profiles and independently pinned decision/manifest commitments.
4. Emit a self-contained private L3 bundle and finalize records only after graph resolution.
5. Bind evaluation to the mapper/evaluation-plan closure.
6. Add the mutations above and request one final focused exact-SHA review.

Exploratory transcript mapping may continue as `DERIVED` notes. Canonical `EXACT`, L4 credit, and an
auto-proposer should still wait: otherwise the proposer cannot forge hashes, but it can choose its own
report, obligation set, and authority.

## Closure conditions for the next handoff

```text
coherent invented report + commitment          -> REPORT_NOT_PINNED
set_status=FAIL report                          -> REPORT_NOT_CLEAN
implicit event subset                          -> SET_MISMATCH or explicit projection+loss
index address/remove-entry mutation             -> BUNDLE_ID_MISMATCH
L2_REFUSED -> CLEAN flag flip                   -> BUNDLE_ID_MISMATCH
self-issued completeness/publication authority  -> AUTHORITY_NOT_ADMITTED
replacement one-unit manifest                   -> MANIFEST_NOT_PINNED
graph EXACT -> CONFLICTED                       -> final record_id rotates
serialized private L3 only                      -> L4 re-derives or typed refusal
mapper/profile mutation                         -> evaluation_plan_id/evaluation_id rotates
```
