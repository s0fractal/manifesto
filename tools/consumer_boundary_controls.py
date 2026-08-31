#!/usr/bin/env python3
"""Prove this repository consumes an INSTALLED evaluator, not a checkout.

    python3 tools/consumer_boundary_controls.py

NON-NORMATIVE. Nothing here modifies the sealed SSD pack.

Each control breaks one property of `tools/sigma_boundary.py` and requires the
refusal to name its own reason. The two that matter are the last pair: a
restored absolute-path injection must make a control go red, and the module the
consumer actually uses must be shown to live outside this repository — checked,
not printed.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
results = []


def chk(label, condition, detail=""):
    results.append(bool(condition))
    print(("  OK    " if condition else "  FAIL  ") + label
          + (f" — {detail}" if detail and not condition else ""))


def run(code, env=None, cwd=None):
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment.update(env or {})
    return subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True, env=environment, cwd=str(cwd or ROOT))


def main():
    print("The consumer boundary: an installed package, or a named refusal.\n")

    where = run(f"import sys; sys.path.insert(0, {str(TOOLS)!r});"
                "from sigma_boundary import sigma;"
                "print(sigma().__file__)")
    chk("the evaluator is importable for this run", where.returncode == 0,
        where.stderr.strip()[-200:])
    module_file = where.stdout.strip().splitlines()[-1] if where.returncode == 0 else ""
    print(f"        evaluator at {module_file}")

    # Checked, not printed: the path must be outside this repository.
    chk("the evaluator the consumer uses is NOT inside this repository",
        module_file and str(ROOT.resolve()) not in str(Path(module_file).resolve()),
        module_file)
    chk("...and it is inside a site-packages directory",
        "site-packages" in module_file, module_file)

    # No absolute path or sibling discovery survives in the consumer sources.
    for name in ("glyphlib.py", "conf_mono_settle.py"):
        text = (TOOLS / name).read_text()
        chk(f"{name} contains no absolute path into a Sigma checkout",
            "/Users/" not in text and "Projects/sigma-glyph" not in text)
        chk(f"{name} does not inject a Sigma checkout onto sys.path",
            'os.path.join(SIGMA' not in text and '"impl"' not in text)

    # A missing package must refuse, by name, and say what was expected.
    missing = run(f"import sys; sys.path.insert(0, {str(TOOLS)!r});"
                  "sys.modules['sigma_glyph'] = None;"
                  "import builtins; real = builtins.__import__\n"
                  "def blocked(name, *a, **k):\n"
                  "    if name == 'sigma_glyph': raise ImportError('blocked')\n"
                  "    return real(name, *a, **k)\n"
                  "builtins.__import__ = blocked\n"
                  "from sigma_boundary import sigma, SigmaUnavailable\n"
                  "try:\n"
                  "    sigma(); print('IMPORTED')\n"
                  "except SigmaUnavailable as why: print('REFUSED:', why)\n")
    text = missing.stdout + missing.stderr
    chk("a missing package is refused, not worked around",
        "REFUSED:" in text and "IMPORTED" not in text, text.strip()[-200:])
    chk("...and the refusal names the required API and the required names",
        "book1-eval-hash/1" in text and "eval_hash" in text, text.strip()[-200:])
    chk("...and it says there is deliberately no checkout fallback",
        "no fallback to a source checkout" in text, text.strip()[-200:])

    # A partial surface is refused up front rather than midway.
    partial = run(f"import sys, types; sys.path.insert(0, {str(TOOLS)!r});"
                  "from sigma_boundary import sigma, SigmaUnavailable;"
                  "half = types.ModuleType('half'); half.eval_hash = lambda *a: None;"
                  "\ntry:\n    sigma(module=half); print('ACCEPTED')\n"
                  "except SigmaUnavailable as why: print('REFUSED:', why)\n")
    text = partial.stdout + partial.stderr
    chk("a partially compatible module is refused, naming what is missing",
        "REFUSED:" in text and "does not carry" in text and "sha" in text,
        text.strip()[-200:])

    # The legacy override must be inert AND visible.
    with tempfile.TemporaryDirectory() as elsewhere:
        noisy = run(f"import sys; sys.path.insert(0, {str(TOOLS)!r});"
                    "from sigma_boundary import sigma; print(sigma().__file__)",
                    env={"SIGMA_GLYPH": str(ROOT)}, cwd=elsewhere)
        text = noisy.stdout + noisy.stderr
        chk("SIGMA_GLYPH pointed at this repository does NOT change where the "
            "evaluator comes from",
            noisy.returncode == 0
            and str(ROOT.resolve()) not in noisy.stdout.strip(),
            noisy.stdout.strip()[-160:])
        chk("...and the run says out loud that it was ignored",
            "IGNORED" in text, text.strip()[-160:])

    # M1: restore the defect. The absolute-path injection must break a control.
    restored = ('SIGMA = os.environ.get("SIGMA_GLYPH", '
                '"/Users/s0fractal/Projects/sigma-glyph")')
    chk("M1. the restored absolute-path injection is exactly what the source "
        "controls above forbid",
        "/Users/" in restored and "/Users/" not in (TOOLS / "glyphlib.py").read_text())

    print()
    if all(results):
        print(f"CONSUMER-BOUNDARY-CONTROLS: ALL PASS ({len(results)}/{len(results)})")
        return 0
    print(f"CONSUMER-BOUNDARY-CONTROLS: FAILURES ({sum(results)}/{len(results)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
