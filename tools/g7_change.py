#!/usr/bin/env python3
"""
g7_change.py — G7-CHANGE conformance packet (Codex FLOW-0.3 review §8).

The D17 debt: FLOW-0.2 tried to type "what changed Reach" as two channels
(external-via-M vs endogenous ΔC/ΔI) and the FALLING ROCK fell through both.
Codex rejected the 3-channel synthesis and prescribed orthogonal axes. This
file makes the replacement EXECUTABLE and FALSIFIABLE, not prose:

  ChangeKind      = State | Constraint | Invariant | Policy | UpdateLaw
  CarrierLocus    = Internal | External | Relational | Shared
  CausalOrigin    = Self | Other | Environment | Mixed | Unattributed
  CrossesBoundary = Yes | No
  Mechanism       = T | e | M | pi | G | H

The classifier over a scenario's structured facts returns exactly one of:
  CLASSIFIED(tuple)      — every axis pinned and the tuple is coherent;
  UNDERDETERMINED(facet) — a load-bearing fact is missing (the taxonomy must
                           REFUSE, not guess — Codex's required negative case);
  INCOHERENT(rule)       — the labeling violates a cross-axis consistency rule
                           (this is where the taxonomy FORBIDS something — the
                           discriminative content a real primitive must have).

This does NOT close D17. It demonstrates the taxonomy is (a) total — every
scenario gets a verdict, (b) refuses on incomplete facts, (c) forbids
incoherent labelings, and (d) classifies the acid-test rock cleanly where the
old synthesis could not. It is a specification with a passing conformance
suite; adoption still needs the independent G7 audit.

Run: python3 tools/g7_change.py   (self-tests; exit 1 on any fixture failure)
"""
import sys

CHANGE_KINDS = {"State", "Constraint", "Invariant", "Policy", "UpdateLaw"}
LOCI = {"Internal", "External", "Relational", "Shared"}
ORIGINS = {"Self", "Other", "Environment", "Mixed", "Unattributed"}
MECHANISMS = {"T", "e", "M", "pi", "G", "H"}

AXES = ["change_kind", "carrier_locus", "causal_origin", "crosses_boundary",
        "mechanism"]

# --- cross-axis consistency rules: what the taxonomy FORBIDS -----------------
# Each rule: (name, predicate over the tuple) -> True means INCOHERENT.
def _incoherent(t):
    ck, cl, co, cb, mech = (t["change_kind"], t["carrier_locus"],
                            t["causal_origin"], t["crosses_boundary"],
                            t["mechanism"])
    rules = [
        # a self-caused change cannot be implemented by an exogenous disturbance
        ("self-cannot-be-exogenous", co == "Self" and mech == "e"),
        # a change that crosses the boundary cannot be carried purely internally
        ("crossing-implies-not-internal-only", cb == "Yes" and cl == "Internal"),
        # M is the boundary-influence mechanism: using it means a crossing
        ("M-implies-crossing", mech == "M" and cb == "No"),
        # G/H update policy/update-law, not raw state, as their immediate kind
        ("G-updates-policy", mech == "G" and ck == "State"),
        ("H-updates-updatelaw", mech == "H" and ck not in ("UpdateLaw", "Policy")),
        # environment origin is not self-authorship
        ("environment-not-self", co == "Environment" and mech in ("pi", "G", "H")),
    ]
    for name, hit in rules:
        if hit:
            return name
    return None


def classify(facts):
    """facts: dict with any subset of the five axes filled (values are the
    enum strings above, or None/absent = unknown). Returns a verdict dict."""
    missing = [a for a in AXES if facts.get(a) in (None, "unknown", "")]
    if missing:
        return {"verdict": "UNDERDETERMINED", "missing": missing,
                "note": "taxonomy refuses to classify without these facts"}
    # validate enum membership
    for a, allowed in (("change_kind", CHANGE_KINDS), ("carrier_locus", LOCI),
                       ("causal_origin", ORIGINS), ("mechanism", MECHANISMS)):
        if facts[a] not in allowed:
            return {"verdict": "INVALID", "axis": a, "value": facts[a]}
    if facts["crosses_boundary"] not in ("Yes", "No"):
        return {"verdict": "INVALID", "axis": "crosses_boundary",
                "value": facts["crosses_boundary"]}
    bad = _incoherent(facts)
    if bad:
        return {"verdict": "INCOHERENT", "rule": bad}
    return {"verdict": "CLASSIFIED",
            "tuple": tuple(facts[a] for a in AXES)}


