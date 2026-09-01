#!/usr/bin/env python3
"""
test_corpus.py — the frozen acceptance oracle (F1-F9) as real mutation tests, plus the
identity/regeneration properties. Fully synthetic: needs NO quarantine and NO
sigma-glyph, so mechanism CI never touches local session state. Run:
`python3 papers/corpus/test_corpus.py`.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids                                  # noqa: E402
from corpus_extract import (extract_blob, extract_from_quarantine,   # noqa: E402
                            extractor_identity, BlobRefused)
from corpus_map import build_l3, make_public_projection    # noqa: E402

fails = []


def expect(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        fails.append(name)


def blob(*objs):
    return ("\n".join(json.dumps(o) for o in objs) + "\n").encode()


GOOD = blob(
    {"type": "user", "message": {"role": "user", "content": "ROOT: monotonicity 0030"}},
    {"type": "assistant", "message": {"role": "assistant", "content": "verdict + offspring"}},
)
EXT = extractor_identity()

# ============================ L1 -> L2 extraction ============================ #
bid, events = extract_blob(GOOD, EXT)
expect("baseline extract yields 2 events", len(events) == 2)
expect("events ordered by byte offset", [e["event_index"] for e in events] == [0, 1])
expect("each event carries blob+span+digest+id",
       all({"blob_id", "byte_start", "byte_end", "line_digest", "event_id"} <= e.keys()
           for e in events))

# repeat export is byte-identical
bid2, events2 = extract_blob(GOOD, EXT)
expect("repeat export byte-identical (ids stable)",
       bid == bid2 and [e["event_id"] for e in events] == [e["event_id"] for e in events2])

# F1: one byte change rotates blob_id AND dependent event ids AND the content address
mut = bytearray(GOOD); mut[10] ^= 0x01
bidm, eventsm = extract_blob(bytes(mut), EXT)
expect("F1 byte mutation rotates blob_id", bidm != bid)
expect("F1 byte mutation rotates event ids",
       {e["event_id"] for e in eventsm}.isdisjoint({e["event_id"] for e in events}))
expect("F1 content address changes", ids.raw_sha256(bytes(mut)) != ids.raw_sha256(GOOD))

# unknown event type is EMITTED, never skipped
_, ev_unk = extract_blob(blob({"type": "mystery-kind", "x": 1},
                              {"type": "user", "message": {"role": "user"}}), EXT)
expect("unknown event type emitted not skipped",
       len(ev_unk) == 2 and ev_unk[0]["unknown_event_type"] is True
       and ev_unk[0]["event_type"].startswith("UNKNOWN_EVENT_TYPE"))

# F2: duplicate JSON key -> whole-blob refusal (not skip-and-continue)
try:
    extract_blob(b'{"a":1,"a":2}\n', EXT)
    expect("F2 duplicate key refuses blob", False)
except BlobRefused as e:
    expect("F2 duplicate key refuses blob", e.reason == "DUPLICATE_KEY")

# malformed line -> whole-blob refusal
try:
    extract_blob(b'{"ok":1}\nnot json at all\n{"ok":2}\n', EXT)
    expect("malformed line refuses whole blob", False)
except BlobRefused as e:
    expect("malformed line refuses whole blob", e.reason == "MALFORMED_LINE")


def make_quarantine(root: Path, raw: bytes):
    sha = ids.raw_sha256(raw)
    (root / "blobs").mkdir(parents=True, exist_ok=True)
    (root / "blobs" / (sha + ".jsonl")).write_bytes(raw)
    inv = {"transcripts": [{"agent": "agent-x", "sha256": sha, "experiment": "EXP-RVB-1c"}]}
    receipt = {"records": [{"agent": "agent-x", "status": "VERIFIED",
                            "inventory_sha256": sha, "experiment": "EXP-RVB-1c"}]}
    return inv, receipt, sha


# path permutation leaves ids unchanged (ids are content-derived, not path-derived)
d1 = Path(tempfile.mkdtemp()); d2 = Path(tempfile.mkdtemp())
inv1, rec1, sha1 = make_quarantine(d1, GOOD)
inv2, rec2, _ = make_quarantine(d2, GOOD)
p1, r1 = extract_from_quarantine(d1, rec1, inv1)
p2, r2 = extract_from_quarantine(d2, rec2, inv2)
expect("path permutation leaves blob_id unchanged",
       p1["agent-x"]["blob_id"] == p2["agent-x"]["blob_id"])
expect("path permutation leaves event ids unchanged",
       [e["event_id"] for e in p1["agent-x"]["events"]]
       == [e["event_id"] for e in p2["agent-x"]["events"]])
expect("extraction report is metadata-only (no content)",
       "events" not in json.dumps(r1["blobs"]) or all("content" not in b for b in r1["blobs"]))

# F9: source digest drift -> BLOB_DRIFT (never silent update)
(d1 / "blobs" / (sha1 + ".jsonl")).chmod(0o600)
(d1 / "blobs" / (sha1 + ".jsonl")).write_bytes(GOOD + b'{"tamper":1}\n')
_, rdrift = extract_from_quarantine(d1, rec1, inv1)
expect("F9 source drift -> BLOB_DRIFT",
       rdrift["blobs"][0]["status"] == "BLOB_DRIFT")

# ============================ L2 -> L3 mapping ============================ #
L2 = {"evt:a", "evt:b", "evt:c", "evt:d", "evt:e", "evt:f", "evt:g", "evt:h"}


def entry(ref, root, verifier, run, span, ev="evt:a", status="EXACT",
          complete="COMPLETE", pub="CLEARED_FOR_PUBLICATION",
          evidence=True, sampling=None, exp="EXP-RVB-1c", parent=None, children=()):
    mev = ([{"kind": k, "event_id": ev} for k in
            ("experiment_id", "root_digest", "verifier_identity", "agent_run_occurrence")]
           if evidence else [])
    return {"local_ref": ref, "blob_id": "blob:z", "byte_start": span, "byte_end": span + 1,
            "event_ids": [ev], "experiment_id": exp, "root_digest": root,
            "verifier_identity": verifier, "agent_run_occurrence": run,
            "mapping_status": status, "mapping_evidence": mev,
            "completeness_status": complete, "publication_eligibility": pub,
            "parent_local_ref": parent, "selected_child_refs": list(children),
            "sampling": sampling or {}}


# no table -> every view REFUSED
rep0 = build_l3(L2, [], EXT)
expect("no table -> all views REFUSED",
       all(v["status"] == "REFUSED" for v in rep0["views"].values()))

# F3: dangling evidence/event -> AMBIGUOUS + DANGLING_REF, C2 refused
rep = build_l3(L2, [entry("X", "r1", "Fable", "run1", 0, ev="evt:MISSING")], EXT)
expect("F3 dangling ref faulted",
       any("DANGLING_REF" in a["faults"] for a in
           json.loads(json.dumps(rep["acts"]))) )
expect("F3 -> C2 REFUSED", rep["views"]["C2"]["status"] == "REFUSED")

# F2 (act): duplicate act id
dup = [entry("A", "r1", "Fable", "run1", 5), entry("B", "r1", "Fable", "run1", 5)]
repd = build_l3(L2, dup, EXT)
expect("F2 duplicate act id",
       any("DUPLICATE_ID" in a["faults"] for a in repd["acts"]))

# F4: summary masquerade (no events)
noev = [{"local_ref": "S", "blob_id": "blob:z", "byte_start": 0, "byte_end": 1,
         "event_ids": [], "experiment_id": "EXP-RVB-1c", "root_digest": "r",
         "verifier_identity": "Fable", "agent_run_occurrence": "run",
         "mapping_status": "EXACT", "mapping_evidence": []}]
expect("F4 no-events faulted (NO_EVENTS)",
       "NO_EVENTS" in build_l3(L2, noev, EXT)["acts"][0]["faults"])

# F5: EXACT without full evidence -> AMBIGUOUS -> C2 REFUSED
rep5 = build_l3(L2, [entry("X", "r1", "Fable", "run1", 0, evidence=False)], EXT)
expect("F5 EXACT-without-evidence -> AMBIGUOUS",
       rep5["acts"][0]["mapping_status"] == "AMBIGUOUS")
# count/verdict as evidence -> AMBIGUOUS
badev = entry("Y", "r1", "Fable", "run1", 1)
badev["mapping_evidence"] = [{"kind": "count", "event_id": "evt:a"}]
expect("F5 count-as-evidence -> AMBIGUOUS",
       build_l3(L2, [badev], EXT)["acts"][0]["mapping_status"] == "AMBIGUOUS")

# removing a mapping evidence span breaks the mapping
noev_span = entry("Z", "r1", "Fable", "run1", 2)
noev_span["mapping_evidence"] = [
    {"kind": k, "event_id": "evt:GONE"} for k in
    ("experiment_id", "root_digest", "verifier_identity", "agent_run_occurrence")]
expect("removing evidence span breaks mapping",
       build_l3(L2, [noev_span], EXT)["acts"][0]["mapping_status"] == "AMBIGUOUS")

# F7: silent-defaulted sampling
samp = entry("SD", "r1", "Fable", "run1", 3, sampling={"temperature": 0.7})
expect("F7 silent default faulted",
       "SILENT_DEFAULT" in build_l3(L2, [samp], EXT)["acts"][0]["faults"])

# F8: redaction id reuse / missing loss report
expect("F8 missing loss report fails",
       make_public_projection("act:src", "prof", None)["status"] == "FAIL")
proj = make_public_projection("act:src", "prof", {"lost": "system prompt"})
expect("F8 public projection gets a NEW id",
       proj["status"] == "OK" and proj["public_id"].startswith("pub:")
       and proj["public_id"] != "act:src")

# F6 + C2 bijection: a full, clean 8-act crossed set -> C2 COMPLETE
roots = ["r0030", "r0025", "rFLOW15", "rFLOW17"]
verifiers = ["Fable", "Sonnet"]
full = []
i = 0
letters = list(L2)
for r in roots:
    for v in verifiers:
        full.append(entry(f"{r}-{v}", r, v, f"run-{r}-{v}", i, ev=letters[i]))
        i += 1
repC2 = build_l3(L2, full, EXT)
expect("C2 full clean bijection -> COMPLETE",
       repC2["views"]["C2"]["status"] == "COMPLETE")

# F6: flip one act to PARTIAL -> C2 REFUSED (incomplete tree)
full[0]["completeness_status"] = "PARTIAL"
expect("F6 partial tree -> C2 REFUSED",
       build_l3(L2, full, EXT)["views"]["C2"]["status"] == "REFUSED")
full[0]["completeness_status"] = "COMPLETE"

# drop one act -> incomplete bijection -> REFUSED
repDrop = build_l3(L2, full[:7], EXT)
expect("incomplete bijection -> REFUSED",
       repDrop["views"]["C2"]["reason"] == "INCOMPLETE_C2_BIJECTION")

# repeated run of one (root,verifier) pair -> CONFLICTED -> REFUSED
rep_rr = full[:8] + [entry("duppair", "r0030", "Fable", "run-OTHER", 20, ev=letters[0])]
outRR = build_l3(L2, rep_rr, EXT)
expect("repeated run -> CONFLICTED",
       any(a["mapping_status"] == "CONFLICTED" for a in outRR["acts"]))
expect("repeated run -> C2 REFUSED", outRR["views"]["C2"]["status"] == "REFUSED")

print()
if fails:
    print(f"RED: {len(fails)} corpus mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: extraction is mechanical+reproducible; mapping is explicit and fails-closed.")
