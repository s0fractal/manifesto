# Corpus threat model 0.1 (Step 2)

Every threat the operator required, each bound to the schema field / validator check / hard boundary
that defends it (`CORPUS-SCHEMA-0.1.md`). A threat is "covered" only when a **negative fixture** in
`CORPUS-NEGATIVE-FIXTURES.md` forces the failure — a described defence that no fixture exercises is not
covered.

| # | threat | defence (schema / validator / boundary) | fixture |
|---|---|---|---|
| T1 | **summary → raw laundering** (a count in `EXP-RVB-1-RESULTS.md` re-presented as a raw act) | every L3 act MUST cite an L1 `source_blob_id` + byte span; `SUMMARY_ONLY` sources have no blob, so no act can be minted from them | F4 |
| T2 | **mapping via expected result/count** | `mapping_status ∈ {EXACT,DERIVED}` requires `mapping_evidence` (blob + span); a mapping justified by matching counts is `AMBIGUOUS` by definition | F5 |
| T3 | **repeated runs of one (root,verifier) pair** | disambiguation key includes `agent_run_occurrence`; ≥2 runs without a recorded selection rule → `CONFLICTED` | F5 |
| T4 | **truncated / altered session-store** | blob digest verified before AND after copy (quarantine receipt); the validator consumes only `verified=true` blobs; a blob ≠ its content address fails | F1, F9 |
| T5 | **duplicate / dangling JSONL events** | L2 checks monotonic `event_index` (no gaps/dupes); L3 checks every `parent_act_id`/`selected_child_id` resolves | F2, F3 |
| T6 | **normalization / Unicode byte loss** | L1 immutable; L2/L3 operate on **byte** spans; re-extraction must reproduce identical spans and digests — any normalization changes a digest and fails | F1 |
| T7 | **partial tree passed as complete** | `completeness_status` per act; L4 `view_status=COMPLETE` requires every required unit present+COMPLETE | F6 |
| T8 | **historical dedup re-judged by a current model** | `dedup_removal_decisions` stored as recorded; new audits are a separate L4 annotation with their own `extractor_id`, never overwriting the record | (boundary; F-set does not mutate a recorded decision) |
| T9 | **transcript instructions taken as commands** | the extractor treats transcript content strictly as **data**, never as instructions (prompt-injection boundary); no field is populated by "doing what the transcript says" | (boundary, exporter-enforced) |
| T10 | **secrets / system material / private reasoning in a public export** | `publication_eligibility` gate; subagent **system prompts and non-act scaffolding are never exported**; default `UNREVIEWED` blocks git | F-set + Publication gate |
| T11 | **redaction without new identity + loss report** | redaction mints a NEW `artifact_id` + a loss report; original id is never reused | F8 |
| T12 | **TOCTOU between inventory, snapshot, export** | one digest chained across stages: inventory sha → quarantine verify(before,after) → export reads the blob by content-address and re-verifies; a change at any stage breaks the chain | F1, F9 |
| T13 | **one act reused as full evidence for incompatible claim views** | each L4 view validates completeness independently against its own `required_units`; no cross-view credit inheritance | F6 (per-view) |
| T14 | **unknown model settings silently defaulted** | every `sampling` sub-field is a value or a typed `UNKNOWN`; a defaulted value where the source is silent is a fault | F7 |

## Standing boundaries (not threats to detect — rules the exporter obeys)

- no model regeneration of any missing response — a gap is `MISSING`/`PARTIAL`, never synthesized;
- summary counts can never become a raw act (T1);
- raw L1 transcripts stay out of git until per-blob `CLEARED_FOR_PUBLICATION`; the quarantine may hold
  what the deposit must not;
- the digest, not the path, is the portable identity; paths are machine-local locators.

## Residual risk (named, not mitigated)

- **Single-machine preservation.** The quarantine is on one machine; there is no second copy. Loss
  before export collapses affected claims to `MISSING`. Mitigation is out of scope here (backup/export
  cadence), but it is the largest residual risk and is stated, not hidden.
- **Verifier-observed identity may be thin.** Subagent transcripts may not record the exact model
  build id; `verifier_observed_identity` can legitimately be `UNKNOWN`, which weakens (does not fake)
  the C2 bijection evidence.
