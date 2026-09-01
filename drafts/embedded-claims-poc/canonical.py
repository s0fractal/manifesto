#!/usr/bin/env python3
"""
canonical.py — embedded-claims PoC, phase 2 step 1.

The closed canonicalization + record-identity profile the fixtures are addressed
under. Phase 1 hashed capsule bodies with an ad-hoc domain-separated helper; this
pins the profile so two implementations agree on record IDs.

DECISIONS (drafts/EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md §17, operator defaults):
  #1 canonicalization — a CLOSED custom JSON profile, NOT JCS yet:
       * keys sorted by Unicode code point (json sort_keys)
       * separators (",", ":"), no insignificant whitespace
       * UTF-8, no BOM
       * floats / NaN / Infinity FORBIDDEN in an identity-bearing body
       * duplicate object keys FORBIDDEN (rejected at parse time)
     JCS/RFC 8785 is a later, reversible choice if cross-impl interop is needed;
     it is not adopted here.
  #2 hash — SHA-256, domain-separated per §8.1.

record_id = "sha256:" + SHA256( domain_separator || 0x00 || canonical(body) )

Deterministic and dependency-free (stdlib only), so the CI gate needs no package
beyond the evaluator.
"""
import hashlib
import json

# §8.1 domain separators — one per record kind, so a claim body and a plan body
# with identical bytes never collide.
DOMAINS = {
    "claim": "manifesto.claim.v0",
    "binding": "manifesto.semantic-binding.v0",
    "plan": "manifesto.verification-plan.v0",
    "dependency": "manifesto.dependency-manifest.v0",
    "result": "manifesto.result.v0",
    "receipt": "manifesto.verification-receipt.v0",
}


class CanonicalError(ValueError):
    """A body that cannot be canonicalized under this closed profile."""


def _reject(o, path="body"):
    """Refuse anything the identity profile does not admit, by name."""
    if isinstance(o, bool):
        return                      # bool is fine (and is an int subclass, check first)
    if isinstance(o, float):
        raise CanonicalError(f"float forbidden at {path} (identity bodies are exact)")
    if isinstance(o, (str, int)) or o is None:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if not isinstance(k, str):
                raise CanonicalError(f"non-string key at {path}")
            _reject(v, f"{path}.{k}")
        return
    if isinstance(o, list):
        for i, v in enumerate(o):
            _reject(v, f"{path}[{i}]")
        return
    raise CanonicalError(f"unserializable type {type(o).__name__} at {path}")


def canonicalize(body):
    """Canonical bytes of an identity-bearing body under the closed profile."""
    _reject(body)
    return json.dumps(body, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _no_dup_keys(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise CanonicalError(f"duplicate object key {k!r} (ambiguous identity)")
        seen[k] = v
    return seen


def loads_strict(text):
    """Parse JSON, rejecting duplicate keys (json.loads silently keeps the last —
    which would let two different source texts map to one canonical body)."""
    return json.loads(text, object_pairs_hook=_no_dup_keys)


def record_id(kind, body):
    """Content address of a record body, domain-separated by kind."""
    if kind not in DOMAINS:
        raise CanonicalError(f"unknown record kind {kind!r}")
    dom = DOMAINS[kind].encode()
    return "sha256:" + hashlib.sha256(dom + b"\x00" + canonicalize(body)).hexdigest()


if __name__ == "__main__":
    # tiny self-test / conformance witness
    b = {"z": 1, "a": [1, 2, {"m": "x"}], "t": True, "n": None}
    print("canonical:", canonicalize(b).decode())
    print("claim id :", record_id("claim", b))
    for bad, why in [({"f": 1.5}, "float"), (float("nan"), "nan")]:
        try:
            canonicalize(bad); print("FAIL: accepted", why)
        except CanonicalError as e:
            print("rejected", why, "->", e)
    try:
        loads_strict('{"a":1,"a":2}'); print("FAIL: accepted dup key")
    except CanonicalError as e:
        print("rejected dup key ->", e)
