# Corpus source inventory — Paper A act corpus (Phase 0)

Human summary of `CORPUS-SOURCE-INVENTORY.json`. **Phase 0 locates and statuses primary material;
it copies, exports, reconstructs, and derives nothing.** It exists to answer one question honestly
before an exporter is written: *do the primary verification acts behind Paper A physically exist, and
where?*

## Headline finding

**They largely exist — and were not reconstructed from the summary numbers.** The experiments of
2026-08-30 were run one subagent per verification chain/tree, and **53 of those Aug-30 subagent
transcripts survive** in this machine's session store, carrying the actual verdicts and offspring.
That is the good case the phase was meant to distinguish from `MISSING`.

Two honest caveats keep this from being a clean "AVAILABLE_EXACT" across the board:

1. **Machine-local, not in git, not portable.** The locators point into `~/.claude/…/subagents/` on
   *this* machine. The sha256 digests in the JSON are the portable identity; the bytes are session
   state. If this store is lost before export, the affected claims collapse to `MISSING` permanently.
2. **`drafts/EXP-RVB-1-RESULTS.md` is `SUMMARY_ONLY`** — per-depth counts and prose, never offspring
   texts (its own line 27 says the full JSON trees live in the transcripts). Counts here can **never**
   be promoted to raw acts.

## Per-claim status

| claim | experiment | designed | raw status | note |
|---|---|---|---|---|
| C1 | EXP-RVB-1 (d0–2) | 12 trees / 60 acts | `AVAILABLE_PARTIAL` | tree agents sit in the UNCLASSIFIED set; map to F1–F4/E1–E4/C1–C4 |
| C1, C3 | EXP-RVB-1b (d0–4) | 8 chains V1–V8 / 40 acts | `AVAILABLE_PARTIAL` | 11 chain transcripts (8 designed + extras/reruns **and the crossed X1–X4**) — map to V1–V8 |
| **C2** | EXP-RVB-1c (crossed) | 4 acts X1–X4 | `AVAILABLE_PARTIAL` **(disambiguation risk)** | X1–X4 share the 1b template → **no dedicated transcripts**; need both verifiers' offspring on the same root. **Highest-risk claim.** |
| C4 | EXP-RVB-1-NC | 6 controls T1–T6 | `AVAILABLE_EXACT` | 6 transcripts = 6 designed controls |
| C4 | EXP-RVB-NC2 | 4 controls S1–S4 | `AVAILABLE_PARTIAL` | 6 transcripts vs 4 designed — reconcile 2 extras |
| C7 | EXP-RVB-2 (glossary) | pre/post windows G4/G5/G6 | `AVAILABLE_PARTIAL` | 8 transcripts; map to the exact intervention boundary |
| roots | Monday corpus | — | `AVAILABLE_EXACT` (in git) | `quotes/Monday/chat-0001/` (76 files) |

Out of the act-corpus scope: **C5** (COMPILE-0030 — already CHECKED by replay), **C6** (owed as an
executable simulation, not acts), **C8** (receipt-backed legacy gate).

## What this changes for the deposit gate

Nothing flips yet. `deposit_check` still refuses C1–C4/C7 as `FROZEN_CORPUS_NOT_DEPOSITED`, which is
correct: *available-but-unexported* is not *deposited*. The inventory upgrades our **knowledge** from
"maybe MISSING" to "AVAILABLE, machine-local, needs byte-preserving export + act-mapping". Each row
flips `REFUSED → CHECKED` only after export + validation, and **address-by-address**: C2 stays
`REFUSED` until the crossed offspring are disambiguated, even if its V/X neighbours are `CHECKED`.

## Hard boundaries carried into the exporter (do not weaken)

- no model regeneration of missing responses; summary counts never become a raw act;
- historical removal/dedup decisions are recorded decisions — any new semantic audit is a separate layer;
- redaction makes a new artifact id + loss report, never an in-place byte edit;
- never export secrets, subagent system prompts, or non-act scaffolding — `WITHHELD` + reason instead.

## Next in the cadence

`schema + threat model → byte-preserving exporter → corpus validator + mutations → deposit_check
strategies → CI`. The schema must separate raw bytes from the derived index and carry
`act_id / root_id / parent_act_id`, prompt/response digests, model/vendor/version or honest `UNKNOWN`,
pre-dedup offspring, recorded removal/dedup decisions, selected child ids, and source provenance.
