#!/usr/bin/env python3
"""
verify.py — embedded-claims PoC, phase 1.  (rev 3, after Codex reviews 2026-09)

A THIN layer over the existing engine (tools/settle_gate.py + glyphlib.py + the
real Σ-GLYPH runtime). It reports an embedded claim on TWO independent axes and
NOTHING it cannot honestly compute.

REV 3 (second Codex pass)
  P0  world-dependent classes now REQUIRE a dependency pin whose PATH and DIGEST
      both match what was actually read: DEPENDENCY_MISSING / _PATH_MISMATCH /
      _STALE. No exact path+digest ⇒ no replay credit.
  P1  the engine is LAZY-LOADED: the effect path imports neither settle_gate nor
      the evaluator, so `effect-sandbox://` is genuinely Sigma-independent (runs
      under `python -S` with no Sigma package). Non-effect classes share one
      bootstrap import (settle_gate → glyphlib → sigma()); that whole closure —
      dispatch/renderer, gate, glyphlib, resolver, evaluator — is bound into their
      IDs. `sigma()` is called only for non-effect classes. Closure is over CODE
      FILES; the interpreter build / OS / import environment are deliberately OUT.
  P1  the effect address must be a FULL 64-hex digest (identity-bearing), not an
      8-hex display prefix.
  P2  result identity is split: `result_value_id` (canonical result, class-local)
      vs `evaluation_id` (claim-bound: claim+plan+dependency+value+verdict). The
      author pins `evaluation_id`. No field carries two meanings.

REV 2 (first Codex pass): per-class verifier identity + digest closure;
missing/wrong pin ⇒ UNVERIFIED; independent execution facts; binding clamped to
ASSERTED; distinct claim/plan/result identities; REPORT (not receipt) with a body
commitment; effect settles on observed post-state, not stdout.

A fixture is Markdown with one inline claim ⟦class: payload⟧ and an optional fenced
```json capsule of AUTHOR ASSERTIONS (pinned verifier, dependency for freshness,
the evaluation_id the author bets on, a semantic binding). Assertions are claims,
not verdicts; this tool recomputes and reports whether they reproduce.

Deterministic: same file bytes + same repo state + same evaluator => same output.
Usage:  verify.py <fixture.md>
"""
import hashlib
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "tools"))
sys.path.insert(0, TOOLS)
from sigma_boundary import sigma    # noqa: E402  (import is safe; sigma() resolves lazily)
# settle_gate is imported LAZILY inside verify_file: importing it pulls glyphlib,
# whose module-level `sg = sigma()` would resolve the evaluator for EVERY class.
# The effect path must not depend on Sigma, so it never imports settle_gate.

CAPSULE = re.compile(r"```json capsule\s*\n(.*?)\n```", re.S)
CLAIM_RE = re.compile(r"⟦([a-z0-9_]+):\s*([^⟧]+)⟧")   # == settle_gate.CLAIM, kept local
GLYPHLIB = os.path.join(TOOLS, "glyphlib.py")
SETTLE_GATE = os.path.join(TOOLS, "settle_gate.py")
SIGMA_BOUNDARY = os.path.join(TOOLS, "sigma_boundary.py")
SELF = os.path.abspath(__file__)
WORLD_CLASSES = {"count", "sha256", "cite", "citei"}   # read repository bytes


def _h(domain, *parts):
    """Domain-separated digest of ordered parts."""
    m = hashlib.sha256()
    m.update(domain.encode() + b"\0")
    for p in parts:
        m.update(str(p).encode("utf-8") + b"\0")
    return m.hexdigest()


def _closure_digest(paths):
    """Digest of the exact bytes of every CODE FILE on the settlement path."""
    m = hashlib.sha256()
    for p in sorted(paths):
        with open(p, "rb") as f:
            m.update(hashlib.sha256(f.read()).digest())
    return m.hexdigest()


