#!/usr/bin/env python3
"""
corpus_map.py — L2 -> L3. EXPLICIT, AUTHENTICATED, ADJUDICATED MAPPING.

Everything the mapper trusts is re-derived, never asserted (Codex exact-HEAD review
57d41e5). The L2 index is AUTHENTICATED (event ids recomputed from raw bytes before
any mapping); occurrences/blob/closure are validated against the authenticated events;
required-unit manifests are closed and non-vacuous; adjudication is bound to the exact
value-validated evidence; graph faults/status are finalized BEFORE mapping ids/views
are minted; a duplicate local_ref or act_id invalidates ALL of its members.

Credit rules: DERIVED is a proposal forever; only EXACT (adjudicated + fully
value-evidenced + fault-free + COMPLETE + CLEARED) can satisfy a required unit.
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
    "dedup_removal_decisions", "selected_child_refs", "sampling",
    "completeness_status", "publication_eligibility",
)
CANDIDATE_FIELDS = set(ACTRECORD_REQUIRED) | {
    "local_ref", "blob_id", "event_occurrences", "experiment_id", "root_digest",
    "verifier_identity", "agent_run_occurrence", "mapping_status", "mapping_evidence",
    "adjudication", "parent_local_ref",
}


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


# --------------------------------------------------------------------------- #
# Authenticated L2 boundary: recompute every event id from raw bytes (P0-1).
# --------------------------------------------------------------------------- #
def authenticate_l2(entries):
    """
    entries: iterable of {blob_id, byte_start, byte_end, raw_bytes, extraction_closure,
                          event_id?(claimed)}.
    Returns a bundle {status, index, faults}. A claimed event_id that does not recompute
    from its bytes is an L2_INTEGRITY_BREAK and the whole bundle is refused.
    """
    index, faults = {}, []
    for e in entries:
        try:
            ld = ids.line_digest(e["raw_bytes"])
            eid = ids.event_id(e["extraction_closure"], e["blob_id"],
                               int(e["byte_start"]), int(e["byte_end"]), ld)
        except (KeyError, TypeError, ValueError):
            faults.append({"code": "MALFORMED_L2_ENTRY"}); continue
        if e.get("event_id") is not None and e["event_id"] != eid:
            faults.append({"code": "L2_INTEGRITY_BREAK",
                           "claimed": e["event_id"], "recomputed": eid}); continue
        index[eid] = {"blob_id": e["blob_id"], "byte_start": int(e["byte_start"]),
                      "byte_end": int(e["byte_end"]), "raw_bytes": e["raw_bytes"],
                      "extraction_closure": e["extraction_closure"]}
    return {"status": "CLEAN" if not faults else "L2_INTEGRITY_BREAK",
            "index": index, "faults": faults}


def bundle_from_private(private_l2):
    entries = []
    for data in (private_l2 or {}).values():
        for ev in data["events"]:
            entries.append({"blob_id": ev["blob_id"], "byte_start": ev["byte_start"],
                            "byte_end": ev["byte_end"],
                            "raw_bytes": base64.b64decode(ev["raw_b64"]),
                            "extraction_closure": ev["extraction_closure"],
                            "event_id": ev["event_id"]})
    return authenticate_l2(entries)


# --------------------------------------------------------------------------- #
def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _check_evidence(cand, index):
    """Value-check each evidence span against the authenticated body.
    Returns (validated_kinds, validated_event_ids, faults)."""
    validated, used, faults = set(), set(), []
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
        if kind == "root_digest":
            ok = (ids.raw_sha256(sub) == cand.get("root_digest"))
        else:
            try:
                ok = (sub.decode("utf-8") == cand.get(kind))
            except UnicodeDecodeError:
                ok = False
        if ok:
            validated.add(kind); used.add(ev["event_id"])
        else:
            faults.append("EVIDENCE_VALUE_MISMATCH")
    return validated, used, faults


def _adjudication_ok(adj, validated_event_ids):
    if not isinstance(adj, dict):
        return False, "EXACT_WITHOUT_ADJUDICATION"
    for k in ("adjudicator_identity", "authority", "decision", "evidence_commitments"):
        if not adj.get(k):
            return False, "EXACT_WITHOUT_ADJUDICATION"
    if adj["decision"] != "EXACT":
        return False, "ADJUDICATION_DECISION"
    if set(adj["evidence_commitments"]) != set(validated_event_ids):
        return False, "ADJUDICATION_MISMATCH"     # not bound to the actual evidence
    return True, None


def _validate_occurrences(cand, index):
    """Every occurrence must equal a real authenticated event (blob+span+closure)."""
    ordered, bodies, faults = [], [], []
    occ = cand.get("event_occurrences")
    if not isinstance(occ, list) or not occ:
        return [], [], ["NO_EVENTS"]
    closures = set()
    for o in occ:
        if not (isinstance(o, dict) and _is_int(o.get("byte_start")) and _is_int(o.get("byte_end"))):
            faults.append("BAD_OCCURRENCE"); continue
        rec = index.get(o.get("event_id"))
        if rec is None:
            faults.append("NO_RAW_PROVENANCE"); continue
        if (rec["blob_id"] != cand.get("blob_id") or rec["byte_start"] != o["byte_start"]
                or rec["byte_end"] != o["byte_end"]):
            faults.append("NO_RAW_PROVENANCE"); continue      # forged blob/occurrence
        closures.add(rec["extraction_closure"])
        ordered.append((o["event_id"], o["byte_start"], o["byte_end"]))
        bodies.append(rec["raw_bytes"])
    if len(closures) > 1:
        faults.append("MIXED_EXTRACTION_CLOSURE")
    return ordered, bodies, faults


def _process(cand, index):
    """Validate one candidate into a provisional act record (never raises)."""
    if not isinstance(cand, dict):
        return {"local_ref": "?", "act_id": "act:INVALID", "experiment_id": None,
                "root_digest": None, "verifier_identity": None, "agent_run_occurrence": None,
                "status": "AMBIGUOUS", "completeness_status": "UNKNOWN",
                "publication_eligibility": "UNREVIEWED", "parent_local_ref": None,
                "selected_child_refs": [], "validated_event_ids": [], "adjudication": {},
                "mapping_evidence": [], "faults": ["CANDIDATE_MALFORMED"]}
    f = []
    lr = cand.get("local_ref")
    if not isinstance(lr, str) or not lr:
        f.append("BAD_LOCAL_REF"); lr = str(lr)
    if set(cand) - CANDIDATE_FIELDS:
        f.append("UNKNOWN_FIELD")
    for k in ACTRECORD_REQUIRED:
        if k not in cand:
            f.append("SCHEMA_INCOMPLETE"); break

    ordered, bodies, of = _validate_occurrences(cand, index)
    f += of
    closure = index[ordered[0][0]]["extraction_closure"] if ordered else "unknown"
    aid = (ids.act_id(closure, cand.get("blob_id", ""), ordered, ids.content_digest(bodies))
           if ordered else "act:INVALID")

    validated, used, ef = _check_evidence(cand, index)
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
        adj_ok, adj_fault = _adjudication_ok(cand.get("adjudication"), used)
        if not adj_ok:
            f.append(adj_fault); status = "AMBIGUOUS"
        elif missing or "NO_RAW_PROVENANCE" in f:
            f.append("EXACT_WITHOUT_EVIDENCE"); status = "AMBIGUOUS"
        else:
            status = "EXACT"
    else:
        status = "DERIVED"

    return {"local_ref": lr, "act_id": aid, "experiment_id": cand.get("experiment_id"),
            "root_digest": cand.get("root_digest"), "verifier_identity": cand.get("verifier_identity"),
            "agent_run_occurrence": cand.get("agent_run_occurrence"), "status": status,
            "completeness_status": cand.get("completeness_status", "UNKNOWN"),
            "publication_eligibility": cand.get("publication_eligibility", "UNREVIEWED"),
            "parent_local_ref": cand.get("parent_local_ref"),
            "selected_child_refs": cand.get("selected_child_refs") or [],
            "validated_event_ids": sorted(used), "adjudication": cand.get("adjudication") or {},
            "mapping_evidence": cand.get("mapping_evidence") or [], "faults": f}


def build_l3(l2_bundle, table, manifests=None):
    """l2_bundle: output of authenticate_l2/bundle_from_private. Returns metadata report."""
    if not isinstance(l2_bundle, dict) or "index" not in l2_bundle:
        l2_bundle = {"status": "L2_INTEGRITY_BREAK", "index": {}, "faults": [{"code": "BAD_BUNDLE"}]}
    index = l2_bundle["index"]
    l2_clean = l2_bundle["status"] == "CLEAN"

    acts = [_process(c, index) for c in (table or [])]

    # --- finalize graph faults/status BEFORE minting ids/views (P0-4) --- #
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

    # mint mapping_id over the FINAL status/evidence/adjudication
    mclo = mapper_closure_id()
    for a in acts:
        a["mapping_id"] = ids.mapping_id(
            mclo, a["act_id"], a["experiment_id"] or "", a["root_digest"] or "",
            a["verifier_identity"] or "", a["agent_run_occurrence"] or "",
            ids.json_digest(a["mapping_evidence"]), a["status"], ids.json_digest(a["adjudication"]))

    views = {c: _view(c, acts, (manifests or {}).get(c), l2_clean, l2_bundle["faults"])
             for c in ("C1", "C3", "C2", "C4", "C7")}
    return {
        "schema": "manifesto.corpus.act-graph-report.v0",
        "mapper_closure": mclo, "l2_status": l2_bundle["status"], "l2_faults": l2_bundle["faults"],
        "act_count": len(acts), "fault_count": sum(len(a["faults"]) for a in acts),
        "faults": [{"local_ref": a["local_ref"], "faults": a["faults"]} for a in acts if a["faults"]],
        "views": views,
        "acts": [{k: a[k] for k in ("local_ref", "act_id", "mapping_id", "experiment_id",
                  "status", "completeness_status", "publication_eligibility", "faults")} for a in acts],
        "note": "metadata only. DERIVED never credits; views need a closed non-vacuous manifest and a CLEAN L2.",
    }


def _by(acts, key):
    d = defaultdict(list)
    for a in acts:
        d[a[key]].append(a)
    return d


def validate_manifest(m):
    if not isinstance(m, dict):
        return "MALFORMED_MANIFEST"
    for k in ("claim", "experiment_ids", "unit_key", "required_units"):
        if k not in m:
            return "MALFORMED_MANIFEST"
    if not (isinstance(m["experiment_ids"], list) and m["experiment_ids"]):
        return "MALFORMED_MANIFEST"
    if not (isinstance(m["unit_key"], list) and m["unit_key"]
            and set(m["unit_key"]) <= ALLOWED_UNIT_KEYS):
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


def _publishable_exact(a):
    return (not a["faults"] and a["status"] == "EXACT"
            and a["completeness_status"] == "COMPLETE"
            and a["publication_eligibility"] == "CLEARED_FOR_PUBLICATION")


def _view(claim, acts, manifest, l2_clean, l2_faults):
    if not l2_clean:
        return {"status": "REFUSED", "reason": "L2_INTEGRITY_BREAK"}
    if manifest is None:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_UNSPECIFIED"}
    bad = validate_manifest(manifest)
    if bad:
        return {"status": "REFUSED", "reason": bad}
    if manifest.get("claim") != claim:
        return {"status": "REFUSED", "reason": "MANIFEST_CLAIM_MISMATCH"}
    exps = set(manifest["experiment_ids"])
    key = manifest["unit_key"]
    required = {tuple(u) for u in manifest["required_units"]}
    allowed_extra = {tuple(u) for u in manifest.get("allowed_exclusions", [])}
    rel = [a for a in acts if a["experiment_id"] in exps]

    def unit(a):
        return tuple(a.get(k) for k in key)
    present_any = {unit(a) for a in rel}
    present_ok = {unit(a) for a in rel if _publishable_exact(a)}
    missing = sorted(map(list, required - present_any))          # no act at all
    incomplete = sorted(map(list, (required & present_any) - present_ok))  # act present, not clean
    extra = sorted(map(list, present_ok - required - allowed_extra))
    if missing:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_MISSING", "missing": missing}
    if incomplete:
        return {"status": "REFUSED", "reason": "INCOMPLETE_TREE", "incomplete": incomplete}
    if extra:
        return {"status": "REFUSED", "reason": "UNEXPECTED_UNITS", "extra": extra}
    return {"status": "COMPLETE", "units": len(required)}


def make_public_projection(source_act_id, redaction_profile_id, public_body,
                           loss_report, proposed_id=None):
    """New id bound to public body + redaction profile + source + exact loss report (F8)."""
    if not loss_report:
        return {"status": "FAIL", "reason": "MISSING_LOSS_REPORT"}
    if not public_body:
        return {"status": "FAIL", "reason": "EMPTY_PUBLIC_BODY"}
    pid = ids.public_id(mapper_closure_id(), source_act_id, redaction_profile_id,
                        ids._h(b"public-body", public_body), ids.json_digest(loss_report))
    if proposed_id is not None and proposed_id == source_act_id:
        return {"status": "FAIL", "reason": "REDACTION_ID_REUSE"}
    return {"status": "OK", "public_id": pid, "derived_from": source_act_id}
