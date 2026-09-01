#!/usr/bin/env python3
"""
runner.py — embedded-claims PoC, phase 2 step 3d/3d.1: the verifier / runner.

    document → PARSE → COMPILE  ──epistemic membrane──  EXECUTE → vector REPORT

Consumes a COMPILED bundle and NOTHING else (reads no Markdown). Before any evaluator
call it VALIDATES the bundle (closed capsule.v2 schema, local_id linkage + uniqueness,
actual compiler identity, exception-safe on malformed structures) and RE-DERIVES every
id/link from `capsule.body`; any failure refuses the whole bundle with the evaluator
invocation count still 0. Then it settles each claim and returns one result per record —
the document gets NO global MATCH; the REPORT is a vector (§13.11: local greenness is
non-transitive). Execution never raises `binding` above `ASSERTED`.

Honest limit (Codex): content-addressing catches an INCOHERENT mutation — an id that no
longer matches its body, a broken link, an invalid shape. A FULLY recomputed, schema-valid
bundle is a NEW bundle, not a detectable tamper; distinguishing it from the historical
original needs an external commitment / signature / receipt, which this layer does NOT
claim. That is the next, separate boundary.

3d.1 REPORT: each result addresses the ACTUAL operands and output —
declared_dependency vs observed_dependency (the bytes the evaluator really read),
result_value {id, body} (normal forms / post-state / measured), and a claim-bound
evaluation {id, body}. UNSETTLED gets no invented result_value.

Settlement reuses the same engine as the legacy PoC (settle_core / settle_gate / Σ-GLYPH).
COMPILED did not mean REPLAYED; replay happens here, per record, only after the bundle
verifies.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "tools"))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import canonical      # noqa: E402
import compiler       # noqa: E402
import settle_core as sc  # noqa: E402

RUNNER = [os.path.abspath(__file__), os.path.join(HERE, "canonical.py"),
          os.path.join(HERE, "compiler.py")]
RESULT_VALUE_DOMAIN = "manifesto.result-value.v0"
EVALUATION_DOMAIN = "manifesto.evaluation.v0"


def runner_id():
    digs = sorted(hashlib.sha256(open(p, "rb").read()).digest() for p in RUNNER)
    m = hashlib.sha256()
    for d in digs:
        m.update(d)
    return "runner://sha256:" + m.hexdigest()


def validate_bundle(cr):
    """Closed, exception-safe structural validation BEFORE any id recompute or evaluator
    call. Returns a list of typed errors (empty = ok). Catches the mutations content
    addressing alone misses: unknown capsule fields (schema), a local_id changed out of
    its claim (linkage), a swapped compiler identity, and malformed nested structures."""
    errors = []
    if cr.get("compiler") != compiler.compiler_id():
        errors.append({"code": "COMPILER_IDENTITY_MISMATCH"})
    seen = set()
    for i, rec in enumerate(cr.get("records", [])):
        if not isinstance(rec, dict):
            errors.append({"code": "MALFORMED_RECORD", "index": i}); continue
        cap = rec.get("capsule")
        if not isinstance(cap, dict) or not isinstance(cap.get("body"), dict):
            errors.append({"code": "MALFORMED_CAPSULE", "index": i}); continue
        cb = cap["body"]
        v = compiler.validate_v2(cb)          # closed capsule.v2 schema
        if v:
            errors.append({"code": "CAPSULE_SCHEMA_INVALID", "index": i, "detail": v}); continue
        lid = rec.get("local_id")
        if lid != cb.get("claim", {}).get("local_id"):
            errors.append({"code": "LOCAL_ID_LINKAGE", "index": i})
        if lid in seen:
            errors.append({"code": "DUPLICATE_LOCAL_ID", "index": i})
        seen.add(lid)
    return errors


def _reverify(rec):
    """Re-derive every id/link from capsule.body + occurrence; list what does not match."""
    bad = []
    cb = rec["capsule"]["body"]
    if rec["capsule"].get("id") != compiler._did(compiler.CAPSULE_DOMAIN, cb):
        bad.append("capsule.id")
    claim = cb["claim"]
    claim_body = {"class": claim.get("class"), "payload": claim.get("payload")}
    claim_id = canonical.record_id("claim", claim_body)
    if rec.get("claim") != {"id": claim_id, "body": claim_body}:
        bad.append("claim")
    dep_body = cb.get("dep")
    dep_id = canonical.record_id("dependency", dep_body) if dep_body is not None else None
    exp_dep = {"id": dep_id, "body": dep_body} if dep_body is not None else None
    if rec.get("dependency") != exp_dep:
        bad.append("dependency")
    plan_body = {"claim": claim_id, "verifier": cb.get("verifier"), "dependency": dep_id}
    if rec.get("plan") != {"id": canonical.record_id("plan", plan_body), "body": plan_body}:
        bad.append("plan")
    exp_b = None
    if "binding" in cb:
        bbody = {"claim": claim_id, **cb["binding"]}
        exp_b = {"id": canonical.record_id("binding", bbody), "body": bbody}
    if rec.get("binding") != exp_b:
        bad.append("binding")
    if rec.get("occurrence_id") != compiler._did(compiler.OCCURRENCE_DOMAIN,
                                                 rec.get("occurrence")):
        bad.append("occurrence_id")
    return bad


def _summary(facts):
    fset = set(facts)
    if {"VERIFIER_MISSING", "VERIFIER_MISMATCH"} & fset or \
       {"DEPENDENCY_MISSING", "DEPENDENCY_PATH_MISMATCH"} & fset:
        return "UNVERIFIED"
    if "RESULT_UNSETTLED" in fset:
        return "DECLARED"
    if "DEPENDENCY_STALE" in fset:
        return "STALE"
    if "RESULT_MISMATCH" in fset:
        return "MISMATCH"
    return "REPLAYED"


def _settle_one(rec):
    """Settle one verified record. INVOKES the evaluator. Two axes + addressed operands."""
    cb = rec["capsule"]["body"]
    cls, payload = cb["claim"]["class"], cb["claim"]["payload"]
    if cls == "effect":
        res = sc.settle_effect(payload)
    else:
        import settle_gate as gate
        res = gate.settle(cls, payload, {})
    layer = res.get("layer")
    verifier = sc.verifier_id(layer)
    verdict = res["verdict"]

    facts = []
    pinned = rec["plan"]["body"].get("verifier")
    if not pinned:
        facts.append("VERIFIER_MISSING")
    elif pinned != verifier:
        facts.append("VERIFIER_MISMATCH")
    facts.append({"PASS": "RESULT_MATCH", "REFUTED": "RESULT_MISMATCH"}
                 .get(verdict, "RESULT_UNSETTLED"))

    declared_dependency = rec.get("dependency")
    obs = res.get("dep")                       # the bytes the evaluator ACTUALLY read
    observed_dependency = ({"id": canonical.record_id("dependency", obs), "body": obs}
                           if obs else None)
    if cls in sc.WORLD_CLASSES:
        if not declared_dependency:
            facts.append("DEPENDENCY_MISSING")
        else:
            db = declared_dependency["body"]
            if obs and obs.get("path") and db.get("path") != obs.get("path"):
                facts.append("DEPENDENCY_PATH_MISMATCH")
            if obs and obs.get("sha256") and db.get("sha256") != obs.get("sha256"):
                facts.append("DEPENDENCY_STALE")

    # result value — a stable body only when there is one (no invented id for UNSETTLED)
    result_value, normal_forms = None, None
    checks = res.get("ski_checks")
    if verdict in ("PASS", "REFUTED") and checks and len(checks) >= 2:
        lhs, rhs = checks[0]["expect"], checks[1]["expect"]
        normal_forms = {"lhs": lhs, "rhs": rhs}
        rv = {"kind": "normal-forms", "lhs": lhs, "rhs": rhs}
        result_value = {"id": compiler._did(RESULT_VALUE_DOMAIN, rv), "body": rv}
    elif cls == "effect" and res.get("state_digest"):
        rv = {"kind": "post-state", "state": res["state_digest"],
              "stdout": res.get("stdout_digest")}
        result_value = {"id": compiler._did(RESULT_VALUE_DOMAIN, rv), "body": rv}
    elif verdict in ("PASS", "REFUTED") and cls in sc.WORLD_CLASSES and observed_dependency:
        rv = {"kind": "world", "observed_dependency": observed_dependency["id"],
              "detail": res.get("detail")}
        result_value = {"id": compiler._did(RESULT_VALUE_DOMAIN, rv), "body": rv}

    eval_body = {
        "claim": rec["claim"]["id"], "plan": rec["plan"]["id"],
        "declared_dependency": declared_dependency["id"] if declared_dependency else None,
        "observed_dependency": observed_dependency["id"] if observed_dependency else None,
        "verifier": verifier,
        "result_value": result_value["id"] if result_value else None,
        "verdict": verdict,
    }
    evaluation = {"id": compiler._did(EVALUATION_DOMAIN, eval_body), "body": eval_body}

    return {
        "local_id": rec["local_id"], "class": cls, "payload": payload,
        "execution": _summary(facts), "execution_facts": sorted(facts),
        "binding": "ASSERTED" if rec.get("binding") else "UNTIED",   # never raised
        "verifier": verifier, "layer": layer, "atp": res.get("atp"),
        "claim_id": rec["claim"]["id"], "plan_id": rec["plan"]["id"],
        "binding_id": rec["binding"]["id"] if rec.get("binding") else None,
        "capsule_id": rec["capsule"]["id"], "occurrence_id": rec["occurrence_id"],
        "occurrence": rec["occurrence"],
        "declared_dependency": declared_dependency,
        "observed_dependency": observed_dependency,
        "normal_forms": normal_forms,
        "result_value": result_value,
        "evaluation": evaluation,
    }


def run(compile_report):
    base = {"runner": runner_id(),
            "parser_id": compile_report.get("parser_id"),
            "compiler_id": compile_report.get("compiler"),
            "evaluator_invocations": 0, "results": []}
    if compile_report.get("status") != "COMPILED":
        return {**base, "status": "REFUSED", "reason": "NOT_COMPILED",
                "detail": f"compile status {compile_report.get('status')!r} != COMPILED"}
    try:
        verrs = validate_bundle(compile_report)
        if verrs:
            return {**base, "status": "REFUSED", "reason": "INVALID_BUNDLE", "detail": verrs}
        for rec in compile_report.get("records", []):
            bad = _reverify(rec)
            if bad:
                return {**base, "status": "REFUSED", "reason": "BUNDLE_TAMPERED",
                        "detail": {"local_id": rec.get("local_id"), "fields": bad}}
    except Exception as e:   # malformed structure ⇒ typed refusal, never a crash
        return {**base, "status": "REFUSED", "reason": "MALFORMED_BUNDLE",
                "detail": f"{type(e).__name__}: {e}"}

    results, n = [], 0
    for rec in compile_report.get("records", []):
        results.append(_settle_one(rec))
        n += 1
    return {**base, "status": "RUN", "evaluator_invocations": n, "results": results}


if __name__ == "__main__":
    import json
    import parser as P
    if len(sys.argv) != 2:
        print("usage: runner.py <file.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "rb") as f:
        src = f.read()
    rep = run(compiler.compile_report(P.parse(src.decode("utf-8")), src))
    print(f"status={rep['status']} evaluator_invocations={rep['evaluator_invocations']} "
          f"results={[(r['local_id'], r['execution'], r['binding']) for r in rep['results']]}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
