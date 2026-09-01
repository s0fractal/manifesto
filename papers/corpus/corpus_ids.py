#!/usr/bin/env python3
"""
corpus_ids.py — domain-separated, path-independent identity for the act corpus.

Every id is derived from canonical content + source occurrence + the extractor/schema
closure — NEVER from a filesystem path. The absolute quarantine path is a provenance
locator, not an identity. Ids for raw blob / event / act / mapping / public projection
are in different domains (different tag + different prefix), so one can never be
mistaken for another.

Properties (exercised by test_corpus.py):
- permuting filesystem paths leaves every id unchanged;
- changing one raw byte rotates every dependent id;
- a different extractor/schema closure rotates event/act ids (closure discipline).
"""
import hashlib

DOMAIN = b"manifesto.corpus.v0"
SCHEMA_VERSION = "0.1"


def _b(x) -> bytes:
    return x if isinstance(x, bytes) else str(x).encode("utf-8")


def _h(tag: bytes, *parts) -> str:
    """Length-prefixed, domain-separated hash (no concatenation ambiguity)."""
    h = hashlib.sha256()
    h.update(_b(DOMAIN)); h.update(b"\x00")
    h.update(tag); h.update(b"\x00")
    for p in parts:
        pb = _b(p)
        h.update(len(pb).to_bytes(8, "big"))
        h.update(pb)
    return h.hexdigest()


def raw_sha256(raw: bytes) -> str:
    """The content-address used by the quarantine (locator identity of the bytes)."""
    return hashlib.sha256(raw).hexdigest()


def blob_id(raw: bytes) -> str:
    return "blob:" + _h(b"blob", raw)


def extractor_id(extractor_code: bytes) -> str:
    return "ext:" + _h(b"extractor", extractor_code, SCHEMA_VERSION)


def line_digest(raw_line: bytes) -> str:
    return "line:" + _h(b"line", raw_line)


def event_id(ext_id: str, blob: str, start: int, end: int, ld: str) -> str:
    return "evt:" + _h(b"event", ext_id, blob,
                       start.to_bytes(8, "big"), end.to_bytes(8, "big"), ld)


def act_id(ext_id: str, blob: str, start: int, end: int, canonical_body: bytes) -> str:
    return "act:" + _h(b"act", ext_id, blob,
                       start.to_bytes(8, "big"), end.to_bytes(8, "big"), canonical_body)


def mapping_id(experiment_id: str, root_digest: str,
               verifier_identity: str, agent_run_occurrence: str) -> str:
    return "map:" + _h(b"mapping", experiment_id, root_digest,
                       verifier_identity, agent_run_occurrence)


def public_id(redaction_profile_id: str, derived_from: str) -> str:
    return "pub:" + _h(b"public", redaction_profile_id, derived_from)
