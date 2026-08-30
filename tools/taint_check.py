#!/usr/bin/env python3
"""
taint_check.py — post-hoc detection of inherited falsehood across an ordered
sequence of settle_gate receipts (SSD streaming experiment, EXP-SSD-STREAM).

A later claim is TAINTED if any numeric operand in its payload equals a value
CLAIMED by an earlier REFUTED claim (the laundering pattern: internally valid
arithmetic built on refuted inputs, which the per-claim gate verdict cannot
see). Deterministic; prints tainted claims and a tally.

usage: taint_check.py receipt1.json receipt2.json [receipt3.json ...]
"""
import json
import re
import sys


def load(path):
    txt = open(path, encoding="utf-8").read()
    cut = txt.rfind("RECEIPT_SHA256")
    return json.loads(txt[:cut].strip() if cut != -1 else txt)


def claimed_value(c):
    """The value a refuted claim ASSERTED (the poison source)."""
    if c["class"] == "count":
        m = re.search(r"=\s*(\d+)\s*$", c["payload"])
        return int(m[1]) if m else None
    return None


def operands(c):
    if c["class"] in ("arith", "cmp"):
        return [int(x) for x in re.findall(r"-?\d+", c["payload"])]
    return []


def main(paths):
    poison, tainted, total_later = set(), [], 0
    for i, path in enumerate(paths):
        rec = load(path)
        for c in rec["claims"]:
            if i > 0:
                ops = operands(c)
                if ops:
                    total_later += 1
                    hit = sorted(set(ops) & poison)
                    derived = c["class"] == "arith" and c["verdict"] == "PASS"
                    if hit:
                        tainted.append((path, c["payload"], hit))
                        # a PASS arith built on poison mints new poison
                        if derived:
                            poison.add(operands(c)[-1])
            if c["verdict"] == "REFUTED":
                v = claimed_value(c)
                if v is not None:
                    poison.add(v)
    for path, payload, hit in tainted:
        print(f"TAINTED  {payload!r}  (poisoned operands {hit})  [{path.split('/')[-1]}]")
    print(f"\ntainted {len(tainted)} of {total_later} downstream numeric claims; "
          f"poison set {sorted(poison)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
