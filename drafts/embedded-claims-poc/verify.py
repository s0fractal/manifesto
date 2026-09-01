#!/usr/bin/env python3
"""
verify.py — embedded-claims PoC: CLI + human renderer.

This file is deliberately OUTSIDE the verifier closure. All verdict-determining
logic lives in settle_core.py (bound into the verifier identity); here we only
read a file, delegate, and render. So editing a docstring, the CLI, or the
renderer never rotates a verifier id — only a change to what actually decides a
verdict does.

Usage:  verify.py <fixture.md>

A fixture is Markdown with one inline claim ⟦class: payload⟧ and an optional fenced
```json capsule of AUTHOR ASSERTIONS (pinned verifier, dependency for freshness,
the evaluation_id the author bets on, a semantic binding). Assertions are claims,
not verdicts; the tool recomputes and reports whether they reproduce, on two
independent axes (execution, binding) with an explicit fact list. See README.md.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settle_core as core  # noqa: E402

# Re-exports so callers/tests keep a single entry point.
verify_report = core.verify_report
verifier_id = core.verifier_id
identities = core.identities
commit = core.commit
EFFECT_OPS = core.EFFECT_OPS
_sandbox_state = core._sandbox_state
_short = core._short


def verify_file(path):
    with open(path, encoding="utf-8") as f:
        return core.verify_report(f.read())


def render(report):
    if "error" in report:
        return "✗ " + report["error"]
    c = report["claim"]
    i = report["identity"]
    lines = [f"⟦{c['class']}: {c['payload']}⟧",
             f"  execution : {report['execution']}   facts={report['execution_facts']}",
             f"  binding   : {report['binding']}",
             f"  verifier  : {core._short(report['verifier'])}",
             f"  claim_id       : {i['claim_id'][:16]}",
             f"  result_value_id: {i['result_value_id'][:16]}",
             f"  evaluation_id  : {i['evaluation_id'][:16]}",
             f"  dependency_id  : {(i['dependency_id'] or '—')[:16]}"]
    if report.get("normal_forms"):
        nf = report["normal_forms"]
        lines.append(f"  normal_forms   : lhs={nf['lhs_nf'][:12]} rhs={nf['rhs_nf'][:12]}")
    for n in report["notes"]:
        lines.append(f"  · {n}")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <fixture.md>", file=sys.stderr)
        return 2
    report = verify_file(sys.argv[1])
    print(render(report))
    print("REPORT " + json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
