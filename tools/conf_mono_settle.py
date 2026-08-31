#!/usr/bin/env python3
"""
conf_mono_settle.py — end-to-end compilation of claim 0030
("confidence must be monotone across translation unless evidence is added")
from informal English into a settled, content-addressed verdict on the
Σ-GLYPH machine.

Pipeline:
  Stage A (formal invariant, documented in drafts/COMPILE-0030-CONF-MONO.md):
      Trace = [(claim_hash, conf_ppm: u32, evidence_hash | None), ...]
      I_mono: ∀i < n-1:  conf[i+1] <= conf[i]  ∨  evidence[i] ≠ None
  Stage B: deterministic integer-only checker over ppm values + receipt.
  Stage C: per-trace compilation to an SKI term (Church encodings, bracket
      abstraction) evaluated by the real sigma-glyph oracle eval_hash();
      verdict comes back as the content-addressed literal PASS / VIOLATION
      with an exact ATP spend.

Determinism contract: no clocks, no randomness, no floats. Two runs on any
machine with the same sigma-glyph checkout print byte-identical receipts.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sigma_boundary import sigma  # noqa: E402

# The evaluator as an INSTALLED PACKAGE. This was a hardcoded
# absolute path into one machine's checkout; see sigma_boundary.py.
sg = sigma()

# ---------------------------------------------------------------- Stage B ---
def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_trace_bytes(trace):
    return json.dumps(trace, sort_keys=True, separators=(",", ":")).encode()

def check_mono_ppm(trace):
    """Integer-only checker at full ppm precision.
    Returns ('PASS', None) or ('VIOLATION', first_bad_step)."""
    for i in range(len(trace) - 1):
        conf_now = trace[i]["conf_ppm"]
        conf_next = trace[i + 1]["conf_ppm"]
        evidence = trace[i + 1].get("evidence")
        if conf_next > conf_now and evidence is None:
            return "VIOLATION", i + 1
    return "PASS", None

# ------------------------------------------------- Stage C: λ → SKI compiler
V = lambda x: ("v", x)
L = lambda x, b: ("l", x, b)
A = lambda f, *xs: _apps(f, xs)
def _apps(f, xs):
    t = f
    for x in xs:
        t = ("a", t, x)
    return t

def free(x, e):
    tag = e[0]
    if tag == "v":
        return e[1] == x
    if tag == "a":
        return free(x, e[1]) or free(x, e[2])
    if tag == "l":
        return e[1] != x and free(x, e[2])
    return False  # S/K/I/lit atoms

def compile_l(e):
    tag = e[0]
    if tag == "a":
        return ("a", compile_l(e[1]), compile_l(e[2]))
    if tag == "l":
        return abstract(e[1], compile_l(e[2]))
    return e

def abstract(x, e):
    if e == ("v", x):
        return ("I",)
    if not free(x, e):
        return ("a", ("K",), e)
    # e is an application (lambdas already compiled away bottom-up)
    l, r = e[1], e[2]
    if r == ("v", x) and not free(x, l):  # η-reduction
        return l
    return opt_S(abstract(x, l), abstract(x, r))

def opt_S(fl, fr):
    """Peephole: S (K a) (K b) -> K (a b);  S (K a) I -> a."""
    if fl[0] == "a" and fl[1] == ("K",):
        if fr[0] == "a" and fr[1] == ("K",):
            return ("a", ("K",), ("a", fl[2], fr[2]))
        if fr == ("I",):
            return fl[2]
    return ("a", ("a", ("S",), fl), fr)

# Church encodings -----------------------------------------------------------
def church(n):
    body = V("x")
    for _ in range(n):
        body = A(V("f"), body)
    return L("f", L("x", body))

TRUE = L("a", L("b", V("a")))
FALSE = L("a", L("b", V("b")))
AND = L("p", L("q", A(V("p"), V("q"), V("p"))))
OR = L("p", L("q", A(V("p"), V("p"), V("q"))))
ISZERO = L("n", A(V("n"), L("w", FALSE), TRUE))
PRED = L("n", L("f", L("x", A(V("n"),
        L("g", L("h", A(V("h"), A(V("g"), V("f"))))),
        L("u", V("x")),
        L("u", V("u"))))))
SUB = L("m", L("n", A(V("n"), PRED, V("m"))))
LEQ = L("m", L("n", A(ISZERO, A(SUB, V("m"), V("n")))))

def build_verdict_lambda(trace):
    """Unrolled instance check: AND over steps of (evidence OR conf_next<=conf_now),
    applied to selector args PASS/VIOLATION (as lit placeholders)."""
    q = lambda ppm: ppm // 100000  # quantization ppm -> 0..10 (FLOW §11; lossy)
    steps = []
    for i in range(len(trace) - 1):
        ev = TRUE if trace[i + 1].get("evidence") is not None else FALSE
        ok = A(OR, ev, A(LEQ, church(q(trace[i + 1]["conf_ppm"])),
                         church(q(trace[i]["conf_ppm"]))))
        steps.append(ok)
    total = steps[0]
    for s in steps[1:]:
        total = A(AND, total, s)
    return A(total, ("lit", b"PASS"), ("lit", b"VIOLATION"))

# SKI term -> sigma-glyph store ----------------------------------------------
def to_machine(t, st, lit_cache):
    tag = t[0]
    if tag == "a":
        l = to_machine(t[1], st, lit_cache)
        r = to_machine(t[2], st, lit_cache)
        node = ("app", l, r)
        st.put(sg.term_bytes(node))
        return node
    if tag in ("S", "K", "I"):
        node = ("lit", sg.sha(tag.encode()))
        st.put(sg.term_bytes(node))
        return node
    if tag == "lit":
        if t[1] not in lit_cache:
            lit_cache[t[1]] = st.put(t[1])
        node = ("lit", lit_cache[t[1]])
        st.put(sg.term_bytes(node))
        return node
    raise ValueError(f"unexpected node {t!r}")

def settle_on_machine(trace, atp=50_000_000):
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    lit_cache = {}
    ski = compile_l(build_verdict_lambda(trace))
    node = to_machine(ski, st, lit_cache)
    th = st.put(sg.term_bytes(node))
    result, spent = sg.eval_hash(th, atp, st)
    # results are hash-transparent (a thunk's hash IS its referent), so compare
    # by term_hash rather than by node shape
    rh = sg.term_hash(result)
    if rh == sg.term_hash(("lit", sg.sha(b"PASS"))):
        verdict = "PASS"
    elif rh == sg.term_hash(("lit", sg.sha(b"VIOLATION"))):
        verdict = "VIOLATION"
    elif result[1] == sg.sha(b"ATP Exhausted"):
        verdict = "ATP_EXHAUSTED"
    elif result[1] == sg.sha(b"Unresolved Reference"):
        verdict = "UNRESOLVED_REFERENCE"
    else:
        verdict = "UNEXPECTED:" + rh.hex()[:16]
    return {"term_hash": th.hex(), "verdict": verdict, "atp_spent": spent}

# Traces ---------------------------------------------------------------------
def h(s):  # stable pseudo-hashes for claim/evidence ids in the demo traces
    return sha256_hex(s.encode())[:16]

TRACES = {
    "clean_summarization": [
        {"claim": h("source-report"), "conf_ppm": 900000, "evidence": None},
        {"claim": h("summary-l1"), "conf_ppm": 850000, "evidence": None},
        {"claim": h("summary-l2"), "conf_ppm": 850000, "evidence": None},
        {"claim": h("summary-l3"), "conf_ppm": 700000, "evidence": None},
    ],
    "confidence_laundering": [
        {"claim": h("hedged-finding"), "conf_ppm": 600000, "evidence": None},
        {"claim": h("exec-summary"), "conf_ppm": 600000, "evidence": None},
        {"claim": h("press-release"), "conf_ppm": 900000, "evidence": None},
    ],
    "licensed_by_evidence": [
        {"claim": h("hypothesis"), "conf_ppm": 600000, "evidence": None},
        {"claim": h("confirmed"), "conf_ppm": 900000, "evidence": h("exp-42-data")},
    ],
}

def main():
    with open(os.path.abspath(__file__), "rb") as f:
        script_hash = sha256_hex(f.read())
    receipt = {"invariant": "forall i: conf[i+1]<=conf[i] or evidence[i+1]!=None",
               "checker_script_sha256": script_hash,
               "quantization": {"machine_layer": "conf_ppm // 100000 (0..10)",
                                "lost": ["sub-0.1 confidence increases",
                                         "violation index (machine verdict is boolean)"],
                                "preserved": ["verdict on all supplied traces",
                                              "determinism", "priced work"]},
               "traces": {}}
    for name, trace in sorted(TRACES.items()):
        verdict, bad = check_mono_ppm(trace)
        receipt["traces"][name] = {
            "trace_sha256": sha256_hex(canonical_trace_bytes(trace)),
            "python_layer": {"verdict": verdict, "first_violation_step": bad},
            "machine_layer": settle_on_machine(trace),
        }
    out = json.dumps(receipt, sort_keys=True, indent=2)
    print(out)
    print("\nRECEIPT_SHA256:", sha256_hex(out.encode()))

if __name__ == "__main__":
    main()
