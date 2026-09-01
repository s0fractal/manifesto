# Corpus negative fixtures 0.1 — the frozen acceptance oracle (Step 2)

The validator and exporter are implemented **against this oracle**, not the reverse. Step 2 is
accepted only when every fixture below is specified precisely enough to be executable and each forces
its typed failure. A green validator must **fail** each of these; the exporter must refuse to emit the
offending artifact.

Each fixture states: the positive baseline it perturbs, the exact mutation, the layer it hits, and the
required outcome (a typed failure — never a silent pass, never a default).

Positive baseline (the only shape allowed to succeed): a `VERIFIED` L1 blob → gap-free L2 events with
byte spans → an L3 act with full provenance, recorded decisions, and either real sampling values or
typed `UNKNOWN` → an L4 view whose `required_units` are all present, `COMPLETE`, and
`CLEARED_FOR_PUBLICATION`.

| id | fixture | mutation | layer | required outcome (typed) |
|---|---|---|---|---|
| **F1** | byte mutation | flip one byte of an L1 blob after quarantine | L1 | `FAIL: INTEGRITY_BREAK` — recomputed sha256 ≠ content-address; blob rejected, no L2/L3 built |
| **F2** | duplicate id | two L2 events share an `event_index`, or two L3 acts share an `act_id` | L2/L3 | `FAIL: DUPLICATE_ID` |
| **F3** | dangling reference | an act's `parent_act_id` or a `selected_child_id` names an act that does not exist | L3 | `FAIL: DANGLING_REF` |
| **F4** | summary-only masquerading as raw | an "act" whose `source_blob_id` is absent, or points at `EXP-RVB-1-RESULTS.md` (a `SUMMARY_ONLY` source with no blob) | L3 | `FAIL: NO_RAW_PROVENANCE` (this is the summary→raw laundering block, T1) |
| **F5** | ambiguous C2 mapping | a C2 act with `mapping_status=AMBIGUOUS` (or two runs of one (root,verifier) pair, `CONFLICTED`), or a mapping whose only evidence is matching counts | L3→L4 | C2 view `REFUSED` — never `CHECKED`; the ambiguous act does not enter the C2 bijection |
| **F6** | partial tree wants complete credit | an L4 view whose `required_units` include an act with `completeness_status=PARTIAL`, asking for `COMPLETE` credit | L4 | `REFUSED: INCOMPLETE_TREE` (no complete-table credit; T7/T13) |
| **F7** | unknown settings silently defaulted | a `sampling` field set to a default value where the source records nothing | L3 | `FAIL: SILENT_DEFAULT` — the field must be typed `UNKNOWN`, not defaulted (T14) |
| **F8** | redacted record keeps original id | a redacted artifact reusing the original `artifact_id`, or missing its loss report | L3/L4 | `FAIL: REDACTION_ID_REUSE` — redaction requires a new id + loss report (T11) |
| **F9** | source digest drift | an L1 source whose current digest ≠ the inventory digest, presented for export | L1 | `FAIL: SOURCE_DRIFT` — recorded, never a silent inventory update (T4/T12) |

## Notes binding the oracle to the pipeline

- Failure codes reuse the `deposit_check` vocabulary family so an L4 view's refusal surfaces as a
  typed `REFUSED` reason in the gate (e.g. `INCOMPLETE_TREE`, `NO_RAW_PROVENANCE`) rather than a
  generic error.
- Every table row in the paper (§3 counts, §5 crossed, §6.1 windows) must be **recomputed from the L3
  acts**; a validator that finds a paper literal by string search instead of recomputation is itself a
  failure of F4 in spirit and must be treated as `NO_RAW_PROVENANCE`.
- The C2 bijection (F5) is the acceptance gate for Paper A's highest-risk claim: until all eight
  crossed acts map `EXACT`/`DERIVED` with blob+span evidence, C2 stays `REFUSED` regardless of how many
  neighbouring chains pass.

## Step-2 acceptance checklist

- [x] four-layer contract with immutable L1 and fully-regenerable L2–L4 (`CORPUS-SCHEMA-0.1.md`);
- [x] derived-act minimum fields, with typed `UNKNOWN` discipline;
- [x] C2 disambiguation key + `mapping_status`/`mapping_evidence`, bijection requirement;
- [x] publication gate (`CLEARED_FOR_PUBLICATION`) separating quarantine from git;
- [x] threat model with every required threat bound to a defence (`CORPUS-THREAT-MODEL-0.1.md`);
- [x] nine negative fixtures F1–F9 specified as an executable oracle (this file).

**Next in the cadence:** byte-preserving exporter (L1→L2→L3) implemented against F1–F9, then the corpus
validator + these mutations, then `deposit_check` L4 strategies, then CI. No corpus is called a corpus
until identity, completeness, and publication eligibility are proven.
