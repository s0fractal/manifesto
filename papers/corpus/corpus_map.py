#!/usr/bin/env python3
"""
corpus_map.py — L2 -> L3 under an EXTERNAL TRUST ROOT.

Addressing is not authority (Codex review f532023). Every credit-affecting operand is
now verified against a PINNED trust root supplied from outside the submitted report:

  trust_root = {report_id, corpus_commitment, extraction_closure,
                authorities: {completeness:[..], publication:[..], mapping:[..]},
                pinned_manifests: {claim: manifest_id}, mapper_closure}

- a coherent invented report/commitment fails REPORT_NOT_PINNED; a non-CLEAN report
  fails REPORT_NOT_CLEAN;
- the L2 bundle must be the FULL committed event set (subset -> SET_MISMATCH); the
  bundle id binds status+faults+ordered event records, so a status flip or index-address
  change fails BUNDLE_ID_MISMATCH; the runtime index is RECONSTRUCTED from the committed
  body, not a second mutable representation;
- completeness/publication/mapping decisions must be issued by an ADMITTED authority
  (self-issued -> AUTHORITY_NOT_ADMITTED); the required-unit manifest must equal the
  pinned manifest id for the claim (replacement -> MANIFEST_NOT_PINNED);
- records are finalized AFTER graph resolution, emitted as a self-contained private L3
  bundle {id, records:[{record_id, body}]} so L4 can replay from serialized L3 alone;
- the evaluation identity binds the mapper closure.

DERIVED is a proposal forever. With no admitted authority and no pinned manifest, every
real view is REFUSED — the honest state until governance is established.
"""
from collections import defaultdict
from pathlib import Path
import base64
import json

import corpus_ids as ids


def _reject_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"DUPLICATE_KEY:{k}")
        d[k] = v
    return d


def load_strict_json(path):
    """Governance operands (proposal, report, trust root) use the SAME strict profile as
    extraction: duplicate keys and non-finite constants are rejected (P1-6). A malformed
    operand raises ValueError — never a silent permissive parse."""
    def _no_const(tok):
        raise ValueError(f"NON_FINITE_CONSTANT:{tok}")
    return json.loads(Path(path).read_text(), object_pairs_hook=_reject_dupes, parse_constant=_no_const)


PROPOSAL_NONSEMANTIC = {"proposal_id", "generated", "note"}


def proposal_identity(proposal):
    """Closed semantic identity of an activation proposal (P1-6): hashes the WHOLE body —
    schema, for, operand, operand_digest, manifest, overlay_rows, trust_root_diff — excluding
    only the explicitly non-semantic commentary/time fields. A schema/for/profile mutation
    rotates the id."""
    return "prop:" + ids.json_digest({k: v for k, v in proposal.items()
                                      if k not in PROPOSAL_NONSEMANTIC})

# experiment_id (EXP-RVB-1c) is not present in the raw transcripts and cannot be evidenced;
# per the governance narrowing (operator, 2026-09-02) C2 is the OBSERVED-MODEL 4x2 unit, so the
# required-evidence components are the three that ARE in the transcript bytes. experiment_id stays
# an asserted field (1b/1c provenance AMBIGUOUS) — part of the mapping subject, not evidence-gated.
REQUIRED_COMPONENTS = ("root_digest", "verifier_identity", "agent_run_occurrence")
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
    "adjudication", "parent_local_ref"}
MANIFEST_FIELDS = {"claim", "paper_pin", "experiment_ids", "unit_key", "required_units", "allowed_exclusions"}
BLOCKING = {"NO_RAW_PROVENANCE", "SCHEMA_INVALID", "NO_EVENTS", "BAD_OCCURRENCE",
            "BAD_SAMPLING", "UNKNOWN_FIELD", "SILENT_DEFAULT", "BAD_LOCAL_REF",
            "AUTHORITY_NOT_ADMITTED", "DECISION_NOT_PINNED"}


