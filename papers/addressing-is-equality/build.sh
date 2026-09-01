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
python3 check_claims.py
pandoc paper.md --citeproc --bibliography=references.bib \
  -o addressing-is-equality.html --standalone
echo "built: addressing-is-equality.html"
