# Paper Disposition Report 0.1

This is a metadata-only disposition report for Paper A (`every-check-spawns-more`) and Paper B (`addressing-is-equality`) against the repository's closed deposit gate.

## 1. Checker and Environmen

- **Git Revision:** `3a32394e4cb059a1bff63019916d18f66b94f5d8` (branch `sprint/01-manifesto-paper-disposition`)
- **Environment:** `python 3.12` / `sigma-glyph==0.6.7`
- **Checker Engine:** `papers/deposit_check.py`
- **Paper A Manifest:** `papers/every-check-spawns-more/claim-manifest.json`
- **Paper B Manifest:** `papers/addressing-is-equality/claim-manifest.json`

## 2. Execution and Vectors

### Paper A: every-check-spawns-more
**Command:** `.venv/bin/python papers/deposit_check.py papers/every-check-spawns-more/claim-manifest.json`
**Exit Code:** 1 (BLOCKED)
**Candidate Digest:** `9e64513b807db16f2c070c79ab4e1d51c360824b22c6fbdb4fb2b1bb8d96b991`

**Vector (1 CHECKED / 0 EXCLUDED / 9 REFUSED):**
- C5: CHECKED
- C1: missing/unadmitted evidence `[FROZEN_CORPUS_NOT_DEPOSITED]`
- C2: missing/unadmitted evidence `[FROZEN_CORPUS_NOT_DEPOSITED]`
- C3: missing/unadmitted evidence `[FROZEN_CORPUS_NOT_DEPOSITED]`
- C4: missing/unadmitted evidence `[FROZEN_CORPUS_NOT_DEPOSITED]`
- C6: missing/unadmitted evidence `[SIMULATION_NOT_DEPOSITED]`
- C7: missing/unadmitted evidence `[FROZEN_CORPUS_NOT_DEPOSITED]`
- C8: substantive refusal `[SOURCE_MISMATCH]`
- C2-MAP: missing/unadmitted evidence `[OPERATOR_COMMIT_PROVENANCE_UNAVAILABLE]`
- C2-MEAS: missing/unadmitted evidence `[MEASUREMENT_NOT_REPLAYED]`

### Paper B: addressing-is-equality
**Command:** `.venv/bin/python papers/deposit_check.py papers/addressing-is-equality/claim-manifest.json`
**Exit Code:** 1 (BLOCKED)
**Candidate Digest:** `8cc37f16ef84b067a688b14e91244ab9dc58e0a293c04d0efccb5c46e09edc6d`

**Vector (3 CHECKED / 3 EXCLUDED / 2 REFUSED):**
- B1: CHECKED
- B3: CHECKED
- B6: CHECKED
- B2: substantive refusal `[DERIVED_FROM_B1]`
- B5: substantive refusal `[ARGUED_OBLIGATION]`
- B8: substantive refusal `[DEFINITIONAL]`
- B4: missing/unadmitted evidence `[PROFILE_NOT_VENDORED]`
- B7: environment failure `[COMMAND_UNAVAILABLE]`

## 3. Negative Controls and Tests

- **Determinism:** Executing the engine twice yields identical, deterministic vectors.
- **Negative Control:**
  - **Command:** Mutated Paper B manifest digest in `.tmp_control/claim-manifest.json` and ran engine.
  - **Result:** `ENGINE: FAIL_CLOSED (report untrustworthy) — CANDIDATE_MISSING`. Exit code 3.
- **Suite Tests:** `.venv/bin/python papers/test_deposit_check.py` exited 0 (22 tests passed). `.venv/bin/python tools/aie_errata_check.py` exited 0 (11/11 checks passed).
- **Reproducibility Limitations:** Non-reproducibility issues on Paper A's per-act tables and Paper B's Warrant pack persist and are correctly typed as `NOT_DEPOSITED` or omitted from reproducible CI assertions rather than bypassed.

## 4. Selection and Decision

**Comparison:** Paper B has 2 blockers (REFUSED). Paper A has 9 blockers (REFUSED).
**Selection:** Candidate selected is **Paper B**, as its vector is objectively closer to zero blockers.

**Stopping Decision:** Stop. The repository's checker successfully measured both candidates and failed closed on missing prerequisites.
**Bounded Next Action:** Vendor the DRAFT profile at commit `196c45a2` and supply the `warrant` command to clear Paper B's remaining two blockers. Do not narrow or repair claims in this item.
