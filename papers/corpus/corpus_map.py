#!/usr/bin/env python3
"""
corpus_map.py — L2 -> L3. SOURCE-BOUND, ADJUDICATED MAPPING.

The mapper no longer trusts a self-consistent L2: it consumes a committed L2 bundle
that is bound to the extraction's `corpus_commitment` + `event_manifest` (Codex review
9e50479). A coherent invented L2 is refused (UNKNOWN_SOURCE); a hand-minted bundle is
refused (BUNDLE_ID_MISMATCH / BUNDLE_NOT_COMMITTED); post-validation tampering of the
bundle or its bodies is caught before mapping (INDEX_TAMPER).

Credit is content-addressed: an ActRecord {id, body} binds every meaning-bearing field
including the completeness and publication *decisions*, so flipping PARTIAL->COMPLETE or
WITHHELD->CLEARED rotates the record id and the view evaluation id. Only EXACT (adjudicated
to the exact evidence spans, fault-free, decided COMPLETE + CLEARED) satisfies a unit.
DERIVED is a proposal forever.
"""
import base64
from collections import defaultdict
from pathlib import Path

import corpus_ids as ids

REQUIRED_COMPONENTS = ("experiment_id", "root_digest", "verifier_identity", "agent_run_occurrence")
FORBIDDEN_EVIDENCE = {"count", "verdict"}
ALLOWED_UNIT_KEYS = {"root_digest", "verifier_identity", "depth", "agent_run_occurrence", "experiment_id"}
ACTRECORD_REQUIRED = (
    "root_id", "verifier_declared_identity", "verifier_observed_identity",
    "prompt_digest", "response_digest", "offspring_before_dedup",
    "dedup_removal_decisions", "selected_child_refs",
    "sampling", "completeness_decision", "publication_decision",
)
CANDIDATE_FIELDS = set(ACTRECORD_REQUIRED) | {
    "local_ref", "blob_id", "event_occurrences", "experiment_id", "root_digest",
    "verifier_identity", "agent_run_occurrence", "mapping_status", "mapping_evidence",
    "adjudication", "parent_local_ref",
}
MANIFEST_FIELDS = {"claim", "paper_pin", "experiment_ids", "unit_key",
                   "required_units", "allowed_exclusions"}


def _schema_bytes():
    p = Path(__file__).resolve().parent.parent / "every-check-spawns-more" / "CORPUS-SCHEMA-0.1.md"
    return p.read_bytes() if p.exists() else b"MISSING_SCHEMA"


