# Narrow adversarial review — the eight C2 rows

**Reviewer:** Claude (Opus 4.8), self-review of its own artifact, 2026-09-02
**Reviewed:** `CORPUS-C2-MAPPING-0.1.json` — first at `25929da`, then the repaired table (digest
`11a92c08899beda09643568a590b6567a9fc9e285b14bc609640225f1c74f667`).
**Scope (as directed):** verify the eight concrete addresses of the semantic transition. No new
architectural pass — the pipeline architecture is already accepted.
**Disposition:** **CLEAN after one minimal repair. The repaired table is a frozen semantic operand
for the pre-governance infra step.** Still `DERIVED / UNREVIEWED`; no credit.

## Method

Every field re-derived **independently from the quarantine**, not trusted from the table: each event
id recomputed from the real blob bytes at its span; the observed model re-read from each transcript's
assistant `model` field; the root re-classified from the ROOT prompt; the run occurrence checked
against the transcript's agent. Then seven mutations run through the pipeline.

## Row checks — all PASS (15/15)

- every occurrence span resolves in the authenticated L2 index;
- every occurrence event id recomputes from the real blob bytes;
- no occurrence and no evidence-span reused across rows;
- observed model == transcript `model` field (independent), for all 8;
- root_digest == digest of the verbatim ROOT-file token, independently and by evidence span;
- run occurrence == the transcript's agent, for all 8;
- declared `Fable 5` is separated from the observed model on every row;
- both evidence spans (root + verifier) re-read to their asserted values;
- exact **4 roots × 2 observed models = 8 distinct** units (`claude-opus-5`, `claude-sonnet-5`);
- all rows `DERIVED`; decisions non-crediting (`PARTIAL` / `WITHHELD`, authority `none`);
- metadata only — no `raw_b64` / transcript content;
- baseline pipeline: **0 `EXACT` acts; C2 view `REFUSED`**.

## Finding (found and repaired in-review)

**F-ROW-1 — `root_digest` was asserted, not evidenced.** In the `25929da` table, `root_digest` was a
hash of a root *label* with **no evidence span** (only `verifier_identity` was evidenced). The
**root-swap mutation therefore did not break anything** (evidence unaffected; the 4×2 *set* is
preserved when two same-verifier rows exchange roots) — credit stayed 0, so the safety invariant held,
but detection did not.

**Minimal repair (done):** `root_digest` is now the digest of the **verbatim ROOT-file token** that
appears in each transcript's ROOT prompt (`0030_Monday.md`, `0025_Monday.md`, `FLOW.md §15`,
`FLOW.md §17`), with a `root_digest` evidence span pointing at it. Root-swap now breaks evidence
validation. Each row now carries **two** value-validated evidence spans (root + verifier).

## After the repair — all seven mutations break AND credit stays 0

| mutation | breaks | credit |
|---|---|---|
| verifier swap | evidence validation | 0 |
| root swap | evidence validation | 0 |
| span shift | `NO_RAW_PROVENANCE` | 0 |
| duplicate row | `DUPLICATE_LOCAL_REF` | 0 |
| missing row | 4×2 bijection | 0 |
| reused run occurrence | run-uniqueness check | 0 |
| declared↔observed substitution | evidence validation | 0 |

## Residuals — for the EXACT/governance step, NOT DERIVED defects

These do not affect the DERIVED table (credit is 0 by construction), but must be closed before any
`EXACT` promotion:

1. **`root_digest` is the ROOT-file-token digest, not the verbatim-claim digest.** It cleanly
   distinguishes and evidences the four roots, but EXACT should hash the exact root *claim* text the
   model recorded, with that span as evidence.
2. **Run-occurrence uniqueness is enforced at review, not in the pipeline.** `build_l3` does not yet
   reject two acts sharing an `agent_run_occurrence` across different units; add that check before EXACT.
3. **`experiment_id = EXP-RVB-1c` is asserted, not evidenced.** The 1b-original vs 1c-crossed provenance
   is not recoverable from the identical prompts (`AMBIGUOUS`); for the C2 *unit* (root × verifier) it is
   not needed, but a claim that the contrast is specifically the *crossed* design remains open.

## Conclusion

The eight C2 rows are each an honest, independently-verified address: real event occurrences in the
pinned 1239-event bundle, the observed model evidenced against the transcript, four roots evidenced by
their ROOT-file tokens, a clean 4×2 bijection, and zero credit. **The repaired table is frozen as the
semantic operand.** Pre-governance infra (decision register, L3 validator, serialized-L3-only L4
replay) may now be built against this reviewed table rather than against an assumption about it.
