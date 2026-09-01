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

## Authentication fixtures added after the exact-HEAD review (57d41e5)

The `a690789`→`57d41e5` review showed the eight literal mutations were closed but the *boundary*
(supplied L2 assertions → credit) was not. These fixtures close it and are all executable in
`papers/corpus/test_corpus.py`:

| id | fixture | required outcome |
|---|---|---|
| **G1** | mutated L2 body under a stale `event_id` | `authenticate_l2` recomputes the id → `L2_INTEGRITY_BREAK`; every view `REFUSED: L2_INTEGRITY_BREAK` **before** any mapping |
| **G2** | forged `blob_id` or an occurrence span ≠ the authenticated event | act faulted `NO_RAW_PROVENANCE`; cannot be `EXACT` |
| **G3** | empty / malformed required-unit manifest | `REFUSED: EMPTY_REQUIRED_SET` / `MALFORMED_MANIFEST` / `BAD_UNIT_KEY` — never `COMPLETE(0)` |
| **G4** | adjudication whose `evidence_commitments` ≠ the value-validated evidence | `AMBIGUOUS` (`ADJUDICATION_MISMATCH`); `decision≠EXACT` → `ADJUDICATION_DECISION` |
| **G5** | `EXACT` → `CONFLICTED` at graph finalization | `mapping_id` is minted **after** finalization, so it addresses `CONFLICTED`, not the pre-final `EXACT` |
| **G6** | duplicate `local_ref` (or `act_id`) that a view needs | **all** members invalidated (not just the second) → the unit is missing → view `REFUSED` |
| **G7** | malformed sampling / manifest / inventory / receipt | typed fault (`BAD_SAMPLING` / `MALFORMED_MANIFEST` / `MALFORMED_OPERAND`), never an uncaught exception |
| **G8** | schema/id/code byte change | the relevant closure (`clo:extract` / `clo:map`) rotates; ids derive from it |

## Source-authentication fixtures added after the 3rd review (9e50479)

The word *authenticated* previously meant only internal self-consistency. These fixtures bind L2 to
the **frozen extraction** (a committed `corpus_commitment` + `event_manifest`) and content-address the
credit path. All executable in `test_corpus.py`:

| id | fixture | required outcome |
|---|---|---|
| **H1** | coherent invented L2 event not in the extraction's `event_manifest` | `UNKNOWN_SOURCE`; bundle not `CLEAN`; every view `REFUSED` |
| **H2** | caller-minted `{status:CLEAN, index:…}` | `MALFORMED_BUNDLE` (build_l3 recomputes the bundle id, never trusts a supplied one) |
| **H3** | wrong `corpus_commitment` | `BUNDLE_NOT_COMMITTED` |
| **H4** | post-mint mutation of a committed event / of an index body | `BUNDLE_ID_MISMATCH` / `INDEX_TAMPER` before mapping |
| **H5** | duplicate L2 event / impossible span (`byte_end−byte_start ≠ len`) / index gap | typed L2 refusal (`DUPLICATE_L2_EVENT` / `IMPOSSIBLE_SPAN` / `INDEX_GAP`) |
| **H6** | `PARTIAL/WITHHELD → COMPLETE/CLEARED` | the `completeness`/`publication` *decisions* are in the ActRecord body, so `record_id` (and the view `evaluation_id`) rotate |
| **H7** | a required ActRecord field is `None` | `SCHEMA_INVALID` → not `EXACT` (presence is not enough; null is rejected) |
| **H8** | adjudication commitment ≠ the exact value-validated evidence-record digests | `ADJUDICATION_MISMATCH` → `AMBIGUOUS` |
| **H9** | one-unit replacement manifest / claim mismatch | `manifest_id` changes (visible in the view) and the view binds `manifest_id`+`paper_pin`+`l2_bundle_id`; claim mismatch → `MANIFEST_CLAIM_MISMATCH` |
| **H10** | actual schema-byte change | `extraction_closure` rotates (the closure hashes the real `CORPUS-SCHEMA-0.1.md` bytes) |

A COMPLETE view now emits an `evaluation_id` binding `manifest_id`, `l2_bundle_id`, `corpus_commitment`,
and the sorted `record_id`s — so credit is content-addressed to the exact obligation set, corpus, and
records, not a bare status word.

## Notes binding the oracle to the pipeline

- Only `EXACT` (adjudicated + fully value-evidenced + fault-free + `COMPLETE` + `CLEARED_FOR_PUBLICATION`)
  can satisfy a required unit. **`DERIVED` is a proposal and NEVER enters the C2 bijection or any credit**
  (corrects the earlier note). A view is complete only on exact set-equality with a closed, non-vacuous
  required-unit manifest.
- Failure codes reuse the `deposit_check` vocabulary family so an L4 view's refusal surfaces as a typed
  `REFUSED` reason in the gate.
- Every paper table (§3 counts, §5 crossed, §6.1 windows) must be **recomputed from the L3 acts**;
  finding a paper literal by string search is `NO_RAW_PROVENANCE` in spirit.
- The C2 bijection is Paper A's highest-risk gate: until all eight crossed acts map **`EXACT`** with
  authenticated blob+span evidence and an adjudication bound to that evidence, C2 stays `REFUSED`.

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
