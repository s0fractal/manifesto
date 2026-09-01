#!/usr/bin/env python3
"""
corpus_ids.py — domain-separated, path-independent identity for the act corpus.

Every id is derived from canonical meaning-bearing content + source occurrence + the
relevant CLOSURE (all verdict-affecting code + schema bytes). Never from a filesystem
path. Ids for blob / event / act / mapping / public projection live in different
domains (different tag + prefix) so one can never be mistaken for another; act identity
is kept distinct from mapping identity but linked (mapping_id binds the act_id).

Properties (test_corpus.py):
- permuting filesystem paths leaves every id unchanged;
- changing one raw byte rotates event/act ids;
- event ORDER is semantic: reordering the composing events rotates act_id;
- a mapping-field change rotates mapping_id (not act_id);
- a loss-report / public-body change rotates public_id;
- changing corpus_ids.py / the extractor / the mapper / the schema rotates only the
  appropriate downstream closure and its ids.
"""
import hashlib
import json

DOMAIN = b"manifesto.corpus.v0"
SCHEMA_VERSION = "0.1"


def _b(x) -> bytes:
    return x if isinstance(x, bytes) else str(x).encode("utf-8")


def _h(tag: bytes, *parts) -> str:
    """Length-prefixed, domain-separated hash (no concatenation ambiguity)."""
    h = hashlib.sha256()
    h.update(DOMAIN); h.update(b"\x00"); h.update(tag); h.update(b"\x00")
    for p in parts:
        pb = _b(p)
        h.update(len(pb).to_bytes(8, "big"))
        h.update(pb)
    return h.hexdigest()


def json_digest(obj) -> str:
    """Canonical digest of a JSON-able object (sorted keys, no NaN)."""
    return _h(b"json", json.dumps(obj, sort_keys=True, allow_nan=False,
                                  separators=(",", ":")))


def raw_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


# --- closures over verdict-affecting bytes (ordered, path-independent) --------- #
def closure_id(tag: str, named_bytes) -> str:
    """named_bytes: iterable of (logical_name, bytes). Ordered by name; path-free."""
    items = sorted(named_bytes, key=lambda kv: kv[0])
    parts = []
    for name, data in items:
        parts.append(name.encode())
        parts.append(data)
    return "clo:" + tag + ":" + _h(b"closure", *parts)


# --- entity ids ---------------------------------------------------------------- #
def blob_id(raw: bytes) -> str:
    return "blob:" + _h(b"blob", raw)


def line_digest(raw_line: bytes) -> str:
    return "line:" + _h(b"line", raw_line)


def event_id(extraction_closure: str, blob: str, start: int, end: int, ld: str) -> str:
    return "evt:" + _h(b"event", extraction_closure, blob,
                       start.to_bytes(8, "big"), end.to_bytes(8, "big"), ld)


def act_id(extraction_closure: str, blob: str, ordered_occurrences, content_digest: str) -> str:
    """ordered_occurrences: list of (event_id, start, end) IN ORDER (not sorted)."""
    parts = [b"act", extraction_closure, blob, content_digest]
    for i, (eid, s, e) in enumerate(ordered_occurrences):
        parts += [i.to_bytes(8, "big"), eid, s.to_bytes(8, "big"), e.to_bytes(8, "big")]
    return "act:" + _h(*[_b(p) for p in parts])


def content_digest(ordered_bodies) -> str:
    """Digest of the ordered raw bodies composing an act (order is semantic)."""
    parts = []
    for i, body in enumerate(ordered_bodies):
        parts += [i.to_bytes(8, "big"), body]
    return _h(b"content", *parts)


def mapping_id(mapper_closure: str, subject_act_id: str, experiment_id: str,
               root_digest: str, verifier_identity: str, agent_run_occurrence: str,
               evidence_commitment_digest: str, mapping_status: str,
               adjudication_digest: str) -> str:
    return "map:" + _h(b"mapping", mapper_closure, subject_act_id, experiment_id,
                       root_digest, verifier_identity, agent_run_occurrence,
                       evidence_commitment_digest, mapping_status, adjudication_digest)


def public_id(pub_closure: str, source_act_id: str, redaction_profile_id: str,
              public_body_digest: str, loss_report_digest: str) -> str:
    return "pub:" + _h(b"public", pub_closure, source_act_id, redaction_profile_id,
                       public_body_digest, loss_report_digest)
