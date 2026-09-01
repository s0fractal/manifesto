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


def _did(domain, body):
    """Domain-separated content id for compiler-owned aggregate records (capsule,
    occurrence), matching canonical.record_id's HASH(domain || 0x00 || canonical)."""
    return "sha256:" + hashlib.sha256(
        domain.encode() + b"\x00" + canonical.canonicalize(body)).hexdigest()


CAPSULE_DOMAIN = "manifesto.capsule.v2"
OCCURRENCE_DOMAIN = "manifesto.occurrence.v0"


def compile_report(parse_report, source_bytes):
    """Compile a VALID ParseReport into a SELF-CONTAINED bundle of canonical records —
    each entity as `{id, body}`, so the 3d runner can select the verifier, resolve the
    dependency, and form the binding axis WITHOUT reparsing the source Markdown.
    STRUCTURAL only — no settlement. `source_bytes` anchors every occurrence to a
    document digest (a byte span alone is not a source address)."""
    parser_id = parse_report.get("parser")
    if parse_report.get("status") != "VALID":
        return {"compiler": compiler_id(), "parser_id": parser_id, "status": "REFUSED",
                "parser_status": parse_report.get("status"), "records": [],
                "errors": [{"code": "PRECONDITION_NOT_VALID", "line": 0,
                            "detail": f"parser status {parse_report.get('status')!r} "
                                      f"!= VALID; whole report refused"}]}

    document = "sha256:" + hashlib.sha256(source_bytes).hexdigest()
    records, errors, seen = [], [], set()
    for cap in parse_report.get("capsules", []):
        line = cap.get("line")
        span = cap.get("span")
        # P0: the occurrence must actually address the capsule bytes in the source.
        # A mutated ParseReport (new body_raw, old span) is caught here — a byte span
        # alone is not a source address; it must slice back to exactly body_raw.
        if not (isinstance(span, list) and len(span) == 2
                and all(isinstance(x, int) for x in span)
                and 0 <= span[0] <= span[1] <= len(source_bytes)
                and source_bytes[span[0]:span[1]] == cap.get("body_raw", "").encode("utf-8")):
            errors.append({"code": "SOURCE_OCCURRENCE_MISMATCH", "line": line,
                           "detail": "capsule body_raw does not equal source_bytes[span]"})
            continue
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

        claim_body = {"class": claim["class"], "payload": claim["payload"]}
        claim_id = canonical.record_id("claim", claim_body)
        dep_body = body.get("dep")
        dep_id = (canonical.record_id("dependency", dep_body) if dep_body is not None else None)
        dep_rec = {"id": dep_id, "body": dep_body} if dep_body is not None else None
        # P0: a VerificationPlan names its inputs — bind the dependency into plan_id, so
        # changing the dependency rotates the plan identity ("this verifier over these
        # inputs"), null when absent.
        plan_body = {"claim": claim_id, "verifier": body.get("verifier"),
                     "dependency": dep_id}
        plan_id = canonical.record_id("plan", plan_body)
        binding_rec = None
        if "binding" in body:
            # P0: bind the binding to its claim, so an identical relation/target/status
            # on a DIFFERENT claim cannot share a binding_id (composition laundering).
            binding_body = {"claim": claim_id, **body["binding"]}
            binding_rec = {"id": canonical.record_id("binding", binding_body),
                           "body": binding_body}
        occurrence = {"document": document, "span": cap.get("span"),
                      "region": cap.get("region")}

        records.append({
            "local_id": lid,
            # capsule.body is the single source of truth: the runner re-derives every
            # id/link from it, so a mutation of any field is caught before execution.
            "capsule": {"id": _did(CAPSULE_DOMAIN, body), "body": body},
            "occurrence_id": _did(OCCURRENCE_DOMAIN, occurrence),
            "occurrence": occurrence,
            "claim": {"id": claim_id, "body": claim_body},
            "plan": {"id": plan_id, "body": plan_body},
            "dependency": dep_rec,
            "binding": binding_rec,
        })

    # Fail-closed as a whole: records are handed forward ONLY from a COMPILED report.
    status = "COMPILED" if not errors else "INVALID"
    return {"compiler": compiler_id(), "parser_id": parser_id, "status": status,
            "parser_status": "VALID",
            "records": records if status == "COMPILED" else [], "errors": errors}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    import parser as P
    if len(sys.argv) != 2:
        print("usage: compiler.py <file.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "rb") as f:
        src = f.read()
    pr = P.parse(src.decode("utf-8"))
    rep = compile_report(pr, src)
    print(f"parser={pr['status']} compile={rep['status']} "
          f"records={len(rep['records'])} "
          f"errors={sorted({e['code'] for e in rep['errors']})}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
