# Deposit manifest — every-check-spawns-more v0.2.0

- Repository: https://github.com/s0fractal/manifesto
- Commit: `448d6de56a7737ecbbd00280caeed4a716867b77` (tag `paper-every-check-spawns-more-v0.2.0`)
- Paper source: `papers/every-check-spawns-more/paper-v0.2-draft.md`
- Build: `papers/every-check-spawns-more/build.sh` — pandoc 3.11, tectonic 0.17.0, DejaVu fonts,
  `SOURCE_DATE_EPOCH=1789344000`. Rebuilding from the source archive reproduced `paper.pdf` byte for byte.
- Evaluator for the gate: `sigma-glyph==0.6.7`.

## Gate vector at deposit (`deposit-report.json`)

engine `OK`, deposit `BLOCKED` — this version is deposited with its refusals as known loss
(owner decision 2026-09-14; `DEPOSIT-AND-AUDIT.md` §J). It is not deposit-clean.

- CHECKED: C5, C2-MAP
- REFUSED C1: `FROZEN_CORPUS_NOT_DEPOSITED`
- REFUSED C2: `FROZEN_CORPUS_NOT_DEPOSITED`
- REFUSED C3: `FROZEN_CORPUS_NOT_DEPOSITED`
- REFUSED C4: `FROZEN_CORPUS_NOT_DEPOSITED`
- REFUSED C6: `SIMULATION_NOT_DEPOSITED`
- REFUSED C7: `FROZEN_CORPUS_NOT_DEPOSITED`
- REFUSED C8: `SOURCE_MISMATCH`
- REFUSED C2-MEAS: `MEASUREMENT_NOT_REPLAYED`

## Files

| file | sha256 | license |
|---|---|---|
| `paper.pdf` | `fee800275c10f1ab079f5c85a4e737c5f19fa76831bbebbb6e10290e7ab9b351` | CC BY-SA 4.0 |
| `paper-v0.2-draft.md` | `40dd28d39364c7c9e36b349a8f3d114c192cd3121b87c521d938c81f04f76552` | CC BY-SA 4.0 |
| `CLAIM-LEDGER.md` | `dba3e72b87afed8bfd32533ac0e0d513168d79ae474ac30508ebda34260a33e3` | CC BY-SA 4.0 |
| `claim-manifest.json` | `1b21566cb2f9d170104ed0188845ce2ba6a7a8eb226d78d9436030376eecafa3` | CC BY-SA 4.0 |
| `deposit-report.json` | `737a1f569876563c8df2c5501d9ac65aa8d31725db42c907fab1e2cc0b4749ae` | CC BY-SA 4.0 |
| `manifesto-every-check-v0.2.0-source.tar.gz` | `4c664a56eb60aae013e11824740eff3809a17a89228db2c71f60c2a9ec406cd6` | mixed: see LICENSE in archive (docs CC BY-SA 4.0, software AGPL-3.0-only) |

Not peer-reviewed. A frozen artifact, not a venue, endorsement, adoption or protocol release.
