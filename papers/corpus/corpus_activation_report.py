#!/usr/bin/env python3
"""
corpus_activation_report.py — generate the machine-local C2-MAP ACTIVATION-REPORT.

Deterministic. Binds, in one content-addressed artifact, the completed proof construction
for a C2-MAP activation: the 0.2 operand digest + proposal id, the extraction report /
quarantine receipt / corpus + L2 commitments, all 24 evidence spans and their revalidation
results, the manifest / mapper closure / decision ids / exact trust_root_diff, the baseline
(C2-MAP REFUSED, 0 EXACT) and the applied-proposal (C2-MAP COMPLETE, 8 EXACT, L4 evaluation
id match), the MANDATORY C2-MEAS REFUSED: MEASUREMENT_NOT_REPLAYED, and a generator/schema
closure + a metadata-only check.

TERMINOLOGY: this is a machine-local ACTIVATION-REPORT, NOT a receipt in the authenticity
sense. It does NOT change the trust root. Only after the report is committed and the operator
act addressably pins it does the governance act itself become a receipt-like artifact.

Run (machine-local, needs the quarantine): `python3 papers/corpus/corpus_activation_report.py`.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids
from corpus_extract import extract_from_quarantine
from corpus_map import (mint_l2_bundle, verify_bundle, build_l3, manifest_id, mapper_closure_id,
                        _content_subject, _mapping_subject, decision_record_id,
                        load_strict_json, proposal_identity, recompute_report_id, validate_manifest)
from corpus_l4 import l4_evaluate, validate_l3_bundle

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "papers" / "every-check-spawns-more"
QDIR = Path.home() / ".manifesto-corpus-quarantine"
GEN_DATE = "2026-09-02"     # constant -> deterministic


def _sha(p):
    return "sha256:" + hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _generator_closure():
    here = Path(__file__).resolve().parent
    return ids.closure_id("activation-report", [
        ("corpus_activation_report.py", Path(__file__).read_bytes()),
        ("corpus_map.py", (here / "corpus_map.py").read_bytes()),
        ("corpus_l4.py", (here / "corpus_l4.py").read_bytes()),
        ("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
        ("corpus_extract.py", (here / "corpus_extract.py").read_bytes()),
        ("CORPUS-SCHEMA-0.1.md", (PAPER / "CORPUS-SCHEMA-0.1.md").read_bytes())])


def generate():
    report = load_strict_json(PAPER / "CORPUS-EXTRACTION-REPORT.json")
    tr = load_strict_json(PAPER / "CORPUS-TRUST-ROOT.json")
    operand = load_strict_json(PAPER / "CORPUS-C2-MAPPING-0.2.json")
    proposal = load_strict_json(PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
    inventory = load_strict_json(PAPER / "CORPUS-SOURCE-INVENTORY.json")
    receipt = load_strict_json(PAPER / "CORPUS-QUARANTINE-RECEIPT.json")   # P1-6: strict here too
    rows, overlay = operand["rows"], proposal["overlay_rows"]
    man = proposal["manifest"]
    diff = proposal["trust_root_diff"]

    # authenticated L2 bundle from the quarantine bytes
    private, rep2 = extract_from_quarantine(QDIR, receipt, inventory)
    assert rep2["report_id"] == report["report_id"], "report drift"
    bundle = mint_l2_bundle(private, report, tr)
    ok, reason, index = verify_bundle(bundle, tr)
    assert ok, reason

    # revalidate every evidence span against the raw quarantine bytes
    span_results, all_spans_ok = [], True
    for r in rows:
        for e in r["mapping_evidence"]:
            rec = index.get(e["event_id"])
            passed = False
            if rec is not None and rec["byte_start"] <= e["value_start"] <= e["value_end"] <= rec["byte_end"]:
                sub = rec["raw_bytes"][e["value_start"] - rec["byte_start"]: e["value_end"] - rec["byte_start"]]
                digest_ok = (ids._h(b"value", sub) == e["observed_value_digest"])
                if e["kind"] == "root_digest":
                    val_ok = (ids.raw_sha256(sub) == r["root_digest"])
                else:
                    try:
                        val_ok = (sub.decode("utf-8") == r[e["kind"]])
                    except UnicodeDecodeError:
                        val_ok = False
                passed = digest_ok and val_ok
            all_spans_ok = all_spans_ok and passed
            span_results.append({"local_ref": r["local_ref"], "kind": e["kind"],
                                 "event_id": e["event_id"],
                                 "byte_span": [e["value_start"], e["value_end"]],
                                 "observed_value_digest": e["observed_value_digest"], "verified": passed})

    # baseline: DERIVED operand under the committed empty trust root
    base = build_l3(bundle, rows, {"C2-MAP": man}, tr)["metadata_report"]
    base_view = base["views"]["C2-MAP"]
    base_exact = sum(a["status"] == "EXACT" for a in base["acts"])

    # applied: the proposal's trust_root_diff over the explicit EXACT overlay
    act_tr = {**tr, **diff}
    act = build_l3(bundle, overlay, {"C2-MAP": man}, act_tr)
    act_view = act["metadata_report"]["views"]["C2-MAP"]
    act_exact = sum(a["status"] == "EXACT" for a in act["metadata_report"]["acts"])
    l4 = l4_evaluate(act["private_l3"], {"C2-MAP": man}, act_tr)["views"]["C2-MAP"]
    applied_l3_id = act["private_l3"]["l3_bundle_id"]
    applied_record_ids = [r["record_id"] for r in act["private_l3"]["records"]]

    # Emit the serialized applied L3 as an INDEPENDENTLY-ADDRESSED, metadata-only operand
    # (no transcript bytes) so the quarantine-free verifier can RECOMPUTE every record id, the
    # l3 bundle id, and rerun L4 to recompute the evaluation id + vector (closes forged-id path).
    serialized_l3 = act["private_l3"]
    assert not any(k in json.dumps(serialized_l3) for k in ("raw_b64", '"content"', '"text"')), "L3 leak"
    (PAPER / "CORPUS-C2-MAP-L3-0.1.json").write_text(json.dumps(serialized_l3, indent=1, ensure_ascii=False))

    # mandatory: C2-MEAS is not claimed by this path. Record the engine's ACTUAL typed result
    # (do NOT overwrite it with a stronger authored reason — P0-1); the normative reading is a
    # SEPARATE, explicitly-authored policy_projection field.
    meas = build_l3(bundle, overlay, {}, act_tr)["metadata_report"]["views"]["C2"]
    meas_engine_reason = meas.get("reason")

    body = {
        "schema": "manifesto.corpus.c2-map-activation-report.v0.1",
        "kind": "ACTIVATION-REPORT (machine-local; NOT an authenticity receipt)",
        "generated": GEN_DATE, "generator_closure": _generator_closure(),
        "operand": {"file": "CORPUS-C2-MAPPING-0.2.json",
                    "digest": _sha(PAPER / "CORPUS-C2-MAPPING-0.2.json")},
        "proposal": {"file": "CORPUS-C2-MAP-ACTIVATION-0.1.json",
                     "proposal_id": proposal["proposal_id"],
                     "digest": _sha(PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json"),
                     "operand_digest_bound": proposal["operand_digest"] == _sha(PAPER / "CORPUS-C2-MAPPING-0.2.json"),
                     "proposal_identity_recomputes": proposal_identity(proposal) == proposal["proposal_id"]},
        "provenance": {"extraction_report_id": report["report_id"],
                       "corpus_commitment": report["corpus_commitment"],
                       "inventory_commitment": report["inventory_commitment"],
                       "l2_bundle_id": tr["l2_bundle_id"],
                       "quarantine_receipt_digest": _sha(PAPER / "CORPUS-QUARANTINE-RECEIPT.json"),
                       "l2_bundle_verified": ok, "events_total": len(bundle["body"]["events"])},
        "serialized_l3": {"file": "CORPUS-C2-MAP-L3-0.1.json",
                          "digest": _sha(PAPER / "CORPUS-C2-MAP-L3-0.1.json"),
                          "l3_bundle_id": applied_l3_id},
        "evidence": {"span_count": len(span_results), "all_verified": all_spans_ok,
                     "spans": span_results},
        "activation": {"manifest": man, "manifest_id": manifest_id(man),
                       "mapper_closure": diff["mapper_closure"],
                       "mapper_closure_matches_current": diff["mapper_closure"] == mapper_closure_id(),
                       "authorities": diff["authorities"], "decision_register": diff["decision_register"],
                       "trust_root_diff": diff},
        "result_vector": {
            "baseline": {"C2-MAP": base_view["status"], "exact_acts": base_exact},
            "applied": {"C2-MAP": act_view["status"], "exact_acts": act_exact,
                        "evaluation_id": act_view.get("evaluation_id"),
                        "l3_bundle_id": applied_l3_id, "record_ids": applied_record_ids,
                        "l4_C2-MAP": l4["status"], "l4_evaluation_id_matches": l4.get("evaluation_id") == act_view.get("evaluation_id")},
            "C2-MEAS": {"status": meas["status"], "engine_reason": meas_engine_reason,
                        "policy_projection": "MEASUREMENT_NOT_REPLAYED",
                        "note": "engine_reason is the engine's ACTUAL typed result for the unclaimed "
                                "measurement view (no C2-MEAS manifest); policy_projection is the "
                                "authored normative reading, kept SEPARATE (P0-1). offspring/dedup/o-hat "
                                "are not extracted or derived by this path; greening C2-MEAS from "
                                "C2-MAP would be composition laundering."}},
        "assertions": {
            "all_24_spans_verified": all_spans_ok and len(span_results) == 24,
            "baseline_refused_zero_exact": base_view["status"] == "REFUSED" and base_exact == 0,
            "applied_complete_eight_exact": act_view["status"] == "COMPLETE" and act_exact == 8,
            "l4_reproduces": l4["status"] == "COMPLETE" and l4.get("evaluation_id") == act_view.get("evaluation_id"),
            "c2_meas_refused": meas["status"] == "REFUSED",
            "c2_meas_engine_reason_preserved": meas_engine_reason is not None
                and meas_engine_reason != "MEASUREMENT_NOT_REPLAYED",
            "proposal_identity_recomputes": proposal_identity(proposal) == proposal["proposal_id"],
            "committed_operand_stays_derived": all(r["mapping_status"] == "DERIVED" for r in rows),
            "trust_root_unchanged": tr.get("decision_register") == [] and not tr.get("authorities", {}).get("mapping")},
    }
    body["metadata_only"] = not any(k in json.dumps(body) for k in ("raw_b64", '"content"', '"text"'))
    report_id = "arpt:" + ids.json_digest(body)
    out = {"report_id": report_id, **body}
    (PAPER / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False))
    return out


def verify_activation_report(paper=PAPER):
    """Independent, quarantine-FREE verification of the committed activation report (P0-2).

    RECOMPUTES every non-raw relation and cross-checks it against the OTHER committed artifacts
    (proposal, operand, extraction report, committed trust root, receipt) — it never trusts the
    report's own stored booleans. A coherent single-file re-forge (e.g. forged l2_bundle_id +
    emptied registers with only report_id recomputed) fails here, because the forged field no
    longer matches the independently-recomputed value or the other pinned artifact.

    Raw-byte SPAN truth stays machine-local (revalidated by generate() against the quarantine);
    this function checks that the report's span SET equals the operand's exact closed set and that
    every recomputable id/commitment/relation holds. Returns (ok, faults)."""
    F = []

    def need(cond, code):
        if not cond:
            F.append(code)
        return cond
    try:
        ar = load_strict_json(paper / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json")
        prop = load_strict_json(paper / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
        operand = load_strict_json(paper / "CORPUS-C2-MAPPING-0.2.json")
        tr = load_strict_json(paper / "CORPUS-TRUST-ROOT.json")
        erpt = load_strict_json(paper / "CORPUS-EXTRACTION-REPORT.json")
    except (ValueError, FileNotFoundError) as e:
        return False, [f"STRICT_JSON:{e}"]

    # 1. report identity recomputes over its own body (necessary, NOT sufficient on its own)
    body = {k: v for k, v in ar.items() if k != "report_id"}
    need(ar.get("report_id") == "arpt:" + ids.json_digest(body), "REPORT_ID_MISMATCH")
    need(ar.get("generator_closure") == _generator_closure(), "GENERATOR_CLOSURE_MISMATCH")
    need(ar.get("metadata_only") is True, "NOT_METADATA_ONLY")

    # 2. operand + proposal digests and CLOSED proposal identity (P1-6)
    op_sha = _sha(paper / "CORPUS-C2-MAPPING-0.2.json")
    pr_sha = _sha(paper / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
    need(ar.get("operand", {}).get("digest") == op_sha == prop.get("operand_digest"), "OPERAND_DIGEST_MISMATCH")
    need(ar.get("proposal", {}).get("digest") == pr_sha, "PROPOSAL_DIGEST_MISMATCH")
    need(proposal_identity(prop) == prop.get("proposal_id")
         == ar.get("proposal", {}).get("proposal_id"), "PROPOSAL_ID_MISMATCH")

    # 3. activation binds the proposal EXACTLY (manifest, diff, register, mapper)
    diff = prop.get("trust_root_diff", {})
    man = prop.get("manifest", {})
    act = ar.get("activation", {})
    need(act.get("manifest") == man, "MANIFEST_MISMATCH")
    need(validate_manifest(man) is None, "MANIFEST_INVALID")
    need(act.get("manifest_id") == manifest_id(man)
         == (diff.get("pinned_manifests") or {}).get("C2-MAP"), "MANIFEST_ID_MISMATCH")
    need(act.get("trust_root_diff") == diff, "DIFF_MISMATCH")
    reg = diff.get("decision_register", [])
    need(act.get("decision_register") == reg, "REGISTER_MISMATCH")
    need(len(reg) == 24 and len(set(reg)) == 24, "REGISTER_NOT_24")
    need(act.get("mapper_closure") == diff.get("mapper_closure") == mapper_closure_id(), "MAPPER_MISMATCH")

    # 4. provenance is pinned to the committed extraction report + trust root + receipt
    prov = ar.get("provenance", {})
    need(recompute_report_id(erpt) == erpt.get("report_id") == prov.get("extraction_report_id"), "EXTRACTION_ID_MISMATCH")
    need(prov.get("corpus_commitment") == erpt.get("corpus_commitment"), "CORPUS_COMMITMENT_MISMATCH")
    need(prov.get("inventory_commitment") == erpt.get("inventory_commitment"), "INVENTORY_COMMITMENT_MISMATCH")
    need(prov.get("l2_bundle_id") == tr.get("l2_bundle_id"), "L2_NOT_PINNED_TO_TRUST_ROOT")
    need(prov.get("quarantine_receipt_digest") == _sha(paper / "CORPUS-QUARANTINE-RECEIPT.json"), "RECEIPT_DIGEST_MISMATCH")

    # 5. the evidence-span SET equals the operand's exact closed 24-set (raw truth is machine-local),
    #    AND the report's OWN typed verdict must be POSITIVE — a report that says every span failed
    #    cannot support a claim whose evidence class asserts the spans were revalidated (P0-1).
    ev = ar.get("evidence", {})
    spans = ev.get("spans", [])
    want = {(r["local_ref"], e["kind"], e["event_id"], e["value_start"], e["value_end"],
             e["observed_value_digest"]) for r in operand.get("rows", []) for e in r["mapping_evidence"]}
    got = {(s["local_ref"], s["kind"], s["event_id"], s["byte_span"][0], s["byte_span"][1],
            s["observed_value_digest"]) for s in spans}
    need(len(want) == 24 and want == got, "EVIDENCE_SPAN_SET_MISMATCH")
    need(ev.get("all_verified") is True and ev.get("span_count") == 24
         and len(spans) == 24 and all(s.get("verified") is True for s in spans)
         and ar.get("assertions", {}).get("all_24_spans_verified") is True, "SPAN_VERDICT_NOT_POSITIVE")

    # 5b. RECOMPUTE the result addresses from the committed serialized L3 operand and rerun L4 under
    #     the proposal-applied root (independent of whether the live root is applied yet). Forged
    #     l3/record/evaluation ids no longer pass; the 24-id register (bound by proposal_id) anchors
    #     publishability, so a fabricated coherent L3 cannot yield COMPLETE (P0-2).
    try:
        l3 = load_strict_json(paper / "CORPUS-C2-MAP-L3-0.1.json")
    except (ValueError, FileNotFoundError) as e:
        return False, F + [f"L3_OPERAND:{e}"]
    need(_sha(paper / "CORPUS-C2-MAP-L3-0.1.json") == ar.get("serialized_l3", {}).get("digest"), "L3_DIGEST_MISMATCH")
    l3_ok, l3_reason, _ = validate_l3_bundle(l3)              # recomputes every record id + l3 bundle id
    need(l3_ok, f"L3_INVALID:{l3_reason}")
    need(l3.get("l2_bundle_id") == tr.get("l2_bundle_id"), "L3_L2_NOT_PINNED")
    applied_root = {**{k: tr[k] for k in ("schema", "note", "report_id", "corpus_commitment",
                    "extraction_closure", "l2_bundle_id") if k in tr},
                    "authorities": diff["authorities"], "pinned_manifests": diff["pinned_manifests"],
                    "mapper_closure": diff["mapper_closure"], "decision_register": diff["decision_register"]}
    l4 = l4_evaluate(l3, {"C2-MAP": man}, applied_root).get("views", {}).get("C2-MAP", {})
    app = ar.get("result_vector", {}).get("applied", {})
    need(l3.get("l3_bundle_id") == app.get("l3_bundle_id") == ar.get("serialized_l3", {}).get("l3_bundle_id"), "L3_ID_REPORT_MISMATCH")
    need(sorted(r["record_id"] for r in l3.get("records", [])) == sorted(app.get("record_ids") or []), "RECORD_ID_SET_MISMATCH")
    need(l4.get("status") == "COMPLETE" and l4.get("evaluation_id") == app.get("evaluation_id"), "L4_RECOMPUTE_MISMATCH")

    # 6. C2-MEAS keeps the engine's ACTUAL reason (P0-1); no laundering
    meas = ar.get("result_vector", {}).get("C2-MEAS", {})
    need(meas.get("status") == "REFUSED", "C2_MEAS_NOT_REFUSED")
    need(meas.get("engine_reason") and meas.get("engine_reason") != "MEASUREMENT_NOT_REPLAYED"
         and meas.get("policy_projection") == "MEASUREMENT_NOT_REPLAYED", "ENGINE_REASON_NOT_PRESERVED")

    # 7. applied vector is internally coherent (COMPLETE / 8 EXACT / 8 record ids / L4 match)
    rv = ar.get("result_vector", {})
    base_v, app = rv.get("baseline", {}), rv.get("applied", {})
    need(base_v.get("C2-MAP") == "REFUSED" and base_v.get("exact_acts") == 0, "BASELINE_NOT_REFUSED")
    need(app.get("C2-MAP") == "COMPLETE" and app.get("exact_acts") == 8, "APPLIED_NOT_COMPLETE")
    need(app.get("l4_C2-MAP") == "COMPLETE" and app.get("l4_evaluation_id_matches") is True, "L4_NOT_REPRODUCED")
    rids = app.get("record_ids") or []
    need(isinstance(app.get("l3_bundle_id"), str) and app["l3_bundle_id"].startswith("l3:"), "L3_ID_MISSING")
    need(len(rids) == 8 and len(set(rids)) == 8, "RECORD_IDS_NOT_8")
    need(bool(app.get("evaluation_id")), "EVALUATION_ID_MISSING")
    return len(F) == 0, F


if __name__ == "__main__":
    r = generate()
    a = r["assertions"]
    print("report_id:", r["report_id"][:28])
    for k, v in a.items():
        print(f"  {'ok ' if v else 'XX '} {k}")
    print("metadata_only:", r["metadata_only"])
    vok, vf = verify_activation_report()
    print("independent verify_activation_report:", "PASS" if vok else f"FAIL {vf}")
    ok_all = all(a.values()) and r["metadata_only"] and vok
    print("ACTIVATION-REPORT:", "COMPLETE PROOF (machine-local; trust root unchanged)" if ok_all else "INCOMPLETE")
    sys.exit(0 if ok_all else 1)
