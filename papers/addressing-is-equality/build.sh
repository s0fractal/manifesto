#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 check_claims.py
pandoc paper.md --citeproc --bibliography=references.bib \
  -o addressing-is-equality.html --standalone
echo "built: addressing-is-equality.html"
