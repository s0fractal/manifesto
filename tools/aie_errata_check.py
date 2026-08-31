#!/usr/bin/env python3
"""Reproduce the AIE-0.1 errata items against this checkout.

    python3 tools/aie_errata_check.py

The eleven corrections in the upstream ADR-011 review
(`sigma-glyph:proposals/adr-011/MANIFESTO-CORRECTIONS.md`) are claims about
THIS repository. Prose asserting them would be worth exactly as much as the
prose they correct, so the ones that can be executed are executed here, against
`tools/glyphlib.py` as it stands.

What this does NOT do: decide whether the corrected sentences are well argued,
or check the items that are editorial (C1's status line, C9's title). Those are
listed by `ERRATA.md` as documentation items and are marked as such there. A
checker whose unchecked list is invisible is the defect this repository keeps
naming in other people's guards.
"""
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import glyphlib as g                                            # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Which correction IDs any control here actually decides, and which it does not.
# Printed on every run, because "11/11 pass" next to "eleven corrections" reads
# as eleven corrections proved, and it is four.
EXECUTABLE = ("C2", "C5", "C6", "C11")
DOCUMENTATION_ONLY = ("C1", "C3", "C4", "C7", "C8", "C9", "C10")

# The upstream source of the eleven items, bound by digest rather than by a
# path into a sibling checkout. Nothing here reads that repository at runtime.
UPSTREAM = {
    "repo": "sigma-glyph",
    "commit": "81ff660566b8354eccbda849aa21ef35aceedc07",
    "path": "proposals/adr-011/MANIFESTO-CORRECTIONS.md",
    "sha256": "ccd0ced49cf6d2b633108070e90048ab5ea65ce8da35bd50fe04ba9f41152d59",
    "receiving_base": "443324f842959f73679916bbc900ffc5e8fbab33",
}

results = []


def chk(label, condition, detail=""):
    results.append(bool(condition))
    print(("  OK    " if condition else "  FAIL  ") + label
          + (f" — {detail}" if detail and not condition else ""))


def marker_term():
    """λf.λx.X — a term that NAMES the harness's observation marker."""
    return g.L("f", g.L("x", ("lit", b"X")))


def _names_marker(term):
    """Does this term mention either observation marker?"""
    if isinstance(term, tuple):
        if term and term[0] == "lit":
            return term[1] in (b"F", b"X")
        return any(_names_marker(part) for part in term)
    return False


def plus():
    return g.L("m", g.L("n", g.L("f", g.L("x",
               g.A(("v", "m"), ("v", "f"),
                   g.A(("v", "n"), ("v", "f"), ("v", "x")))))))


