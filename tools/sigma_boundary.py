#!/usr/bin/env python3
"""How this repository reaches the Σ-GLYPH evaluator: as an installed package.

    from sigma_boundary import sigma
    sg = sigma()

WHY THIS EXISTS
---------------
`glyphlib.py` and `conf_mono_settle.py` each began:

    SIGMA = os.environ.get("SIGMA_GLYPH", "/Users/s0fractal/Projects/sigma-glyph")
    sys.path.insert(0, os.path.join(SIGMA, "impl"))
    import sigma_glyph as sg

That is one machine's directory layout compiled into a library. It worked for
exactly one person, silently, and anywhere else it either failed with
`ModuleNotFoundError` or — worse — succeeded against whatever happened to be at
that path. This repository's own CI hit the first case the moment a check was
wired up.

WHAT REPLACES IT
----------------
A plain package import. `sigma-glyph` is a dependency like any other; install
it, and this works. Do not install it, and this says so, by name, and stops.

WHAT IT WILL NOT DO
-------------------
- fall back to a source checkout, a sibling directory, or an environment
  variable naming one;
- substitute a local copy of the evaluator or the canonical serializer;
- continue with a partial surface, so that a missing name surfaces later as a
  wrong answer instead of now as a refusal.

Injection is allowed for tests — `sigma(module=...)` — and the injected module
is checked against the same required surface. A test double that does not carry
these names is refused exactly like a missing install; a test double that
reimplements Σ semantics is out of scope for this boundary and would defeat the
point of having one.
"""
import os

# Every name this repository actually calls on the evaluator. Checked as a set,
# so a partially-compatible package is refused up front rather than midway
# through a settlement.
REQUIRED_SURFACE = (
    "eval_hash",
    "sha",
    "term_bytes",
    "term_hash",
    "Store",
    "ResourceFault",
    "I_BYTES",
    "K_BYTES",
    "S_BYTES",
)

# The shape consumed, not the release consumed. A package version tells a reader
# which upload this was; this tells them which surface was relied on.
REQUIRED_API = "book1-eval-hash/1"

LEGACY_OVERRIDE = "SIGMA_GLYPH"


class SigmaUnavailable(ImportError):
    """The evaluator is not importable, or does not carry the surface used."""


def sigma(module=None):
    """The evaluator module, or a refusal that names what was expected."""
    if module is None:
        try:
            import sigma_glyph as module
        except ImportError as failure:
            raise SigmaUnavailable(
                "the sigma-glyph package is not importable: "
                f"{failure}.\n"
                "This repository consumes the evaluator as an INSTALLED "
                "PACKAGE. Install it (for example `pip install sigma-glyph`, "
                "or install a candidate wheel) and re-run.\n"
                f"Required API: {REQUIRED_API}\n"
                f"Required names: {', '.join(REQUIRED_SURFACE)}\n"
                "There is deliberately no fallback to a source checkout: "
                "reaching into one made this library depend on a single "
                "machine's directory layout."
            ) from failure

    missing = [name for name in REQUIRED_SURFACE if not hasattr(module, name)]
    if missing:
        raise SigmaUnavailable(
            f"the importable sigma_glyph does not carry: {', '.join(missing)}.\n"
            f"Required API: {REQUIRED_API}\n"
            f"Found at: {getattr(module, '__file__', '<no file>')}\n"
            "Refusing rather than continuing with a partial surface: a missing "
            "name that surfaces later is a wrong answer, not an error."
        )

    if os.environ.get(LEGACY_OVERRIDE):
        # Not fatal — a stale export in someone's shell should not break a run —
        # but it must never look like it did anything, because for a long time
        # it did.
        import sys
        print(f"note: {LEGACY_OVERRIDE} is set and is IGNORED; the evaluator "
              f"comes from {getattr(module, '__file__', '<unknown>')}",
              file=sys.stderr)
    return module


def where():
    """Where the evaluator actually came from. For reports, not for logic."""
    return getattr(sigma(), "__file__", "<unknown>")
