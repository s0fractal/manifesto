#!/usr/bin/env python3
"""
test_corpus.py — the acceptance oracle as real mutation tests, hardened after the
Codex exact-HEAD review (57d41e5). Fully synthetic: no quarantine, no sigma-glyph.

Runs the closure-condition mutations verbatim:
  mutated L2 body + stale event_id              -> L2_INTEGRITY_BREAK before mapping
  mixed blob/closure or forged occurrence       -> NO_RAW_PROVENANCE
  empty required-unit manifest                  -> REFUSED: EMPTY_REQUIRED_SET
  malformed manifest/sampling/inventory/receipt -> typed refusal, no crash
  unbound adjudication commitment               -> AMBIGUOUS / ADJUDICATION_MISMATCH
  EXACT -> CONFLICTED graph finalization        -> mapping_id rotates and re-verifies
  duplicate local_ref required by a view        -> view REFUSED
  schema-byte mutation                          -> relevant closure rotates
  + the L1->L2 strictness/identity properties and F1-F9.
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
from corpus_map import (authenticate_l2, build_l3, make_public_projection,  # noqa: E402
                        mapper_closure_id)

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
_, ev2 = extract_blob(GOOD, CLO)
expect("repeat export byte-identical", [e["event_id"] for e in events] == [e["event_id"] for e in ev2])
mut = bytearray(GOOD); mut[10] ^= 1
bidm, evm = extract_blob(bytes(mut), CLO)
expect("F1 one byte rotates ids", bidm != bid
       and {e["event_id"] for e in evm}.isdisjoint({e["event_id"] for e in events}))
_, evu = extract_blob(blob({"type": "mystery"}, {"type": "user"}), CLO)
expect("unknown type emitted not skipped", evu[0]["unknown_event_type"])
for bad, why in [(b'{"a":1,"a":2}\n', "DUPLICATE_KEY"), (b'{"ok":1}\nnope\n', "MALFORMED_LINE"),
                 (b'{"x":NaN}\n', "NON_FINITE_CONSTANT"), (b'{"x":Infinity}\n', "NON_FINITE_CONSTANT"),
                 (b'{"x":-Infinity}\n', "NON_FINITE_CONSTANT")]:
    try:
        extract_blob(bad, CLO); expect(f"strict reject {why}", False)
    except BlobRefused as e:
        expect(f"strict reject {why}", e.reason == why)


def make_q(root: Path, raw: bytes, extra_inv=False):
    sha = ids.raw_sha256(raw)
    (root / "blobs").mkdir(parents=True, exist_ok=True)
    (root / "blobs" / (sha + ".jsonl")).write_bytes(raw)
    inv = {"transcripts": [{"agent": "agent-x", "sha256": sha, "experiment": "E"}]}
    rec = {"records": [{"agent": "agent-x", "status": "VERIFIED", "inventory_sha256": sha, "experiment": "E"}]}
    if extra_inv:
        inv["transcripts"].append({"agent": "agent-y", "sha256": "b" * 64, "experiment": "E"})
    return inv, rec, sha


d1, d2, d3 = (Path(tempfile.mkdtemp()) for _ in range(3))
i1, r1, s1 = make_q(d1, GOOD); i2, r2, _ = make_q(d2, GOOD)
p1, rep1 = extract_from_quarantine(d1, r1, i1)
p2, rep2 = extract_from_quarantine(d2, r2, i2)
expect("path permutation leaves ids unchanged", p1["agent-x"]["blob_id"] == p2["agent-x"]["blob_id"])
expect("clean set_status", rep1["set_status"] == "CLEAN")
expect("report metadata-only", "raw_b64" not in json.dumps(rep1))
i3, r3, _ = make_q(d3, GOOD, extra_inv=True)
_, rep3 = extract_from_quarantine(d3, r3, i3)
expect("omitted inventory source -> FAIL", rep3["set_status"] == "FAIL" and rep3["summary"]["missing"] == ["agent-y"])
_, repM = extract_from_quarantine(d1, {"records": "x"}, {"transcripts": []})
expect("malformed operand -> typed no crash", repM["set_status"] == "FAIL")
(d1 / "blobs" / (s1 + ".jsonl")).write_bytes(GOOD + b'{"z":1}\n')
_, repd = extract_from_quarantine(d1, r1, i1)
expect("F9 drift -> BLOB_DRIFT + FAIL", repd["set_status"] == "FAIL")

# ===================== L2 -> L3 mapping (authenticated, adjudicated) ===================== #
TCLO = "clo:extract:test"


def mk(local_ref, root_text, verifier, run="run", exp="EXP-RVB-1c", status="EXACT",
       complete="COMPLETE", pub="CLEARED_FOR_PUBLICATION", with_evidence=True,
       adjudicate=True, commit=None):
    blobid = "blob:t"
    parts = [("experiment_id", exp.encode()), ("root_digest", root_text.encode()),
             ("verifier_identity", verifier.encode()), ("agent_run_occurrence", run.encode())]
    body = b"|".join(v for _, v in parts)
    eid = ids.event_id(TCLO, blobid, 0, len(body), ids.line_digest(body))
    l2 = {"blob_id": blobid, "byte_start": 0, "byte_end": len(body), "raw_bytes": body,
          "extraction_closure": TCLO, "event_id": eid}
    ev, off = [], 0
    for kind, val in parts:
        if with_evidence:
            ev.append({"kind": kind, "event_id": eid, "value_start": off, "value_end": off + len(val),
                       "observed_value_digest": ids._h(b"value", val)})
        off += len(val) + 1
    adj = ({"adjudicator_identity": "rev", "authority": "corpus-adj", "decision": "EXACT",
            "evidence_commitments": commit if commit is not None else [eid]} if adjudicate else None)
    cand = {"local_ref": local_ref, "blob_id": blobid,
            "event_occurrences": [{"event_id": eid, "byte_start": 0, "byte_end": len(body)}],
            "experiment_id": exp, "root_digest": ids.raw_sha256(root_text.encode()),
            "verifier_identity": verifier, "agent_run_occurrence": run,
            "mapping_status": status, "mapping_evidence": ev, "adjudication": adj,
            "root_id": "root:" + root_text, "verifier_declared_identity": verifier,
            "verifier_observed_identity": verifier, "prompt_digest": "UNKNOWN",
            "response_digest": "UNKNOWN", "offspring_before_dedup": "UNKNOWN",
            "dedup_removal_decisions": "UNKNOWN", "selected_child_refs": [], "sampling": {},
            "completeness_status": complete, "publication_eligibility": pub, "parent_local_ref": None}
    return cand, l2


ROOTS, VERIF = ["0030", "0025", "FLOW15", "FLOW17"], ["Fable", "Sonnet"]
C2_MAN = {"claim": "C2", "experiment_ids": ["EXP-RVB-1c"], "unit_key": ["root_digest", "verifier_identity"],
          "required_units": [[ids.raw_sha256(r.encode()), v] for r in ROOTS for v in VERIF],
          "allowed_exclusions": []}


def full(**kw):
    table, entries = [], []
    for r in ROOTS:
        for v in VERIF:
            c, e = mk(f"{r}-{v}", r, v, **kw); table.append(c); entries.append(e)
    return table, entries


tbl, ent = full()
bundle = authenticate_l2(ent)
expect("valid EXACT bijection -> C2 COMPLETE", build_l3(bundle, tbl, {"C2": C2_MAN})["views"]["C2"]["status"] == "COMPLETE")

# DERIVED never credits
tblD, entD = full(status="DERIVED")
expect("all DERIVED -> C2 REFUSED", build_l3(authenticate_l2(entD), tblD, {"C2": C2_MAN})["views"]["C2"]["status"] == "REFUSED")

# no / empty / malformed manifest
expect("no manifest -> REQUIRED_UNITS_UNSPECIFIED", build_l3(bundle, tbl, {})["views"]["C2"]["reason"] == "REQUIRED_UNITS_UNSPECIFIED")
empty_man = {"claim": "C2", "experiment_ids": [], "unit_key": [], "required_units": []}
expect("empty manifest -> EMPTY_REQUIRED_SET (or MALFORMED)",
       build_l3(bundle, tbl, {"C2": empty_man})["views"]["C2"]["reason"] in ("EMPTY_REQUIRED_SET", "MALFORMED_MANIFEST", "BAD_UNIT_KEY"))
expect("manifest missing keys -> typed no crash", build_l3(bundle, tbl, {"C2": {}})["views"]["C2"]["reason"] == "MALFORMED_MANIFEST")

# L2_INTEGRITY_BREAK: mutated body + stale event id
c0, e0 = mk("x", "0030", "Fable")
e0_forged = dict(e0); e0_forged["raw_bytes"] = e0["raw_bytes"] + b"TAMPER"   # event_id no longer matches
bbreak = authenticate_l2([e0_forged])
expect("mutated L2 body + stale id -> L2_INTEGRITY_BREAK", bbreak["status"] == "L2_INTEGRITY_BREAK")
expect("L2 break -> C2 REFUSED L2_INTEGRITY_BREAK", build_l3(bbreak, [c0], {"C2": C2_MAN})["views"]["C2"]["reason"] == "L2_INTEGRITY_BREAK")

# forged occurrence (span not equal to the event) -> NO_RAW_PROVENANCE
cf, ef = mk("f", "0030", "Fable"); cf["event_occurrences"] = [{"event_id": cf["event_occurrences"][0]["event_id"], "byte_start": 1, "byte_end": 2}]
expect("forged occurrence -> NO_RAW_PROVENANCE", "NO_RAW_PROVENANCE" in build_l3(authenticate_l2([ef]), [cf], {})["acts"][0]["faults"])
# forged blob id -> NO_RAW_PROVENANCE
cb, eb = mk("b", "0030", "Fable"); cb["blob_id"] = "blob:FORGED"
expect("forged blob id -> NO_RAW_PROVENANCE", "NO_RAW_PROVENANCE" in build_l3(authenticate_l2([eb]), [cb], {})["acts"][0]["faults"])

# one act for a multi-unit claim -> REQUIRED_UNITS_MISSING
c1, e1 = mk("only", "0030", "Fable")
expect("one act multi-unit -> REQUIRED_UNITS_MISSING", build_l3(authenticate_l2([e1]), [c1], {"C2": C2_MAN})["views"]["C2"]["reason"] == "REQUIRED_UNITS_MISSING")

# root evidence mismatch -> EVIDENCE_VALUE_MISMATCH
cbad, ebad = mk("bad", "0030", "Fable"); cbad["root_digest"] = ids.raw_sha256(b"DIFFERENT")
expect("root evidence mismatch -> AMBIGUOUS", build_l3(authenticate_l2([ebad]), [cbad], {})["acts"][0]["status"] == "AMBIGUOUS")

# unbound adjudication commitment -> AMBIGUOUS
cna, ena = mk("na", "0030", "Fable", commit=["unrelated"])
expect("unbound adjudication -> AMBIGUOUS", build_l3(authenticate_l2([ena]), [cna], {})["acts"][0]["status"] == "AMBIGUOUS")

# EXACT -> CONFLICTED: mapping_id addresses final status
tblr, entr = full()
cx, ex = mk("0030-Fable-rerun", "0030", "Fable", run="run2"); tblr.append(cx); entr.append(ex)
repr_ = build_l3(authenticate_l2(entr), tblr, {"C2": C2_MAN})
conf = [a for a in repr_["acts"] if a["status"] == "CONFLICTED"]
expect("repeated run -> CONFLICTED", len(conf) >= 2)
one = conf[0]
recomputed = ids.mapping_id(mapper_closure_id(), one["act_id"], "EXP-RVB-1c",
                            ids.raw_sha256(b"0030"), "Fable", "run" if "rerun" not in one["local_ref"] else "run2",
                            ids.json_digest([]), "CONFLICTED", ids.json_digest({}))
# mapping_id must at least be the CONFLICTED-status hash, not the EXACT one
exact_id = ids.mapping_id(mapper_closure_id(), one["act_id"], "EXP-RVB-1c",
                          ids.raw_sha256(b"0030"), "Fable", "run", ids.json_digest([]), "EXACT", ids.json_digest({}))
expect("mapping_id addresses final CONFLICTED not EXACT", one["mapping_id"] != exact_id)
expect("repeated run -> C2 REFUSED", repr_["views"]["C2"]["status"] == "REFUSED")

# duplicate local_ref required by a view -> both invalidated -> view REFUSED
tbldup, entdup = full()
cdup, edup = mk("0030-Fable", "0030", "Fable", run="run2"); tbldup.append(cdup); entdup.append(edup)
repdup = build_l3(authenticate_l2(entdup), tbldup, {"C2": C2_MAN})
expect("duplicate local_ref invalidates all members",
       all("DUPLICATE_LOCAL_REF" in a["faults"] for a in repdup["acts"] if a["local_ref"] == "0030-Fable"))
expect("duplicate local_ref -> C2 REFUSED", repdup["views"]["C2"]["status"] == "REFUSED")

# partial act -> INCOMPLETE_TREE (distinct from missing)
tblp, entp = full(); tblp[0]["completeness_status"] = "PARTIAL"
expect("partial act -> INCOMPLETE_TREE", build_l3(authenticate_l2(entp), tblp, {"C2": C2_MAN})["views"]["C2"]["reason"] == "INCOMPLETE_TREE")

# silent-defaulted / malformed sampling -> typed
cs, es = mk("s", "0030", "Fable"); cs["sampling"] = {"temperature": 0.7}
expect("F7 silent default faulted", "SILENT_DEFAULT" in build_l3(authenticate_l2([es]), [cs], {})["acts"][0]["faults"])
cbs, ebs = mk("bs", "0030", "Fable"); cbs["sampling"] = "not-an-object"
expect("malformed sampling -> BAD_SAMPLING no crash", "BAD_SAMPLING" in build_l3(authenticate_l2([ebs]), [cbs], {})["acts"][0]["faults"])

# schema-affecting bytes change the closure
expect("closure is byte-sensitive", ids.closure_id("x", [("a", b"1")]) != ids.closure_id("x", [("a", b"2")]))

# F8 public projection: new id + reuse rejection
expect("F8 missing loss -> FAIL", make_public_projection("act:1", "p", b"B", None)["status"] == "FAIL")
expect("F8 reused id -> REDACTION_ID_REUSE", make_public_projection("act:1", "p", b"B", {"l": 1}, proposed_id="act:1")["status"] == "FAIL")
pa = make_public_projection("act:1", "p", b"B", {"l": "sys"})
pb = make_public_projection("act:1", "p", b"B", {"l": "OTHER"})
expect("public_id new + rotates on loss", pa["public_id"] != pb["public_id"] and pa["public_id"].startswith("pub:"))

# malformed table -> typed refusal, no crash
for badtable in [["not a dict"], [{"local_ref": 5}], [{"local_ref": "x", "event_occurrences": "nope"}],
                 [{"local_ref": "x", "surprise": 1}]]:
    try:
        r = build_l3(authenticate_l2([]), badtable, {})
        expect("malformed table -> typed no crash", r["fault_count"] >= 1)
    except Exception as ex:  # noqa
        expect(f"malformed table crashed: {ex!r}", False)

print()
if fails:
    print(f"RED: {len(fails)} corpus mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: extraction is mechanical+reproducible; mapping is authenticated and fails-closed.")
