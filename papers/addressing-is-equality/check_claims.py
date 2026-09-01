#!/usr/bin/env python3
"""DEPRECATED — replaced by the closed-manifest deposit gate (Codex closure P0-4).

This file used to re-run benchmark figures and read `manifest.json` for the Warrant
ATP values (it did not execute the checks) and depended on an absolute author-machine
path for the ADR-011 file — a **stale-green** deposit signal. It no longer decides
anything itself.

Running it now invokes the real gate — `deposit_check.py` on this paper's
`claim-manifest.json` — and exits with the gate's code (0 deposit-clean, 1 BLOCKED,
3 engine fail-closed). The gate emits a per-claim CHECKED/EXCLUDED/REFUSED vector,
never an aggregate 'paper MATCH'.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from deposit_check import evaluate, human_summary, exit_code  # noqa: E402

report = evaluate(HERE / "claim-manifest.json")
print(human_summary(report))
sys.exit(exit_code(report))