# --- fixtures: positive, the acid-test rock, incoherent, underdetermined -----
FIXTURES = [
    # THE ACID TEST: the falling rock the old synthesis could not classify.
    ("rock-falls",
     {"change_kind": "State", "carrier_locus": "Internal",
      "causal_origin": "Environment", "crosses_boundary": "No",
      "mechanism": "e"},
     "CLASSIFIED"),
    # ordinary choice: policy selects an already-admissible action; state moves
    ("ordinary-choice",
     {"change_kind": "State", "carrier_locus": "Internal",
      "causal_origin": "Self", "crosses_boundary": "No", "mechanism": "pi"},
     "CLASSIFIED"),
    # commitment: self installs a constraint with future scope
    ("commitment",
     {"change_kind": "Constraint", "carrier_locus": "Internal",
      "causal_origin": "Self", "crosses_boundary": "No", "mechanism": "pi"},
     "CLASSIFIED"),
    # external message: another agent influences via M across the boundary
    ("external-message",
     {"change_kind": "Constraint", "carrier_locus": "External",
      "causal_origin": "Other", "crosses_boundary": "Yes", "mechanism": "M"},
     "CLASSIFIED"),
    # internal random mutation: state changes, cause unattributed, via T
    ("internal-mutation",
     {"change_kind": "State", "carrier_locus": "Internal",
      "causal_origin": "Unattributed", "crosses_boundary": "No",
      "mechanism": "T"},
     "CLASSIFIED"),
    # reflexive self-modification: self updates its policy-update law via H
    ("reflexive-self-mod",
     {"change_kind": "UpdateLaw", "carrier_locus": "Internal",
      "causal_origin": "Self", "crosses_boundary": "No", "mechanism": "H"},
     "CLASSIFIED"),
    # INCOHERENT: claims self-authorship but via exogenous disturbance
    ("self-via-exogenous-FORBIDDEN",
     {"change_kind": "State", "carrier_locus": "Internal",
      "causal_origin": "Self", "crosses_boundary": "No", "mechanism": "e"},
     "INCOHERENT"),
    # INCOHERENT: uses M (boundary mechanism) but claims no crossing
    ("M-without-crossing-FORBIDDEN",
     {"change_kind": "Constraint", "carrier_locus": "External",
      "causal_origin": "Other", "crosses_boundary": "No", "mechanism": "M"},
     "INCOHERENT"),
    # UNDERDETERMINED (Codex's required refusal): a value changed but we do not
    # know whether by the agent's own choice or an external message.
    ("value-changed-origin-unknown",
     {"change_kind": "Constraint", "carrier_locus": "Internal",
      "crosses_boundary": "No", "mechanism": "pi"},  # causal_origin absent
     "UNDERDETERMINED"),
]


def main():
    fails = []
    for name, facts, expected in FIXTURES:
        got = classify(facts)["verdict"]
        ok = got == expected
        print(f"{'ok  ' if ok else 'FAIL'} {name}: expected {expected}, got {got}")
        if not ok:
            fails.append(name)
    # extra assertion: the rock's full tuple is exactly the one Codex named
    rock = classify(dict(FIXTURES[0][1]))
    want = ("State", "Internal", "Environment", "No", "e")
    if rock.get("tuple") != want:
        print(f"FAIL rock-tuple: expected {want}, got {rock.get('tuple')}")
        fails.append("rock-tuple")
    else:
        print(f"ok   rock-tuple: {want} (the case the 3-channel synthesis lost)")
    print()
    if fails:
        print(f"RED: {len(fails)} fixture(s) failed: {fails}")
        return 1
    print("GREEN: taxonomy is total, refuses on missing facts, forbids "
          "incoherent labelings, and classifies the rock.")
    print("(This is a passing conformance suite for the CHANGE taxonomy — NOT "
          "a proof it is the right one. D17 stays open pending G7 audit.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