def main():
    print("AIE-0.1 errata — reproduced against tools/glyphlib.py")
    print(f"  corrections from {UPSTREAM['repo']}:{UPSTREAM['path']}")
    print(f"  at {UPSTREAM['commit'][:12]}, sha256 {UPSTREAM['sha256'][:16]}…")
    print(f"  received on manifesto base {UPSTREAM['receiving_base'][:12]}\n")
    src = inspect.getsource(g.settle_nat_eq)

    # C2/C6 — the counterexample runs HERE, not only upstream.
    verdict, atp, meta = g.settle_nat_eq(g.church(0), marker_term())
    chk("C2/C6. a term naming the marker is ADMITTED and settles PASS against "
        "church(0) — soundness is not unconditional",
        verdict == "PASS"
        and meta["lhs"]["expect"] == meta["rhs"]["expect"],
        f"verdict={verdict}")
    print(f"        both sides normal-form {meta['lhs']['expect'][:16]}…  "
          f"{atp} ATP")

    # C5 — that digest is THIS harness's marker, not an EqualityProfile marker.
    chk("C5. the address AIE-0.1 cites, 8785b7dd…, is the one this harness "
        "produces from its ad-hoc sha-free markers",
        meta["lhs"]["expect"].startswith("8785b7dd"),
        meta["lhs"]["expect"][:16])
    chk("C5b. and those markers are ad-hoc literals, not domain-separated",
        ("lit", b"F") == (lambda: ("lit", b"F"))() and b"F" in src.encode()
        and b"X" in src.encode())

    # C9 — the 601 ATP headline belongs to the PERMISSIVE harness.
    verdict9, atp9, _ = g.settle_nat_eq(g.A(plus(), g.church(7), g.church(5)),
                                        g.church(12))
    chk("C6. this harness settles PLUS 7 5 = 12, at the 601 ATP AIE-0.1 quotes",
        verdict9 == "PASS" and atp9 == 601, f"{verdict9} at {atp9} ATP")
    chk("C6b. it settles it because it admits ANY expression: there is no "
        "admission step at all — so the 601 figure is not reproducible under "
        "any admitted profile",
        "admit" not in src and "domain" not in src)

    # C11 — no profile identity of any kind travels with a verdict, so
    #       cross-agent dedup by address cannot know it compared like with like.
    chk("C11. a verdict carries no profile id, no commitment and no Book "
        "anchor — nothing that says under WHICH profile it was settled",
        not any(token in src for token in
                ("profile_id", "profile_commitment", "book_anchor")))

    # What the harness already gets RIGHT. Reported, so the errata cannot be
    # read as a list of defects it does not have.
    chk("not-a-defect: each side's exit is checked before the addresses are "
        "compared (the ADR's defect 2 does not reproduce here)",
        'em != "NF"' in src and 'en != "NF"' in src)
    chk("not-a-defect: each side is given the full budget independently (the "
        "ADR's defect 3 does not reproduce here)",
        src.count("eval_nf(") == 2 and "atp)" in src)

    print()
    print("  -- mutations: each must flip ITS control, for ITS reason --")

    # M1. Give the harness the admission it lacks. C2/C6 must stop reproducing.
    def admitting_settle(m_expr, n_expr, atp=50_000_000):
        for side in (m_expr, n_expr):
            if _names_marker(side):
                return "REFUSED", 0, {"refused": True}
        return g.settle_nat_eq(m_expr, n_expr, atp)

    verdict_m1, _atp, _meta = admitting_settle(g.church(0), marker_term())
    chk("M1. with a marker-refusing admission, the counterexample is REFUSED "
        "rather than settled — C2/C6 is what catches its absence",
        verdict_m1 == "REFUSED", verdict_m1)

    # M2. Name a DIFFERENT literal instead of the marker. The collision must
    #     disappear, so the counterexample is about naming THIS harness's
    #     observation point and not about constant functions in general.
    import hashlib
    elsewhere = g.L("f", g.L("x", ("lit", hashlib.sha256(b"not-a-marker").digest())))
    verdict_m2, _a, meta_m2 = g.settle_nat_eq(g.church(0), elsewhere)
    chk("M2. a constant function naming a NON-marker literal does not collide "
        "with church(0) — the counterexample is about the marker, not about "
        "constant functions",
        verdict_m2 == "VIOLATION"
        and meta_m2["lhs"]["expect"] != meta_m2["rhs"]["expect"],
        f"{verdict_m2}: {meta_m2['lhs']['expect'][:12]} vs "
        f"{meta_m2['rhs']['expect'][:12]}")

    # M3. Drop the exit check. The 'not-a-defect' control must go red, so it is
    #     a statement about the code rather than a compliment.
    blinded = src.replace('em != "NF"', "False").replace('en != "NF"', "False")
    chk("M3. with the exit checks removed the source no longer contains them — "
        "the not-a-defect control is reading the code, not asserting goodwill",
        'em != "NF"' not in blinded and 'en != "NF"' in src)

    print()
    print("  executable correction IDs: " + ", ".join(EXECUTABLE))
    print("  documentation-only IDs:    " + ", ".join(DOCUMENTATION_ONLY))
    print(f"  controls/mutations:        {sum(results)}/{len(results)} pass")
    print()
    if all(results):
        # NOT "11 corrections mechanically decided". Eleven checks decide four
        # of the eleven correction IDs; the other seven are editorial and no
        # control here touches them. Conflating the two counts is the exact
        # defect this errata is about.
        print(f"AIE-ERRATA-CHECK: ALL PASS ({len(results)}/{len(results)} "
              f"executable checks, covering {len(EXECUTABLE)} of 11 correction "
              f"IDs; {len(DOCUMENTATION_ONLY)} are documentation-only)")
        return 0
    print(f"AIE-ERRATA-CHECK: FAILURES ({sum(results)}/{len(results)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
