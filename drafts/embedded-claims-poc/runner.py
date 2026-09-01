#!/usr/bin/env python3
"""
runner.py — embedded-claims PoC, phase 2 step 3d: the verifier / runner.

The last layer, across the epistemic membrane:

    document → PARSE → COMPILE  ──membrane──  EXECUTE → vector REPORT

It consumes a COMPILED bundle and NOTHING else — it never reads Markdown. For each
record it first re-derives every id and link from `capsule.body` (the single source of
truth) and refuses the WHOLE bundle on any mismatch BEFORE the evaluator is ever
invoked; then it settles each contained claim and returns a per-record two-axis result.

Frozen boundary (operator + Codex):
  - accepts only `status == COMPILED`; anything else is a whole-bundle refusal;
  - re-verifies all ids/links; a mutation ⇒ typed refusal, evaluator invocations = 0;
  - reads no Markdown — the serialized bundle is sufficient;
  - one result PER record; the document gets NO global MATCH — the REPORT is a vector;
  - execution never raises `binding` above `ASSERTED`;
  - the REPORT preserves parser_id, compiler_id, runner_id, the per-record verifier
    identity, and every operand id.

It settles nothing itself: settlement reuses the same engine as the legacy PoC
(settle_core / settle_gate / the Σ-GLYPH evaluator). `COMPILED` did not mean `REPLAYED`;
this is where replay actually happens, per record, and only after the bundle verifies.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "tools"))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import canonical      # noqa: E402
import compiler       # noqa: E402  (id scheme authority: record_id + _did + domains)
import settle_core as sc  # noqa: E402  (verifier_id, WORLD_CLASSES, settle_effect)

RUNNER = [os.path.abspath(__file__), os.path.join(HERE, "canonical.py"),
          os.path.join(HERE, "compiler.py")]


def runner_id():
    """Orchestration identity (runner + id authority), path-independent. The engine
    that actually decides each verdict is bound separately, per record, by the verifier
    identity in the result."""
    digs = sorted(hashlib.sha256(open(p, "rb").read()).digest() for p in RUNNER)
    m = hashlib.sha256()
    for d in digs:
        m.update(d)
    return "runner://sha256:" + m.hexdigest()


def _reverify(rec):
    """Re-derive every id/link from capsule.body + occurrence; return the list of
    fields that do not reproduce (empty means intact)."""
    bad = []
    cap = rec.get("capsule") or {}
    cb = cap.get("body")
    if not isinstance(cb, dict) or "claim" not in cb:
        return ["capsule.body"]
    if cap.get("id") != compiler._did(compiler.CAPSULE_DOMAIN, cb):
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
    if "binding" in cb:
        bbody = {"claim": claim_id, **cb["binding"]}
        exp_b = {"id": canonical.record_id("binding", bbody), "body": bbody}
    else:
        exp_b = None
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
    """Settle one verified record. INVOKES the evaluator. Two independent axes."""
    cb = rec["capsule"]["body"]
    cls, payload = cb["claim"]["class"], cb["claim"]["payload"]
    if cls == "effect":
        res = sc.settle_effect(payload)
    else:
        import settle_gate as gate
        res = gate.settle(cls, payload, {})
    layer = res.get("layer")
    verifier = sc.verifier_id(layer)

    facts = []
    pinned = rec["plan"]["body"].get("verifier")
    if not pinned:
        facts.append("VERIFIER_MISSING")
    elif pinned != verifier:
        facts.append("VERIFIER_MISMATCH")
    v = res["verdict"]
    facts.append({"PASS": "RESULT_MATCH", "REFUTED": "RESULT_MISMATCH"}
                 .get(v, "RESULT_UNSETTLED"))
    if cls in sc.WORLD_CLASSES:
        dep = rec.get("dependency")
        actual = res.get("dep") or {}
        if not dep:
            facts.append("DEPENDENCY_MISSING")
        else:
            if actual.get("path") and dep["body"].get("path") != actual.get("path"):
                facts.append("DEPENDENCY_PATH_MISMATCH")
            if actual.get("sha256") and dep["body"].get("sha256") != actual.get("sha256"):
                facts.append("DEPENDENCY_STALE")

    binding_axis = "ASSERTED" if rec.get("binding") else "UNTIED"   # never raised
    return {
        "local_id": rec["local_id"],
        "class": cls, "payload": payload,
        "execution": _summary(facts), "execution_facts": sorted(facts),
        "binding": binding_axis,
        "verifier": verifier, "layer": layer, "atp": res.get("atp"),
        "claim_id": rec["claim"]["id"], "plan_id": rec["plan"]["id"],
        "dependency_id": rec["dependency"]["id"] if rec.get("dependency") else None,
        "binding_id": rec["binding"]["id"] if rec.get("binding") else None,
        "capsule_id": rec["capsule"]["id"], "occurrence_id": rec["occurrence_id"],
        "occurrence": rec["occurrence"],
    }


def run(compile_report):
    """COMPILED bundle → vector REPORT. No Markdown. No document-level MATCH."""
    base = {"runner": runner_id(),
            "parser_id": compile_report.get("parser_id"),
            "compiler_id": compile_report.get("compiler"),
            "evaluator_invocations": 0, "results": []}
    if compile_report.get("status") != "COMPILED":
        return {**base, "status": "REFUSED", "reason": "NOT_COMPILED",
                "detail": f"compile status {compile_report.get('status')!r} != COMPILED"}
    # pass 1: re-verify EVERY record before any evaluator call
    for rec in compile_report.get("records", []):
        bad = _reverify(rec)
        if bad:
            return {**base, "status": "REFUSED", "reason": "BUNDLE_TAMPERED",
                    "detail": {"local_id": rec.get("local_id"), "fields": bad}}
    # pass 2: settle each (this is the only place the evaluator runs)
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
