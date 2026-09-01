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

# --- P0 fixes (Codex review 2026-08, findings F2) -------------------------
MAX_READ_BYTES = 8 * 1024 * 1024   # bound file work (ReDoS / exhaustion surface)
REGEX_TIMEOUT_S = 2                # bound regex work

def resolve_in_repo(path):
    """Resolve `path` under REPO and REFUSE escapes and out-of-tree symlinks.
    Returns an absolute path or raises ValueError. Closes the sandbox escape
    Codex reproduced (sha256 reading ../../../../etc/hosts)."""
    repo_real = os.path.realpath(REPO)
    target = os.path.realpath(os.path.join(REPO, path))
    if target != repo_real and not target.startswith(repo_real + os.sep):
        raise ValueError(f"path escapes repository: {path}")
    return target

def read_bounded(fp):
    """Read at most MAX_READ_BYTES; raise if the file is larger."""
    size = os.path.getsize(fp)
    if size > MAX_READ_BYTES:
        raise ValueError(f"file too large ({size} > {MAX_READ_BYTES} bytes)")
    with open(fp, encoding="utf-8", errors="replace") as f:
        return f.read()

def findall_bounded(pattern, text, flags=0):
    """re.findall with a wall-clock bound, via a worker thread (no signal
    dependence, works off the main thread too). Raises TimeoutError."""
    import threading
    result, error = [], []
    def run():
        try:
            result.append(re.findall(pattern, text, flags))
        except Exception as e:  # invalid pattern etc. surface as settle errors
            error.append(e)
    t = threading.Thread(target=run, daemon=True)
    t.start(); t.join(REGEX_TIMEOUT_S)
    if t.is_alive():
        raise TimeoutError(f"regex exceeded {REGEX_TIMEOUT_S}s (possible ReDoS)")
    if error:
        raise error[0]
    return result[0]

ARITH = re.compile(r"^(-?\d+)\s*([+*-])\s*(-?\d+)\s*=\s*(-?\d+)$")
CMP = re.compile(r"^(-?\d+)\s*(<=|>=|<|>|=)\s*(-?\d+)$")
COUNT = re.compile(r"^/(.+)/\s+in\s+(\S+)\s*=\s*(\d+)(?:\s+@(\w+))?$")
BINDARITH = re.compile(r"^(\w+)\s*([+*-])\s*(\w+)\s*=\s*(\w+)$")
SHA = re.compile(r"^(\S+)\s*=\s*([0-9a-f]{12,64})$")
CITE = re.compile(r"^\"(.+)\"\s+in\s+(\S+)$", re.S)
MONO = re.compile(r"^([\d,\s]+?)(?:\s+ev\s+([\d,\s]+))?$")

MACHINE_MAX = 400   # arith via hash-equality of normal forms: linear cost
CMP_MAX = 12        # cmp needs Church SUB/LEQ: expensive, small values only
GATE_VERSION = "settle_gate/0.3+deps"  # dependency-bound receipts (Codex F3/F4)

def _dep(path, content):
    """A dependency record: the path a claim read and the digest of what it
    actually read, so a receipt commits to the world it settled against."""
    return {"path": path,
            "sha256": hashlib.sha256(content.encode("utf-8", "replace")).hexdigest()}


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


