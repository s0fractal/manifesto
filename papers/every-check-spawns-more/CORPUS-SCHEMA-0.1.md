# Corpus schema 0.1 — the frozen export contract (Step 2)

The contract the exporter, validator, and `deposit_check` strategies are built against. It is frozen
here **before** the exporter exists, so the exporter is implemented against an oracle, not the other
way round. Nothing in this file copies, extracts, or publishes act data.

Companion: `CORPUS-THREAT-MODEL-0.1.md` (what this defends against) and `CORPUS-NEGATIVE-FIXTURES.md`
(the acceptance oracle). Preservation is already done: `CORPUS-QUARANTINE-RECEIPT.json`.

## Four layers, one direction

```
Layer 1  raw source blob            immutable · content-addressed · never edited
   │        (a quarantined transcript, identity = its sha256)
   ▼
Layer 2  extracted source events    fully regenerated from L1 by a pinned extractor
   │        (JSONL events, byte spans)
   ▼
Layer 3  derived act graph          fully regenerated from L2 by a pinned extractor+profile
   │        (acts, roots, offspring, recorded decisions)
   ▼
Layer 4  claim-specific evidence view   a projection with a per-claim completeness contract
            (C1 / C2 / C3 / C4 / C7)
```

**Invariants.**
- **L1 is immutable.** The raw blob is never normalized, re-encoded, or edited. Its identity is its
  sha256 (the content address in the quarantine).
- **L2–L4 are fully regenerable** from L1 + a pinned `extractor_id` (content digest of the extractor
  code) and, for L3/L4, a `profile_id`. A derived layer that cannot be reproduced byte-identically
  from L1 + the pinned ids is invalid. No hand-editing at any derived layer.
- **Provenance is mandatory downward.** Every L3 act cites the exact L1 `source_blob_id` + byte span;
  every L4 view cites the L3 acts it selects. An artifact with no L1 provenance cannot exist — this is
  the structural block on summary→raw laundering.

## Layer 1 — raw source blob

| field | meaning |
|---|---|
| `blob_id` | sha256 of the raw bytes (= quarantine content address) |
| `bytes` | length |
| `source_path` | the inventory locator it was preserved from |
| `verified` | `true` only if quarantine verified the digest before AND after copy |

Blobs live in the local restricted quarantine, **out of git**, until a per-blob
`CLEARED_FOR_PUBLICATION` decision (see Publication gate). The exact quarantine may contain material
the deposit must never contain.

## Layer 2 — extracted source events

Regenerated from one blob by `extractor_id`. One record per JSONL event.

| field | meaning |
|---|---|
| `blob_id` | the L1 blob |
| `event_index` | position in the blob (monotonic, gap-checked) |
| `byte_span` | `[start, end]` into the raw bytes (no normalization; spans are byte offsets) |
| `event_type` | as found (user / assistant / tool_use / tool_result / …) |
| `event_digest` | sha256 of the exact raw bytes of the span |
| `extractor_id` | content digest of the extractor that produced this layer |

## Layer 3 — derived act. Minimum fields (all required; absence is a typed `UNKNOWN`, never a default)

| field | meaning |
|---|---|
| `source_blob_id` + `occurrence` | L1 blob + exact byte span / line occurrence the act was read from |
| `experiment_id` | `EXP-RVB-1` / `-1b` / `-1c` / `-1-NC` / `-NC2` / `-2` |
| `act_id` | stable id = digest of (blob_id, occurrence, role_id) |
| `root_id`, `parent_act_id` | tree/chain structure; `parent_act_id=null` for a root act |
| `root_content_digest` | sha256 of the exact root text (ties the act to a Monday-corpus root) |
| `verifier_declared_identity` | what the prompt/agent said the verifier was (e.g. "Fable 5") |
| `verifier_observed_identity` | what the transcript metadata actually shows; mismatch is a finding |
| `agent_run_occurrence` | which agent transcript + position produced this act (run identity) |
| `prompt_digest`, `response_digest` | sha256 of the exact prompt-to-verifier and the response |
| `offspring_before_dedup` | the full offspring list **as generated**, each with its own digest |
| `dedup_removal_decisions` | the recorded removal-test / dedup decisions, **as found** (see Layer discipline) |
| `selected_child_ids` | which offspring were expanded at the next depth |
| `sampling` | `{temperature, top_p, model_build_id, …}` or a typed `UNKNOWN` per field |
| `completeness_status` | `COMPLETE` \| `PARTIAL` \| `UNKNOWN` — whether the full act (verdict+offspring+decisions) was recovered |
| `publication_eligibility` | `CLEARED_FOR_PUBLICATION` \| `WITHHELD:<reason>` \| `UNREVIEWED` |

**Layer discipline for decisions.** `dedup_removal_decisions` are stored **as historically recorded**.
Any *new* semantic audit (e.g. Kimi's paraphrase-leak question) is a **separate Layer-4 annotation**
carrying its own `extractor_id`/`profile_id`; it never overwrites or re-judges the recorded decision.

## Layer 4 — claim-specific evidence view

A projection selecting L3 acts for one claim, with an explicit completeness contract:

- `claim_id` (C1 / C2 / C3 / C4 / C7);
- `required_units` (e.g. C1b: the 8 chains V1–V8 × depths 0–4);
- `present_units`, `missing_units`;
- `view_status`: `COMPLETE` only if every required unit is present with `completeness_status=COMPLETE`
  and `publication_eligibility=CLEARED_FOR_PUBLICATION`; otherwise `INCOMPLETE`.
- An act may appear in several views, but **each view validates completeness independently** — no
  cross-view credit inheritance.

`deposit_check` consumes L4: a claim flips `FROZEN_CORPUS_NOT_DEPOSITED → CHECKED` only when its L4
view is `COMPLETE` and every number in the paper re-derives from the L3 acts (not from summary counts).

## C2 disambiguation contract (the hard case)

`root + verifier` is necessary but **not sufficient** — the same (root, verifier) pair may have retries
or several runs. The disambiguation key is:

```
experiment_id + root_digest + verifier_identity + agent_run_occurrence
```

Every C2 act carries:

- `mapping_status`: `EXACT` \| `DERIVED` \| `AMBIGUOUS` \| `CONFLICTED`;
- `mapping_evidence`: `source_blob_id` + the raw occurrence/span that proves the mapping.

Rules:
- **Never map by expected counts or expected results.** A mapping justified only by "the counts match
  the paper" is `AMBIGUOUS` by definition.
- C2 requires a **proven unique bijection** between the four crossed roots and the two verifier
  observations each (8 acts: X1–X4 + their V5/V6/V1/V2 counterparts).
- Any act `AMBIGUOUS` or `CONFLICTED`, or any missing side of a pair, leaves **C2 `REFUSED`** — even if
  neighbouring V/X chains are `CHECKED`.

## Publication gate

Raw L1 transcripts do **not** enter git until a separate, per-blob `CLEARED_FOR_PUBLICATION` decision.
Export to the repo carries only `CLEARED_FOR_PUBLICATION` L3/L4 material; anything else is
`WITHHELD:<reason>`. Redaction produces a **new** artifact id + a loss report; the original id is never
reused for the redacted artifact and lives only in the quarantine.
