#!/usr/bin/env python3
"""
corpus_extract.py — L1 -> L2. MECHANICAL EXTRACTION ONLY.

Reads QUARANTINE blobs (never the mutable ~/.claude store), requires inventory + the
quarantine receipt as operands, proves closed set-equality among inventory/receipt/
blobs/report, re-verifies each blob digest, parses STRICT JSON (duplicate keys AND
non-finite constants rejected), orders events by BYTE OFFSET. No root/verifier/
experiment assumption — that is corpus_map.py's explicit pass.

Private L2 carries a canonical event body (base64 of the exact raw span bytes) so the
mapper can value-validate evidence without reopening L1; the committed report is
metadata-only. Boundaries: unknown type -> UNKNOWN_EVENT_TYPE (emitted); malformed
line / non-finite constant / duplicate key -> typed refusal of the WHOLE blob; digest
drift or omitted source -> fail-closed set report.
"""
import base64
import json
import re
from pathlib import Path

import corpus_ids as ids

KNOWN_EVENT_TYPES = {
    "user", "assistant", "system", "summary",
    "tool_use", "tool_result", "attachment", "progress",
    "file-history-snapshot", "x-command", "x-command-stdout",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class BlobRefused(Exception):
    def __init__(self, reason, **info):
        super().__init__(reason)
        self.reason = reason
        self.info = info


def extraction_closure_id():
    """Closure over ALL verdict-affecting extraction bytes (P0-6)."""
    here = Path(__file__).resolve().parent
    return ids.closure_id("extract", [
        ("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
        ("corpus_extract.py", (here / "corpus_extract.py").read_bytes()),
        ("schema_version", ids.SCHEMA_VERSION.encode()),
    ])


def _reject_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise BlobRefused("DUPLICATE_KEY", key=k)
        seen[k] = v
    return seen


def _reject_constant(_s):
    raise BlobRefused("NON_FINITE_CONSTANT")


def _split_lines(raw: bytes):
    start, n = 0, len(raw)
    for i in range(n):
        if raw[i] == 0x0A:
            yield (start, i, raw[start:i])
            start = i + 1
    if start < n:
        yield (start, n, raw[start:])


def _event_type(obj):
    et = obj.get("type")
    if et is None and isinstance(obj.get("message"), dict):
        et = obj["message"].get("role")
    if et in KNOWN_EVENT_TYPES:
        return et, False
    return f"UNKNOWN_EVENT_TYPE:{et!r}", True


def extract_blob(raw: bytes, closure: str):
    """Return (blob_id, [private events]). Raises BlobRefused on any strictness break."""
    bid = ids.blob_id(raw)
    events, idx = [], 0
    for (start, end, line) in _split_lines(raw):
        if line.strip() == b"":
            continue
        try:
            obj = json.loads(line.decode("utf-8"),
                             object_pairs_hook=_reject_dupes,
                             parse_constant=_reject_constant)
        except BlobRefused:
            raise
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise BlobRefused("MALFORMED_LINE", byte_start=start, detail=str(e))
        et, unknown = (_event_type(obj) if isinstance(obj, dict)
                       else ("UNKNOWN_EVENT_TYPE:non-object", True))
        ld = ids.line_digest(line)
        eid = ids.event_id(closure, bid, start, end, ld)
        events.append({
            "event_index": idx, "blob_id": bid,
            "byte_start": start, "byte_end": end,
            "line_digest": ld, "event_type": et, "unknown_event_type": unknown,
            "event_id": eid, "extraction_closure": closure,
            "raw_b64": base64.b64encode(line).decode(),   # canonical body (private only)
        })
        idx += 1
    return bid, events


def _meta(ev):
    return {k: ev[k] for k in ("event_index", "blob_id", "byte_start", "byte_end",
                               "line_digest", "event_type", "unknown_event_type",
                               "event_id")}


def extract_from_quarantine(quarantine_dir, receipt: dict, inventory: dict):
    """
    Closed extraction over the inventory contract. Returns (private_l2, report).
    Fails closed on set drift, duplicate agents/digests, bad digest format, or omitted
    sources — never a clean-looking summary over a silent subset.
    """
    qdir = Path(quarantine_dir)
    closure = extraction_closure_id()

    inv_list = inventory.get("transcripts", [])
    rec_list = receipt.get("records", [])
    faults = []

    def _dupes(names):
        seen, dup = set(), set()
        for n in names:
            (dup if n in seen else seen).add(n)
        return sorted(dup)

    inv_dupes = _dupes([t["agent"] for t in inv_list])
    rec_dupes = _dupes([r["agent"] for r in rec_list])
    if inv_dupes:
        faults.append({"code": "DUPLICATE_INVENTORY_AGENT", "ids": inv_dupes})
    if rec_dupes:
        faults.append({"code": "DUPLICATE_RECEIPT_AGENT", "ids": rec_dupes})

    inv_by = {t["agent"]: t for t in inv_list}
    rec_by = {r["agent"]: r for r in rec_list}
    inv_set, rec_set = set(inv_by), set(rec_by)
    missing = sorted(inv_set - rec_set)          # inventory names it, receipt omits it
    extra = sorted(rec_set - inv_set)            # receipt has a source not in inventory
    if missing:
        faults.append({"code": "RECEIPT_MISSING_INVENTORY_SOURCE", "ids": missing})
    if extra:
        faults.append({"code": "RECEIPT_EXTRA_SOURCE", "ids": extra})

    private, rows = {}, []
    for agent in sorted(inv_set | rec_set):
        row = {"agent": agent}
        inv, rec = inv_by.get(agent), rec_by.get(agent)
        if inv is None or rec is None:
            row["status"] = "SET_DRIFT"; rows.append(row); continue
        row["experiment"] = rec.get("experiment", "?")
        sha = rec.get("inventory_sha256")
        row["inventory_sha256"] = sha
        if not (isinstance(sha, str) and HEX64.match(sha)):
            row["status"] = "BAD_DIGEST_FORMAT"; rows.append(row); continue
        if inv.get("sha256") != sha:
            row["status"] = "INVENTORY_MISMATCH"; rows.append(row); continue
        if rec.get("status") != "VERIFIED":
            row["status"] = "SKIPPED_NOT_VERIFIED"; rows.append(row); continue
        blob_path = qdir / "blobs" / (sha + ".jsonl")
        if not blob_path.exists():
            row["status"] = "BLOB_MISSING"; rows.append(row); continue
        raw = blob_path.read_bytes()
        if ids.raw_sha256(raw) != sha:
            row["status"] = "BLOB_DRIFT"; row["observed_sha256"] = ids.raw_sha256(raw)
            rows.append(row); continue
        try:
            bid, events = extract_blob(raw, closure)
        except BlobRefused as e:
            row["status"] = f"BLOB_REFUSED:{e.reason}"; row["info"] = e.info
            rows.append(row); continue
        private[agent] = {"blob_id": bid, "events": events}
        row.update({"status": "EXTRACTED", "blob_id": bid, "event_count": len(events),
                    "unknown_event_types": sum(e["unknown_event_type"] for e in events)})
        rows.append(row)

    ok_states = {"EXTRACTED"}
    refused = [r for r in rows if str(r["status"]).startswith("BLOB_REFUSED")]
    drift = [r for r in rows if r["status"] in
             ("BLOB_DRIFT", "INVENTORY_MISMATCH", "SET_DRIFT", "BAD_DIGEST_FORMAT")]
    skipped = [r for r in rows if r["status"] in ("BLOB_MISSING", "SKIPPED_NOT_VERIFIED")]
    set_clean = not faults and not drift and not skipped and not refused
    report = {
        "schema": "manifesto.corpus.extraction-report.v0",
        "extraction_closure": closure,
        "layer": "L1->L2 (mechanical; occurrence index + private canonical body)",
        "set_status": "CLEAN" if set_clean else "FAIL",
        "set_faults": faults,
        "summary": {
            "expected": len(inv_set), "present_in_both": len(inv_set & rec_set),
            "extracted": sum(r["status"] in ok_states for r in rows),
            "refused": len(refused), "drift": len(drift), "skipped": len(skipped),
            "missing": missing, "extra": extra,
            "events_total": sum(r.get("event_count", 0) for r in rows),
        },
        "blobs": rows,
        "note": "metadata only — no event content. Private L2 (with canonical body) stays out of git.",
    }
    return private, report