def settle(cls, payload, env=None):
    """Returns dict: verdict PASS|REFUTED|UNSETTLED, layer, detail, atp.
    `env` is the document's binding environment {name: measured_value}, used by
    semantic-binding classes so arithmetic operates on MEASURED reality rather
    than on generator-chosen literals (Codex F3: '3 and 6 were never bound to
    the sets they count')."""
    if env is None:
        env = {}
    payload = payload.strip()
    if cls == "bindarith":
        m = BINDARITH.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed bindarith"}
        na, op, nb, nc = m[1], m[2], m[3], m[4]
        missing = [x for x in (na, nb, nc) if x not in env and not x.isdigit()]
        if missing:
            return {"verdict": "UNSETTLED", "layer": "bind",
                    "detail": f"unbound name(s): {', '.join(missing)} "
                              f"(bind via a measured claim's @name first)"}
        va = int(na) if na.isdigit() else env[na]
        vb = int(nb) if nb.isdigit() else env[nb]
        vc = int(nc) if nc.isdigit() else env[nc]
        actual = {"+": va + vb, "*": va * vb, "-": va - vb}[op]
        ok = actual == vc
        return {"verdict": "PASS" if ok else "REFUTED", "layer": "bind",
                "detail": f"measured {na}={va} {op} {nb}={vb} = {actual}"
                          + ("" if ok else f" ≠ {nc}={vc}")}
    if cls == "arith":
        m = ARITH.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed arith"}
        a, op, b, c = int(m[1]), m[2], int(m[3]), int(m[4])
        mach = _machine_arith(a, op, b, c)
        if mach and mach[0] in ("PASS", "VIOLATION"):
            v, spent, meta = mach
            return {"verdict": "PASS" if v == "PASS" else "REFUTED",
                    "layer": "sigma-glyph", "atp": spent,
                    "ski_checks": [dict(meta["lhs"], means=f"NF of {a}{op}{b} at a generic point"),
                                   dict(meta["rhs"], means=f"NF of {c} at a generic point")],
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
            entry = {"verdict": "PASS" if v == "PASS" else "REFUTED",
                     "layer": "sigma-glyph", "atp": spent, "detail": payload}
            if isinstance(ev, dict) and "lhs" in ev:  # settle_nat_eq meta
                entry["ski_checks"] = [dict(ev["lhs"], means=f"NF of {a}"),
                                       dict(ev["rhs"], means=f"NF of {b}")]
            else:  # settle_bool term hash
                entry["evidence"] = str(ev)[:16]
            return entry
        ok = {"<=": a <= b, ">=": a >= b, "=": a == b, "<": a < b, ">": a > b}[rel]
        return {"verdict": "PASS" if ok else "REFUTED", "layer": "integer",
                "detail": payload}
    if cls == "count":
        m = COUNT.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed count"}
        pat, path, n, name = m[1], m[2], int(m[3]), m[4]
        try:
            fp = resolve_in_repo(path)
        except ValueError as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        if not os.path.isfile(fp):
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": f"no file {path}"}
        try:
            content = read_bounded(fp)
            actual = len(findall_bounded(pat, content, re.MULTILINE))
        except (ValueError, TimeoutError) as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        if name:  # bind the MEASURED value (not the claimed n) for semantic binding
            env[name] = actual
        det = f"actual count = {actual}" + (f" (bound {name}={actual})" if name else "")
        return {"verdict": "PASS" if actual == n else "REFUTED", "layer": "repo",
                "detail": det, "dep": _dep(path, content)}
    if cls == "sha256":
        m = SHA.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed sha256"}
        path, prefix = m[1], m[2]
        try:
            fp = resolve_in_repo(path)
        except ValueError as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        if not os.path.isfile(fp):
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": f"no file {path}"}
        try:
            content = read_bounded(fp)
        except ValueError as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        actual = hashlib.sha256(content.encode("utf-8", "replace")).hexdigest()
        return {"verdict": "PASS" if actual.startswith(prefix) else "REFUTED",
                "layer": "repo", "detail": f"actual {actual[:16]}...",
                "dep": _dep(path, content)}
    if cls in ("cite", "citei"):
        m = CITE.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": f"malformed {cls}"}
        quote, path = m[1], m[2]
        try:
            fp = resolve_in_repo(path)
        except ValueError as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        if not os.path.isfile(fp):
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": f"no file {path}"}
        try:
            content = read_bounded(fp)
        except ValueError as e:
            return {"verdict": "UNSETTLED", "layer": "repo", "detail": str(e)}
        if cls == "citei":
            found = quote.lower() in content.lower()
            kind = "case-insensitive"
        else:
            found = quote in content
            kind = "verbatim"
        return {"verdict": "PASS" if found else "REFUTED", "layer": "repo",
                "detail": f"{kind} quote found" if found else f"{kind} quote NOT in file",
                "dep": _dep(path, content)}
    if cls == "mono":
        # ⟦mono: c1,c2,c3 ev i,j⟧ — confidence chain in ppm (0..1000000);
        # invariant 0030: conf[k+1] <= conf[k] unless entry k+1 carries evidence.
        m = MONO.match(payload)
        if not m:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed mono"}
        try:
            confs = [int(x) for x in m[1].replace(" ", "").split(",") if x]
            evs = {int(x) for x in (m[2] or "").replace(" ", "").split(",") if x}
        except ValueError:
            return {"verdict": "UNSETTLED", "layer": None, "detail": "malformed mono"}
        if len(confs) < 2 or any(not 0 <= c <= 1_000_000 for c in confs):
            return {"verdict": "UNSETTLED", "layer": None,
                    "detail": "need >=2 confidences in 0..1000000 ppm"}
        for i in range(len(confs) - 1):
            if confs[i + 1] > confs[i] and (i + 1) not in evs:
                return {"verdict": "REFUTED", "layer": "integer",
                        "detail": f"confidence laundering at step {i + 1} "
                                  f"({confs[i]} -> {confs[i + 1]}, no evidence)"}
        return {"verdict": "PASS", "layer": "integer",
                "detail": f"monotone ({len(confs)} entries, evidence at {sorted(evs) or '—'})"}
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
    env = {}   # binding environment, populated left-to-right as claims settle

    def repl(m):
        cls, payload = m.group(1), m.group(2)
        res = settle(cls, payload, env)
        results.append({"class": cls, "payload": payload.strip(), **res})
        return badge(res, cls, payload)

    return CLAIM.sub(repl, text), results


def main():
    args = [a for a in sys.argv[1:] if a not in ("--strict", "--no-write")]
    strict = "--strict" in sys.argv   # P1 fix (Codex): fail-closed on ANY non-PASS
    # --no-write: diagnostic run, print the tally/receipt digest but write no files.
    # Default remains write-on (the .settled.md / .receipt.json artifacts are canonical
    # evidence and stay tracked); --no-write is for read-only inspection.
    nowrite = "--no-write" in sys.argv
    if len(args) != 1:
        print("usage: settle_gate.py [--strict] [--no-write] <file.md>", file=sys.stderr)
        return 2
    src = args[0]
    with open(src, encoding="utf-8") as f:
        text = f.read()
    settled_text, results = gate(text)
    tally = {"claims": len(results),
             "settled_true": sum(r["verdict"] == "PASS" for r in results),
             "refuted": sum(r["verdict"] == "REFUTED" for r in results),
             "unsettled": sum(r["verdict"] == "UNSETTLED" for r in results),
             "atp_total": sum(r.get("atp") or 0 for r in results)}
    # dependency closure: every file a claim actually read, by digest, so a
    # freshness checker can detect a stale receipt without re-running anything
    # (Codex F3/F4). Conflicting digests for one path => the file changed
    # mid-run; recorded as a list so that is visible, not averaged away.
    deps = {}
    for r in results:
        d = r.get("dep")
        if d:
            deps.setdefault(d["path"], set()).add(d["sha256"])
    deps = {p: sorted(v) for p, v in sorted(deps.items())}
    receipt = {"source_sha256": hashlib.sha256(text.encode()).hexdigest(),
               "gate_version": GATE_VERSION, "deps": deps,
               "tally": tally, "claims": results}
    body = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2)
    receipt_sha = hashlib.sha256(body.encode()).hexdigest()
    print(json.dumps(tally, sort_keys=True))
    if nowrite:
        print("RECEIPT_SHA256:", receipt_sha, "(--no-write: nothing written)")
    else:
        out_md = src.rsplit(".md", 1)[0] + ".settled.md"
        out_js = src.rsplit(".md", 1)[0] + ".receipt.json"
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(settled_text)
        with open(out_js, "w", encoding="utf-8") as f:
            f.write(body + "\nRECEIPT_SHA256: " + receipt_sha + "\n")
        print("settled ->", out_md)
        print("receipt ->", out_js)
    if strict:
        # a publication/CI gate must fail on refuted OR unsettled (unsupported,
        # malformed, budget-exhausted, path-refused): only all-PASS exits 0.
        return 0 if tally["refuted"] == 0 and tally["unsettled"] == 0 else 1
    return 1 if tally["refuted"] else 0


if __name__ == "__main__":
    sys.exit(main())
