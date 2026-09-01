#!/usr/bin/env python3
"""
corpus_extract.py — L1 -> L2. MECHANICAL EXTRACTION ONLY.

It reads QUARANTINE blobs (never the mutable ~/.claude store), requires the inventory
and the quarantine receipt as operands, re-verifies each blob digest, parses strict
JSONL with duplicate-key rejection, and orders events by BYTE OFFSET (not timestamp).

It makes NO root / verifier / experiment assumption — that is L2->L3's explicit,
reviewable mapping pass (corpus_map.py). Boring on purpose.

Boundaries:
- unknown event type -> UNKNOWN_EVENT_TYPE (emitted, never skipped);
- malformed line -> typed refusal of the WHOLE blob (never skip-and-continue);
- blob digest drift -> BLOB_DRIFT (never a silent inventory update).

The private L2 (with content) stays OUT of git; only a metadata-only report is
returned for committing.
"""
import json
from pathlib import Path

from corpus_ids import (blob_id as mk_blob_id, event_id as mk_event_id,
                        extractor_id as mk_extractor_id, line_digest as mk_line_digest,
                        raw_sha256)

KNOWN_EVENT_TYPES = {
    "user", "assistant", "system", "summary",
    "tool_use", "tool_result", "attachment", "progress",
    "file-history-snapshot", "x-command", "x-command-stdout",
}


class BlobRefused(Exception):
    def __init__(self, reason, **info):
        super().__init__(reason)
        self.reason = reason
        self.info = info


def _reject_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise BlobRefused("DUPLICATE_KEY", key=k)
        seen[k] = v
    return seen


def _split_lines(raw: bytes):
    """Yield (start, end, line_bytes) by byte offset; line excludes the trailing \\n."""
    start = 0
    n = len(raw)
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


def extractor_identity():
    return mk_extractor_id(Path(__file__).read_bytes())


def extract_blob(raw: bytes, ext_id: str):
    """Return (blob_id, [events]). Raises BlobRefused on any malformed line."""
    bid = mk_blob_id(raw)
    events = []
    idx = 0
    for (start, end, line) in _split_lines(raw):
        if line.strip() == b"":
            continue  # whitespace-only line is not an event
        try:
            obj = json.loads(line.decode("utf-8"), object_pairs_hook=_reject_dupes)
        except BlobRefused:
            raise
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise BlobRefused("MALFORMED_LINE", byte_start=start, detail=str(e))
        et, unknown = _event_type(obj) if isinstance(obj, dict) else ("UNKNOWN_EVENT_TYPE:non-object", True)
        ld = mk_line_digest(line)
        events.append({
            "event_index": idx,
            "blob_id": bid,
            "byte_start": start,
            "byte_end": end,
            "line_digest": ld,
            "event_type": et,
            "unknown_event_type": unknown,
            "event_id": mk_event_id(ext_id, bid, start, end, ld),
            "extractor_id": ext_id,
        })
        idx += 1
    return bid, events


def extract_from_quarantine(quarantine_dir, receipt: dict, inventory: dict):
    """
    Extract every VERIFIED blob named by the receipt. Returns
    (private_l2: {agent: {blob_id, events}}, report: metadata-only).
    Reads blobs by content-address from quarantine/blobs/<inventory_sha256>.jsonl.
    """
    qdir = Path(quarantine_dir)
    ext_id = extractor_identity()
    inv_by_agent = {t["agent"]: t for t in inventory["transcripts"]}
    private, rows = {}, []
    for rec in receipt["records"]:
        agent = rec["agent"]
        row = {"agent": agent, "experiment": rec.get("experiment", "?"),
               "inventory_sha256": rec.get("inventory_sha256")}
        if rec.get("status") != "VERIFIED":
            row["status"] = "SKIPPED_NOT_VERIFIED"
            rows.append(row); continue
        blob_path = qdir / "blobs" / (rec["inventory_sha256"] + ".jsonl")
        if not blob_path.exists():
            row["status"] = "BLOB_MISSING"; rows.append(row); continue
        raw = blob_path.read_bytes()
        if raw_sha256(raw) != rec["inventory_sha256"]:          # re-verify at read time
            row["status"] = "BLOB_DRIFT"
            row["observed_sha256"] = raw_sha256(raw)
            rows.append(row); continue
        # cross-check the inventory still agrees (operand consistency)
        if inv_by_agent.get(agent, {}).get("sha256") != rec["inventory_sha256"]:
            row["status"] = "INVENTORY_MISMATCH"; rows.append(row); continue
        try:
            bid, events = extract_blob(raw, ext_id)
        except BlobRefused as e:
            row["status"] = f"BLOB_REFUSED:{e.reason}"; row["info"] = e.info
            rows.append(row); continue
        private[agent] = {"blob_id": bid, "events": events}
        row.update({"status": "EXTRACTED", "blob_id": bid, "event_count": len(events),
                    "unknown_event_types": sum(e["unknown_event_type"] for e in events)})
        rows.append(row)
    report = {
        "schema": "manifesto.corpus.extraction-report.v0",
        "extractor_id": ext_id,
        "layer": "L1->L2 (mechanical extraction; no mapping)",
        "quarantine": str(qdir),
        "summary": {
            "extracted": sum(r["status"] == "EXTRACTED" for r in rows),
            "refused": sum(str(r["status"]).startswith("BLOB_REFUSED") for r in rows),
            "drift": sum(r["status"] in ("BLOB_DRIFT", "INVENTORY_MISMATCH") for r in rows),
            "events_total": sum(r.get("event_count", 0) for r in rows),
        },
        "blobs": rows,
        "note": "metadata only — no event content, no mapping. Private L2 stays out of git.",
    }
    return private, report
