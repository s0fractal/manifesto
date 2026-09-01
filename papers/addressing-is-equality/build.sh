#!/bin/sh
set -e
cd "$(dirname "$0")"
# Controlled-forgetting guard (Codex closure P0-3): refuse to build a SUPERSEDED source.
# paper.md is a retired v0.1 comparator carrying a tombstone; the live surface is
# paper-v0.2-draft.md. Promotion (rename v0.2-draft -> paper.md) removes the `status: SUPERSEDED`
# front-matter and lifts this guard. See DEPOSIT-AND-AUDIT.md §H.
if grep -qiE '^status:[[:space:]]*SUPERSEDED' paper.md; then
  echo "REFUSED: paper.md is SUPERSEDED (retired v0.1). Do not build the retired body." >&2
  echo "  live surface: paper-v0.2-draft.md — promote it to paper.md to lift this guard." >&2
  exit 2
fi
# Render gate: the closed-manifest checker mechanism must be sound and both
# claim-manifests must bind their drafts. Deposit-clean is a SEPARATE gate, run at
# deposit time: `python3 ../deposit_check.py claim-manifest.json` (exit 0 only when
# no claim is REFUSED). A draft may legitimately render while its deposit is BLOCKED.
python3 ../test_deposit_check.py
pandoc paper.md --citeproc --bibliography=references.bib \
  -o addressing-is-equality.html --standalone
echo "built: addressing-is-equality.html"
