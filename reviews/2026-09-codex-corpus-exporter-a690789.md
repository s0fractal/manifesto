# Codex adversarial review — corpus exporter at `a690789`

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `a690789723a818969641c55d88ee7b5d9e3b74d0` (`origin/main`)  
**Scope:** `papers/corpus/`, corpus schema/threat-model/oracle, committed extraction report, and
`papers-deposit-check` integration  
**Disposition:** **BLOCKED before an auto-proposer, L4 deposit strategies, or any
`REFUSED → CHECKED` transition.** The quarantine preservation and current 55-blob mechanical scan are
useful; the mapping/identity layer can presently mint complete claim views from unverified assertions.

## What was checked

- read all exporter/mapper/identity/test code and the frozen schema/threat model;
- ran `papers/corpus/test_corpus.py` at the reviewed SHA;
- verified live Actions: all four workflows are green at this SHA;
- inspected the committed 55-row extraction report against inventory and quarantine receipt;
- ran independent mutations for evidence-free `DERIVED`, one-act completeness, mapping/ID aliasing,
  public-projection aliasing, event-order aliasing, non-finite JSON, and omitted inventory entries.

Green CI currently establishes that the shipped synthetic tests pass. It does not establish the
schema's claimed L2→L4 credit boundary, because several positive fixtures encode the defect.

## Findings

### P0-1 — `DERIVED` with no mapping evidence can mint `C2 COMPLETE`

`corpus_map.py:_resolve_status` requires all four evidence components only when the entry claims
`EXACT`. A `DERIVED` entry with an empty `mapping_evidence` list remains `DERIVED` without a fault.
`_publishable_complete` then accepts both `EXACT` **and `DERIVED`**. Therefore an auto-proposer — whose
contract is specifically “may assign DERIVED, never EXACT” — is already authorized to complete C2.

Reproducer at `a690789`: eight entries over four arbitrary root strings × two arbitrary verifier
strings, each `DERIVED`, `COMPLETE`, `CLEARED_FOR_PUBLICATION`, with **zero mapping evidence**, produce:

```text
C2 derived/no-evidence: {'status': 'COMPLETE', 'acts': 8}
fault_count: 0
```

The current positive C2 fixture has the same underlying weakness: its generic synthetic event IDs do
not contain or prove the root/verifier/run values; the test table merely asserts them.

**Required repair:**

- proposer output is `PROPOSED`/`DERIVED` and is never publishable or L4-complete;
- L4 claim credit requires `EXACT` mappings only;
- promotion to `EXACT` requires a separate review/adjudication record with identity, authority,
  decision, and exact evidence commitments;
- a mutation replacing every EXACT mapping by DERIVED must force every affected view to REFUSED.

**Type:** `integrity_break` / self-issued validation credit.

### P0-2 — mapping evidence proves only that an event ID exists, not what the event says

`_resolve_status` receives only a **set of event-ID strings**. For each evidence kind it checks only:

```text
event_id ∈ l2_event_ids
```

It never verifies that the cited event/span contains the asserted `experiment_id`, `root_digest`,
`verifier_identity`, or `agent_run_occurrence`; indeed `mapping_evidence` has no value commitment or
byte subspan. The same unrelated valid event can be cited four times and upgrades a mapping to EXACT.

Similarly, `build_l3` accepts author-supplied `blob_id`, `byte_start`, and `byte_end` but cannot check
them against the referenced events, because it receives no event records. A valid event from blob A
can be presented as evidence for a forged occurrence in blob B.

This does not satisfy `CORPUS-SCHEMA-0.1.md:32–34, 101–121`, whose promise is downward provenance and
raw occurrence evidence.

**Required repair:** pass a closed L2 event index, not a set of IDs. Each mapping-evidence item must
bind at least:

```text
kind
event_id
source_blob_id
byte_start / byte_end (or a narrower value span)
observed_value_digest
extraction_profile_id
```

The validator must reread the raw span, apply a pinned field-extraction rule, and compare the observed
value to the mapping body. Manual assertion is not evidence of itself.

**Type:** `integrity_break` / provenance laundering.

### P0-3 — claim completeness has no closed required-unit manifest

For C1/C3/C4/C7, `_view` selects every act with a matching experiment name and returns `COMPLETE` if
all **present** acts are complete/publishable. It does not know how many units are required or which
roots/depths/runs must be present. One arbitrary act is enough:

```text
C1 one-act: {'status': 'COMPLETE', 'acts': 1}
```

The code comments acknowledge `required_units` as a “later refinement”, but the current function emits
the final word `COMPLETE` now. For C2 the check is only cardinality: any four root strings × any two
verifier strings qualify; it does not compare against the exact expected root digests, verifier
identities, or selected run occurrences.

