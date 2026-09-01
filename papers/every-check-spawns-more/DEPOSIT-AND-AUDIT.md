# Deposit & audit — Every Check Spawns More v0.2

Consolidates deliverables §7.3–§7.8 of the rewrite brief: checker gap list, bibliography audit,
non-reproducible-sentence list, clean-environment reproduction, and a deposit manifest proposal.
Nothing here deposits, tags, licenses, or reserves a DOI.

## A. Checker — the current one is STALE-GREEN; replace it (Codex P0-S2)

**The current `check_claims.py` is stale-green with respect to this ledger.** It searches
`EXP-RVB-1-RESULTS.md` for μ **literals** — it does not parse a row, recount an act, verify a
denominator, or bind a number to a claim ID. It discards `RECEIPT_SHA256` without verifying it, and
combines a stale committed `SSD-INDEX-AUDIT.receipt.json` (source digest `dad53f…`) with the current
`SSD-INDEX-AUDIT.md` (`0a75d8…`) yet stays green. Its banner says "matches `paper.md`" while the
reviewed surface is the unpromoted v0.2 file. This is the exact failure the embedded-claims work exists
to prevent: a true local check borrowing a broader claim.

**Do not implement the old gap-list verbatim (Codex).** Replace the checker so it *decides this
ledger*:

1. **Closed claim manifest → checks.** Compile `CLAIM-LEDGER.md` (C1–C8) into checks; bind every
   checked number to a claim ID, a source row, and (where relevant) a profile. Emit exact `checked`,
   `excluded`, and `refused` sets. No `100+` where an exact count exists.
2. **Verify commitments before consuming bodies.** Re-hash each receipt and compare to its
   `RECEIPT_SHA256`; re-hash each source file and compare to the digest the receipt names. A digest
   mismatch (e.g. the index-audit receipt vs the current file) is a **typed refusal**, not a green.
3. **A missing raw record is a typed refusal, not a string-presence pass.** The frozen act corpus
   (§10 of the paper) does not yet exist; the checker must REFUSE the ô tables as `NOT_DEPOSITED`
   rather than confirm a literal appears somewhere.
4. **Executable scheduler counterexample.** Ship a deterministic simulation of the two reviewer
   counterexamples (μ=0.5 closes 75%; μ=1.2 closes 40% on the first act) so the retired theorem
   cannot return.
5. **The deposit gate invokes the v0.2 artifact it deposits**, not `paper.md`.

## B. Bibliography audit (source exists · supports the sentence · not borrowed authority)

| key | in-text? | supports its sentence? | borrowed authority risk | verdict |
|---|---|---|---|---|
| `sigma-glyph` | yes (§1,§4,§6→relocated,§7) | yes — the reference machine / compilation target | no | **keep** |
| `warrant` | yes (§1,§5.3,§7) | yes — the sealing/decision-record substrate | **watch**: cite as conformance target, never as validation of the paper's interpretation | **keep, scoped** |
| `cacm-verification-debt` | yes (§1,§7) | yes — names "verification debt" without a model/coefficient; the gap this improves on | no | **keep** |
| `luu2015demystifying` | yes (§1,§7) | yes — verifier's dilemma as an orthogonal problem | no | **keep** |
| `barendregt2005challenge` | yes (§1,§7) | yes — de Bruijn criterion for the anchor leg | no | **keep** |
| `garrabrant2016` | §7 only | contrast (logical induction) | low | keep as related, not load-bearing |
| `irving2018debate`, `christiano2018amplification` | §7 only | contrast, framed as "μ-reduction engineering" | **watch**: do not imply these methods are validated here | keep as related |
| `ershov1958`, `filliatre2006`, `merkle1987`, `berger1991` | §6 (AIE) | attribution of classical components | n/a | **relocate to Paper B** with the AIE material |

Named-only references (no bib key; disclaimed as non-contributions): Gödel II, Löb, Tarski,
Agrippa, Galton–Watson, Little, Loynes, renewal–reward. v0.2 keeps them named and explicitly adds
nothing to them.

## C. Sentences that depend on transcript-only / external-live / unverified evidence

Each must be labeled in the deposited paper as transcript/manual, not presented as replayable:

