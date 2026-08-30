#!/usr/bin/env python3
"""check_claims.py — re-run every benchmark figure paper.md asserts.
Red (exit 1) on drift; prints what it does NOT check."""
import json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))
import glyphlib as gl

failures = []
def check(name, got, expect):
    ok = got == expect
    print(f"{'ok  ' if ok else 'FAIL'} {name}: expected {expect!r}, got {got!r}")
    if not ok: failures.append(name)

nat = lambda a, op, b, c: gl.settle_nat_eq(
    gl.A(gl.PLUS if op == '+' else gl.MULT, gl.church(a), gl.church(b)), gl.church(c))[:2]
check("idiom 7+5=12", nat(7,'+',5,12), ("PASS", 601))
check("idiom 20+20", nat(20,'+',20,40), ("PASS", 1997))
check("idiom 100+100", nat(100,'+',100,200), ("PASS", 9997))
check("idiom 200+200", nat(200,'+',200,400), ("PASS", 19997))
check("idiom 6*7", nat(6,'*',7,42), ("PASS", 2213))
check("idiom 20*20", nat(20,'*',20,400), ("PASS", 21453))

eqn = lambda a, b, atp: gl.settle_bool(
    gl.A(gl.EQN, gl.A(gl.PLUS, gl.church(a), gl.church(b)), gl.church(a+b)), atp=atp)[:2]
check("in-language 3+2", eqn(3,2,60_000_000), ("PASS", 260780))
check("in-language 5+5", eqn(5,5,60_000_000), ("PASS", 26212480))
v, s = eqn(7,5,60_000_000)
check("in-language 7+5 exhausts 50M", (v, s > 50_000_000), ("ATP_EXHAUSTED", True))

manifest = json.loads((REPO / "drafts/ssd-pack/manifest.json").read_text())
aie = manifest["ski_checks"][1]
check("warrant AIE check atp", aie["atp"], 2108)
check("warrant WPL check atp", manifest["ski_checks"][0]["atp"], 501)
adr = Path("/Users/s0fractal/Projects/sigma-glyph/proposals/ADR-011-eq-by-normal-form-address.md")
check("ADR-011 on file upstream", adr.is_file(), True)

print("\nNOT checked: `warrant check` re-execution (re-run it: cd drafts/ssd-pack &&")
print("warrant --store .warrants check " + aie["check"] + ");")
print("external citation details; upstream gate status of ADR-011 (F4).")
print()
if failures:
    print(f"RED: {failures}"); sys.exit(1)
print("GREEN: every benchmark figure re-executed and matched.")
