#!/usr/bin/env python3
"""
glyphlib.py — shared settlement library: λ→SKI compiler, Church encodings,
and the interface to the real Σ-GLYPH machine (eval_hash).

Deterministic: no clocks, no randomness, no floats. Extracted from
conf_mono_settle.py (COMPILE-0030) into a reusable layer for settle_gate.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sigma_boundary import sigma  # noqa: E402

# The evaluator as an INSTALLED PACKAGE. This was a hardcoded
# absolute path into one machine's checkout; see sigma_boundary.py.
sg = sigma()

# ---- Lambda AST ------------------------------------------------------------
V = lambda x: ("v", x)
L = lambda x, b: ("l", x, b)

def A(f, *xs):
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
    return False

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
    l, r = e[1], e[2]
    if r == ("v", x) and not free(x, l):  # η
        return l
    return opt_S(abstract(x, l), abstract(x, r))

def opt_S(fl, fr):
    if fl[0] == "a" and fl[1] == ("K",):
        if fr[0] == "a" and fr[1] == ("K",):
            return ("a", ("K",), ("a", fl[2], fr[2]))
        if fr == ("I",):
            return fl[2]
    return ("a", ("a", ("S",), fl), fr)

# ---- Church encodings ------------------------------------------------------
def church(n):
    body = V("x")
    for _ in range(n):
        body = A(V("f"), body)
    return L("f", L("x", body))

TRUE = L("a", L("b", V("a")))
FALSE = L("a", L("b", V("b")))
AND = L("p", L("q", A(V("p"), V("q"), V("p"))))
OR = L("p", L("q", A(V("p"), V("p"), V("q"))))
NOT = L("p", L("a", L("b", A(V("p"), V("b"), V("a")))))
ISZERO = L("n", A(V("n"), L("w", FALSE), TRUE))
PRED = L("n", L("f", L("x", A(V("n"),
        L("g", L("h", A(V("h"), A(V("g"), V("f"))))),
        L("u", V("x")),
        L("u", V("u"))))))
SUB = L("m", L("n", A(V("n"), PRED, V("m"))))
LEQ = L("m", L("n", A(ISZERO, A(SUB, V("m"), V("n")))))
EQN = L("m", L("n", A(AND, A(LEQ, V("m"), V("n")), A(LEQ, V("n"), V("m")))))
PLUS = L("m", L("n", L("f", L("x", A(V("m"), V("f"), A(V("n"), V("f"), V("x")))))))
MULT = L("m", L("n", L("f", A(V("m"), A(V("n"), V("f"))))))

# ---- Machine interface -----------------------------------------------------
def _to_machine(t, st, lit_cache):
    tag = t[0]
    if tag == "a":
        l = _to_machine(t[1], st, lit_cache)
        r = _to_machine(t[2], st, lit_cache)
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

def eval_nf(lambda_expr, atp=50_000_000):
    """Evaluate a lambda expression to its canonical result on the machine.
    Returns (result_hash_hex | None, atp_spent, exit) where exit is
    'NF' | 'ATP_EXHAUSTED' | 'UNRESOLVED' | 'RESOURCE_FAULT'. Content
    addressing makes result hashes comparable across independent stores."""
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    node = _to_machine(compile_l(lambda_expr), st, {})
    th = st.put(sg.term_bytes(node))
    try:
        result, spent = sg.eval_hash(th, atp, st, limits=GATE_LIMITS)
    except sg.ResourceFault:
        return None, 0, "RESOURCE_FAULT"
    if result[0] != "app" and result[1] == sg.sha(b"ATP Exhausted"):
        return None, spent, "ATP_EXHAUSTED", th.hex()
    if result[0] != "app" and result[1] == sg.sha(b"Unresolved Reference"):
        return None, spent, "UNRESOLVED", th.hex()
    return sg.term_hash(result).hex(), spent, "NF", th.hex()


def settle_nat_eq(m_expr, n_expr, atp=50_000_000):
    """Settle numeric equality of two Church-numeral expressions by comparing
    canonical normal forms of (expr F X) with inert literals F, X — the
    content-addressed equality idiom: equal numbers reduce to the same
    F^k(X), hence the same hash. Linear cost, no SUB blowup.
    Returns (verdict, atp_spent, meta) where meta carries, for each side,
    the evaluated term hash, its normal-form hash and its ATP spend — the
    exact shape of a Warrant evidence-pack `ski_checks` entry
    ({check, term, expect, atp})."""
    F, X = ("lit", b"F"), ("lit", b"X")
    hm, sm, em, tm = eval_nf(A(m_expr, F, X), atp)
    if em != "NF":
        return em, sm, {"failed": "lhs"}
    hn, sn, en, tn = eval_nf(A(n_expr, F, X), atp)
    if en != "NF":
        return en, sm + sn, {"failed": "rhs"}
    meta = {"lhs": {"term": tm, "expect": hm, "atp": sm},
            "rhs": {"term": tn, "expect": hn, "atp": sn}}
    return ("PASS" if hm == hn else "VIOLATION"), sm + sn, meta


# Our verifier policy: admit more in-flight growth than DEFAULT_LIMITS, but
# stay bounded; a breach is reported as RESOURCE_FAULT (local, non-canonical).
GATE_LIMITS = {"max_node_depth": 65_536,
               "max_materialized_nodes": 8_000_000,
               "max_store_fetches": 8_000_000,
               "max_atp": None}

def settle_bool(lambda_bool_expr, atp=50_000_000):
    """Evaluate a lambda expression that reduces to a Church boolean on the
    Σ-GLYPH machine. Returns (verdict, atp_spent, term_hash_hex) with verdict
    in {'PASS', 'VIOLATION', 'ATP_EXHAUSTED', 'UNRESOLVED', 'RESOURCE_FAULT',
    'UNEXPECTED:...'}."""
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    lit_cache = {}
    applied = A(lambda_bool_expr, ("lit", b"PASS"), ("lit", b"VIOLATION"))
    node = _to_machine(compile_l(applied), st, lit_cache)
    th = st.put(sg.term_bytes(node))
    try:
        result, spent = sg.eval_hash(th, atp, st, limits=GATE_LIMITS)
    except sg.ResourceFault as e:
        return "RESOURCE_FAULT", 0, th.hex()
    rh = sg.term_hash(result)
    if rh == sg.term_hash(("lit", sg.sha(b"PASS"))):
        return "PASS", spent, th.hex()
    if rh == sg.term_hash(("lit", sg.sha(b"VIOLATION"))):
        return "VIOLATION", spent, th.hex()
    if result[1] == sg.sha(b"ATP Exhausted"):
        return "ATP_EXHAUSTED", spent, th.hex()
    if result[1] == sg.sha(b"Unresolved Reference"):
        return "UNRESOLVED", spent, th.hex()
    return "UNEXPECTED:" + rh.hex()[:16], spent, th.hex()
