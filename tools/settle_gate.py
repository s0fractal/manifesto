#!/usr/bin/env python3
"""
settle_gate.py — Speculative Semantic Decoder, Phase 1 gate (SSD-PLAN.md).

Reads a markdown file containing inline claims in ⟦class: payload⟧ markup,
settles each claim deterministically, and writes:
  <input>.settled.md   — the text with claims replaced by badged verdicts
  <input>.receipt.json — machine-readable settlement report (+ RECEIPT_SHA256)

Claim classes (v0.1):
  ⟦arith: A op B = C⟧    op ∈ {+, *, -}; small values settle on the real
                          Σ-GLYPH machine (Church encoding, ATP-priced,
                          content-addressed verdict), large fall back to the
                          deterministic integer layer (layer recorded).
  ⟦cmp: A ⋈ B⟧           ⋈ ∈ {<, <=, =, >=, >}; same two layers.
  ⟦count: /re/ in path = N⟧  regex match count over a repo file (integer layer).
  ⟦sha256: path = hexprefix⟧ content-identity claim, prefix >= 12 hex chars.

Badges: ⚓ settled-true, ✗ REFUTED (caught before publication), ◇ unsettled
(unsupported class / malformed / budget) — stays typed speculation.

Deterministic: same input bytes + same repo state -> same output bytes.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glyphlib as gl  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIM = re.compile(r"⟦([a-z0-9_]+):\s*([^⟧]+)⟧")

ARITH = re.compile(r"^(-?\d+)\s*([+*-])\s*(-?\d+)\s*=\s*(-?\d+)$")
CMP = re.compile(r"^(-?\d+)\s*(<=|>=|<|>|=)\s*(-?\d+)$")
COUNT = re.compile(r"^/(.+)/\s+in\s+(\S+)\s*=\s*(\d+)$")
SHA = re.compile(r"^(\S+)\s*=\s*([0-9a-f]{12,64})$")

MACHINE_MAX = 400   # arith via hash-equality of normal forms: linear cost
CMP_MAX = 12        # cmp needs Church SUB/LEQ: expensive, small values only


def _machine_arith(a, op, b, c):
    if min(a, b, c) < 0 or max(a, b, c) > MACHINE_MAX:
        return None
    if op == "+":
        lhs = gl.A(gl.PLUS, gl.church(a), gl.church(b))
    elif op == "*":
        lhs = gl.A(gl.MULT, gl.church(a), gl.church(b))
    else:  # '-' : settle a-b=c as a = b+c to avoid truncated SUB semantics
        return _machine_arith(b, "+", c, a)
    return gl.settle_nat_eq(lhs, gl.church(c))


def _machine_cmp(a, rel, b):
    if min(a, b) < 0 or max(a, b) > CMP_MAX:
        return None
    if rel == "=":
        return gl.settle_nat_eq(gl.church(a), gl.church(b))
    m, n = gl.church(a), gl.church(b)
    expr = {"<=": gl.A(gl.LEQ, m, n),
            ">=": gl.A(gl.LEQ, n, m),
            "=": gl.A(gl.EQN, m, n),
            "<": gl.A(gl.AND, gl.A(gl.LEQ, m, n), gl.A(gl.NOT, gl.A(gl.EQN, m, n))),
            ">": gl.A(gl.AND, gl.A(gl.LEQ, n, m), gl.A(gl.NOT, gl.A(gl.EQN, m, n)))}[rel]
    return gl.settle_bool(expr)


def settle(cls, payload):
    """Returns dict: verdict PASS|REFUTED|UNSETTLED, layer, detail, atp."""
    payload = payload.strip()
    if cls == "arith":
        m = ARITH.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed arith"}
        a, op, b, c = int(m[1]), m[2], int(m[3]), int(m[4])
        mach = _machine_arith(a, op, b, c)
        if mach and mach[0] in ("PASS", "VIOLATION"):
            v, spent, ev = mach
            return {"verdict": "PASS" if v == "PASS" else "REFUTED",
                    "layer": "sigma-glyph", "atp": spent, "evidence": ev,
                    "detail": f"{a}{op}{b}={c}"}
        actual = {"+": a + b, "*": a * b, "-": a - b}[op]
        return {"verdict": "PASS" if actual == c else "REFUTED",
                "layer": "integer", "detail": f"actual {a}{op}{b}={actual}"}
    if cls == "cmp":
        m = CMP.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed cmp"}
        a, rel, b = int(m[1]), m[2], int(m[3])
        mach = _machine_cmp(a, rel, b)
        if mach and mach[0] in ("PASS", "VIOLATION"):
            v, spent, ev = mach
            return {"verdict": "PASS" if v == "PASS" else "REFUTED",
                    "layer": "sigma-glyph", "atp": spent, "evidence": ev[:16],
                    "detail": payload}
        ok = {"<=": a <= b, ">=": a >= b, "=": a == b, "<": a < b, ">": a > b}[rel]
        return {"verdict": "PASS" if ok else "REFUTED", "layer": "integer",
                "detail": payload}
    if cls == "count":
        m = COUNT.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed count"}
        pat, path, n = m[1], m[2], int(m[3])
        fp = os.path.join(REPO, path)
        if not os.path.isfile(fp):
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": f"no file {path}"}
        with open(fp, encoding="utf-8", errors="replace") as f:
            actual = len(re.findall(pat, f.read()))
        return {"verdict": "PASS" if actual == n else "REFUTED", "layer": "repo",
                "detail": f"actual count = {actual}"}
    if cls == "sha256":
        m = SHA.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed sha256"}
        path, prefix = m[1], m[2]
        fp = os.path.join(REPO, path)
        if not os.path.isfile(fp):
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": f"no file {path}"}
        with open(fp, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        return {"verdict": "PASS" if actual.startswith(prefix) else "REFUTED",
                "layer": "repo", "detail": f"actual {actual[:16]}..."}
    return {"verdict": "UNSETTLED", "layer": None, "detail": f"unknown class {cls}"}


def badge(res, cls, payload):
    p = payload.strip()
    if res["verdict"] == "PASS":
        extra = f", ATP {res['atp']}" if res.get("atp") is not None else ""
        return f"{p} ⚓⟨{res['layer']}{extra}⟩"
    if res["verdict"] == "REFUTED":
        return f"~~{p}~~ ✗REFUTED⟨{res['detail']}⟩"
    return f"{p} ◇unsettled⟨{res['detail']}⟩"


def gate(text):
    results = []

    def repl(m):
        cls, payload = m.group(1), m.group(2)
        res = settle(cls, payload)
        results.append({"class": cls, "payload": payload.strip(), **res})
        return badge(res, cls, payload)

    return CLAIM.sub(repl, text), results


def main():
    if len(sys.argv) != 2:
        print("usage: settle_gate.py <file.md>", file=sys.stderr)
        return 2
    src = sys.argv[1]
    with open(src, encoding="utf-8") as f:
        text = f.read()
    settled_text, results = gate(text)
    tally = {"claims": len(results),
             "settled_true": sum(r["verdict"] == "PASS" for r in results),
             "refuted": sum(r["verdict"] == "REFUTED" for r in results),
             "unsettled": sum(r["verdict"] == "UNSETTLED" for r in results),
             "atp_total": sum(r.get("atp") or 0 for r in results)}
    receipt = {"source_sha256": hashlib.sha256(text.encode()).hexdigest(),
               "tally": tally, "claims": results}
    out_md = src.rsplit(".md", 1)[0] + ".settled.md"
    out_js = src.rsplit(".md", 1)[0] + ".receipt.json"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(settled_text)
    body = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2)
    with open(out_js, "w", encoding="utf-8") as f:
        f.write(body + "\nRECEIPT_SHA256: "
                + hashlib.sha256(body.encode()).hexdigest() + "\n")
    print(json.dumps(tally, sort_keys=True))
    print("settled ->", out_md)
    print("receipt ->", out_js)
    return 1 if tally["refuted"] else 0


if __name__ == "__main__":
    sys.exit(main())