# --- P0-1/P1: verifier identity — code closure on the settlement path --------
# Covers the .py files whose bytes could change THIS claim's verdict OR its
# executability. It does NOT cover the interpreter build, OS, or import
# environment — that closure is deliberately left open, and the identity claim is
# scoped to code accordingly.
BOOTSTRAP = [SELF, SETTLE_GATE, GLYPHLIB, SIGMA_BOUNDARY]  # the shared engine import


def verifier_id(layer):
    if layer == "effect-sandbox":
        # Genuinely independent: the effect path imports neither settle_gate nor
        # the evaluator, so this closure is verify.py alone — no Sigma required.
        return "effect-sandbox://sha256:" + _closure_digest([SELF])
    if layer is None:
        return None
    # Every non-effect class settles through settle_gate, whose import resolves
    # glyphlib and the evaluator; the ID binds that whole bootstrap (executability),
    # not only verdict-affecting code. sigma() is called only here — never on the
    # effect path.
    files = BOOTSTRAP + [sigma().__file__]
    scheme = "glyph" if layer == "sigma-glyph" else "settle-gate"
    return f"{scheme}://sha256:" + _closure_digest(files)


def _short(vid):
    if not vid:
        return "—"
    scheme, _, digest = vid.partition("://sha256:")
    return f"{scheme}://sha256:{digest[:12]}"


# --- P1-5: effects are OBSERVED post-state, not enforced --------------------
# A TemporaryDirectory is NOT a sandbox: an op could write outside it, touch the
# network, or write-then-delete, and the digest would not see it. The credit is
# "observed post-state differs", never "effects enforced" (see limits/ fixture).
def _op_echo_only(sandbox):
    return b"hello\n"                                   # prints, writes nothing


def _op_echo_and_touch(sandbox):
    with open(os.path.join(sandbox, "marker"), "wb") as f:
        f.write(b"x")                                   # same stdout, but writes
    return b"hello\n"


def _op_echo_then_delete(sandbox):
    p = os.path.join(sandbox, "transient")
    with open(p, "wb") as f:                            # writes, then removes —
        f.write(b"x")                                   # invisible to a surviving-
    os.remove(p)                                        # files digest (the LIMIT)
    return b"hello\n"


EFFECT_OPS = {"echo_only": _op_echo_only,
              "echo_and_touch": _op_echo_and_touch,
              "echo_then_delete": _op_echo_then_delete}


def _sandbox_state(sandbox):
    entries = []
    for root, _dirs, files in os.walk(sandbox):
        for name in sorted(files):
            fp = os.path.join(root, name)
            with open(fp, "rb") as f:
                entries.append((os.path.relpath(fp, sandbox),
                                hashlib.sha256(f.read()).hexdigest()))
    return json.dumps(sorted(entries), separators=(",", ":")).encode()


def settle_effect(payload):
    """⟦effect: <op> addr=<64-hex>⟧ — run <op>, settle on the OBSERVED post-state
    digest (stdout ++ surviving sandbox files), compare to the author's FULL
    asserted digest. Reports the stdout-only digest, so a stdout match the state
    rejects is visible (D6). An identity-bearing commitment requires all 64 hex."""
    m = re.match(r"^(\w+)\s+addr=([0-9a-f]{64})$", payload.strip())
    if not m:
        return {"verdict": "UNSETTLED", "layer": None,
                "detail": "malformed effect (need '<op> addr=<64-hex>')"}
    op_name, want = m[1], m[2]
    if op_name not in EFFECT_OPS:
        return {"verdict": "UNSETTLED", "layer": None,
                "detail": f"unknown effect op {op_name} "
                          f"(allowlist: {', '.join(sorted(EFFECT_OPS))})"}
    with tempfile.TemporaryDirectory() as sandbox:
        stdout = EFFECT_OPS[op_name](sandbox)
        stdout_digest = hashlib.sha256(stdout).hexdigest()
        state_digest = hashlib.sha256(
            stdout + b"\x00" + _sandbox_state(sandbox)).hexdigest()
    ok = state_digest == want
    note = ""
    if not ok and stdout_digest == want:
        note = (" — NOTE: stdout-only digest WOULD have matched; caught because "
                "we settle on observed post-state, not stdout (D6)")
    return {"verdict": "PASS" if ok else "REFUTED", "layer": "effect-sandbox",
            "detail": f"state={state_digest[:16]} stdout={stdout_digest[:16]}{note}",
            "stdout_digest": stdout_digest, "state_digest": state_digest}


