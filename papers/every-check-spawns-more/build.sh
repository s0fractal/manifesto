#!/bin/sh
# Build the paper HTML (requires pandoc; add --pdf-engine for PDF; the paper is readable as markdown
# without it). Run check_claims.py FIRST — red means the text drifted from
# the repository and must not be built.
set -e
cd "$(dirname "$0")"
python3 check_claims.py
pandoc paper.md --citeproc --bibliography=references.bib \
  -V geometry:margin=1in -V fontsize=11pt \
  -o every-check-spawns-more.html --standalone
echo "built: every-check-spawns-more.html"
