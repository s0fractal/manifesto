#!/usr/bin/env python3
"""
schema.py — embedded-claims PoC, phase 2 step 1.

A CLOSED schema for the authoring capsule, hand-rolled (stdlib only, no jsonschema
dependency so the CI gate needs nothing beyond the evaluator). Closed means
`additionalProperties: false` at every level: an unknown field is a fail-closed
error, never ignored "for forward compatibility" (§13.8).

This validates SHAPE only. It does not settle anything, does not grant credit, and
does not decide binding review status (that clamp lives in verify.py).
"""
import re

HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERIFIER = re.compile(r"^(glyph|settle-gate|effect-sandbox)://sha256:[0-9a-f]{64}$")
BINDING_RELATIONS = {"supports", "refutes", "defines", "instantiates", "measures"}
BINDING_STATUS = {"ASSERTED", "REVIEWED", "CONTESTED"}   # vocabulary; verify.py clamps raw→ASSERTED


def _closed(errors, val, where, allowed, required):
    """Record unknown/missing fields; return True iff `val` is a dict so deeper
    checks are safe. Never short-circuits sibling checks — all errors surface."""
    if not isinstance(val, dict):
        errors.append(f"{where} must be an object")
        return False
    for k in val:
        if k not in allowed:
            errors.append(f"unknown field {where}.{k}")
    for r in required:
        if r not in val:
            errors.append(f"missing required field {where}.{r}")
    return True


def validate_capsule(cap):
    """Return a list of typed error strings; empty means the capsule is well-formed
    under the closed schema. Missing capsule ({}) is valid — assertions are optional."""
    errors = []
    if not _closed(errors, cap, "capsule",
                   allowed={"verifier", "evaluation_id", "dep", "binding"},
                   required=()):
        return errors

    if "verifier" in cap and not (isinstance(cap["verifier"], str)
                                  and VERIFIER.match(cap["verifier"])):
        errors.append("capsule.verifier must be '<scheme>://sha256:<64hex>'")

    if "evaluation_id" in cap and not (isinstance(cap["evaluation_id"], str)
                                       and HEX64.match(cap["evaluation_id"])):
        errors.append("capsule.evaluation_id must be 64 lowercase hex")

    if "dep" in cap:
        dep = cap["dep"]
        if _closed(errors, dep, "capsule.dep",
                allowed={"path", "sha256"}, required=("path", "sha256")):
            if "path" in dep and (not isinstance(dep["path"], str) or not dep["path"]):
                errors.append("capsule.dep.path must be a non-empty string")
            if "sha256" in dep and not (isinstance(dep["sha256"], str)
                                        and HEX64.match(dep["sha256"])):
                errors.append("capsule.dep.sha256 must be 64 lowercase hex")

    if "binding" in cap:
        b = cap["binding"]
        if _closed(errors, b, "capsule.binding",
                allowed={"relation", "target", "status"},
                required=("relation", "target")):
            rel = b.get("relation")
            if not isinstance(rel, str) or rel not in BINDING_RELATIONS:
                errors.append(f"capsule.binding.relation must be one of "
                              f"{sorted(BINDING_RELATIONS)}")
            if not isinstance(b.get("target"), str) or not b["target"]:
                errors.append("capsule.binding.target must be a non-empty string")
            if "status" in b:
                st = b["status"]
                if not isinstance(st, str) or st not in BINDING_STATUS:
                    errors.append(f"capsule.binding.status must be one of "
                                  f"{sorted(BINDING_STATUS)}")
    return errors


if __name__ == "__main__":
    ok = {"verifier": "glyph://sha256:" + "0" * 64,
          "binding": {"relation": "measures", "target": "x"}}
    print("valid capsule errors:", validate_capsule(ok))
    bad = {"verifier": "x", "surprise": 1, "dep": {"path": "p"}}
    print("bad capsule errors:")
    for e in validate_capsule(bad):
        print("  -", e)
