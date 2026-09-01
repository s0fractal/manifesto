#!/usr/bin/env python3
"""
settle_core.py — embedded-claims PoC: the verdict-determining core.

Everything whose bytes can change a REPORTED verdict, parse, or identity lives
here, so it can be bound into the verifier closure: claim/capsule selection, the
closed-schema gate, settlement dispatch, identities, facts→execution, and the body
commitment. The CLI and the human renderer live in verify.py and are deliberately
OUT of the closure — editing a docstring or a print must not rotate a verifier id.

Closure (Codex P0): the per-class verifier identity digests THIS module plus
canonical.py and schema.py (both change parse/execution) plus, for non-effect
classes, the engine bootstrap and the evaluator. The effect path imports neither
settle_gate nor Sigma, so its closure is core+canonical+schema alone.
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
sys.path.insert(0, HERE)
from sigma_boundary import sigma    # noqa: E402  (import is safe; sigma() resolves lazily)
import canonical                     # noqa: E402
import schema                        # noqa: E402
# settle_gate is imported LAZILY (non-effect only): importing it pulls glyphlib,
# whose module-level sigma() would resolve the evaluator for EVERY class.

CAPSULE = re.compile(r"```json capsule\s*\n(.*?)\n```", re.S)
CLAIM_RE = re.compile(r"⟦([a-z0-9_]+):\s*([^⟧]+)⟧")   # == settle_gate.CLAIM, kept local
GLYPHLIB = os.path.join(TOOLS, "glyphlib.py")
SETTLE_GATE = os.path.join(TOOLS, "settle_gate.py")
SIGMA_BOUNDARY = os.path.join(TOOLS, "sigma_boundary.py")
CANONICAL = os.path.join(HERE, "canonical.py")
SCHEMA = os.path.join(HERE, "schema.py")
SETTLE_CORE = os.path.abspath(__file__)
WORLD_CLASSES = {"count", "sha256", "cite", "citei"}   # read repository bytes
ALLOWED_BINDING_STATUS = {"ASSERTED"}                  # raw capsule may only assert (P1-4)

# The verdict-determining code shared by every class. canonical.py and schema.py
# are here because they change parse and execution (Codex P0).
CORE_FILES = [SETTLE_CORE, CANONICAL, SCHEMA]


def _h(domain, *parts):
    m = hashlib.sha256()
    m.update(domain.encode() + b"\0")
    for p in parts:
        m.update(str(p).encode("utf-8") + b"\0")
    return m.hexdigest()


def _closure_digest(paths):
    """Digest over the SET of file contents — ordered by content digest, never by
    path, so the same code at a different location yields the same id."""
    digs = sorted(hashlib.sha256(open(p, "rb").read()).digest() for p in paths)
    m = hashlib.sha256()
    for d in digs:
        m.update(d)
    return m.hexdigest()


def verifier_id(layer):
    if layer == "effect-sandbox":
        # imports neither settle_gate nor the evaluator; closure is core alone.
        return "effect-sandbox://sha256:" + _closure_digest(CORE_FILES)
    if layer is None:
        return None
    # non-effect classes settle through settle_gate; bind the whole bootstrap and
    # the evaluator. sigma() is resolved only here, never on the effect path.
    files = CORE_FILES + [SETTLE_GATE, GLYPHLIB, SIGMA_BOUNDARY, sigma().__file__]
    scheme = "glyph" if layer == "sigma-glyph" else "settle-gate"
    return f"{scheme}://sha256:" + _closure_digest(files)


def _short(vid):
    if not vid:
        return "—"
    scheme, _, digest = vid.partition("://sha256:")
    return f"{scheme}://sha256:{digest[:12]}"


# --- P1-5: effects are OBSERVED post-state, not enforced --------------------
def _op_echo_only(sandbox):
    return b"hello\n"


def _op_echo_and_touch(sandbox):
    with open(os.path.join(sandbox, "marker"), "wb") as f:
        f.write(b"x")
    return b"hello\n"


def _op_echo_then_delete(sandbox):
    p = os.path.join(sandbox, "transient")
    with open(p, "wb") as f:
        f.write(b"x")
    os.remove(p)
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
            "observed_value": {"kind": "post-state", "state": state_digest,
                               "stdout": stdout_digest},
            "detail": f"state={state_digest[:16]} stdout={stdout_digest[:16]}{note}",
            "stdout_digest": stdout_digest, "state_digest": state_digest}


# --- P0-2/P2: distinct identities; value vs claim-bound evaluation -----------
def identities(cls, payload, res, verifier):
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


def _parse_capsule(text):
    """Return (capsule, errors). Any malformed input — bad JSON, duplicate keys,
    a value outside the closed scalar profile, or a shape the closed schema
    rejects — yields ({}, [reasons]) and never raises (Codex P1: fail closed)."""
    capm = CAPSULE.search(text)
    if not capm:
        return {}, []
    try:
        parsed = canonical.loads_strict(capm.group(1))   # dup keys + scalar profile
    except (canonical.CanonicalError, json.JSONDecodeError, UnicodeError) as e:
        return {}, [str(e)]
    errors = schema.validate_capsule(parsed)             # closed schema
    return (parsed, []) if not errors else ({}, errors)


def verify_report(text):
    """The verdict logic over a fixture's text. Returns the report body dict."""
    cm = CLAIM_RE.search(text)
    if not cm:
        return {"error": "no inline ⟦class: payload⟧ claim found"}
    cls, payload = cm.group(1), cm.group(2).strip()
    capsule, capsule_errors = _parse_capsule(text)

    if cls == "effect":
        res = settle_effect(payload)               # no settle_gate, no Sigma
    else:
        import settle_gate as gate                 # lazy: only non-effect pulls the engine
        res = gate.settle(cls, payload, {})
    layer = res.get("layer")
    verifier = verifier_id(layer)
    ident, extra = identities(cls, payload, res, verifier)

    facts, notes = [], []
    if capsule_errors:
        facts.append("CAPSULE_INVALID")
        for e in capsule_errors:
            notes.append("capsule: " + e)
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

    verifier_bad = {"VERIFIER_MISSING", "VERIFIER_MISMATCH"} & set(facts)
    dep_hard = {"DEPENDENCY_MISSING", "DEPENDENCY_PATH_MISMATCH"} & set(facts)
    if verifier_bad or dep_hard or "CAPSULE_INVALID" in facts:
        execution = "UNVERIFIED"
    elif "RESULT_UNSETTLED" in facts:
        execution = "DECLARED"
    elif "DEPENDENCY_STALE" in facts:
        execution = "STALE"
    elif "RESULT_MISMATCH" in facts or "ADDRESS_MISMATCH" in facts:
        execution = "MISMATCH"
    else:
        execution = "REPLAYED"

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
    with `commitment` excluded. Not yet a receipt — no replay-verifier."""
    core = {k: v for k, v in body.items() if k != "commitment"}
    return "sha256:" + hashlib.sha256(canonical.canonicalize(core)).hexdigest()