**Required repair:** add a closed, candidate-bound required-unit manifest before any view can become
complete. It must name exact units, not counts alone:

- experiment/profile ID;
- exact root digests;
- exact verifier identities;
- run-selection policy/occurrences;
- required depths/parent-child structure;
- expected act set and allowed exclusions.

Compare required and present sets for equality and emit exact missing/extra/refused units. Until that
manifest exists, all real views must return `REFUSED: REQUIRED_UNITS_UNSPECIFIED`.

**Type:** `integrity_break` / vacuous completeness.

### P0-4 — the emitted “L3 acts” do not implement the frozen L3 schema

`CORPUS-SCHEMA-0.1.md:62–80` requires source occurrence, root/parent identities, exact root digest,
declared and observed verifier identities, prompt/response digests, offspring-before-dedup, recorded
dedup/removal decisions, selected child IDs, sampling, completeness, and publication eligibility.

The report emitted by `build_l3` contains only:

```text
local_ref, act_id, experiment_id, mapping_status,
completeness_status, publication_eligibility, faults
```

Most required fields are neither emitted nor validated. `completeness_status=COMPLETE` and
`CLEARED_FOR_PUBLICATION` are accepted as table literals; no tree, offspring list, decision record,
clearance record, prompt, or response is present to justify them.

Local refs are also not closed: duplicate `local_ref` values silently overwrite `by_local`, making
parent/child resolution depend on the last entry.

**Required repair:** distinguish a `MappingCandidate` from a schema-valid `ActRecord`. Do not call the
current metadata rows L3 acts. An ActRecord must be closed-schema, self-contained for every required
field, recomputed from L2/raw evidence, and validated before it enters a graph. Duplicate local refs,
bad scalar types, invalid spans, and unknown fields must be typed fail-closed outcomes, not crashes or
overwrites.

**Type:** `integrity_break` / schema non-conformance.

### P0-5 — identities do not bind the semantics they claim to identify

There are four independent address gaps.

1. **Act mapping alias.** `act_id` binds blob/span plus a sorted set of event IDs, but not
   experiment/root/verifier/run/mapping evidence. Mutating only `root_digest` produced the same
   `act_id`.
2. **Order alias.** `_canonical_body` sorts event IDs. `[prompt,response]` and `[response,prompt]`
   receive the same act body identity even though order is semantic.
3. **Mapping identity unused.** `mapping_id()` exists in `corpus_ids.py` but is never emitted and does
   not bind mapping evidence/status even if called.
4. **Public-projection alias.** `public_id` binds only `(redaction_profile_id, source_act_id)`, not the
   projected public content or loss report. Two different loss reports produced the same public ID.

Reproduced:

```text
same act id across different root mapping: True
act body order ignored: True
same public id across different loss: True
```

**Required repair:** define canonical bodies per entity and hash the complete meaning-bearing body:

- Act ID: ordered event occurrences plus reconstructed act content/provenance;
- Mapping ID: subject act/event, all four mapped values, exact evidence commitments, mapper profile,
  mapping status, and adjudication record;
- Public projection ID: canonical public bytes/body, redaction profile, source ID, and exact loss
  report.

Keep act identity distinct from mapping identity, but link both explicitly.

**Type:** `integrity_break` / address aliasing.

### P0-6 — extractor identity is not the claimed code/schema closure

`extractor_identity()` hashes only `corpus_extract.py`. It excludes:

- `corpus_ids.py`, although that module determines every emitted ID;
- `CORPUS-SCHEMA-0.1.md` / a machine-readable schema;
- strict-JSON and event-type profile identity;
- Python/runtime dependency assumptions;
- `corpus_map.py` and any future mapping profile for L3.

Changing the ID algorithm or frozen schema without editing `corpus_extract.py` leaves the extractor ID
unchanged, contrary to the module docstring and schema's closure promise. L3 records carry only this L2
extractor ID; there is no separate mapper/profile closure.

**Required repair:** use an ordered, path-independent closure manifest over all verdict-affecting code
and protocol/schema bytes. Give extraction and mapping distinct closure IDs. Add mutations proving that
changing `corpus_ids.py`, strict-JSON profile, schema, event extraction, or mapping rules rotates only
the appropriate downstream identities.

**Type:** `integrity_break` / incomplete verifier closure.

### P1-7 — extraction completeness is reported over the receipt subset, not the inventory contract

`extract_from_quarantine` iterates `receipt["records"]`; it never proves set equality with
`inventory["transcripts"]`. If inventory names two sources and the receipt silently omits one, the
function reports:

```text
{'extracted': 1, 'refused': 0, 'drift': 0, 'events_total': 1}
```

