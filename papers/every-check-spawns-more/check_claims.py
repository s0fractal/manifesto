#!/usr/bin/env python3
"""
check_claims.py — recount the countable numbers paper.md asserts, from the
repository artifacts themselves. Red (exit 1) on any drift. Prints the claim
classes it does NOT check rather than implying full coverage.

Discipline copied from warrant/papers and sigma-glyph/papers.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
failures = []


def check(name, got, expect):
    ok = got == expect
    print(f"{'ok  ' if ok else 'FAIL'} {name}: expected {expect!r}, recounted {got!r}")
    if not ok:
        failures.append(name)


def receipt(path):
    txt = (REPO / path).read_text()
    return json.loads(txt[:txt.rfind("RECEIPT_SHA256")].strip())


# --- §5.2 live episode: SSD-DEMO receipts -----------------------------------
r1 = receipt("drafts/SSD-DEMO-0.1.receipt.json")
check("demo-0.1 claims", r1["tally"]["claims"], 11)
check("demo-0.1 settled", r1["tally"]["settled_true"], 7)
check("demo-0.1 refuted", r1["tally"]["refuted"], 4)
check("demo-0.1 atp", r1["tally"]["atp_total"], 5638)
refuted_counts = sorted(int(re.search(r"= (\d+)", c["detail"]).group(1))
                        for c in r1["claims"]
                        if c["verdict"] == "REFUTED" and c["class"] == "count")
check("demo-0.1 refuted are all count-claims",
      sum(c["verdict"] == "REFUTED" for c in r1["claims"]),
      sum(c["verdict"] == "REFUTED" and c["class"] == "count" for c in r1["claims"]))
check("demo-0.1 actual counts", refuted_counts, [7, 12, 12, 67])

r2 = receipt("drafts/SSD-DEMO-0.2.receipt.json")
check("demo-0.2 clean pass", (r2["tally"]["refuted"], r2["tally"]["settled_true"]), (0, 11))
check("loop total atp", r1["tally"]["atp_total"] + r2["tally"]["atp_total"], 11276)

# --- §5.2 index audit -------------------------------------------------------
ra = receipt("drafts/SSD-INDEX-AUDIT.receipt.json")
cites = [c for c in ra["claims"] if c["class"] == "cite"]
check("index-audit cite predictions", len(cites), 30)
check("index-audit refuted total", ra["tally"]["refuted"], 28)
absent = case_only = 0
for c in cites:
    if c["verdict"] != "REFUTED":
        continue
    m = re.match(r'^"(.+)"\s+in\s+(\S+)$', c["payload"], re.S)
    content = (REPO / m[2]).read_text(encoding="utf-8", errors="replace")
    if m[1].lower() in content.lower():
        case_only += 1
    else:
        absent += 1
check("index-audit case-only", case_only, 10)
check("index-audit absent", absent, 18)

# --- §5.3 evidence pack -----------------------------------------------------
manifest = json.loads((REPO / "drafts/ssd-pack/manifest.json").read_text())
check("pack records", len(manifest["records"]), 4)
check("pack wpl-check atp", manifest["ski_checks"][0]["atp"], 501)
check("pack aie-check atp", manifest["ski_checks"][1]["atp"], 2108)

# --- §4 compiled claim (COMPILE-0030): re-run the settlement live -----------
out = subprocess.run([sys.executable, str(REPO / "tools/conf_mono_settle.py")],
                     capture_output=True, text=True, check=True).stdout
body = json.loads(out[:out.rfind("RECEIPT_SHA256")].strip())
tr = body["traces"]
check("0030 clean PASS atp", tr["clean_summarization"]["machine_layer"]["atp_spent"], 4151277)
check("0030 laundering atp", tr["confidence_laundering"]["machine_layer"]["atp_spent"], 554678)
check("0030 evidence atp", tr["licensed_by_evidence"]["machine_layer"]["atp_spent"], 25)
check("0030 verdicts",
      [tr[k]["machine_layer"]["verdict"] for k in sorted(tr)],
      ["PASS", "VIOLATION", "PASS"])

# --- §6 AIE benchmark: re-run the two costs the abstract leans on -----------
sys.path.insert(0, str(REPO / "tools"))
import glyphlib as gl  # noqa: E402
v, s, _ = gl.settle_nat_eq(gl.A(gl.PLUS, gl.church(7), gl.church(5)), gl.church(12))
check("AIE 7+5 idiom", (v, s), ("PASS", 601))
v, s, _ = gl.settle_nat_eq(gl.A(gl.PLUS, gl.church(200), gl.church(200)), gl.church(400))
check("AIE 200+200 idiom", (v, s), ("PASS", 19997))
v, s, _ = gl.settle_bool(gl.A(gl.EQN, gl.A(gl.PLUS, gl.church(3), gl.church(2)),
                              gl.church(5)), atp=60_000_000)
check("Church EQN 3+2 atp", (v, s), ("PASS", 260780))

# --- §3 measured-μ tables: recounted from the frozen experiment notes -------
exp = (REPO / "drafts/EXP-RVB-1-RESULTS.md").read_text()
for label, val in [("μ_0 round1", "5.42"), ("μ_1 round1", "3.38"),
                   ("μ_2 round1", "2.50"), ("round2 μ_0", "3.50"),
                   ("round2 μ_1", "2.75"), ("round2 μ_3", "2.13"),
                   ("round2 μ_4", "2.25")]:
    check(f"EXP notes contain {label}", val in exp, True)
check("EXP notes: control ratio", "0.14" in exp, True)

print()
print("NOT checked here (listed, not covered): the per-act offspring counts of")
print("§3 (recorded in drafts/EXP-RVB-1-RESULTS.md from subagent transcripts;")
print("re-runnable in kind, not byte-reproducible); external citation")
print("bibliographic details; the warrant CLI verification results (re-run them:")
print("cd drafts/ssd-pack && warrant --store .warrants verify --settlement")
print("--trust-config trust.json).")
print()
if failures:
    print(f"RED: {len(failures)} drift(s): {failures}")
    sys.exit(1)
print("GREEN: every recounted figure matches paper.md.")
