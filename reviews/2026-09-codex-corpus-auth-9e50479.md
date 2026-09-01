# Codex exact-HEAD closure review — corpus authentication at `9e50479`

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `9e5047986b02c85472099bb236e2b794ea5027c0` (`origin/main`)  
**Substantive repair:** `8de40a9`  
**Disposition:** **BLOCKED before canonical `EXACT` mappings, pinned required-unit manifests, L4
credit, or an auto-proposer.**

The second repair is again real: all eight G-regressions pass; stale-event-ID tampering is caught;
occurrences are checked; vacuous empty manifests are refused; duplicates are finalized before IDs;
schema bytes enter the closures. The current 55-source extraction also remains reproducible.

The remaining gap is narrower and now sharply visible: `authenticate_l2()` proves that a supplied
entry is self-consistent, but not that it came from the frozen extraction. Then `COMPLETE` and
`CLEARED_FOR_PUBLICATION` remain caller-controlled, unaddressed fields. A coherent invented L2 plus a
one-unit runtime manifest can therefore still produce corpus credit.

## Exact state and positive evidence

- `HEAD == origin/main == 9e5047986b02c85472099bb236e2b794ea5027c0`;
- all four GitHub workflows are green at that SHA;
- `python3 papers/corpus/test_corpus.py` passes;
- live quarantine extraction is `CLEAN`, `55/55`, `1239 events`;
- live extraction report is JSON-equal to committed `CORPUS-EXTRACTION-REPORT.json`;
- G1–G8 produce their asserted outcomes in the current suite;
- no deposit claim has flipped to `CHECKED`.

These facts preserve the L1→L2 result. The findings concern the general L2→credit mechanism.

## Findings

### P0-1 — `authenticate_l2()` establishes self-consistency, not source authentication

The function recomputes an event ID from five **supplied** operands: body, blob ID, span, and extraction
closure. It does not receive or verify the inventory, extraction report, expected closure, blob
membership, or a committed L2 bundle identity. Thus a caller can invent all five coherently.

Independent mutation:

```text
invented extraction_closure + invented blob_id + invented body
authenticate_l2                  -> CLEAN []
mapping                           -> EXACT []
one-unit view                     -> COMPLETE, units=1
```

There are two even simpler bypasses:

1. `build_l3()` accepts any dictionary containing `status="CLEAN"`, `index`, and `faults`; it does not
   prove the dictionary came from `authenticate_l2()`;
2. the returned bundle is mutable, and `build_l3()` does not reauthenticate it after post-validation
   mutation.

G1 only proves detection of an **incoherent** mutation that retains a stale event ID. It does not prove
the event belongs to the preserved corpus.

**Required repair:** make L2 an externally bound artifact, not a structural dictionary. Mint a
content-addressed L2 bundle ID from the exact inventory/extraction-report commitment, expected
extraction closure, closed source set, ordered event records, and event bodies/commitments. `build_l3()`
must revalidate canonical bundle bytes (or accept an opaque immutable validated type impossible for a
caller to construct), and bind the consumed `l2_bundle_id` into every downstream report/ID.

### P0-2 — Credit changes while every emitted operand ID stays unchanged

`act_id` binds occurrences/content. `mapping_id` binds mapping fields/evidence/status/adjudication.
Neither binds `completeness_status` nor `publication_eligibility`, even though `_publishable_exact()`
uses both to grant a required unit.

I ran the same act and mapping twice:

```text
run A: completeness=PARTIAL, publication=WITHHELD:x -> view REFUSED
run B: completeness=COMPLETE, publication=CLEARED  -> view COMPLETE

act_id(A)    == act_id(B)       True
mapping_id(A)== mapping_id(B)   True
```

This is a direct unaddressed credit flip. The fields are also accepted from the mapping candidate
without evidence, adjudication, publication authority, or a separate decision record.

**Required repair:** derive completeness from a closed act/tree contract and represent publication
clearance as a separate adjudicated, content-addressed decision. Bind both decisions—and the manifest
used—into a claim-view/evaluation ID. A mapping identity alone should not be presented as the identity
of credit.

### P0-3 — The frozen L3 `ActRecord` is still presence-checked, discarded, and non-replayable

`ACTRECORD_REQUIRED` checks only whether keys exist. `None` satisfies `root_id`, declared/observed
verifier identity, prompt/response digests, offspring, and dedup decisions. With those fields all set to
`None`, my record still became `EXACT []` and satisfied the view.

The fields are then discarded. The emitted act contains only:

```text
act_id, completeness_status, experiment_id, faults, local_ref,
mapping_id, publication_eligibility, status
```

Consequently L4 cannot independently recompute the paper's claims from this output, and the purported
ActRecord cannot be serialized, transferred, or replayed without the original candidate table.

**Required repair:** implement a real closed ActRecord body with typed `UNKNOWN`, source occurrence,
topology, prompt/response, offspring/dedup, verifier identities, and provenance. Validate types and
semantic links, emit `{id, body}`, and ensure mutations of any meaning-bearing field rotate the record
identity. Keep a metadata report separate from the private/self-contained L3 bundle.

### P0-4 — Required-unit manifests are non-vacuous but still caller-defined and unaddressed

`validate_manifest()` prevents `required_units=[]`, which closes the literal vacuous-green mutation.
But the manifest remains an arbitrary runtime dictionary. It is not closed against unknown fields,
not content-addressed, not pinned to a paper/claim revision, not independently authorized, and absent
from the returned report identity.

