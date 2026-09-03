#!/usr/bin/env python3
"""active_surface.py — does surface/rows.json still hold?   python3 tools/active_surface.py

The rows ARE the surface. Four classes, one predicate each; anything else is refused.
  operational  `check` argv exits 0 now
  normative    `authority` file exists in this repo; `scope` and `revocation` nonempty
  intent       a `review_trigger` or an `expiry` not yet passed; no `check` field
  retired      `mode` from CONTROLLED-FORGETTING §2; `loss` nonempty; `successor` resolves or null
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = {"SUPERSEDED", "WITHDRAWN", "REFUTED", "ARCHIVED", "ABANDONED", "QUARANTINED", "REDACTED"}
FIELDS = {
    "operational": {"check", "falsifier"},
    "normative": {"authority", "scope", "revocation"},
    "intent": {"review_trigger", "expiry"},
    "retired": {"mode", "loss", "successor"},
}


def problems(rows, today):
    ids = {r.get("id") for r in rows}
    for r in rows:
        rid, cls = r.get("id"), r.get("class")
        if cls not in FIELDS or set(r) != {"id", "class", "statement"} | FIELDS[cls]:
            yield f"{rid}: fields do not match class {cls!r}"
            continue
        if cls == "operational":
            if subprocess.run(r["check"], cwd=ROOT, capture_output=True).returncode != 0:
                yield f"{rid}: check is RED ({' '.join(r['check'])})"
            if not r["falsifier"]:
                yield f"{rid}: no falsifier"
        elif cls == "normative":
            if not (ROOT / r["authority"]).is_file():
                yield f"{rid}: authority missing {r['authority']}"
            if not (r["scope"] and r["revocation"]):
                yield f"{rid}: scope or revocation empty"
        elif cls == "intent":
            if not r["review_trigger"] and not r["expiry"]:
                yield f"{rid}: intent unbounded (no trigger, no expiry)"
            if r["expiry"] and dt.date.fromisoformat(r["expiry"]) < today:
                yield f"{rid}: intent expired {r['expiry']} — re-triage"
        else:
            if r["mode"] not in MODES:
                yield f"{rid}: unknown retirement mode {r['mode']!r}"
            if not r["loss"]:
                yield f"{rid}: retired without a loss record"
            if r["successor"] is not None and r["successor"] not in ids:
                yield f"{rid}: successor {r['successor']!r} does not resolve"


def main(argv):
    today = dt.date.fromisoformat(argv[1]) if len(argv) > 1 else dt.date.today()
    rows = json.loads((ROOT / "surface" / "rows.json").read_text(encoding="utf-8"))
    if len({r.get("id") for r in rows}) != len(rows):
        print("REFUSED  duplicate id"); return 1
    found = list(problems(rows, today))
    for p in found:
        print(f"REFUSED  {p}")
    if found:
        return 1
    n = {c: sum(r["class"] == c for r in rows) for c in FIELDS}
    print(f"CHECKED  surface/rows.json holds  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
