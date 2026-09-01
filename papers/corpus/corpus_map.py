#!/usr/bin/env python3
"""
corpus_map.py — L2 -> L3. EXPLICIT, REVIEWABLE, ADJUDICATED MAPPING.

A mapping table turns L2 event occurrences into act records ONLY through evidence that
is re-read and value-checked against the raw L2 spans — never by asserting an event id.
Credit rules (Codex closure review a690789):

- `DERIVED` is a PROPOSAL: forever a candidate, never publishable, never L4-complete.
  Only `EXACT` mappings earn claim credit.
- `EXACT` requires (a) an adjudication record (identity, authority, decision,
  evidence commitments) AND (b) all four components (experiment/root/verifier/run)
  proven by evidence whose raw span re-reads to the asserted value. Otherwise the
  mapping is downgraded to `AMBIGUOUS`.
- counts/verdicts are forbidden as evidence.
- a claim view is COMPLETE only against a CLOSED required-unit manifest (exact units,
  not counts); with no manifest every real view is `REFUSED: REQUIRED_UNITS_UNSPECIFIED`.
- duplicate local_ref, bad scalar types, invalid spans, unknown fields, malformed
  shapes -> typed fail-closed faults, never crashes or silent overwrites.

Extraction identity and mapping identity are distinct but linked: `mapping_id` binds the
subject `act_id`, the four values, the evidence commitment, the status, and the
adjudication. `act_id` binds ORDERED event occurrences + reconstructed content.
"""
import base64
from collections import defaultdict
from pathlib import Path

import corpus_ids as ids

REQUIRED_COMPONENTS = ("experiment_id", "root_digest", "verifier_identity", "agent_run_occurrence")
FORBIDDEN_EVIDENCE = {"count", "verdict"}
CANDIDATE_FIELDS = {
    "local_ref", "blob_id", "event_occurrences", "experiment_id", "root_digest",
    "verifier_identity", "agent_run_occurrence", "mapping_status", "mapping_evidence",
    "adjudication", "completeness_status", "publication_eligibility",
    "parent_local_ref", "selected_child_refs", "sampling",
}