Thus the caller can replace an eight-unit obligation with one convenient unit and obtain `COMPLETE`.
No ID reveals which obligation set produced that status.

This is consistent with the handoff saying the real pinned manifests are the *next* step, but it means
the present mechanism must not yet claim a closed manifest boundary.

**Required repair:** the next manifests must be separate reviewed artifacts with closed schemas,
manifest IDs, exact claim/candidate/source bindings, fixed allowed keys, typed exclusions, and temporal
provenance. A view report/evaluation ID must bind the manifest ID.

### P1-5 — Adjudication commits to event IDs, not to the exact evidence

`_adjudication_ok()` compares a set of event IDs. Evidence identity, however, includes kind, exact
span, observed-value digest, and asserted component. If the same value occurs twice in one event, an
author can move all evidence spans while retaining the same adjudication commitment.

Mutation result:

```text
evidence spans A -> EXACT
evidence spans B in the same event -> EXACT
same adjudication record -> accepted for both
mapping_id rotates -> True
```

The mapping ID notices the changed evidence; the adjudication does not authorize that exact mapping.
Commit to canonical evidence-record IDs or the exact evidence commitment digest, not merely the set of
container event IDs. Preserve multiplicity/order where meaningful.

### P1-6 — L2 structural validation is incomplete

The new boundary still accepts:

- the same event twice (`CLEAN`, silently collapsed to one index entry);
- an event claiming `[0,999]` over a ten-byte body (`CLEAN`);
- arbitrary/missing expected extraction closures;
- no `event_index`, gap/ordering check, source-agent membership, or bundle-level closed set.

This leaves F2's L2 branch and the schema's gap-free ordered-event promise unimplemented. Validate
non-negative exact spans/body lengths, uniqueness, ordering/index continuity, one expected closure, and
closed source membership before minting a bundle ID.

### P1-7 — Public boundary shapes remain mutable and partly exception-unsafe

Despite the new shape checks, `build_l3({"status":"CLEAN","index":{}}...)` crashes when `faults` is
missing; nested manifest exclusions and bundle/index shapes are not closed; `bundle_from_private()` can
still throw on malformed entries/base64. More fundamentally, every “validated” structure is a mutable
ordinary dictionary.

Use canonical serialized inputs plus closed validators at each public boundary. Return typed refusal
for every malformed nested operand and avoid a validation token that callers can fabricate or mutate.

### P1-8 — Two G-tests do not prove their named closure

- G5 computes `recomputed` but never asserts equality. Its asserted `exact_id` uses empty evidence and
  adjudication digests, so `mapping_id != exact_id` would pass even if the implementation had retained
  `EXACT`.
- G8 only proves that the generic `closure_id()` hash changes when arbitrary bytes change. It does not
  mutate the actual schema/code dependency and assert that `extraction_closure_id()` and
  `mapper_closure_id()` rotate with the intended downstream scope.

The implementation appears to mint after finalization and does read the schema bytes, but the named
regressions should test those facts rather than an easier surrogate. Also add the coherent-forgery,
post-validation mutation, credit-field aliasing, duplicate-event, and impossible-span cases above.

## What is genuinely closed at `9e50479`

- stale-ID mutation of an L2 body is rejected;
- candidate occurrences must match the supplied index's blob and span;
- empty manifests do not produce `COMPLETE(0)`;
- duplicate local/act IDs invalidate all members;
- graph status is finalized before current mapping-ID minting;
- the literal unrelated-event adjudication mutation is rejected;
- schema bytes are now read into extraction and mapping closures;
- malformed sampling and the tested operand shapes receive typed faults;
- the current real extraction remains exact and clean.

This is meaningful narrowing. The word that still overclaims is **authenticated**: the current code
has internal content consistency, not provenance authentication to the frozen corpus.

## Minimal repair order

1. Freeze and authenticate a canonical L2 bundle against inventory + extraction report + expected
   closure; eliminate caller-minted/mutable `CLEAN` bundles.
2. Emit complete content-addressed L3 `{id, body}` records; derive/validate all schema fields.
3. Separate and address completeness, publication clearance, and adjudication decisions; no credit
   field may be a bare candidate assertion.
4. Introduce the independently pinned required-unit manifests and bind their IDs into view reports.
5. Bind adjudication to exact evidence-record commitments.
6. Close L2 structure/public operand schemas and repair the G5/G8 regressions.
7. Re-run adversarial mutations, then request another exact-SHA closure pass.

Human exploration of likely transcript mappings may continue as explicitly untrusted `DERIVED`
working notes. Do not yet canonize `EXACT`, mint L4 credit, or build a proposer against this boundary.

## Required mutations for the next handoff

```text
coherent invented L2 event/source/closure     -> UNKNOWN_SOURCE / BUNDLE_NOT_COMMITTED
caller-minted {status:CLEAN,index:...}        -> MALFORMED_BUNDLE
post-validation bundle mutation               -> BUNDLE_ID_MISMATCH before mapping
duplicate event / impossible span / gap       -> typed L2 refusal
PARTIAL/WITHHELD -> COMPLETE/CLEARED           -> decision/view IDs rotate
null/forged ActRecord fields                   -> SCHEMA_INVALID / evidence mismatch
same event, different evidence spans          -> ADJUDICATION_MISMATCH
one-unit replacement manifest                 -> manifest_id changes; pinned claim binding refuses
serialized L3 only, source table removed       -> L4 re-derives or refuses
actual schema/code mutation                    -> exact intended closures rotate
```