There is no `expected`, `missing`, or `extra` count. Duplicate agents in inventory overwrite silently
in `inv_by_agent`; duplicate receipt agents overwrite private L2 in `private[agent]`. `BLOB_MISSING`
and `SKIPPED_NOT_VERIFIED` are not counted as `refused` or `drift`, so the headline summary can look
clean while sources were skipped.

The actual committed report is internally consistent at this SHA (55 rows, 55 unique agents/digests,
all EXTRACTED, zero unknown event types). The defect is that the mechanism does not establish that
closed-set fact.

**Required repair:** validate closed schemas and exact set equality among inventory, receipt,
quarantine blobs, and report. Reject duplicate agents/digests as specified, validate digests as 64
lowercase hex before path construction, and report exact expected/present/missing/extra/refused sets.

**Type:** `integrity_break` in corpus completeness reporting.

### P1-8 — “strict JSONL” currently accepts non-JSON constants

Python's `json.loads` accepts `NaN`, `Infinity`, and `-Infinity` unless `parse_constant` rejects them.
The current extractor accepted:

```json
{"type":"user","x":NaN}
```

as one valid event. This is outside strict JSON and can introduce cross-implementation disagreement.

**Required repair:** reject non-finite constants explicitly and add fixtures for all three spellings,
top-level non-object policy, invalid UTF-8, CRLF, empty/whitespace lines, and a final line without LF.

**Type:** `integrity_break` / parser-profile gap.

### P1-9 — fault accounting is not closed

Repeated-run detection appends `REPEATED_RUN` to each act after the top-level `faults` list is built,
but does not append a corresponding report fault. `fault_count` can therefore disagree with act-level
faults. Several malformed table shapes can also raise untyped Python exceptions (`int()`/negative
`to_bytes`, non-dict evidence, missing keys) rather than produce the promised fail-closed report.

**Required repair:** one closed validator pass should produce a single canonical fault set from which
both per-record and summary counts are projected. Fuzz malformed table shapes and require typed output
with no uncaught exception.

**Type:** `integrity_break` / report inconsistency.

### P1-10 — “private L2 with content” is actually an event-occurrence index

`extract_blob` parses each JSON line but discards `obj`; private L2 retains only IDs, offsets, type,
and digest. This is a useful byte index, but it is not an extracted event record “with content”, and it
cannot support value-bearing mapping validation without reopening L1.

Choose and document one design:

- call it an L2 occurrence index and make mapping validation reread exact L1 spans; or
- store a private canonical event body linked to the raw span and prove it re-extracts byte-identically.

Either is defensible. The current mixed description is not.

**Type:** `scope_boundary`.

## What is established at `a690789`

- The committed inventory and receipt describe 55 unique preserved sources, and the committed report
  contains 55 unique EXTRACTED rows with 1,239 event occurrences and zero unknown event types.
- The L1 reader uses quarantine content addresses, byte offsets, duplicate-key rejection, whole-blob
  refusal on ordinary parse errors, and path-independent event IDs.
- Raw transcript content was not committed in the extraction report inspected here.
- CI is green for the current synthetic suite and remains correctly distinct from deposit-clean.

These are meaningful preservation/indexing credits. They do **not** yet establish L3 act identity,
mapping truth, corpus completeness, publication clearance, or any Paper A claim.

## Repair order

1. Make all real L4 views refuse `REQUIRED_UNITS_UNSPECIFIED`; require EXACT, independently adjudicated
   mappings for credit.
2. Replace event-ID membership with raw-span/value validation against a closed L2 index.
3. Implement the actual closed L3 ActRecord schema and exact required-unit manifests.
4. Repair entity identities and extraction/mapping closure IDs.
5. Close inventory/receipt/report set validation, strict JSON, malformed-input handling, and fault
   accounting.
6. Re-run mutations, then request a short exact-HEAD review.
7. Only after that introduce an auto-proposer; its outputs remain untrusted DERIVED candidates and
   can never directly change deposit status.

## Closure condition

Do not build the auto-proposer on `a690789`. The next acceptable handoff should include mutation
outputs demonstrating:

```text
8 DERIVED/no-evidence mappings       -> C2 REFUSED
1 present act for a multi-unit claim -> REQUIRED_UNITS_MISSING
arbitrary event cited for root       -> EVIDENCE_VALUE_MISMATCH
mapping-field mutation               -> mapping_id rotates
event-order mutation                 -> act_id rotates
loss/public-content mutation         -> public_id rotates
omitted inventory source             -> fail-closed missing-set report
NaN / malformed table                -> typed refusal, no crash
```

At that point the mechanical extraction boundary can be considered closed enough to begin proposing
mappings without letting the proposer certify itself.
