# Codex exact-HEAD closure review — corpus repair at `57d41e5`

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `57d41e511c874689f0f7fbcf58ae080cc2a724d9` (`origin/main`)  
**Parent under review:** `a690789723a818969641c55d88ee7b5d9e3b74d0`  
**Disposition:** **BLOCKED before canonical `EXACT` mapping, L4 credit, or an auto-proposer.**

The repair is material. It closes the eight literal mutations requested in the `a690789` review,
and the current real extraction remains reproducible. It does **not** yet close the boundary those
mutations were intended to represent: the mapper trusts an unauthenticated L2 index, accepts a
vacuous/unbound required-unit manifest, and emits something much smaller than the frozen L3
`ActRecord`. Those paths can still mint `EXACT` or `COMPLETE` from caller assertions.

## Exact state and checks

- `HEAD == origin/main == 57d41e511c874689f0f7fbcf58ae080cc2a724d9`;
- all four GitHub workflows are green at that exact SHA;
- `python3 papers/corpus/test_corpus.py` is green;
- live re-extraction from the quarantine produced `CLEAN`, `55/55`, `1239 events`;
- the live report is JSON-equal to committed `CORPUS-EXTRACTION-REPORT.json`;
- the actual inventory has 55 unique agents and 55 unique source digests;
- the eight closure-condition regressions named in the prior review pass as claimed.

So the L1 preservation/current mechanical extraction result still stands. The findings below concern
the general mechanism and the proposed transition into adjudicated mapping/credit.

## Findings

### P0-1 — Value validation is performed against an unauthenticated L2 index

`l2_index_from_private()` decodes `raw_b64`, but drops `line_digest`, `event_index`, and any closed
bundle commitment. Neither it nor `build_l3()` recomputes the event identity or checks that the body
still matches the `event_id`, blob, occurrence, and extraction closure.

I extracted a real JSONL event, changed its indexed `raw_bytes` from root `R` to root `X`, retained
the original `event_id`/blob/span/closure, and supplied evidence digests over the forged bytes. Result:

```text
original_event_id_retained                 True
forged_raw_no_longer_matches_line_digest   True
mapper_result                              EXACT []
```

The shipped positive fixtures already demonstrate the structural weakness by constructing event IDs
such as `evt:0030-Fable` directly instead of passing an authenticated extractor output.

**Required repair:** introduce a validated L2 bundle/index boundary. Before mapping, re-derive every
line digest and event ID, validate event ordering/spans/blob membership/extraction closure, and bind
the bundle to the inventory/extraction report (or re-open the content-addressed L1). `build_l3()`
must accept only that validated type/report, not an arbitrary dictionary.

### P0-2 — The required-unit manifest is neither closed nor non-vacuous

`_view()` trusts an arbitrary runtime dictionary. There is no closed schema, manifest identity,
candidate/claim binding, allowed `unit_key`, non-empty requirement, or external commitment.

Executable counterexample:

```text
acts = []
manifest = {experiment_ids: [], unit_key: [], required_units: []}
result = COMPLETE, units = 0
```

This recreates the vacuous-green class at the corpus-credit boundary. A proposer that cannot mint an
`EXACT` mapping can still define the obligation set down to zero unless the manifest is an independent,
pinned operand.

**Required repair:** make required-unit manifests closed, versioned, content-addressed artifacts with
an exact claim set, allowed key schema, non-empty required set, uniqueness/type checks, and a separately
reviewed commitment. A missing or empty manifest must be typed `REFUSED`, never `COMPLETE(0)`.

### P0-3 — The emitted L3 record still does not implement the frozen L3 schema

The frozen schema requires source occurrence, root/parent topology, declared and observed verifier
identities, prompt/response digests, offspring before dedup, recorded dedup decisions, selected child
IDs, sampling provenance, completeness, and publication status. The public `acts` output contains only:

```text
act_id, completeness_status, experiment_id, faults, local_ref,
mapping_id, mapping_status, publication_eligibility
```

In addition, an `EXACT` candidate is accepted when:

- its `blob_id` is unrelated to the cited event;
- its occurrence span does not equal the event occurrence;
- its events could come from different blobs or extraction closures.

My mutation used a forged blob ID and occurrence `[1,2]` for an event actually at its full span. The
result remained `EXACT []`. `act_id` then bound the caller's forged address while hashing the entire
event body. `NO_RAW_PROVENANCE` from F4 is not implemented.

**Required repair:** distinguish a candidate from a full self-contained `ActRecord` in code, not only
in prose. Validate every occurrence against its event; enforce one disclosed source/closure discipline;
emit all required fields or typed `UNKNOWN`; implement summary-only/no-raw-provenance refusal.

### P0-4 — Graph finalization changes semantics after `mapping_id` is minted

`mapping_id` is computed in `_process()`. Later, `build_l3()` changes an act from `EXACT`/`DERIVED` to
`CONFLICTED` and appends `REPEATED_RUN`. The emitted mapping ID therefore does not address the emitted
mapping status.

Mutation result for both repeated-run records:

```text
emitted status = CONFLICTED
emitted mapping_id == recomputed(CONFLICTED)   False
```

The same post-hash issue applies to duplicate/dangling faults. In particular, only the second duplicate
`local_ref` is faulted; the first duplicate can still satisfy a required unit. I obtained:

```text
fault_count = 1
C2 view = COMPLETE, units = 1
```

