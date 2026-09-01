#!/usr/bin/env python3
"""
test_corpus.py — the acceptance oracle as real mutation tests, hardened after the
Codex closure review (a690789). Fully synthetic: no quarantine, no sigma-glyph.

Covers the closure-condition mutations verbatim:
  8 DERIVED/no-evidence mappings       -> C2 REFUSED
  1 present act for a multi-unit claim -> REQUIRED_UNITS_MISSING
  arbitrary event cited for root       -> EVIDENCE_VALUE_MISMATCH
  mapping-field mutation               -> mapping_id rotates
  event-order mutation                 -> act_id rotates
  loss/public-content mutation         -> public_id rotates
  omitted inventory source             -> fail-closed missing-set report
  NaN / malformed table                -> typed refusal, no crash
plus the L1->L2 strictness/identity properties.
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids                                              # noqa: E402
from corpus_extract import (extract_blob, extract_from_quarantine,    # noqa: E402
                            extraction_closure_id, BlobRefused)
from corpus_map import build_l3, make_public_projection              # noqa: E402

fails = []


def expect(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        fails.append(name)


def blob(*objs):
    return ("\n".join(json.dumps(o) for o in objs) + "\n").encode()


GOOD = blob({"type": "user", "message": {"role": "user", "content": "ROOT 0030"}},
            {"type": "assistant", "message": {"role": "assistant", "content": "verdict"}})
CLO = extraction_closure_id()

# ===================== L1 -> L2 extraction (strict, mechanical) ===================== #
bid, events = extract_blob(GOOD, CLO)
expect("baseline 2 events, byte-ordered", [e["event_index"] for e in events] == [0, 1])
_, ev2 = extract_blob(GOOD, CLO)
expect("repeat export byte-identical", [e["event_id"] for e in events] == [e["event_id"] for e in ev2])
mut = bytearray(GOOD); mut[10] ^= 1
bidm, evm = extract_blob(bytes(mut), CLO)
expect("F1 one byte rotates blob+event ids",
       bidm != bid and {e["event_id"] for e in evm}.isdisjoint({e["event_id"] for e in events}))
_, evu = extract_blob(blob({"type": "mystery"}, {"type": "user"}), CLO)
expect("unknown type emitted not skipped",
       len(evu) == 2 and evu[0]["unknown_event_type"] and evu[0]["event_type"].startswith("UNKNOWN"))
for bad, why in [(b'{"a":1,"a":2}\n', "DUPLICATE_KEY"),
                 (b'{"ok":1}\nnope\n', "MALFORMED_LINE"),
                 (b'{"x":NaN}\n', "NON_FINITE_CONSTANT"),
                 (b'{"x":Infinity}\n', "NON_FINITE_CONSTANT"),
                 (b'{"x":-Infinity}\n', "NON_FINITE_CONSTANT")]:
    try:
        extract_blob(bad, CLO); expect(f"strict reject {why}", False)
    except BlobRefused as e:
        expect(f"strict reject {why}", e.reason == why)
# final line without LF, CRLF, whitespace-only lines all handled
_, evx = extract_blob(b'{"type":"user"}\r\n\n   \n{"type":"assistant"}', CLO)
expect("CRLF/blank/no-final-LF handled", len(evx) == 2)


def make_q(root: Path, raw: bytes, extra_inv=False):
    sha = ids.raw_sha256(raw)
    (root / "blobs").mkdir(parents=True, exist_ok=True)
    (root / "blobs" / (sha + ".jsonl")).write_bytes(raw)
    inv = {"transcripts": [{"agent": "agent-x", "sha256": sha, "experiment": "E"}]}
    rec = {"records": [{"agent": "agent-x", "status": "VERIFIED",
                        "inventory_sha256": sha, "experiment": "E"}]}
    if extra_inv:  # inventory names a source the receipt omits
        inv["transcripts"].append({"agent": "agent-y", "sha256": "b" * 64, "experiment": "E"})
    return inv, rec, sha


d1, d2 = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
i1, r1, s1 = make_q(d1, GOOD)
i2, r2, _ = make_q(d2, GOOD)
p1, rep1 = extract_from_quarantine(d1, r1, i1)
p2, rep2 = extract_from_quarantine(d2, r2, i2)
expect("path permutation leaves ids unchanged",
       p1["agent-x"]["blob_id"] == p2["agent-x"]["blob_id"])
expect("clean set_status", rep1["set_status"] == "CLEAN")
expect("report metadata-only (no raw_b64/content)",
       "raw_b64" not in json.dumps(rep1) and '"content"' not in json.dumps(rep1))
# omitted inventory source -> fail-closed missing-set
d3 = Path(tempfile.mkdtemp()); i3, r3, _ = make_q(d3, GOOD, extra_inv=True)
_, rep3 = extract_from_quarantine(d3, r3, i3)
expect("omitted inventory source -> FAIL + missing set",
       rep3["set_status"] == "FAIL" and rep3["summary"]["missing"] == ["agent-y"])
# digest drift
(d1 / "blobs" / (s1 + ".jsonl")).write_bytes(GOOD + b'{"z":1}\n')
_, repd = extract_from_quarantine(d1, r1, i1)
expect("F9 drift -> BLOB_DRIFT + FAIL",
       repd["set_status"] == "FAIL"
       and any(b["status"] == "BLOB_DRIFT" for b in repd["blobs"]))

# ===================== L2 -> L3 mapping (adjudicated, value-checked) ===================== #
def make_valid(local_ref, root_text, verifier, run="run", exp="EXP-RVB-1c",
               status="EXACT", complete="COMPLETE", pub="CLEARED_FOR_PUBLICATION",
               with_evidence=True, adjudicate=True):
    eid = "evt:" + local_ref
    exp_b, root_b, ver_b, run_b = exp.encode(), root_text.encode(), verifier.encode(), run.encode()
    body = exp_b + b"|" + root_b + b"|" + ver_b + b"|" + run_b
    spans = {}
    off = 0
    for kind, val in (("experiment_id", exp_b), ("root_digest", root_b),
                      ("verifier_identity", ver_b), ("agent_run_occurrence", run_b)):
        spans[kind] = (off, off + len(val), val)
        off += len(val) + 1
    l2 = {eid: {"blob_id": "blob:t", "byte_start": 0, "byte_end": len(body),
                "raw_bytes": body, "extraction_closure": "clo:extract:test"}}
    ev = []
    if with_evidence:
        for kind, (vs, ve, val) in spans.items():
            ev.append({"kind": kind, "event_id": eid, "value_start": vs, "value_end": ve,
                       "observed_value_digest": ids._h(b"value", val)})
    cand = {"local_ref": local_ref, "blob_id": "blob:t",
            "event_occurrences": [{"event_id": eid, "byte_start": 0, "byte_end": len(body)}],
            "experiment_id": exp, "root_digest": ids.raw_sha256(root_b),
            "verifier_identity": verifier, "agent_run_occurrence": run,
            "mapping_status": status, "mapping_evidence": ev,
            "adjudication": ({"adjudicator_identity": "rev-1", "authority": "corpus-adj",
                              "decision": "EXACT", "evidence_commitments": [eid]}
                             if adjudicate else None),
            "completeness_status": complete, "publication_eligibility": pub,
            "parent_local_ref": None, "selected_child_refs": [], "sampling": {}}
    return cand, l2


ROOTS = ["0030", "0025", "FLOW15", "FLOW17"]
VERIF = ["Fable", "Sonnet"]
C2_MAN = {"experiment_ids": ["EXP-RVB-1c"], "unit_key": ["root_digest", "verifier_identity"],
          "required_units": [[ids.raw_sha256(r.encode()), v] for r in ROOTS for v in VERIF],
          "allowed_exclusions": []}


def full_c2(**kw):
    table, l2 = [], {}
    for r in ROOTS:
        for v in VERIF:
            c, e = make_valid(f"{r}-{v}", r, v, **kw)
            table.append(c); l2.update(e)
    return table, l2


# baseline: full valid EXACT bijection -> C2 COMPLETE
tbl, l2 = full_c2()
rep = build_l3(l2, tbl, {"C2": C2_MAN})
expect("valid EXACT bijection -> C2 COMPLETE", rep["views"]["C2"]["status"] == "COMPLETE")

# P0-1: all DERIVED (no evidence) -> C2 REFUSED (DERIVED never credits)
tblD, l2D = full_c2(status="DERIVED", with_evidence=False, adjudicate=False)
repD = build_l3(l2D, tblD, {"C2": C2_MAN})
expect("8 DERIVED/no-evidence -> C2 REFUSED", repD["views"]["C2"]["status"] == "REFUSED")

# replace every EXACT by DERIVED -> view REFUSED
tblD2, l2D2 = full_c2(status="DERIVED")
expect("all-DERIVED (even with evidence) -> C2 REFUSED",
       build_l3(l2D2, tblD2, {"C2": C2_MAN})["views"]["C2"]["status"] == "REFUSED")

# no required-unit manifest -> REQUIRED_UNITS_UNSPECIFIED
expect("no manifest -> REQUIRED_UNITS_UNSPECIFIED",
       build_l3(l2, tbl, {})["views"]["C2"]["reason"] == "REQUIRED_UNITS_UNSPECIFIED")

# P0-3: one present act for a multi-unit claim -> REQUIRED_UNITS_MISSING
c1, e1 = make_valid("only", "0030", "Fable")
expect("one act for multi-unit claim -> REQUIRED_UNITS_MISSING",
       build_l3(e1, [c1], {"C2": C2_MAN})["views"]["C2"]["reason"] == "REQUIRED_UNITS_MISSING")

# P0-2: arbitrary event cited for root -> EVIDENCE_VALUE_MISMATCH -> AMBIGUOUS
cbad, ebad = make_valid("bad", "0030", "Fable")
cbad["root_digest"] = ids.raw_sha256(b"DIFFERENT")   # evidence span no longer hashes to this
repbad = build_l3(ebad, [cbad], {"C2": C2_MAN})
a0 = repbad["acts"][0]
expect("root evidence mismatch -> EVIDENCE_VALUE_MISMATCH",
       "EVIDENCE_VALUE_MISMATCH" in a0["faults"] and a0["mapping_status"] == "AMBIGUOUS")

# EXACT without adjudication / without evidence -> AMBIGUOUS
cna, ena = make_valid("na", "0030", "Fable", adjudicate=False)
expect("EXACT without adjudication -> AMBIGUOUS",
       build_l3(ena, [cna], {})["acts"][0]["mapping_status"] == "AMBIGUOUS")
cne, ene = make_valid("ne", "0030", "Fable", with_evidence=False)
expect("EXACT without evidence -> AMBIGUOUS",
       build_l3(ene, [cne], {})["acts"][0]["mapping_status"] == "AMBIGUOUS")

# count/verdict as evidence -> FORBIDDEN_EVIDENCE
cf, ef = make_valid("cf", "0030", "Fable")
cf["mapping_evidence"].append({"kind": "count", "event_id": "evt:cf",
                               "value_start": 0, "value_end": 1, "observed_value_digest": "x"})
expect("count-as-evidence -> FORBIDDEN_EVIDENCE",
       "FORBIDDEN_EVIDENCE" in build_l3(ef, [cf], {})["acts"][0]["faults"])

# P0-5: mapping-field mutation rotates mapping_id (not act_id)
cm, em = make_valid("m", "0030", "Fable")
base = build_l3(em, [cm], {})["acts"][0]
cm2 = dict(cm); cm2["verifier_identity"] = "Sonnet"
mut1 = build_l3(em, [cm2], {})["acts"][0]
expect("mapping-field mutation rotates mapping_id", mut1["mapping_id"] != base["mapping_id"])

# event-order mutation rotates act_id
e_two = {"evt:A": {"blob_id": "b", "byte_start": 0, "byte_end": 3, "raw_bytes": b"AAA",
                   "extraction_closure": "clo:extract:test"},
         "evt:B": {"blob_id": "b", "byte_start": 3, "byte_end": 6, "raw_bytes": b"BBB",
                   "extraction_closure": "clo:extract:test"}}
def occ_cand(ref, order):
    return {"local_ref": ref, "blob_id": "b",
            "event_occurrences": [{"event_id": x, "byte_start": e_two[x]["byte_start"],
                                   "byte_end": e_two[x]["byte_end"]} for x in order],
            "experiment_id": "E", "root_digest": "r", "verifier_identity": "v",
            "agent_run_occurrence": "run", "mapping_status": "DERIVED", "mapping_evidence": [],
            "completeness_status": "UNKNOWN", "publication_eligibility": "UNREVIEWED"}
oa = build_l3(e_two, [occ_cand("a", ["evt:A", "evt:B"])], {})["acts"][0]
ob = build_l3(e_two, [occ_cand("b", ["evt:B", "evt:A"])], {})["acts"][0]
expect("event-order mutation rotates act_id", oa["act_id"] != ob["act_id"])

# P0-5.4: loss/public-content mutation rotates public_id
p_a = make_public_projection("act:1", "prof", b"BODY", {"lost": "sys"})
p_b = make_public_projection("act:1", "prof", b"BODY", {"lost": "OTHER"})
p_c = make_public_projection("act:1", "prof", b"BODY2", {"lost": "sys"})
expect("F8 missing loss -> FAIL",
       make_public_projection("act:1", "prof", b"B", None)["status"] == "FAIL")
expect("public_id new + rotates on loss change",
       p_a["public_id"].startswith("pub:") and p_a["public_id"] != p_b["public_id"])
expect("public_id rotates on body change", p_a["public_id"] != p_c["public_id"])

# duplicate local_ref -> fail-closed (no overwrite)
cdl, edl = make_valid("dup", "0030", "Fable")
cdl2, edl2 = make_valid("dup", "0025", "Sonnet")
edl.update(edl2)
expect("duplicate local_ref -> DUPLICATE_LOCAL_REF",
       any("DUPLICATE_LOCAL_REF" in a["faults"] for a in build_l3(edl, [cdl, cdl2], {})["acts"]))

# duplicate act id
cid, eid_ = make_valid("i1", "0030", "Fable")
cid2 = dict(cid); cid2["local_ref"] = "i2"
expect("duplicate act id -> DUPLICATE_ID",
       any("DUPLICATE_ID" in a["faults"] for a in build_l3(eid_, [cid, cid2], {})["acts"]))

# F6: one PARTIAL act -> C2 REFUSED (missing that unit)
tblp, l2p = full_c2()
tblp[0]["completeness_status"] = "PARTIAL"
expect("partial act -> C2 REFUSED",
       build_l3(l2p, tblp, {"C2": C2_MAN})["views"]["C2"]["status"] == "REFUSED")

# F7: silent-defaulted sampling
cs, es = make_valid("s", "0030", "Fable"); cs["sampling"] = {"temperature": 0.7}
expect("F7 silent default faulted",
       "SILENT_DEFAULT" in build_l3(es, [cs], {})["acts"][0]["faults"])

# repeated run -> CONFLICTED -> C2 REFUSED
tblr, l2r = full_c2()
cextra, eextra = make_valid("0030-Fable-rerun", "0030", "Fable", run="run2")
tblr.append(cextra); l2r.update(eextra)
repr_ = build_l3(l2r, tblr, {"C2": C2_MAN})
expect("repeated run -> CONFLICTED",
       any(a["mapping_status"] == "CONFLICTED" for a in repr_["acts"]))
expect("repeated run -> C2 REFUSED", repr_["views"]["C2"]["status"] == "REFUSED")

# malformed table -> typed refusal, no crash
for badtable in [["not a dict"], [{"local_ref": 5}], [{"local_ref": "x", "event_occurrences": "nope"}],
                 [{"local_ref": "x", "event_occurrences": [{"event_id": "e", "byte_start": -1,
                   "byte_end": 2}]}], [{"local_ref": "x", "surprise": 1}]]:
    try:
        r = build_l3({}, badtable, {})
        expect("malformed table -> typed fault no crash", r["fault_count"] >= 1 or r["acts"][0]["faults"])
    except Exception as ex:  # noqa
        expect(f"malformed table crashed: {ex!r}", False)

print()
if fails:
    print(f"RED: {len(fails)} corpus mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: extraction is mechanical+reproducible; mapping is explicit and fails-closed.")
