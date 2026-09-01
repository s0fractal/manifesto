#!/usr/bin/env python3
"""DEPRECATED — replaced by the closed-manifest deposit gate (Codex closure P0-4).

This file used to recount literals by string-presence and was **stale-green**: it
stayed green even with the candidate draft deleted, and it combined a stale receipt
with a drifted source without noticing. It no longer decides anything itself.

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