- **All per-act offspring counts** (§3 tables; μ values 5.42 … 2.25, 0.14, 1.25; the debt curves
  6→3→3→7→4→8). *Transcript*: re-runnable in kind with the same prompts/corpus, not byte-identical.
- **Verifier effect** (Fable ≈3.2 vs Sonnet ≈2.1) and the counting-instruction effect. *Transcript.*
- **Crossed-design verdict flips** (0030, 0025) and "negative 2/2, positive 0/2". *Transcript.*
- **The SSD guessed values** (the model's original memory guesses). *Transcript*; v0.2 does **not**
  cite the specific guessed numbers, only the machine-measured actual set {7,12,12,67}.
- **Warrant — two different credits (Codex S1).** The named stored SKI checks re-execute under the
  local Warrant (`warrant check 0597575d…` → PASS at 2,108 ATP; `warrant verify --settlement` → 4
  records, 0/0). *External command.* But the pack **as a whole** recorded no dependency closure and is
  historically sealed: `python tools/replay_pack.py replay drafts/ssd-pack` returns
  `REPLAY: LEGACY_UNPINNED` (exit 1). Report both; a stored-check PASS is not pack-level strict replay.
  Any dependency-closed pack must be a **new** artifact, not repaired history.
- **External citation bibliographic details.** *Unverified by the checker* — human bibliography
  audit only (§B above).

Machine-checked (safe to present as replayable): the COMPILE-0030 settlement verdicts/ATP, the AIE
downstream numbers used by the checker, the SSD receipt tallies, the index-audit counts.

## D. Clean-environment reproduction

```sh
# 1. Evaluator, version-pinned (the compiled-instance and AIE numbers depend on it):
python3 -m venv .venv
.venv/bin/pip install "sigma-glyph==0.6.7"
# 2. Recount the countable figures:
.venv/bin/python papers/every-check-spawns-more/check_claims.py
#    expect: the demo-0.1/0.2, index-audit, pack, COMPILE-0030 and μ-literal checks all PASS.
# 3. Compiled instance, live:
.venv/bin/python tools/conf_mono_settle.py            # PASS/VIOLATION/PASS at 4,151,277 / 554,678 / 25 ATP
# 4. (requested) scheduler counterexample + closed claim-ID list — see §A once added.
```

Record: the exact repository revision archived by the deposit; the sigma-glyph release used
(`0.6.7`) and the interpreter version. **Byte reproducibility is claimed only for the evaluator
replay and the receipt tallies, never for the LLM offspring counts.**

## E. Deposit manifest proposal (not a deposit)

```yaml
paper: every-check-spawns-more/paper-v0.2-draft.md   # promote to paper.md only on operator decision
revision: <GIT_REVISION_PLACEHOLDER>                  # filled at deposit time
evaluator: sigma-glyph==0.6.7
included:
  - LICENSE                                             # path-scoped license authority
  - LICENSES/AGPL-3.0-only.txt                          # executable deposit material
  - LICENSES/CC-BY-SA-4.0.txt                           # paper and documentary artifacts
  - papers/every-check-spawns-more/paper-v0.2-draft.md
  - papers/every-check-spawns-more/CLAIM-LEDGER.md
  - papers/every-check-spawns-more/check_claims.py     # after §A additions
  - drafts/EXP-RVB-1-RESULTS.md                         # raw measurement records
  - drafts/RVB-0.1-REFLEXIVE-VERIFICATION-BOUND.md      # demoted model + falsifiers
  - tools/conf_mono_settle.py                           # compiled instance
  - drafts/SSD-DEMO-0.1.md, drafts/SSD-DEMO-0.2.md, drafts/SSD-INDEX-AUDIT.md  # legacy episode
  - drafts/ssd-pack/                                    # Warrant pack (conformance only)
expected_checks:
  - check_claims.py exits 0 on a clean sigma-glyph==0.6.7 install
  - conf_mono_settle.py reproduces the three settlement verdicts and ATP spends
excluded:
  - any DOI reservation, release, tag, or claim of peer review / adoption
  - the offspring counts as byte-reproducible artifacts (they are transcript evidence)
status_note: >
  Publication is a dated trajectory marker, not adoption, peer review, scientific validation,
  or protocol release. This paper is its own version series, not a version of any other paper.
```

## G. Build surface & metadata (Codex S4 — currently wrong)

- `build.sh` builds `paper.md`, **not** `paper-v0.2-draft.md`. The candidate build must take the exact
  reviewed draft (or the draft must be promoted first); the deposit manifest must hash the *generated*
  paper and every included artifact.
- The abstract is now **front-loaded** in the v0.2 draft ("written last" is authoring order, not
  publication location).
- The v0.2 body contains **no Pandoc/BibTeX citation keys**, so `--citeproc` resolves nothing while the
  bibliography audit marks references "in-text: yes". Real `[@key]` citations must be added before the
  audit's "in-text" column is true.
- Author, exact date, keywords, artifact revision, and evaluator/interpreter identifiers are
  placeholders and must be filled at deposit.

## F. Acceptance-gate self-check (brief §8)

- every abstract claim is a ledger row — **yes** (`CLAIM-LEDGER.md` C1–C9);
- no historical false claim survives outside history/counterexample — **theorem/bound/phase-transition
  removed** (§A of MIGRATION-NOTES);
- model assumptions adjacent to the statement — **yes** (§5 policies-first);
- every number re-derived / replayed / classified — **yes** (§C split);
- positive and negative fixtures exercised — **yes** (controls + counterexamples + gate boundary);
- current and legacy pipelines not conflated — **yes** (§7 labels the legacy inline gate);
- CI / replay / review / publication / adoption kept distinct — **yes** (§0 status vocabulary);
- one-paragraph "what would weaken the central claim" — **yes** (§8 falsifiers F1–F6);
- license scope and missing external validation visible — **yes** (§9, §E);
- no document-level green inferred from local green — **N/A to this paper; asserted for the pipeline it cites**.

## H. Zenodo mechanics (cross-paper; from Fable review 2026-09-01 §3) — operator decisions, not executed here

These correct a wrong implicit assumption in §E: **Zenodo binds one `license` field per record; it
has no path-scoped dual license.** The GitHub integration archives the whole repo under a single
field. Therefore, at deposit (operator's call — nothing here reserves a DOI or creates a record):

1. **Two linked records, not one.** A *publication* record under CC BY-SA 4.0 (paper PDF + md +
   ledger + documentary evidence) and a *software* record under AGPL-3.0-only (tools, checkers),
   linked by `isSupplementedBy` / `isSupplementTo` — or a single manual curated upload of the §E
   manifest. Option one matches the repository's own path-scoped `LICENSE`.
2. **Versions.** Deposit **v0.2 as the first version** of the record (concept DOI + version DOI). Do
   **not** deposit v0.1 — it lives in git history; the record links the commit. Promotion order:
   `paper-v0.2-draft.md → paper.md`, and `paper.md → paper-v0.1-superseded.md`.
3. **Author = the accountable human.** Serhii Glova is the sole author (add ORCID
   `0009-0001-8010-420X`). The AI-provenance paragraph stays in the text and is mirrored in the
   record `description`. **Do not** add a model as a contributor — there is no accountability behind
   it, and the field would fake one.
4. **`CITATION.cff`.** Keep `type: software` for the repo; add a `preferred-citation` block
   (`type: article`/`report`) carrying the DOI once minted.
5. **Ship `reviews/` in the record.** Codex, Qwen, and this Fable review, plus responses. This is
   what makes "not peer-reviewed" both honest and informative, and is the record's real distinction
   from an ordinary preprint.
6. **Stale build artifacts.** The `.html` in the paper dirs is built from v0.1 and must be removed or
   regenerated from the promoted draft before deposit; `build.sh` must target the v0.2 surface.

**Review-provenance caveat.** The Fable 2026-09-01 review is **same-lineage** with the drafts (both
Claude-family), so by the papers' own §3.5 logic it is within-lineage replication, **not** the
out-of-lineage adversarial pass. Codex remains the only out-of-lineage review; the planned Kimi/Qwen
pass is still owed before "externally reviewed" may be claimed.
