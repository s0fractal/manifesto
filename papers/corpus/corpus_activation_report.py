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
                        _content_subject, _mapping_subject, decision_record_id)
from corpus_l4 import l4_evaluate

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
    report = json.loads((PAPER / "CORPUS-EXTRACTION-REPORT.json").read_text())
    tr = json.loads((PAPER / "CORPUS-TRUST-ROOT.json").read_text())
    operand = json.loads((PAPER / "CORPUS-C2-MAPPING-0.2.json").read_text())
    proposal = json.loads((PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json").read_text())
    inventory = json.loads((PAPER / "CORPUS-SOURCE-INVENTORY.json").read_text())
    receipt = json.loads((PAPER / "CORPUS-QUARANTINE-RECEIPT.json").read_text())
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

    # mandatory: C2-MEAS is not claimed by this path
    meas = build_l3(bundle, overlay, {}, act_tr)["metadata_report"]["views"]["C2"]

    body = {
        "schema": "manifesto.corpus.c2-map-activation-report.v0.1",
        "kind": "ACTIVATION-REPORT (machine-local; NOT an authenticity receipt)",
        "generated": GEN_DATE, "generator_closure": _generator_closure(),
        "operand": {"file": "CORPUS-C2-MAPPING-0.2.json",
                    "digest": _sha(PAPER / "CORPUS-C2-MAPPING-0.2.json")},
        "proposal": {"file": "CORPUS-C2-MAP-ACTIVATION-0.1.json",
                     "proposal_id": proposal["proposal_id"],
                     "digest": _sha(PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json"),
                     "operand_digest_bound": proposal["operand_digest"] == _sha(PAPER / "CORPUS-C2-MAPPING-0.2.json")},
        "provenance": {"extraction_report_id": report["report_id"],
                       "corpus_commitment": report["corpus_commitment"],
                       "inventory_commitment": report["inventory_commitment"],
                       "l2_bundle_id": tr["l2_bundle_id"],
                       "quarantine_receipt_digest": _sha(PAPER / "CORPUS-QUARANTINE-RECEIPT.json"),
                       "l2_bundle_verified": ok, "events_total": len(bundle["body"]["events"])},
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
                        "l4_C2-MAP": l4["status"], "l4_evaluation_id_matches": l4.get("evaluation_id") == act_view.get("evaluation_id")},
            "C2-MEAS": {"status": meas["status"], "reason": "MEASUREMENT_NOT_REPLAYED",
                        "note": "offspring/dedup/o-hat are not extracted or derived by this path; "
                                "greening C2-MEAS from C2-MAP would be composition laundering."}},
        "assertions": {
            "all_24_spans_verified": all_spans_ok and len(span_results) == 24,
            "baseline_refused_zero_exact": base_view["status"] == "REFUSED" and base_exact == 0,
            "applied_complete_eight_exact": act_view["status"] == "COMPLETE" and act_exact == 8,
            "l4_reproduces": l4["status"] == "COMPLETE" and l4.get("evaluation_id") == act_view.get("evaluation_id"),
            "c2_meas_refused": meas["status"] == "REFUSED",
            "committed_operand_stays_derived": all(r["mapping_status"] == "DERIVED" for r in rows),
            "trust_root_unchanged": tr.get("decision_register") == [] and not tr.get("authorities", {}).get("mapping")},
    }
    body["metadata_only"] = not any(k in json.dumps(body) for k in ("raw_b64", '"content"', '"text"'))
    report_id = "arpt:" + ids.json_digest(body)
    out = {"report_id": report_id, **body}
    (PAPER / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False))
    return out


if __name__ == "__main__":
    r = generate()
    a = r["assertions"]
    print("report_id:", r["report_id"][:28])
    for k, v in a.items():
        print(f"  {'ok ' if v else 'XX '} {k}")
    print("metadata_only:", r["metadata_only"])
    ok_all = all(a.values()) and r["metadata_only"]
    print("ACTIVATION-REPORT:", "COMPLETE PROOF (machine-local; trust root unchanged)" if ok_all else "INCOMPLETE")
    sys.exit(0 if ok_all else 1)