# --- P0-2/P2: distinct identities; value vs claim-bound evaluation -----------
def identities(cls, payload, res, verifier):
    """
      claim_id        predicate + params
      plan_id         claim + verifier
      dependency_id   the world bytes read (freshness lives here; NOT an address)
      result_value_id canonical result, class-local (both normal forms / measured
                      value / post-state digest) — a pure result identity
      evaluation_id   claim-bound: H(claim, plan, dependency, value, verdict) —
                      the address the author pins; uniform across classes.
    """
    claim_id = _h("emb.claim.v0", cls, payload)
    plan_id = _h("emb.plan.v0", claim_id, verifier or "")
    dep = res.get("dep")
    dependency_id = dep["sha256"] if dep else None
    checks = res.get("ski_checks")
    extra = {}
    if checks and len(checks) >= 2:
        lhs, rhs = checks[0]["expect"], checks[1]["expect"]
        result_value_id = _h("emb.resultvalue.v0", "arith", lhs, rhs)
        extra = {"lhs_nf": lhs, "rhs_nf": rhs}
    elif cls == "effect" and res.get("state_digest"):
        result_value_id = _h("emb.resultvalue.v0", "effect", res["state_digest"])
    else:
        result_value_id = _h("emb.resultvalue.v0", "generic",
                             dependency_id or "", res.get("detail", ""))
    evaluation_id = _h("emb.eval.v0", claim_id, plan_id, dependency_id or "",
                       result_value_id, res.get("verdict", ""))
    return ({"claim_id": claim_id, "plan_id": plan_id,
             "dependency_id": dependency_id,
             "result_value_id": result_value_id,
             "evaluation_id": evaluation_id}, extra)


ALLOWED_BINDING_STATUS = {"ASSERTED"}   # raw capsule may only assert (P1-4)