def mapper_closure_id():
    here = Path(__file__).resolve().parent
    return ids.closure_id("map", [
        ("corpus_map.py", (here / "corpus_map.py").read_bytes()),
        ("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
        ("CORPUS-SCHEMA-0.1.md", _schema_bytes()),
    ])


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


# ============================ L2 bundle (source-bound) ============================ #
def mint_l2_bundle(private_l2, report):
    """Bind a validated, committed L2 bundle to THIS extraction. Structural + source
    checks; a fabricated or malformed event is refused, not silently indexed."""
    try:
        expected_closure = report["extraction_closure"]
        commitment = report["corpus_commitment"]
        manifest = {(m["event_id"], m["body_digest"]) for m in report["event_manifest"]}
    except (KeyError, TypeError):
        return {"status": "MALFORMED_REPORT", "bundle_id": None, "commitment": None,
                "expected_closure": None, "events": [], "index": {}, "faults": [{"code": "MALFORMED_REPORT"}]}

    faults, index, canon = [], {}, []
    per_blob = defaultdict(list)
    seen = set()
    for data in (private_l2 or {}).values():
        for ev in data.get("events", []):
            try:
                raw = base64.b64decode(ev["raw_b64"])
                bd = ids.line_digest(raw)
                eid = ids.event_id(ev["extraction_closure"], ev["blob_id"],
                                   int(ev["byte_start"]), int(ev["byte_end"]), bd)
            except (KeyError, TypeError, ValueError, Exception):  # noqa
                faults.append({"code": "MALFORMED_L2_ENTRY"}); continue
            if ev.get("event_id") != eid or bd != ev.get("line_digest"):
                faults.append({"code": "L2_INTEGRITY_BREAK"}); continue
            if ev["extraction_closure"] != expected_closure:
                faults.append({"code": "CLOSURE_MISMATCH"}); continue
            if (int(ev["byte_end"]) - int(ev["byte_start"])) != len(raw) or int(ev["byte_start"]) < 0:
                faults.append({"code": "IMPOSSIBLE_SPAN"}); continue
            if (eid, bd) not in manifest:
                faults.append({"code": "UNKNOWN_SOURCE", "event_id": eid}); continue
            if eid in seen:
                faults.append({"code": "DUPLICATE_L2_EVENT"}); continue
            seen.add(eid)
            index[eid] = {"blob_id": ev["blob_id"], "byte_start": int(ev["byte_start"]),
                          "byte_end": int(ev["byte_end"]), "raw_bytes": raw, "body_digest": bd}
            per_blob[ev["blob_id"]].append(int(ev["event_index"]))
            canon.append({"event_id": eid, "blob_id": ev["blob_id"],
                          "byte_start": int(ev["byte_start"]), "byte_end": int(ev["byte_end"]),
                          "body_digest": bd, "event_index": int(ev["event_index"])})
    for blob, idxs in per_blob.items():
        if sorted(idxs) != list(range(len(idxs))):
            faults.append({"code": "INDEX_GAP", "blob_id": blob})
    canon.sort(key=lambda x: (x["blob_id"], x["event_index"]))
    bundle_id = ids.json_digest({"commitment": commitment, "expected_closure": expected_closure,
                                 "events": canon})
    return {"status": "CLEAN" if not faults else "L2_REFUSED", "bundle_id": bundle_id,
            "commitment": commitment, "expected_closure": expected_closure,
            "events": canon, "index": index, "faults": faults}


def verify_bundle(bundle, corpus_commitment):
    if not isinstance(bundle, dict) or not {"bundle_id", "commitment", "expected_closure",
                                            "events", "index", "status"} <= set(bundle):
        return False, "MALFORMED_BUNDLE"
    recomputed = ids.json_digest({"commitment": bundle["commitment"],
                                  "expected_closure": bundle["expected_closure"],
                                  "events": bundle["events"]})
    if recomputed != bundle["bundle_id"]:
        return False, "BUNDLE_ID_MISMATCH"
    if bundle["commitment"] != corpus_commitment:
        return False, "BUNDLE_NOT_COMMITTED"
    # index bodies must still hash to the committed event bodies (no post-mint tamper)
    committed = {e["event_id"]: e["body_digest"] for e in bundle["events"]}
    for eid, rec in bundle["index"].items():
        if ids.line_digest(rec["raw_bytes"]) != committed.get(eid):
            return False, "INDEX_TAMPER"
    if bundle["status"] != "CLEAN":
        return False, bundle["status"]
    return True, None


# ============================ evidence / adjudication ============================ #
def _evidence_record_digest(ev):
    return ids.json_digest({k: ev.get(k) for k in
                            ("kind", "event_id", "value_start", "value_end", "observed_value_digest")})


def _check_evidence(cand, index):
    validated, committed_digests, faults = set(), set(), []
    for ev in cand.get("mapping_evidence", []) or []:
        if not isinstance(ev, dict):
            faults.append("EVIDENCE_MALFORMED"); continue
        kind = ev.get("kind")
        if kind in FORBIDDEN_EVIDENCE:
            faults.append("FORBIDDEN_EVIDENCE"); continue
        if kind not in REQUIRED_COMPONENTS:
            continue
        rec = index.get(ev.get("event_id"))
        if rec is None:
            faults.append("DANGLING_EVIDENCE"); continue
        vs, ve = ev.get("value_start"), ev.get("value_end")
        if not (_is_int(vs) and _is_int(ve) and rec["byte_start"] <= vs <= ve <= rec["byte_end"]):
            faults.append("BAD_EVIDENCE_SPAN"); continue
        sub = rec["raw_bytes"][vs - rec["byte_start"]: ve - rec["byte_start"]]
        if ids._h(b"value", sub) != ev.get("observed_value_digest"):
            faults.append("EVIDENCE_DIGEST_MISMATCH"); continue
        ok = (ids.raw_sha256(sub) == cand.get("root_digest")) if kind == "root_digest" \
            else _decodes_to(sub, cand.get(kind))
        if ok:
            validated.add(kind); committed_digests.add(_evidence_record_digest(ev))
        else:
            faults.append("EVIDENCE_VALUE_MISMATCH")
    return validated, committed_digests, faults


def _decodes_to(sub, val):
    try:
        return sub.decode("utf-8") == val
    except UnicodeDecodeError:
        return False


def _decision_ok(dec, positive):
    return (isinstance(dec, dict) and dec.get("adjudicator_identity") and dec.get("authority")
            and dec.get("decision") == positive)


def _adjudication_ok(adj, committed_evidence_digests):
    if not isinstance(adj, dict):
        return False, "EXACT_WITHOUT_ADJUDICATION"
    for k in ("adjudicator_identity", "authority", "decision", "evidence_commitments"):
        if not adj.get(k):
            return False, "EXACT_WITHOUT_ADJUDICATION"
    if adj["decision"] != "EXACT":
        return False, "ADJUDICATION_DECISION"
    if set(adj["evidence_commitments"]) != set(committed_evidence_digests):
        return False, "ADJUDICATION_MISMATCH"
    return True, None


# ============================ act record ============================ #
def _actrecord(cand, index):
    """Build a full, self-contained ActRecord {id, body} + provisional status + faults."""
    f = []
    if not isinstance(cand, dict):
        return {"local_ref": "?", "record_id": None, "act_id": "act:INVALID",
                "experiment_id": None, "root_digest": None, "verifier_identity": None,
                "agent_run_occurrence": None, "status": "AMBIGUOUS",
                "parent_local_ref": None, "selected_child_refs": [],
                "faults": ["CANDIDATE_MALFORMED"], "body": None,
                "completeness": None, "publication": None}
    lr = cand.get("local_ref")
    if not isinstance(lr, str) or not lr:
        f.append("BAD_LOCAL_REF"); lr = str(lr)
    if set(cand) - CANDIDATE_FIELDS:
        f.append("UNKNOWN_FIELD")
    # ActRecord fields must be present AND non-null (typed "UNKNOWN" is allowed)
    for k in ACTRECORD_REQUIRED:
        if k not in cand or cand[k] is None:
            f.append("SCHEMA_INVALID"); break

    ordered, bodies, of = _validate_occurrences(cand, index)
    f += of
    closure = index[ordered[0][0]]["extraction_closure"] if ordered and ordered[0][0] in index else "unknown"
    aid = (ids.act_id(closure, cand.get("blob_id", ""), ordered, ids.content_digest(bodies))
           if ordered else "act:INVALID")

    validated, committed_ev, ef = _check_evidence(cand, index)
    f += ef
    samp = cand.get("sampling", {})
    if not isinstance(samp, dict):
        f.append("BAD_SAMPLING")
    else:
        for _k, v in samp.items():
            if v != "UNKNOWN":
                f.append("SILENT_DEFAULT"); break

    claimed = cand.get("mapping_status", "DERIVED")
    if claimed not in ("EXACT", "DERIVED"):
        f.append("BAD_STATUS"); status = "AMBIGUOUS"
    elif claimed == "EXACT":
        missing = [c for c in REQUIRED_COMPONENTS if c not in validated]
        adj_ok, adj_fault = _adjudication_ok(cand.get("adjudication"), committed_ev)
        blocking = {"NO_RAW_PROVENANCE", "SCHEMA_INVALID", "NO_EVENTS", "BAD_OCCURRENCE",
                    "BAD_SAMPLING", "UNKNOWN_FIELD", "SILENT_DEFAULT", "BAD_LOCAL_REF"}
        if not adj_ok:
            f.append(adj_fault); status = "AMBIGUOUS"
        elif missing or (blocking & set(f)):
            f.append("EXACT_WITHOUT_EVIDENCE"); status = "AMBIGUOUS"
        else:
            status = "EXACT"
    else:
        status = "DERIVED"

    comp = cand.get("completeness_decision")
    pub = cand.get("publication_decision")
    body = {
        "source": {"blob_id": cand.get("blob_id"),
                   "occurrences": [{"event_id": e, "byte_start": s, "byte_end": en,
                                    "body_digest": index.get(e, {}).get("body_digest")}
                                   for (e, s, en) in ordered]},
        "experiment_id": cand.get("experiment_id"), "root_id": cand.get("root_id"),
        "root_digest": cand.get("root_digest"), "parent_local_ref": cand.get("parent_local_ref"),
        "verifier_declared_identity": cand.get("verifier_declared_identity"),
        "verifier_observed_identity": cand.get("verifier_observed_identity"),
        "verifier_identity": cand.get("verifier_identity"),
        "agent_run_occurrence": cand.get("agent_run_occurrence"),
        "prompt_digest": cand.get("prompt_digest"), "response_digest": cand.get("response_digest"),
        "offspring_before_dedup": cand.get("offspring_before_dedup"),
        "dedup_removal_decisions": cand.get("dedup_removal_decisions"),
        "selected_child_refs": cand.get("selected_child_refs"),
        "sampling": cand.get("sampling"),
        "completeness_decision": comp, "publication_decision": pub,
        "mapping": {"status": status, "act_id": aid,
                    "evidence_commitment": ids.json_digest(sorted(committed_ev)),
                    "adjudication": cand.get("adjudication")},
    }
    rid = "rec:" + ids.json_digest(body)
    return {"local_ref": lr, "record_id": rid, "act_id": aid,
            "experiment_id": cand.get("experiment_id"), "root_digest": cand.get("root_digest"),
            "verifier_identity": cand.get("verifier_identity"),
            "agent_run_occurrence": cand.get("agent_run_occurrence"), "status": status,
            "parent_local_ref": cand.get("parent_local_ref"),
            "selected_child_refs": cand.get("selected_child_refs") or [],
            "completeness": comp, "publication": pub, "faults": f, "body": body}


def _validate_occurrences(cand, index):
    ordered, bodies, faults = [], [], []
    occ = cand.get("event_occurrences")
    if not isinstance(occ, list) or not occ:
        return [], [], ["NO_EVENTS"]
    closures = set()
    for o in occ:
        if not (isinstance(o, dict) and _is_int(o.get("byte_start")) and _is_int(o.get("byte_end"))):
            faults.append("BAD_OCCURRENCE"); continue
        rec = index.get(o.get("event_id"))
        if rec is None or rec["blob_id"] != cand.get("blob_id") \
                or rec["byte_start"] != o["byte_start"] or rec["byte_end"] != o["byte_end"]:
            faults.append("NO_RAW_PROVENANCE"); continue
        closures.add(index[o["event_id"]].get("extraction_closure", "l2"))
        ordered.append((o["event_id"], o["byte_start"], o["byte_end"]))
        bodies.append(rec["raw_bytes"])
    return ordered, bodies, faults


# ============================ graph + views ============================ #
def build_l3(bundle, table, manifests=None, corpus_commitment=None):
    ok, reason = verify_bundle(bundle, corpus_commitment)
    if not ok:
        return {"schema": "manifesto.corpus.act-graph-report.v0", "bundle_ok": False,
                "bundle_fault": reason, "act_count": 0, "faults": [], "acts": [],
                "views": {c: {"status": "REFUSED", "reason": reason}
                          for c in ("C1", "C3", "C2", "C4", "C7")}}
    index = {eid: {**rec, "extraction_closure": bundle["expected_closure"]}
             for eid, rec in bundle["index"].items()}
    acts = [_actrecord(c, index) for c in (table or [])]

    for lr, group in _by(acts, "local_ref").items():
        if len(group) > 1:
            for a in group:
                a["faults"].append("DUPLICATE_LOCAL_REF"); a["status"] = "AMBIGUOUS"
    for aid, group in _by(acts, "act_id").items():
        if aid != "act:INVALID" and len(group) > 1:
            for a in group:
                a["faults"].append("DUPLICATE_ID"); a["status"] = "AMBIGUOUS"
    live = {a["local_ref"] for a in acts if "DUPLICATE_LOCAL_REF" not in a["faults"]}
    for a in acts:
        if a["parent_local_ref"] is not None and a["parent_local_ref"] not in live:
            a["faults"].append("DANGLING_PARENT"); a["status"] = "AMBIGUOUS"
        for c in a["selected_child_refs"]:
            if c not in live:
                a["faults"].append("DANGLING_CHILD"); a["status"] = "AMBIGUOUS"
    groups = defaultdict(list)
    for a in acts:
        if a["status"] in ("EXACT", "DERIVED"):
            groups[(a["experiment_id"], a["root_digest"], a["verifier_identity"])].append(a)
    for g in groups.values():
        if len({a["agent_run_occurrence"] for a in g}) > 1:
            for a in g:
                a["status"] = "CONFLICTED"; a["faults"].append("REPEATED_RUN")

    mclo = mapper_closure_id()
    for a in acts:
        a["mapping_id"] = ids.mapping_id(
            mclo, a["act_id"], a["experiment_id"] or "", a["root_digest"] or "",
            a["verifier_identity"] or "", a["agent_run_occurrence"] or "",
            a.get("body", {}).get("mapping", {}).get("evidence_commitment", "") if a.get("body") else "",
            a["status"], ids.json_digest((a.get("body") or {}).get("mapping", {}).get("adjudication") or {}))

    views = {c: _view(c, acts, (manifests or {}).get(c), bundle, corpus_commitment)
             for c in ("C1", "C3", "C2", "C4", "C7")}
    return {
        "schema": "manifesto.corpus.act-graph-report.v0", "bundle_ok": True,
        "l2_bundle_id": bundle["bundle_id"], "corpus_commitment": corpus_commitment,
        "mapper_closure": mclo, "act_count": len(acts),
        "fault_count": sum(len(a["faults"]) for a in acts),
        "faults": [{"local_ref": a["local_ref"], "faults": a["faults"]} for a in acts if a["faults"]],
        "views": views,
        "acts": [{k: a[k] for k in ("local_ref", "act_id", "record_id", "mapping_id",
                  "experiment_id", "status", "faults")} for a in acts],
        "note": "metadata only; full ActRecord bodies are the private L3. DERIVED never credits.",
    }


def _by(acts, key):
    d = defaultdict(list)
    for a in acts:
        d[a[key]].append(a)
    return d


def validate_manifest(m):
    if not isinstance(m, dict) or (set(m) - MANIFEST_FIELDS):
        return "MALFORMED_MANIFEST"
    for k in ("claim", "paper_pin", "experiment_ids", "unit_key", "required_units"):
        if k not in m:
            return "MALFORMED_MANIFEST"
    if not (isinstance(m["experiment_ids"], list) and m["experiment_ids"]):
        return "MALFORMED_MANIFEST"
    if not (isinstance(m["unit_key"], list) and m["unit_key"] and set(m["unit_key"]) <= ALLOWED_UNIT_KEYS):
        return "BAD_UNIT_KEY"
    ru = m["required_units"]
    if not isinstance(ru, list) or not ru:
        return "EMPTY_REQUIRED_SET"
    seen = set()
    for u in ru:
        if not (isinstance(u, (list, tuple)) and len(u) == len(m["unit_key"])):
            return "MALFORMED_MANIFEST"
        if tuple(u) in seen:
            return "DUPLICATE_REQUIRED_UNIT"
        seen.add(tuple(u))
    return None


def manifest_id(m):
    return "man:" + ids.json_digest(m)


def _publishable_exact(a):
    return (not a["faults"] and a["status"] == "EXACT"
            and _decision_ok(a["completeness"], "COMPLETE")
            and _decision_ok(a["publication"], "CLEARED_FOR_PUBLICATION"))


def _view(claim, acts, manifest, bundle, corpus_commitment):
    if manifest is None:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_UNSPECIFIED"}
    bad = validate_manifest(manifest)
    if bad:
        return {"status": "REFUSED", "reason": bad}
    if manifest["claim"] != claim:
        return {"status": "REFUSED", "reason": "MANIFEST_CLAIM_MISMATCH"}
    mid = manifest_id(manifest)
    exps = set(manifest["experiment_ids"])
    key = manifest["unit_key"]
    required = {tuple(u) for u in manifest["required_units"]}
    allowed_extra = {tuple(u) for u in manifest.get("allowed_exclusions", [])}
    rel = [a for a in acts if a["experiment_id"] in exps]

    def unit(a):
        return tuple(a.get(k) for k in key)
    present_any = {unit(a) for a in rel}
    ok_acts = [a for a in rel if _publishable_exact(a)]
    present_ok = {unit(a) for a in ok_acts}
    missing = sorted(map(list, required - present_any))
    incomplete = sorted(map(list, (required & present_any) - present_ok))
    extra = sorted(map(list, present_ok - required - allowed_extra))
    base = {"manifest_id": mid, "paper_pin": manifest["paper_pin"],
            "l2_bundle_id": bundle["bundle_id"], "corpus_commitment": corpus_commitment}
    if missing:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_MISSING", "missing": missing, **base}
    if incomplete:
        return {"status": "REFUSED", "reason": "INCOMPLETE_TREE", "incomplete": incomplete, **base}
    if extra:
        return {"status": "REFUSED", "reason": "UNEXPECTED_UNITS", "extra": extra, **base}
    evaluation_id = "eval:" + ids.json_digest(
        {"manifest_id": mid, "l2_bundle_id": bundle["bundle_id"],
         "corpus_commitment": corpus_commitment,
         "record_ids": sorted(a["record_id"] for a in ok_acts)})
    return {"status": "COMPLETE", "units": len(required), "evaluation_id": evaluation_id, **base}


def make_public_projection(source_act_id, redaction_profile_id, public_body,
                           loss_report, proposed_id=None):
    if not loss_report:
        return {"status": "FAIL", "reason": "MISSING_LOSS_REPORT"}
    if not public_body:
        return {"status": "FAIL", "reason": "EMPTY_PUBLIC_BODY"}
    if proposed_id is not None and proposed_id == source_act_id:
        return {"status": "FAIL", "reason": "REDACTION_ID_REUSE"}
    pid = ids.public_id(mapper_closure_id(), source_act_id, redaction_profile_id,
                        ids._h(b"public-body", public_body), ids.json_digest(loss_report))
    return {"status": "OK", "public_id": pid, "derived_from": source_act_id}
