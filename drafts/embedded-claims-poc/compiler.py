#!/usr/bin/env python3
"""
compiler.py — embedded-claims PoC, phase 2 step 3c: the COMPILE layer.

Boundary (Codex): STRUCTURAL only. `VALID ParseReport → strict JSON → capsule.v2 →
canonical records/IDs`. It does NOT settle anything and NEVER runs the evaluator —
`COMPILED` must not come to mean `REPLAYED`. Settlement + the two-axis REPORT are the
3d verifier/runner.

Precondition (the mandatory negative): a ParseReport whose `status != VALID` is
REFUSED as a whole. Even if the parser diagnostically carried a candidate capsule
under an INVALID/INERT status, the compiler compiles NOTHING from it.

Per VALID report it, for each extracted capsule:
  - strict-parses the raw body under the closed scalar profile (canonical.loads_strict);
  - validates the closed capsule.v2 schema (the capsule CONTAINS its claim — no
    inline glyph, no claim_ref: association is containment);
  - derives content-addressed records — claim_id, plan_id, dependency_id, binding_id,
    capsule_id — via the pinned canonicalization/hash profile, plus the source
    occurrence (byte span) the parser committed.

Any capsule that fails strict-JSON / schema / duplicate-local_id makes the whole
compile INVALID (records kept for diagnostics only; the 3d precondition is
`status == COMPILED`).

stdlib-only (canonical.py is stdlib): the compile layer needs no package.
"""
import hashlib
import json
import os
import re

import canonical

HERE = os.path.dirname(os.path.abspath(__file__))
CANONICAL = os.path.join(HERE, "canonical.py")

SCHEMA_VERSION = "manifesto.capsule.v2"
KNOWN_CLASSES = {"arith", "cmp", "count", "sha256", "cite", "citei", "mono",
                 "bindarith", "effect"}
LOCAL_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERIFIER = re.compile(r"^(glyph|settle-gate|effect-sandbox)://sha256:[0-9a-f]{64}$")
BINDING_RELATIONS = {"supports", "refutes", "defines", "instantiates", "measures"}
BINDING_STATUS = {"ASSERTED"}   # a raw capsule may only assert (P1-4)


def compiler_id():
    """Structural identity of the compile layer: compiler.py + canonical.py, by
    content (path-independent). No evaluator, no markdown — the compiler settles
    nothing, so its closure is small and stdlib-only."""
    m = hashlib.sha256()
    for p in sorted((os.path.abspath(__file__), CANONICAL)):
        with open(p, "rb") as f:
            m.update(hashlib.sha256(f.read()).digest())
    return "compiler://sha256:" + m.hexdigest()


def _closed(errors, val, where, allowed, required):
    if not isinstance(val, dict):
        errors.append(f"{where} must be an object")
        return False
    for k in val:
        if k not in allowed:
            errors.append(f"unknown field {where}.{k}")
    for r in required:
        if r not in val:
            errors.append(f"missing required field {where}.{r}")
    return True


def validate_v2(cap):
    """Closed schema for a capsule.v2 body. Returns a list of typed error strings."""
    errors = []
    if not _closed(errors, cap, "capsule",
                   allowed={"schema_version", "claim", "verifier", "dep", "binding"},
                   required=("schema_version", "claim")):
        return errors
    if cap.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"capsule.schema_version must be {SCHEMA_VERSION!r}")
    if "claim" in cap and _closed(errors, cap["claim"], "capsule.claim",
                                  allowed={"local_id", "class", "payload"},
                                  required=("local_id", "class", "payload")):
        cl = cap["claim"]
        if not (isinstance(cl.get("local_id"), str) and LOCAL_ID.match(cl["local_id"])):
            errors.append("capsule.claim.local_id must match [A-Za-z0-9_-]{1,64}")
        if cl.get("class") not in KNOWN_CLASSES:
            errors.append(f"capsule.claim.class must be one of {sorted(KNOWN_CLASSES)}")
        if not (isinstance(cl.get("payload"), str) and cl["payload"]):
            errors.append("capsule.claim.payload must be a non-empty string")
    if "verifier" in cap and not (isinstance(cap["verifier"], str)
                                  and VERIFIER.match(cap["verifier"])):
        errors.append("capsule.verifier must be '<scheme>://sha256:<64hex>'")
    if "dep" in cap and _closed(errors, cap["dep"], "capsule.dep",
                                allowed={"path", "sha256"}, required=("path", "sha256")):
        d = cap["dep"]
        if "path" in d and (not isinstance(d["path"], str) or not d["path"]):
            errors.append("capsule.dep.path must be a non-empty string")
        if "sha256" in d and not (isinstance(d["sha256"], str) and HEX64.match(d["sha256"])):
            errors.append("capsule.dep.sha256 must be 64 lowercase hex")
    if "binding" in cap and _closed(errors, cap["binding"], "capsule.binding",
                                    allowed={"relation", "target", "status"},
                                    required=("relation", "target")):
        b = cap["binding"]
        if not isinstance(b.get("relation"), str) or b["relation"] not in BINDING_RELATIONS:
            errors.append(f"capsule.binding.relation must be one of {sorted(BINDING_RELATIONS)}")
        if not isinstance(b.get("target"), str) or not b["target"]:
            errors.append("capsule.binding.target must be a non-empty string")
        if "status" in b and (not isinstance(b["status"], str) or b["status"] not in BINDING_STATUS):
            errors.append("capsule.binding.status must be 'ASSERTED' (a raw capsule only asserts)")
    return errors


