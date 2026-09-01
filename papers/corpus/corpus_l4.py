#!/usr/bin/env python3
"""
corpus_l4.py — validate a serialized private L3 bundle and reproduce a claim view from
L3 ALONE (no candidate table). Closes P1-4: "L4 can replay" is demonstrated, not asserted.

`validate_l3_bundle` recomputes every record id from its body, recomputes the l3 bundle id
(binding mapper closure, l2 bundle id, the closed local-ref index, and the exact record
set), and resolves parent/child topology through that index — a removed/edited record or a
dangling ref fails typed.

`l4_evaluate` reconstructs the acts from the record bodies and runs the SAME `_view` logic
as `build_l3`, so a serialized L3 (with the candidate table deleted) reproduces the exact
claim-view vector, or refuses typed.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids
import corpus_map as cm


def validate_l3_bundle(private_l3):
    if not isinstance(private_l3, dict) or not all(
            k in private_l3 for k in ("l3_bundle_id", "mapper_closure", "l2_bundle_id",
                                      "local_ref_index", "records")):
        return False, "MALFORMED_L3", {}
    recs = private_l3["records"]
    if not isinstance(recs, list):
        return False, "MALFORMED_L3", {}
    by_ref = {}
    for r in recs:
        if not isinstance(r, dict) or "record_id" not in r or not isinstance(r.get("body"), dict):
            return False, "MALFORMED_L3", {}
        if "rec:" + ids.json_digest(r["body"]) != r["record_id"]:
            return False, "RECORD_ID_MISMATCH", {}
        lr = r["body"].get("local_ref")
        if private_l3["local_ref_index"].get(lr) != r["record_id"]:
            return False, "LOCAL_REF_INDEX_MISMATCH", {}
        by_ref[lr] = r
    recomputed = "l3:" + ids.json_digest({
        "mapper_closure": private_l3["mapper_closure"], "l2_bundle_id": private_l3["l2_bundle_id"],
        "local_ref_index": private_l3["local_ref_index"],
        "records": sorted(r["record_id"] for r in recs)})
    if recomputed != private_l3["l3_bundle_id"]:
        return False, "L3_BUNDLE_MISMATCH", {}       # record removed/added/edited
    idx = private_l3["local_ref_index"]
    for r in recs:
        b = r["body"]
        if b.get("parent_local_ref") is not None and b["parent_local_ref"] not in idx:
            return False, "DANGLING_REF", {}
        for c in b.get("selected_child_refs") or []:
            if c not in idx:
                return False, "DANGLING_REF", {}
    return True, None, by_ref


def _act_from_body(b, record_id):
    # carry the full body so publishability (register membership, mapper closure, subjects)
    # is re-derived by the SAME record_publishable used by build_l3 — L4 never trusts final_status.
    return {"experiment_id": b.get("experiment_id"), "root_digest": b.get("root_digest"),
            "verifier_identity": b.get("verifier_identity"),
            "agent_run_occurrence": b.get("agent_run_occurrence"),
            "status": b.get("final_status"), "faults": list(b.get("final_faults") or []),
            "act_id": (b.get("mapping") or {}).get("act_id"), "record_id": record_id,
            "local_ref": b.get("local_ref"), "body": b}


def l4_evaluate(private_l3, manifests, trust_root):
    """Reproduce the claim views from serialized L3 ONLY. Returns {status/views}."""
    tr_bad = cm.validate_trust_root(trust_root)
    if tr_bad:
        return {"l3_ok": False, "reason": tr_bad, "views": {}}
    ok, reason, _ = validate_l3_bundle(private_l3)
    if not ok:
        return {"l3_ok": False, "reason": reason,
                "views": {c: {"status": "REFUSED", "reason": reason} for c in ("C1", "C3", "C2", "C4", "C7")}}
    # P0-5: bind the serialized top-level provenance to the trust root and to every record,
    # otherwise a coherent re-forge of l2_bundle_id/mapper_closure could return positive credit.
    def _refuse(rs):
        return {"l3_ok": False, "reason": rs,
                "views": {c: {"status": "REFUSED", "reason": rs} for c in ("C1", "C3", "C2", "C4", "C7")}}
    mclo = private_l3.get("mapper_closure")
    if private_l3.get("l2_bundle_id") != trust_root.get("l2_bundle_id"):
        return _refuse("L2_NOT_PINNED")
    if trust_root.get("mapper_closure"):             # credit-capable root: bind the mapper exactly
        if mclo != trust_root["mapper_closure"]:
            return _refuse("MAPPER_NOT_PINNED")
        if any(r["body"].get("mapper_closure") != mclo for r in private_l3["records"]):
            return _refuse("MAPPER_MISMATCH")
    acts = [_act_from_body(r["body"], r["record_id"]) for r in private_l3["records"]]
    stub_bundle = {"bundle_id": private_l3["l2_bundle_id"]}
    claims = ("C1", "C3", "C2", "C4", "C7",
              *sorted(set(manifests or {}) - {"C1", "C3", "C2", "C4", "C7"}))
    views = {c: cm._view(c, acts, (manifests or {}).get(c), stub_bundle, trust_root, mclo) for c in claims}
    return {"l3_ok": True, "l3_bundle_id": private_l3["l3_bundle_id"], "views": views}