def verify_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    cm = CLAIM_RE.search(text)
    if not cm:
        return {"error": "no inline ⟦class: payload⟧ claim found"}
    cls, payload = cm.group(1), cm.group(2).strip()
    capm = CAPSULE.search(text)
    capsule = json.loads(capm.group(1)) if capm else {}

    if cls == "effect":
        res = settle_effect(payload)               # no settle_gate, no Sigma
    else:
        import settle_gate as gate                 # lazy: only non-effect pulls the engine
        res = gate.settle(cls, payload, {})
    layer = res.get("layer")
    verifier = verifier_id(layer)
    ident, extra = identities(cls, payload, res, verifier)

    # --- P1-4: independent facts, computed unconditionally, hidden by nothing --
    facts, notes = [], []
    pin = capsule.get("verifier")
    if not pin:
        facts.append("VERIFIER_MISSING")
        notes.append("no verifier pinned by author; replay credit refused (D3)")
    elif pin != verifier:
        facts.append("VERIFIER_MISMATCH")
        notes.append(f"asserted verifier {_short(pin)} ≠ actual {_short(verifier)}")

    v = res["verdict"]
    facts.append({"PASS": "RESULT_MATCH", "REFUTED": "RESULT_MISMATCH"}
                 .get(v, "RESULT_UNSETTLED"))
    if v not in ("PASS", "REFUTED"):
        notes.append(f"not executed: {res.get('detail')}")

    # --- P0 (rev 3): world classes REQUIRE an exact path+digest dependency pin --
    if cls in WORLD_CLASSES:
        cap_dep = capsule.get("dep")
        actual_path = (res.get("dep") or {}).get("path")
        if not cap_dep:
            facts.append("DEPENDENCY_MISSING")
            notes.append("world claim without a pinned dependency; replay credit refused")
        else:
            if actual_path and cap_dep.get("path") != actual_path:
                facts.append("DEPENDENCY_PATH_MISMATCH")
                notes.append(f"pinned dependency path {cap_dep.get('path')} ≠ "
                             f"path actually read {actual_path}")
            if ident["dependency_id"] and cap_dep.get("sha256") != ident["dependency_id"]:
                facts.append("DEPENDENCY_STALE")
                notes.append(f"dependency {cap_dep.get('path')} changed since pin "
                             f"({str(cap_dep.get('sha256'))[:12]} → "
                             f"{ident['dependency_id'][:12]})")

    cap_eid = capsule.get("evaluation_id")
    if cap_eid and cap_eid != ident["evaluation_id"]:
        facts.append("ADDRESS_MISMATCH")
        notes.append(f"asserted evaluation_id does not reproduce: pinned "
                     f"{cap_eid[:16]}…, recomputed {ident['evaluation_id'][:16]}…")

    # summary over the facts, fail-closed, highest severity first
    verifier_bad = {"VERIFIER_MISSING", "VERIFIER_MISMATCH"} & set(facts)
    dep_hard = {"DEPENDENCY_MISSING", "DEPENDENCY_PATH_MISMATCH"} & set(facts)
    if verifier_bad or dep_hard:
        execution = "UNVERIFIED"
    elif "RESULT_UNSETTLED" in facts:
        execution = "DECLARED"
    elif "DEPENDENCY_STALE" in facts:
        execution = "STALE"
    elif "RESULT_MISMATCH" in facts or "ADDRESS_MISMATCH" in facts:
        execution = "MISMATCH"
    else:
        execution = "REPLAYED"

    # --- P1-4: binding is a separate axis; raw capsule may only ASSERT ---------
    binding_axis = "UNTIED"
    binding = capsule.get("binding")
    if binding:
        want = binding.get("status", "ASSERTED")
        if want in ALLOWED_BINDING_STATUS:
            binding_axis = want
        else:
            binding_axis = "ASSERTED"
            notes.append(f"binding.status={want!r} clamped to ASSERTED; "
                         f"REVIEWED/CONTESTED require a separate review record")
        notes.append(f"binding relation={binding.get('relation')} is "
                     f"{binding_axis}; NOT established by execution")

    if cls == "effect" and res.get("detail"):
        notes.append(res["detail"])

    body = {
        "claim": {"class": cls, "payload": payload},
        "execution": execution,
        "execution_facts": sorted(facts),
        "binding": binding_axis,
        "verifier": verifier,
        "identity": ident,
        "normal_forms": extra or None,
        "atp": res.get("atp"),
        "layer": layer,
        "notes": notes,
    }
    body["commitment"] = commit(body)
    return body


def commit(body):
    """Self-commitment over the report body (P1-3): sha256 of the canonical body
    with `commitment` excluded. Not yet a receipt — no replay-verifier — but field
    mutation is now detectable."""
    core = {k: v for k, v in body.items() if k != "commitment"}
    return "sha256:" + hashlib.sha256(
        json.dumps(core, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode()).hexdigest()


def render(report):
    if "error" in report:
        return "✗ " + report["error"]
    c = report["claim"]
    i = report["identity"]
    lines = [f"⟦{c['class']}: {c['payload']}⟧",
             f"  execution : {report['execution']}   facts={report['execution_facts']}",
             f"  binding   : {report['binding']}",
             f"  verifier  : {_short(report['verifier'])}",
             f"  claim_id       : {i['claim_id'][:16]}",
             f"  result_value_id: {i['result_value_id'][:16]}",
             f"  evaluation_id  : {i['evaluation_id'][:16]}",
             f"  dependency_id  : {(i['dependency_id'] or '—')[:16]}"]
    if report.get("normal_forms"):
        nf = report["normal_forms"]
        lines.append(f"  normal_forms   : lhs={nf['lhs_nf'][:12]} rhs={nf['rhs_nf'][:12]}")
    for n in report["notes"]:
        lines.append(f"  · {n}")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <fixture.md>", file=sys.stderr)
        return 2
    report = verify_file(sys.argv[1])
    print(render(report))
    print("REPORT " + json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