def mapper_closure_id():
    here = Path(__file__).resolve().parent
    return ids.closure_id("map", [
        ("corpus_map.py", (here / "corpus_map.py").read_bytes()),
        ("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
        ("schema_version", ids.SCHEMA_VERSION.encode()),
    ])


def l2_index_from_private(private_l2):
    """Build {event_id: {blob_id, byte_start, byte_end, raw_bytes}} from private L2."""
    idx = {}
    for data in private_l2.values():
        for e in data["events"]:
            idx[e["event_id"]] = {
                "blob_id": e["blob_id"], "byte_start": e["byte_start"],
                "byte_end": e["byte_end"], "raw_bytes": base64.b64decode(e["raw_b64"]),
                "extraction_closure": e.get("extraction_closure", "unknown")}
    return idx


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _adjudication_valid(adj):
    return (isinstance(adj, dict)
            and adj.get("adjudicator_identity") and adj.get("authority")
            and adj.get("decision") and adj.get("evidence_commitments"))


def _check_evidence(cand, l2_index):
    """Return (validated_kinds, faults). Re-reads each evidence span and value-checks it."""
    validated, faults = set(), []
    for ev in cand.get("mapping_evidence", []):
        if not isinstance(ev, dict):
            faults.append("EVIDENCE_MALFORMED"); continue
        kind = ev.get("kind")
        if kind in FORBIDDEN_EVIDENCE:
            faults.append("FORBIDDEN_EVIDENCE"); continue
        if kind not in REQUIRED_COMPONENTS:
            continue
        eid = ev.get("event_id")
        rec = l2_index.get(eid)
        if rec is None:
            faults.append("DANGLING_EVIDENCE"); continue
        vs, ve = ev.get("value_start"), ev.get("value_end")
        if not (_is_int(vs) and _is_int(ve) and rec["byte_start"] <= vs <= ve <= rec["byte_end"]):
            faults.append("BAD_EVIDENCE_SPAN"); continue
        sub = rec["raw_bytes"][vs - rec["byte_start"]: ve - rec["byte_start"]]
        if ids._h(b"value", sub) != ev.get("observed_value_digest"):
            faults.append("EVIDENCE_DIGEST_MISMATCH"); continue
        # pinned field-extraction rule: does the raw span actually carry the asserted value?
        ok = False
        if kind == "root_digest":
            ok = (ids.raw_sha256(sub) == cand.get("root_digest"))
        else:
            try:
                ok = (sub.decode("utf-8") == cand.get(kind))
            except UnicodeDecodeError:
                ok = False
        if ok:
            validated.add(kind)
        else:
            faults.append("EVIDENCE_VALUE_MISMATCH")
    return validated, faults


def _process(cand, l2_index):
    """Validate one candidate into an act record + faults (never raises)."""
    f = []
    if not isinstance(cand, dict):
        return {"local_ref": "?", "act_id": "act:INVALID", "mapping_id": "map:INVALID",
                "experiment_id": None, "root_digest": None, "verifier_identity": None,
                "agent_run_occurrence": None, "mapping_status": "AMBIGUOUS",
                "completeness_status": "UNKNOWN", "publication_eligibility": "UNREVIEWED",
                "parent_local_ref": None, "selected_child_refs": [],
                "faults": ["CANDIDATE_MALFORMED"]}
    lr = cand.get("local_ref")
    unknown = set(cand) - CANDIDATE_FIELDS
    if unknown:
        f.append("UNKNOWN_FIELD")
    if not isinstance(lr, str) or not lr:
        f.append("BAD_LOCAL_REF"); lr = str(lr)

    occ = cand.get("event_occurrences") or []
    ordered, bodies, dangling = [], [], False
    if not isinstance(occ, list) or not occ:
        f.append("NO_EVENTS")
    else:
        for o in occ:
            if not (isinstance(o, dict) and _is_int(o.get("byte_start"))
                    and _is_int(o.get("byte_end")) and o.get("byte_start") >= 0
                    and o["byte_end"] >= o["byte_start"]):
                f.append("BAD_OCCURRENCE"); continue
            rec = l2_index.get(o.get("event_id"))
            if rec is None:
                f.append("DANGLING_REF"); dangling = True; continue
            ordered.append((o["event_id"], o["byte_start"], o["byte_end"]))
            bodies.append(rec["raw_bytes"])

    # act identity binds the extraction closure of the events it is built from (P0-6),
    # ordered occurrences, and reconstructed content (order is semantic).
    act_closure = l2_index[ordered[0][0]]["extraction_closure"] if ordered else "unknown"
    aid = ids.act_id(act_closure, cand.get("blob_id", ""), ordered,
                     ids.content_digest(bodies)) if ordered else "act:INVALID"

    validated, ef = _check_evidence(cand, l2_index)
    f += ef

    claimed = cand.get("mapping_status", "DERIVED")
    adj = cand.get("adjudication")
    if claimed not in ("EXACT", "DERIVED"):
        f.append("BAD_STATUS"); status = "AMBIGUOUS"
    elif claimed == "EXACT":
        missing = [c for c in REQUIRED_COMPONENTS if c not in validated]
        if not _adjudication_valid(adj):
            f.append("EXACT_WITHOUT_ADJUDICATION"); status = "AMBIGUOUS"
        elif missing or dangling:
            f.append("EXACT_WITHOUT_EVIDENCE"); status = "AMBIGUOUS"
        else:
            status = "EXACT"
    else:
        status = "DERIVED"          # a proposal — never publishable

    # SILENT_DEFAULT: a concrete sampling value must be evidenced, else typed UNKNOWN
    for k, v in (cand.get("sampling") or {}).items():
        if v != "UNKNOWN":
            f.append("SILENT_DEFAULT"); break

    mapping_evidence_digest = ids.json_digest(cand.get("mapping_evidence", []))
    adjud_digest = ids.json_digest(adj if isinstance(adj, dict) else {})
    mid = ids.mapping_id(mapper_closure_id(), aid, cand.get("experiment_id", ""),
                         cand.get("root_digest", ""), cand.get("verifier_identity", ""),
                         cand.get("agent_run_occurrence", ""), mapping_evidence_digest,
                         status, adjud_digest)
    return {
        "local_ref": lr, "act_id": aid, "mapping_id": mid,
        "experiment_id": cand.get("experiment_id"), "root_digest": cand.get("root_digest"),
        "verifier_identity": cand.get("verifier_identity"),
        "agent_run_occurrence": cand.get("agent_run_occurrence"),
        "mapping_status": status, "completeness_status": cand.get("completeness_status", "UNKNOWN"),
        "publication_eligibility": cand.get("publication_eligibility", "UNREVIEWED"),
        "parent_local_ref": cand.get("parent_local_ref"),
        "selected_child_refs": cand.get("selected_child_refs") or [],
        "faults": f,
    }


def build_l3(l2_index, table, required_units=None):
    """required_units: {claim_id: manifest|None}. Returns a metadata-only report."""
    acts, by_local, seen_local, seen_act = [], {}, set(), {}
    for cand in (table or []):
        a = _process(cand, l2_index)
        if a["local_ref"] in seen_local:
            a["faults"].append("DUPLICATE_LOCAL_REF")     # fail-closed, no overwrite
        else:
            seen_local.add(a["local_ref"]); by_local[a["local_ref"]] = a
        if a["act_id"] in seen_act and a["act_id"] != "act:INVALID":
            a["faults"].append("DUPLICATE_ID")
        seen_act[a["act_id"]] = a["local_ref"]
        acts.append(a)

    for a in acts:
        if a["parent_local_ref"] is not None and a["parent_local_ref"] not in by_local:
            a["faults"].append("DANGLING_PARENT")
        for c in a["selected_child_refs"]:
            if c not in by_local:
                a["faults"].append("DANGLING_CHILD")

    groups = defaultdict(list)
    for a in acts:
        if a["mapping_status"] in ("EXACT", "DERIVED"):
            groups[(a["experiment_id"], a["root_digest"], a["verifier_identity"])].append(a)
    for g in groups.values():
        if len({a["agent_run_occurrence"] for a in g}) > 1:
            for a in g:
                a["mapping_status"] = "CONFLICTED"
                a["faults"].append("REPEATED_RUN")

    req = required_units or {}
    views = {c: _view(c, acts, req.get(c)) for c in ("C1", "C3", "C2", "C4", "C7")}

    all_faults = [{"local_ref": a["local_ref"], "faults": a["faults"]} for a in acts if a["faults"]]
    return {
        "schema": "manifesto.corpus.act-graph-report.v0",
        "mapper_closure": mapper_closure_id(),
        "act_count": len(acts), "fault_count": sum(len(a["faults"]) for a in acts),
        "faults": all_faults, "views": views,
        "acts": [{k: a[k] for k in ("local_ref", "act_id", "mapping_id", "experiment_id",
                  "mapping_status", "completeness_status", "publication_eligibility", "faults")}
                 for a in acts],
        "note": "metadata only. DERIVED is a proposal (never credit). Views need a closed "
                "required-unit manifest; without it every real view is REFUSED.",
    }


def _publishable_exact(a):
    return (not a["faults"] and a["mapping_status"] == "EXACT"
            and a["completeness_status"] == "COMPLETE"
            and a["publication_eligibility"] == "CLEARED_FOR_PUBLICATION")


def _view(claim, acts, manifest):
    if manifest is None:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_UNSPECIFIED"}
    exps = set(manifest["experiment_ids"])
    key = manifest["unit_key"]
    required = {tuple(u) for u in manifest["required_units"]}
    allowed_extra = {tuple(u) for u in manifest.get("allowed_exclusions", [])}
    rel = [a for a in acts if a["experiment_id"] in exps]
    # only EXACT + complete + cleared + fault-free acts can satisfy a unit
    present = {tuple(a[k] for k in key) for a in rel if _publishable_exact(a)}
    missing = sorted(map(list, required - present))
    extra = sorted(map(list, present - required - allowed_extra))
    if missing:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_MISSING", "missing": missing}
    if extra:
        return {"status": "REFUSED", "reason": "UNEXPECTED_UNITS", "extra": extra}
    return {"status": "COMPLETE", "units": len(required)}


def make_public_projection(source_act_id, redaction_profile_id, public_body: bytes, loss_report):
    """A redacted/public projection gets a NEW id bound to the public body AND the exact
    loss report; the original id is never reused (F8)."""
    if not loss_report:
        return {"status": "FAIL", "reason": "MISSING_LOSS_REPORT"}
    if not public_body:
        return {"status": "FAIL", "reason": "EMPTY_PUBLIC_BODY"}
    pid = ids.public_id(mapper_closure_id(), source_act_id, redaction_profile_id,
                        ids._h(b"public-body", public_body), ids.json_digest(loss_report))
    return {"status": "OK", "public_id": pid, "derived_from": source_act_id}