def _schema_bytes():
    p = Path(__file__).resolve().parent.parent / "every-check-spawns-more" / "CORPUS-SCHEMA-0.1.md"
    return p.read_bytes() if p.exists() else b"MISSING_SCHEMA"


def mapper_closure_id():
    here = Path(__file__).resolve().parent
    return ids.closure_id("map", [
        ("corpus_map.py", (here / "corpus_map.py").read_bytes()),
        ("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
        ("CORPUS-SCHEMA-0.1.md", _schema_bytes())])


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


# ===================== trust root + report ===================== #
def recompute_report_id(report):
    try:
        return "erpt:" + ids.json_digest({
            "set_status": report["set_status"], "set_faults": report["set_faults"],
            "extraction_closure": report["extraction_closure"],
            "corpus_commitment": report["corpus_commitment"],
            "event_manifest": report["event_manifest"],
            "inventory_commitment": report["inventory_commitment"]})
    except (KeyError, TypeError):
        return None


TRUST_FIELDS = {"schema", "note", "report_id", "corpus_commitment", "extraction_closure",
                "l2_bundle_id", "authorities", "pinned_manifests", "decision_register",
                "mapper_closure"}


def validate_trust_root(tr):
    """Closed schema for the operator-selected trust root (P1-5). Malformed -> TRUST_ROOT_INVALID."""
    if not isinstance(tr, dict) or (set(tr) - TRUST_FIELDS):
        return "TRUST_ROOT_INVALID"
    for k in ("report_id", "corpus_commitment", "extraction_closure", "l2_bundle_id"):
        if not isinstance(tr.get(k), str) or not tr[k]:
            return "TRUST_ROOT_INVALID"
    auth = tr.get("authorities")
    if not isinstance(auth, dict) or (set(auth) - {"completeness", "publication", "mapping"}):
        return "TRUST_ROOT_INVALID"
    for v in auth.values():
        if not isinstance(v, list) or len(v) != len(set(v)):
            return "TRUST_ROOT_INVALID"
    pin = tr.get("pinned_manifests")
    if not isinstance(pin, dict) or not all(isinstance(x, str) for x in pin.values()):
        return "TRUST_ROOT_INVALID"
    reg = tr.get("decision_register", [])          # pinned exact decision-record ids (P0-3)
    if not isinstance(reg, list) or len(reg) != len(set(reg)) or not all(isinstance(x, str) for x in reg):
        return "TRUST_ROOT_INVALID"
    if "mapper_closure" in tr and not (isinstance(tr["mapper_closure"], str) and tr["mapper_closure"]):
        return "TRUST_ROOT_INVALID"                # optional; when present, binds the approved evaluator
    return None


DECISION_SCHEMA = {"completeness": {"adjudicator_identity", "authority", "decision"},
                   "publication": {"adjudicator_identity", "authority", "decision"},
                   "mapping": {"adjudicator_identity", "authority", "decision", "evidence_commitments"}}
_PRE_DECISION_OMIT = {"final_status", "final_faults", "completeness_decision",
                      "publication_decision", "mapping"}


def decision_record_id(kind, subject_id, dec):
    """Content id of a CLOSED decision body, bound to its exact pre-decision subject (P0-2/P0-3).
    Unknown/missing fields -> dec:INVALID (never a partial projection)."""
    if kind not in DECISION_SCHEMA or not isinstance(dec, dict) or set(dec) != DECISION_SCHEMA[kind]:
        return "dec:INVALID"
    body = dict(dec)
    if kind == "mapping":                          # evidence commitment is part of the identity
        body["evidence_commitments"] = sorted(body.get("evidence_commitments") or [])
    return "dec:" + ids.json_digest({"kind": kind, "subject": subject_id, "body": body})


def _content_subject(record_body):
    """The exact pre-decision proposition a completeness/publication decision is about."""
    return ids.json_digest({k: v for k, v in record_body.items() if k not in _PRE_DECISION_OMIT})


MAPPING_BODY_FIELDS = {"status", "act_id", "evidence_commitment", "adjudication"}
MAPPING_PROFILE = "manifesto.corpus.mapping.v0.2"


def _mapping_subject(record_body):
    """The exact PRE-DECISION mapping proposition: the act id + proposed status + four components
    + exact evidence commitment + mapping profile (P0-4). A change to any of these rotates it."""
    m = record_body.get("mapping") or {}
    return ids.json_digest({
        "content": _content_subject(record_body),
        "act_id": m.get("act_id"), "mapping_status": m.get("status"),
        "profile": MAPPING_PROFILE,
        "components": [record_body.get("experiment_id"), record_body.get("root_digest"),
                       record_body.get("verifier_identity"), record_body.get("agent_run_occurrence")],
        "evidence_commitment": m.get("evidence_commitment")})


def record_publishable(body, trust_root):
    """Publishability is a pure function of the FINAL record body + trust root — computed
    identically by build_l3 and L4 (closes P0-1: L4 re-checks the register, never trusts a
    baked-in EXACT). Requires EXACT + fault-free + admitted authority labels + all three
    decision-record ids (kind-specific subjects) pinned in the register."""
    if body.get("final_status") != "EXACT" or body.get("final_faults"):
        return False
    m = body.get("mapping")
    if not isinstance(m, dict) or set(m) != MAPPING_BODY_FIELDS:   # closed mapping schema
        return False
    if m.get("status") != "EXACT":                                # internal consistency (P0-4)
        return False
    comp = body.get("completeness_decision"); pub = body.get("publication_decision")
    adj = m.get("adjudication")
    if not (_decides(comp, "COMPLETE") and _decides(pub, "CLEARED_FOR_PUBLICATION")
            and isinstance(adj, dict)):
        return False
    A = trust_root.get("authorities") or {}
    if comp.get("authority") not in set(A.get("completeness", [])) \
            or pub.get("authority") not in set(A.get("publication", [])) \
            or adj.get("authority") not in set(A.get("mapping", [])):
        return False
    if not trust_root.get("mapper_closure") or body.get("mapper_closure") != trust_root["mapper_closure"]:
        return False                                  # a pinned+matching mapper is MANDATORY for credit
    reg = set(trust_root.get("decision_register", []))
    cs, ms = _content_subject(body), _mapping_subject(body)
    return (decision_record_id("completeness", cs, comp) in reg
            and decision_record_id("publication", cs, pub) in reg
            and decision_record_id("mapping", ms, adj) in reg)


def verify_report(report, trust_root):
    if not isinstance(report, dict) or not isinstance(trust_root, dict):
        return "MALFORMED_INPUT"
    rid = recompute_report_id(report)
    if rid is None or rid != report.get("report_id"):
        return "REPORT_TAMPERED"
    if rid != trust_root.get("report_id") or report["corpus_commitment"] != trust_root.get("corpus_commitment") \
            or report["extraction_closure"] != trust_root.get("extraction_closure"):
        return "REPORT_NOT_PINNED"
    if report.get("set_status") != "CLEAN":
        return "REPORT_NOT_CLEAN"
    return None


# ===================== L2 bundle (full, source + trust bound) ===================== #
def mint_l2_bundle(private_l2, report, trust_root):
    bad = verify_report(report, trust_root)
    if bad:
        return {"status": bad, "bundle_id": None, "body": None, "raw_bodies": {}, "faults": [{"code": bad}]}
    expected_closure = report["extraction_closure"]
    manifest = {(m["event_id"], m["body_digest"]): m for m in report["event_manifest"]}
    faults, seen, canon, raw_bodies = [], {}, [], {}
    per_blob = defaultdict(list)
    for data in (private_l2 or {}).values():
        for ev in data.get("events", []):
            try:
                raw = base64.b64decode(ev["raw_b64"]); bd = ids.line_digest(raw)
                eid = ids.event_id(ev["extraction_closure"], ev["blob_id"],
                                   int(ev["byte_start"]), int(ev["byte_end"]), bd)
            except Exception:  # noqa
                faults.append({"code": "MALFORMED_L2_ENTRY"}); continue
            if ev.get("event_id") != eid or bd != ev.get("line_digest"):
                faults.append({"code": "L2_INTEGRITY_BREAK"}); continue
            if ev["extraction_closure"] != expected_closure:
                faults.append({"code": "CLOSURE_MISMATCH"}); continue
            if (int(ev["byte_end"]) - int(ev["byte_start"])) != len(raw) or int(ev["byte_start"]) < 0:
                faults.append({"code": "IMPOSSIBLE_SPAN"}); continue
            if (eid, bd) not in manifest:
                faults.append({"code": "UNKNOWN_SOURCE"}); continue
            mrow = manifest[(eid, bd)]          # exact manifest-row equality (P0-2)
            if mrow.get("blob_id") != ev["blob_id"] or mrow.get("event_index") != int(ev["event_index"]):
                faults.append({"code": "EVENT_MANIFEST_MISMATCH"}); continue
            if eid in seen:
                faults.append({"code": "DUPLICATE_L2_EVENT"}); continue
            seen[eid] = True
            raw_bodies[bd] = raw
            per_blob[ev["blob_id"]].append(int(ev["event_index"]))
            canon.append({"event_id": eid, "blob_id": ev["blob_id"], "byte_start": int(ev["byte_start"]),
                          "byte_end": int(ev["byte_end"]), "body_digest": bd, "event_index": int(ev["event_index"])})
    for b, idxs in per_blob.items():
        if sorted(idxs) != list(range(len(idxs))):
            faults.append({"code": "INDEX_GAP", "blob_id": b})
    # FULL-SET equality with the committed manifest (P0-3 contract 1: full bundle).
    if set(seen) != {m["event_id"] for m in report["event_manifest"]}:
        faults.append({"code": "SET_MISMATCH"})
    canon.sort(key=lambda x: (x["blob_id"], x["event_index"]))
    status = "CLEAN" if not faults else "L2_REFUSED"
    body = {"status": status, "faults": faults, "report_id": report["report_id"],
            "commitment": report["corpus_commitment"], "expected_closure": expected_closure,
            "events": canon}
    return {"status": status, "bundle_id": "bnd:" + ids.json_digest(body),
            "body": body, "raw_bodies": raw_bodies, "faults": faults}


def verify_bundle(bundle, trust_root):
    if not isinstance(bundle, dict) or not isinstance(bundle.get("body"), dict) \
            or "bundle_id" not in bundle or "raw_bodies" not in bundle:
        return False, "MALFORMED_BUNDLE", {}
    tr_bad = validate_trust_root(trust_root)
    if tr_bad:
        return False, tr_bad, {}
    body = bundle["body"]
    if "bnd:" + ids.json_digest(body) != bundle["bundle_id"]:
        return False, "BUNDLE_ID_MISMATCH", {}
    if body.get("report_id") != trust_root.get("report_id") \
            or body.get("commitment") != trust_root.get("corpus_commitment"):
        return False, "BUNDLE_NOT_COMMITTED", {}
    if bundle["bundle_id"] != trust_root.get("l2_bundle_id"):   # pinned canonical full bundle (P0-1)
        return False, "BUNDLE_NOT_PINNED", {}
    if body.get("status") != "CLEAN":
        return False, body.get("status", "L2_REFUSED"), {}
    # reconstruct the index from the committed events (no second mutable representation)
    index = {}
    for e in body["events"]:
        raw = bundle["raw_bodies"].get(e["body_digest"])
        if raw is None or ids.line_digest(raw) != e["body_digest"]:
            return False, "INDEX_TAMPER", {}
        index[e["event_id"]] = {"blob_id": e["blob_id"], "byte_start": e["byte_start"],
                                "byte_end": e["byte_end"], "raw_bytes": raw,
                                "body_digest": e["body_digest"], "extraction_closure": body["expected_closure"]}
    return True, None, index


# ===================== evidence / authority ===================== #
def _evidence_record_digest(ev):
    return ids.json_digest({k: ev.get(k) for k in
                            ("kind", "event_id", "value_start", "value_end", "observed_value_digest")})


def _decodes_to(sub, val):
    try:
        return sub.decode("utf-8") == val
    except UnicodeDecodeError:
        return False


def _check_evidence(cand, index):
    validated, committed, faults = set(), set(), []
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
            validated.add(kind); committed.add(_evidence_record_digest(ev))
        else:
            faults.append("EVIDENCE_VALUE_MISMATCH")
    return validated, committed, faults


def _adjudication_ok(adj, committed_ev, trust_root):
    """Structural + evidence binding for an EXACT mapping (label admission + exact evidence).
    Register membership is enforced later, by record_publishable on the final record body."""
    if not isinstance(adj, dict) or set(adj) != DECISION_SCHEMA["mapping"]:
        return False, "EXACT_WITHOUT_ADJUDICATION"
    if not all(adj.get(k) for k in ("adjudicator_identity", "authority", "decision")):
        return False, "EXACT_WITHOUT_ADJUDICATION"
    if adj["decision"] != "EXACT":
        return False, "ADJUDICATION_DECISION"
    if adj["authority"] not in set((trust_root.get("authorities") or {}).get("mapping", [])):
        return False, "AUTHORITY_NOT_ADMITTED"
    if set(adj["evidence_commitments"]) != set(committed_ev):
        return False, "ADJUDICATION_MISMATCH"
    return True, None


def _validate_occurrences(cand, index):
    ordered, bodies, faults = [], [], []
    occ = cand.get("event_occurrences")
    if not isinstance(occ, list) or not occ:
        return [], [], ["NO_EVENTS"]
    for o in occ:
        if not (isinstance(o, dict) and _is_int(o.get("byte_start")) and _is_int(o.get("byte_end"))):
            faults.append("BAD_OCCURRENCE"); continue
        rec = index.get(o.get("event_id"))
        if rec is None or rec["blob_id"] != cand.get("blob_id") \
                or rec["byte_start"] != o["byte_start"] or rec["byte_end"] != o["byte_end"]:
            faults.append("NO_RAW_PROVENANCE"); continue
        ordered.append((o["event_id"], o["byte_start"], o["byte_end"])); bodies.append(rec["raw_bytes"])
    return ordered, bodies, faults


def _validate(cand, index, trust_root):
    """Provisional validation (pre-graph). Returns a mutable act dict; no final id yet."""
    if not isinstance(cand, dict):
        return {"local_ref": "?", "act_id": "act:INVALID", "experiment_id": None, "root_digest": None,
                "verifier_identity": None, "agent_run_occurrence": None, "status": "AMBIGUOUS",
                "parent_local_ref": None, "selected_child_refs": [], "faults": ["CANDIDATE_MALFORMED"],
                "cand": {}, "ordered": [], "committed_ev": set(),
                "completeness": None, "publication": None}
    f = []
    lr = cand.get("local_ref")
    if not isinstance(lr, str) or not lr:
        f.append("BAD_LOCAL_REF"); lr = str(lr)
    if set(cand) - CANDIDATE_FIELDS:
        f.append("UNKNOWN_FIELD")
    for k in ACTRECORD_REQUIRED:
        if k not in cand or cand[k] is None:
            f.append("SCHEMA_INVALID"); break

    ordered, bodies, of = _validate_occurrences(cand, index); f += of
    closure = index[ordered[0][0]]["extraction_closure"] if ordered and ordered[0][0] in index else "unknown"
    aid = ids.act_id(closure, cand.get("blob_id", ""), ordered, ids.content_digest(bodies)) if ordered else "act:INVALID"
    validated, committed_ev, ef = _check_evidence(cand, index); f += ef
    samp = cand.get("sampling", {})
    if not isinstance(samp, dict):
        f.append("BAD_SAMPLING")
    elif any(v != "UNKNOWN" for v in samp.values()):
        f.append("SILENT_DEFAULT")

    claimed = cand.get("mapping_status", "DERIVED")
    if claimed not in ("EXACT", "DERIVED"):
        f.append("BAD_STATUS"); status = "AMBIGUOUS"
    elif claimed == "EXACT":
        missing = [c for c in REQUIRED_COMPONENTS if c not in validated]
        adj_ok, adj_fault = _adjudication_ok(cand.get("adjudication"), committed_ev, trust_root)
        if not adj_ok:
            f.append(adj_fault); status = "AMBIGUOUS"
        elif missing or (BLOCKING & set(f)):
            f.append("EXACT_WITHOUT_EVIDENCE"); status = "AMBIGUOUS"
        else:
            status = "EXACT"
    else:
        status = "DERIVED"
    return {"local_ref": lr, "act_id": aid, "experiment_id": cand.get("experiment_id"),
            "root_digest": cand.get("root_digest"), "verifier_identity": cand.get("verifier_identity"),
            "agent_run_occurrence": cand.get("agent_run_occurrence"), "status": status,
            "parent_local_ref": cand.get("parent_local_ref"),
            "selected_child_refs": cand.get("selected_child_refs") or [],
            "faults": f, "cand": cand, "ordered": ordered, "committed_ev": committed_ev,
            "completeness": cand.get("completeness_decision"), "publication": cand.get("publication_decision")}


def _decides(dec, positive):
    return isinstance(dec, dict) and dec.get("decision") == positive


def _finalize_record(a, index, mclo):
    """Build the FINAL ActRecord {record_id, body} after graph resolution."""
    cand = a["cand"]
    ev_digest = ids.json_digest(sorted(a["committed_ev"]))
    body = {
        "mapper_closure": mclo, "local_ref": a["local_ref"],
        "final_status": a["status"], "final_faults": sorted(a["faults"]),
        "source": {"blob_id": cand.get("blob_id"),
                   "occurrences": [{"event_id": e, "byte_start": s, "byte_end": en,
                                    "body_digest": index.get(e, {}).get("body_digest")}
                                   for (e, s, en) in a["ordered"]]},
        "experiment_id": cand.get("experiment_id"), "root_id": cand.get("root_id"),
        "root_digest": cand.get("root_digest"), "parent_local_ref": cand.get("parent_local_ref"),
        "verifier_declared_identity": cand.get("verifier_declared_identity"),
        "verifier_observed_identity": cand.get("verifier_observed_identity"),
        "verifier_identity": cand.get("verifier_identity"),
        "agent_run_occurrence": cand.get("agent_run_occurrence"),
        "prompt_digest": cand.get("prompt_digest"), "response_digest": cand.get("response_digest"),
        "offspring_before_dedup": cand.get("offspring_before_dedup"),
        "dedup_removal_decisions": cand.get("dedup_removal_decisions"),
        "selected_child_refs": cand.get("selected_child_refs"), "sampling": cand.get("sampling"),
        "completeness_decision": a["completeness"], "publication_decision": a["publication"],
        "mapping": {"status": a["status"], "act_id": a["act_id"], "evidence_commitment": ev_digest,
                    "adjudication": cand.get("adjudication")}}
    rid = "rec:" + ids.json_digest(body)
    mid = ids.mapping_id(mclo, a["act_id"], a["experiment_id"] or "", a["root_digest"] or "",
                         a["verifier_identity"] or "", a["agent_run_occurrence"] or "",
                         ev_digest, a["status"], ids.json_digest(cand.get("adjudication") or {}))
    return rid, mid, body


# ===================== build ===================== #
def build_l3(bundle, table, manifests=None, trust_root=None):
    trust_root = trust_root or {}
    ok, reason, index = verify_bundle(bundle, trust_root)
    if not ok:
        return {"metadata_report": {"bundle_ok": False, "bundle_fault": reason, "acts": [],
                "views": {c: {"status": "REFUSED", "reason": reason} for c in ("C1", "C3", "C2", "C4", "C7")}},
                "private_l3": {"l3_bundle_id": None, "records": []}}
    acts = [_validate(c, index, trust_root) for c in (table or [])]

    for lr, g in _by(acts, "local_ref").items():
        if len(g) > 1:
            for a in g:
                a["faults"].append("DUPLICATE_LOCAL_REF"); a["status"] = "AMBIGUOUS"
    for aid, g in _by(acts, "act_id").items():
        if aid != "act:INVALID" and len(g) > 1:
            for a in g:
                a["faults"].append("DUPLICATE_ID"); a["status"] = "AMBIGUOUS"
    live = {a["local_ref"] for a in acts if "DUPLICATE_LOCAL_REF" not in a["faults"]}
    for a in acts:
        if a["parent_local_ref"] is not None and a["parent_local_ref"] not in live:
            a["faults"].append("DANGLING_PARENT"); a["status"] = "AMBIGUOUS"
        for c in a["selected_child_refs"]:
            if c not in live:
                a["faults"].append("DANGLING_CHILD"); a["status"] = "AMBIGUOUS"
    grp = defaultdict(list)
    for a in acts:
        if a["status"] in ("EXACT", "DERIVED"):
            grp[(a["experiment_id"], a["root_digest"], a["verifier_identity"])].append(a)
    for g in grp.values():
        if len({a["agent_run_occurrence"] for a in g}) > 1:
            for a in g:
                a["status"] = "CONFLICTED"; a["faults"].append("REPEATED_RUN")

    mclo = mapper_closure_id()
    records = []
    for a in acts:                                    # finalize AFTER graph resolution
        rid, mid, body = _finalize_record(a, index, mclo)
        a["record_id"], a["mapping_id"], a["body"] = rid, mid, body
        records.append({"record_id": rid, "body": body})
    local_ref_index = {a["local_ref"]: a["record_id"] for a in acts}   # closed topology index (P1-4)
    l3_bundle_id = "l3:" + ids.json_digest({"mapper_closure": mclo, "l2_bundle_id": bundle["bundle_id"],
                                            "local_ref_index": local_ref_index,
                                            "records": sorted(r["record_id"] for r in records)})
    claims = ("C1", "C3", "C2", "C4", "C7", *sorted(set(manifests or {}) - {"C1", "C3", "C2", "C4", "C7"}))
    views = {c: _view(c, acts, (manifests or {}).get(c), bundle, trust_root, mclo) for c in claims}
    meta = {"schema": "manifesto.corpus.act-graph-report.v0", "bundle_ok": True,
            "l2_bundle_id": bundle["bundle_id"], "l3_bundle_id": l3_bundle_id, "mapper_closure": mclo,
            "act_count": len(acts), "fault_count": sum(len(a["faults"]) for a in acts),
            "faults": [{"local_ref": a["local_ref"], "faults": a["faults"]} for a in acts if a["faults"]],
            "views": views,
            "acts": [{k: a[k] for k in ("local_ref", "act_id", "record_id", "mapping_id",
                      "experiment_id", "status", "faults")} for a in acts]}
    return {"metadata_report": meta,
            "private_l3": {"l3_bundle_id": l3_bundle_id, "mapper_closure": mclo,
                           "l2_bundle_id": bundle["bundle_id"], "local_ref_index": local_ref_index,
                           "records": records}}


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
    if not isinstance(m["required_units"], list) or not m["required_units"]:
        return "EMPTY_REQUIRED_SET"
    seen = set()
    for u in m["required_units"]:
        if not (isinstance(u, (list, tuple)) and len(u) == len(m["unit_key"])):
            return "MALFORMED_MANIFEST"
        if tuple(u) in seen:
            return "DUPLICATE_REQUIRED_UNIT"
        seen.add(tuple(u))
    return None


def manifest_id(m):
    return "man:" + ids.json_digest(m)


def _publishable(a, trust_root):
    return record_publishable(a.get("body") or {}, trust_root)


def _view(claim, acts, manifest, bundle, trust_root, mclo):
    if manifest is None:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_UNSPECIFIED"}
    bad = validate_manifest(manifest)
    if bad:
        return {"status": "REFUSED", "reason": bad}
    if manifest["claim"] != claim:
        return {"status": "REFUSED", "reason": "MANIFEST_CLAIM_MISMATCH"}
    mid = manifest_id(manifest)
    if mid != (trust_root.get("pinned_manifests") or {}).get(claim):
        return {"status": "REFUSED", "reason": "MANIFEST_NOT_PINNED", "manifest_id": mid}
    key = manifest["unit_key"]
    required = {tuple(u) for u in manifest["required_units"]}
    allowed_extra = {tuple(u) for u in manifest.get("allowed_exclusions", [])}

    def unit(a):
        return tuple(a.get(k) for k in key)
    # select by the GOVERNED unit cohort, not by an (unevidenced) experiment_id label (P1-6):
    rel = [a for a in acts if unit(a) in required]
    present_any = {unit(a) for a in rel}
    ok_acts = [a for a in rel if _publishable(a, trust_root)]
    present_ok = {unit(a) for a in ok_acts}
    base = {"manifest_id": mid, "paper_pin": manifest["paper_pin"], "l2_bundle_id": bundle["bundle_id"]}
    if required - present_any:
        return {"status": "REFUSED", "reason": "REQUIRED_UNITS_MISSING",
                "missing": sorted(map(list, required - present_any)), **base}
    if (required & present_any) - present_ok:
        return {"status": "REFUSED", "reason": "INCOMPLETE_TREE",
                "incomplete": sorted(map(list, (required & present_any) - present_ok)), **base}
    if present_ok - required - allowed_extra:
        return {"status": "REFUSED", "reason": "UNEXPECTED_UNITS", **base}
    # one run occurrence must not satisfy more than one required unit (view-scoped
    # run-uniqueness; residual #2 from the C2 rows review). A chain's multiple depth
    # acts legitimately share a run, so this is per-unit, not a blanket act rule.
    runs = [a["agent_run_occurrence"] for a in ok_acts if unit(a) in required]
    if len(runs) != len(set(runs)):
        return {"status": "REFUSED", "reason": "DUPLICATE_RUN_ACROSS_UNITS", **base}
    eval_id = "eval:" + ids.json_digest({"mapper_closure": mclo, "manifest_id": mid,
              "l2_bundle_id": bundle["bundle_id"], "corpus_commitment": trust_root.get("corpus_commitment"),
              "record_ids": sorted(a["record_id"] for a in ok_acts)})
    return {"status": "COMPLETE", "units": len(required), "evaluation_id": eval_id, **base}


def make_public_projection(source_act_id, redaction_profile_id, public_body, loss_report, proposed_id=None):
    if not loss_report:
        return {"status": "FAIL", "reason": "MISSING_LOSS_REPORT"}
    if not public_body:
        return {"status": "FAIL", "reason": "EMPTY_PUBLIC_BODY"}
    if proposed_id is not None and proposed_id == source_act_id:
        return {"status": "FAIL", "reason": "REDACTION_ID_REUSE"}
    return {"status": "OK", "derived_from": source_act_id,
            "public_id": ids.public_id(mapper_closure_id(), source_act_id, redaction_profile_id,
                                       ids._h(b"public-body", public_body), ids.json_digest(loss_report))}