def _capsule_id(body):
    return "sha256:" + hashlib.sha256(canonical.canonicalize(body)).hexdigest()


def compile_report(parse_report, source_bytes=None):
    """Compile a ParseReport into canonical records. STRUCTURAL only — no settlement."""
    if parse_report.get("status") != "VALID":
        return {"compiler": compiler_id(), "status": "REFUSED",
                "parser_status": parse_report.get("status"), "records": [],
                "errors": [{"code": "PRECONDITION_NOT_VALID", "line": 0,
                            "detail": f"parser status {parse_report.get('status')!r} "
                                      f"!= VALID; whole report refused"}]}

    records, errors, seen = [], [], set()
    for cap in parse_report.get("capsules", []):
        line = cap.get("line")
        try:
            body = canonical.loads_strict(cap["body_raw"])
        except (canonical.CanonicalError, json.JSONDecodeError, UnicodeError) as e:
            errors.append({"code": "CAPSULE_NOT_STRICT_JSON", "line": line, "detail": str(e)})
            continue
        verrs = validate_v2(body)
        if verrs:
            errors.append({"code": "CAPSULE_SCHEMA_INVALID", "line": line, "detail": verrs})
            continue
        claim = body["claim"]
        lid = claim["local_id"]
        if lid in seen:
            errors.append({"code": "DUPLICATE_LOCAL_ID", "line": line, "detail": lid})
            continue
        seen.add(lid)
        claim_id = canonical.record_id("claim", {"class": claim["class"],
                                                 "payload": claim["payload"]})
        plan_id = canonical.record_id("plan", {"claim": claim_id,
                                               "verifier": body.get("verifier")})
        dep_id = (canonical.record_id("dependency", body["dep"]) if "dep" in body else None)
        binding_id = (canonical.record_id("binding", body["binding"])
                      if "binding" in body else None)
        records.append({
            "local_id": lid, "class": claim["class"], "payload": claim["payload"],
            "capsule_id": _capsule_id(body),
            "claim_id": claim_id, "plan_id": plan_id,
            "dependency_id": dep_id, "binding_id": binding_id,
            "occurrence": {"span": cap.get("span"), "region": cap.get("region")},
        })

    # Fail-closed as a whole: records are handed forward ONLY from a COMPILED report.
    # If any capsule failed, the document is INVALID and emits no records (the errors
    # remain for diagnostics). The 3d runner consumes records only when status==COMPILED.
    status = "COMPILED" if not errors else "INVALID"
    return {"compiler": compiler_id(), "status": status, "parser_status": "VALID",
            "records": records if status == "COMPILED" else [], "errors": errors}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    import parser as P
    if len(sys.argv) != 2:
        print("usage: compiler.py <file.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "rb") as f:
        pr = P.parse(f.read().decode("utf-8"))
    rep = compile_report(pr, None)
    print(f"parser={pr['status']} compile={rep['status']} "
          f"records={len(rep['records'])} "
          f"errors={sorted({e['code'] for e in rep['errors']})}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
