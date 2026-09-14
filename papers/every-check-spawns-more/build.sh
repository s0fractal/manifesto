#!/bin/sh
# Build the paper HTML (requires pandoc; add --pdf-engine for PDF; the paper is readable as markdown
# without it). Run check_claims.py FIRST — red means the text drifted from
# the repository and must not be built.
set -e
cd "$(dirname "$0")"
# Controlled-forgetting guard (Codex closure P0-3): refuse to build a SUPERSEDED source.
# paper.md is a retired v0.1 comparator carrying a tombstone; the live surface is
# paper-v0.2-draft.md. Promotion (rename v0.2-draft -> paper.md) removes the `status: SUPERSEDED`
# front-matter and lifts this guard. See DEPOSIT-AND-AUDIT.md §I.
# The deposit build reads paper-v0.2-draft.md; the guard applies to that exact source, so the
# retired v0.1 body (paper.md, still tombstoned) can never be the built artifact.
SOURCE=paper-v0.2-draft.md
if grep -qiE '^status:[[:space:]]*SUPERSEDED' "$SOURCE"; then
  echo "REFUSED: $SOURCE is SUPERSEDED. Do not build a retired body." >&2
  exit 2
fi
# Render gate: the closed-manifest checker mechanism must be sound and both
# claim-manifests must bind their drafts. Deposit-clean is a SEPARATE gate, run at
# deposit time: `python3 ../deposit_check.py claim-manifest.json` (exit 0 only when
# no claim is REFUSED). A draft may legitimately render while its deposit is BLOCKED.
python3 ../test_deposit_check.py
# Deposit build (operator decision 2026-09-14, DEPOSIT-AND-AUDIT.md §J): the PDF is built from the
# exact gate-bound candidate, not from the tombstoned v0.1 paper.md. The gate report is printed and
# may be BLOCKED; that per-claim vector is shipped with the deposit, never hidden.
# Toolchain versions are enforced: a PDF from other versions is a different artifact.
pandoc --version | head -1 | grep -qx "pandoc 3.11" \
  || { echo "build.sh: need pandoc 3.11, have: $(pandoc --version | head -1)" >&2; exit 1; }
tectonic --version | grep -qx "Tectonic 0.17.0" \
  || { echo "build.sh: need Tectonic 0.17.0, have: $(tectonic --version)" >&2; exit 1; }
python3 ../deposit_check.py claim-manifest.json || true
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1789344000}"   # 2026-09-14T00:00:00Z, the paper date
pandoc "$SOURCE" -o paper.pdf \
  --citeproc --bibliography=references.bib --pdf-engine=tectonic \
  -V geometry:margin=1in -V fontsize=11pt -V colorlinks=true -V linkcolor=blue -V urlcolor=blue \
  -V mainfont=DejaVuSerif.ttf -V monofont=DejaVuSansMono.ttf \
  -M reference-section-title=References
echo "built: paper.pdf (from paper-v0.2-draft.md)"
