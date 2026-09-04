# Paper Disposition Report 0.1

Metadata-only measurement of Paper A (`every-check-spawns-more`) and Paper B
(`addressing-is-equality`) against the repository's closed deposit gate. It is
not a paper verdict, claim repair, promotion, or deposit act.

## 1. Operands and environment

- Git revision: `976fb2cad6487353f7f9f52ff7c2348c29da3d61`, whose parent is the
  Sprint base `3a32394e4cb059a1bff63019916d18f66b94f5d8`.
- Workflow-declared environment: Python 3.12 and `sigma-glyph==0.6.7`.
- Measured clean environment: Python `3.12.13` from `mise`, fresh temporary
  venv, released `sigma-glyph==0.6.7`, and the real repository Git object
  database plus `refs/remotes/origin/main` available to the checker.
- Checker: `papers/deposit_check.py`, SHA-256
  `855b2c043ba998decc19a1635ec1baf03430509181a7b77bfa45e4f0947f1250`.
- Paper A manifest: `papers/every-check-spawns-more/claim-manifest.json`,
  SHA-256 `695fe88887eddc01f2e30765b6b920ee16dc7ae9d5e24bb820fdb0f9c97a9d0d`.
- Paper B manifest: `papers/addressing-is-equality/claim-manifest.json`,
  SHA-256 `71dc79211b35910b11349540ff584d53cc4ebef006b3c819c4be9f1a5c0e17ea`.

The environment was built and both manifests were executed with:

```sh
ENV_DIR=$(mktemp -d /tmp/triad-paper-py312.XXXXXX)
mise exec python@3.12.13 -- python -m venv "$ENV_DIR/venv"
"$ENV_DIR/venv/bin/pip" install 'sigma-glyph==0.6.7'
"$ENV_DIR/venv/bin/python" papers/deposit_check.py papers/every-check-spawns-more/claim-manifest.json
"$ENV_DIR/venv/bin/python" papers/deposit_check.py papers/addressing-is-equality/claim-manifest.json
```

Both deposit commands exited `1` (`BLOCKED`). Repeating them produced
byte-identical summaries: A output SHA-256 `4c5f3ef4c627d422412e77d5b81816617d51e03876aa86c368ea514d3aa5829b`;
B output SHA-256 `f83331de3ed278f56ab4a6268a16339900504c2452bccaa6338b7fca99205a81`.

## 2. Per-claim vectors

### Paper A — 2 CHECKED / 0 EXCLUDED / 8 REFUSED

- `C5`, `C2-MAP`: `CHECKED`.
- `C1`, `C2`, `C3`, `C4`, `C7`: missing/unadmitted evidence
  (`FROZEN_CORPUS_NOT_DEPOSITED`).
- `C6`: missing/unadmitted evidence (`SIMULATION_NOT_DEPOSITED`).
- `C8`: substantive refusal (`SOURCE_MISMATCH`).
- `C2-MEAS`: missing/unadmitted evidence (`MEASUREMENT_NOT_REPLAYED`).

Candidate `papers/every-check-spawns-more/paper-v0.2-draft.md` is bound at
SHA-256 `9e64513b807dc726c93c1626e0e1367502aaacca5c8db5849ead6604287e9232`.
`C2-MAP` is checked only because this run can verify its already-governed Git
provenance. It conveys no credit to `C2-MEAS`.

### Paper B — 3 CHECKED / 3 EXCLUDED / 2 REFUSED

- `B1`, `B3`, `B6`: `CHECKED`.
- `B2`: `EXCLUDED` (`DERIVED_FROM_B1`), non-blocking.
- `B5`: `EXCLUDED` (`ARGUED_OBLIGATION`), non-blocking.
- `B8`: `EXCLUDED` (`DEFINITIONAL`), non-blocking.
- `B4`: missing/unadmitted evidence (`PROFILE_NOT_VENDORED`).
- `B7`: environment failure (`COMMAND_UNAVAILABLE`).

Candidate `papers/addressing-is-equality/paper-v0.2-draft.md` is bound at
SHA-256 `8cc37f16ef84d54fb779b615e04818299cf95ca38687006e7a910b2ff1f683ae`.

## 3. Fail-closed control and suites

A fresh `git archive HEAD` was unpacked under `/tmp`; only one byte of the
copied Paper B candidate was changed (`Budgeted` to `Xudgeted`). The copied
manifest and checker were unchanged. The candidate digest changed from
`8cc37f16...` to `9b637717...`; the checker exited `3` with
`CANDIDATE_DIGEST_MISMATCH`, so the mutated report was untrustworthy rather
than merely blocked.

In the same Python 3.12 environment:

- `papers/test_deposit_check.py`: mechanism suite green;
- `papers/corpus/test_corpus.py`: corpus mechanism and governance controls green;
- `tools/aie_errata_check.py`: `11/11` executable checks green.

## 4. Selection and stopping decision

Mechanical comparison uses blocking `REFUSED` count only: Paper B has `2`,
Paper A has `8`. Paper B is therefore the first candidate. This does not make
Paper B deposit-ready and does not compare novelty or scientific value.

Stop here. The next bounded work may vendor and validate the named DRAFT profile
for `B4`, and may provide the `warrant` executable so `B7` becomes replayable;
execution may still CHECK or REFUSE. No claim is narrowed by this measurement.