**Required repair:** validate/finalize the whole graph before minting identities and views. Recompute
mapping IDs over the final status/fault-bearing body. Duplicate local IDs or act IDs must invalidate
all ambiguous members (or the whole graph), so no view can consume one side of an ambiguous duplicate.

### P1-5 — The adjudication record is present but not bound to the evidence it adjudicates

`_adjudication_valid()` only checks truthiness. `decision` need not be `EXACT`, and
`evidence_commitments` need not equal or commit to `mapping_evidence`. Replacing the commitments with
`["unrelated"]` still produced `EXACT []`.

Require a closed adjudication schema and equality between its committed evidence/body IDs and the
actual evidence commitment used by `mapping_id`. Validate adjudicator/authority/decision types and
allowed values; this establishes structural authorization, not the adjudicator's substantive wisdom.

### P1-6 — The claimed schema closure contains a version label, not the schema bytes

Both closure functions hash `corpus_ids.py`, their local implementation file, and the literal
`SCHEMA_VERSION = "0.1"`. Editing `CORPUS-SCHEMA-0.1.md` without manually changing that constant does
not rotate either closure. The implementation therefore does not yet match “closure over
ids+code+schema.”

Bind exact normative schema/profile bytes (or a generated closed schema artifact), plus every helper
that affects validation. Add a mutation proving a schema-byte change rotates the appropriate closure.

### P1-7 — Malformed operands still escape typed refusal

The mapper docstring says `_process()` never raises, but these inputs crash `build_l3()`:

```text
sampling = "not-an-object"   -> AttributeError
required manifest = {}       -> KeyError: experiment_ids
```

Malformed inventory/receipt shapes likewise raise `TypeError`/`KeyError` before an extraction report
is produced. Close schemas for every public operand and make one top-level exception-safe refusal
boundary; fuzz nested evidence, adjudication, sampling, occurrence, manifest, inventory, and receipt.

### P1-8 — The stated extraction set-equality is narrower than its prose contract

The current real inventory is clean, but the generic mechanism:

- accepts two agents pointing at the same digest as `CLEAN` despite the docstring promising duplicate
  digest rejection;
- ignores extra files in `quarantine/blobs/` while claiming inventory↔receipt↔blobs set-equality.

If the intended boundary is “the inventory selects a subset from a shared blob CAS,” narrow the prose
and keep duplicate-digest detection as a separate run-identity check. If it is closed equality, compare
the actual blob-name set and reject duplicate source digests explicitly.

### P1-9 — “F1–F9 executable oracle” still overstates the suite

Several frozen oracle outcomes are absent or differ from the executable tests:

- F4 `NO_RAW_PROVENANCE` is not implemented;
- F6 asks for `INCOMPLETE_TREE`, while code collapses it into missing units;
- F8 specifies `REDACTION_ID_REUSE`, while the helper does not accept/check a proposed reused ID;
- F2's L2 duplicate/gap branch and F3 are not exercised end-to-end;
- the oracle note still says `EXACT/DERIVED` may enter the C2 bijection, contradicting the new
  “DERIVED never credits” policy.

Either implement the frozen oracle exactly or version/repair it before claiming F1–F9 green. CI is
green for the current suite, not yet for the normative oracle as written.

## What the repair did close

This review does not retract the real progress at `57d41e5`:

- `DERIVED` no longer directly satisfies current non-empty manifests;
- evidence spans are value-checked against the supplied L2 body;
- the eight prior review mutations now have executable regressions;
- event order, mapping fields, public body, and loss report rotate their intended IDs in the tested
  pre-finalization cases;
- strict JSONL rejects duplicate keys and non-finite constants;
- the current 55-source preservation/extraction is clean and reproducible;
- no corpus claim flipped to `CHECKED`.

That is a substantial repair. The remaining issue is that the trusted operand boundaries around it
are still caller assertions.

## Minimal repair order

1. Authenticate and close L2 before any mapper logic; add the forged-body/stale-event-ID mutation.
2. Freeze a separate non-vacuous required-unit manifest artifact and fail closed on malformed/empty.
3. Implement the actual self-contained L3 `ActRecord` and occurrence/source validation.
4. Finalize graph status/faults before computing mapping IDs or views; close duplicate ambiguity.
5. Bind adjudication to the exact evidence commitment.
6. Bind closures to real schema/profile bytes and close all public operand shapes.
7. Reconcile the executable suite with F1–F9, then request another short exact-SHA review.

Exploratory candidate discovery can proceed privately, but do not canonize `EXACT`, create L4 credit,
or build the auto-proposer against `57d41e5`. An auto-proposer remains safe only after its entire input
boundary is authenticated and its output remains structurally incapable of changing credit.

## Closure mutations for the next handoff

```text
mutated L2 body + stale event_id              -> L2_INTEGRITY_BREAK before mapping
mixed blob/closure or forged occurrence       -> NO_RAW_PROVENANCE
empty required-unit manifest                  -> REFUSED: EMPTY_REQUIRED_SET
malformed manifest/sampling/inventory/receipt -> typed refusal, no crash
unbound adjudication commitment               -> AMBIGUOUS / ADJUDICATION_MISMATCH
EXACT -> CONFLICTED graph finalization         -> mapping_id rotates and re-verifies
duplicate local_ref required by a view         -> view REFUSED
schema-byte mutation                           -> relevant closure rotates
F1-F9                                          -> exact documented outcomes
```
