#!/usr/bin/env python3
"""
epistemic_debt.py — aggregate verification-debt report over every settlement
receipt in the repository.

Origin: proposed by Qwen review (reviews/2026-08-qwen-early-stage-critique.md),
re-thought to match this repository's own measured semantics before adoption:

- REPORTS, does not moralize. Qwen's thresholds ("stop generating above 30%
  unsettled") contradict Thesis 7 (speculation is legal while typed) and RVB
  (what matters is the RATE condition λ_G < (1-μ)λ_V and whether debt wears
  its type, not the stock of ◇). So this tool shows the stock honestly and
  reminds about the rate, and leaves the decision to the operator.
- ◇ unsettled here means "no supported claim class / malformed", i.e. typed
  speculation or tooling gap — legal debt. The red-flag class is REFUTED
  claims still standing in a document's LATEST settlement (experiment
  artifacts keep theirs on purpose; the per-path table makes that visible
  instead of averaging it away).

Deterministic; no thresholds baked in; exit code 0 always (a report, not a gate).
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load(path):
    txt = path.read_text(encoding="utf-8")
    cut = txt.rfind("RECEIPT_SHA256")
    return json.loads(txt[:cut].strip() if cut != -1 else txt)


def main():
    rows, tot = [], {"claims": 0, "settled_true": 0, "refuted": 0,
                     "unsettled": 0, "atp_total": 0}
    for p in sorted(REPO.rglob("*.receipt.json")):
        if ".git" in p.parts:
            continue
        t = load(p)["tally"]
        rows.append((p.relative_to(REPO), t))
        for k in tot:
            tot[k] += t[k]

    if not tot["claims"]:
        print("no receipts found")
        return 0

    w = max(len(str(r[0])) for r in rows)
    print("Epistemic Debt Report (stock, per RVB semantics: the rate is what")
    print("matters; the stock below just has to wear its type honestly)")
    print("=" * (w + 34))
    print(f"{'receipt':<{w}}  claims  ⚓   ✗   ◇   ATP")
    for path, t in rows:
        print(f"{str(path):<{w}}  {t['claims']:>6}  {t['settled_true']:>2}  "
              f"{t['refuted']:>2}  {t['unsettled']:>2}  {t['atp_total']}")
    print("-" * (w + 34))
    print(f"{'TOTAL':<{w}}  {tot['claims']:>6}  {tot['settled_true']:>2}  "
          f"{tot['refuted']:>2}  {tot['unsettled']:>2}  {tot['atp_total']}")
    n = tot["claims"]
    print(f"\nsettled {tot['settled_true']}/{n} ({tot['settled_true']/n:.0%}); "
          f"refuted standing {tot['refuted']}/{n} ({tot['refuted']/n:.0%}); "
          f"unsettled {tot['unsettled']}/{n} ({tot['unsettled']/n:.0%})")
    print("\nNOTES: refuted counts include experiment artifacts preserved on")
    print("purpose (drafts/ssd-stream, SSD-DEMO-0.1, SSD-INDEX-AUDIT) — the")
    print("per-path table exists so nobody averages that away. The larger debt")
    print("ledger (conceptual, not claim-level) lives in FLOW-GLOSSARY §5 and")
    print("FLOW.md §36.1; this tool does not see it and says so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
