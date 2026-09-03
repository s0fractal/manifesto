#!/usr/bin/env python3
"""
receipt_freshness.py — is a settlement receipt still true of the current world?

Answers Codex findings F3/F4: a receipt that commits only to its source text
goes stale silently the moment any file it read changes, and a checker that
compares against a frozen tally stays green while a live re-run would be red.

A receipt written by settle_gate/0.3+deps or later records `deps`: {path: [sha256,...]}
— the digest of every file each claim actually read. This tool recomputes
those digests against the repository NOW and reports, per dependency, FRESH /
STALE / MISSING, plus which claims are affected — WITHOUT re-running the gate,
the machine, or any LLM. O(files read), no ATP.

usage: receipt_freshness.py <receipt.json> [<receipt.json> ...]
exit: 0 if every receipt is fresh; 1 if any is stale/missing/legacy.
"""
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    txt = open(path, encoding="utf-8").read()
    cut = txt.rfind("RECEIPT_SHA256")
    return json.loads(txt[:cut].strip() if cut != -1 else txt)


def current_digest(path):
    fp = os.path.realpath(os.path.join(REPO, path))
    repo_real = os.path.realpath(REPO)
    if fp != repo_real and not fp.startswith(repo_real + os.sep):
        return None  # escapes repo; treat as unresolvable
    if not os.path.isfile(fp):
        return None
    with open(fp, encoding="utf-8", errors="replace") as f:
        return hashlib.sha256(f.read().encode("utf-8", "replace")).hexdigest()


def check(receipt_path):
    rec = load(receipt_path)
    deps = rec.get("deps")
    if deps is None:
        print(f"LEGACY  {receipt_path}: no deps recorded (pre-0.3 receipt) — "
              f"freshness cannot be established; re-settle to bind dependencies")
        return "legacy"
    if not deps:
        print(f"FRESH   {receipt_path}: no file dependencies (self-contained)")
        return "fresh"
    stale = []
    for path, settled_digests in deps.items():
        now = current_digest(path)
        if now is None:
            stale.append((path, "MISSING/UNRESOLVABLE"))
        elif now not in settled_digests:
            stale.append((path, f"CHANGED (settled {settled_digests[0][:12]}, "
                                f"now {now[:12]})"))
    if not stale:
        print(f"FRESH   {receipt_path}: all {len(deps)} dependencies unchanged")
        return "fresh"
    print(f"STALE   {receipt_path}: {len(stale)} of {len(deps)} dependencies moved")
    for path, why in stale:
        affected = [c.get("payload", "?") for c in rec.get("claims", [])
                    if c.get("dep", {}).get("path") == path]
        print(f"        - {path}: {why}")
        for a in affected:
            print(f"            affected claim: {a}")
    return "stale"


def main(paths):
    if not paths:
        print("usage: receipt_freshness.py <receipt.json> ...", file=sys.stderr)
        return 2
    verdicts = [check(p) for p in paths]
    fresh = sum(v == "fresh" for v in verdicts)
    print(f"\n{fresh}/{len(verdicts)} receipts fresh; "
          f"{sum(v=='stale' for v in verdicts)} stale, "
          f"{sum(v=='legacy' for v in verdicts)} legacy")
    return 0 if all(v == "fresh" for v in verdicts) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
