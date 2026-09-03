#!/usr/bin/env python3
"""Fail closed if retired embedded-claims drafts re-enter the active surface."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


RETIRED = {
    "drafts/EMBED-FORMAT-DESIGN.md":
        "ee60c7ac375b4ea8d7931688d84840c4ee7bd0d066f5f3e32715b6bb3f6992cc",
    "drafts/EMBEDDING-SETTLEMENT.md":
        "1740691754bef4383a91e7e85cdc6976c36160a1db5ca3459f181008eb43b57a",
    "drafts/EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md":
        "57cc4f47d362bc4c296f866d06430ea482c7aa21d058db359b337c163fdcb726",
    "drafts/EMBEDDED-CLAIMS-REVIEW-0.1.md":
        "5aac3a25db34c852a1b8cd51e6fd1c109f044b16ecd6f6d85f7c517cd73edc94",
    "drafts/embedded-claims-poc/PARSER-THREAT-MODEL.md":
        "789decea49df4bdf782de6bfce4ff9a2e4bea635b86f3ced3b3fef7424526dc9",
}

README = "drafts/embedded-claims-poc/README.md"
TOMBSTONE = "drafts/EMBEDDED-CLAIMS-RETIREMENT-0.1.md"
WORKFLOW = ".github/workflows/embedded-claims-poc.yml"
SELF = "tools/embedded_claims_surface_check.py"

REQUIRED = {
    README: (
        "current operational surface",
        "CAPSULE-ONLY",
        "manifesto.capsule.v2",
        "LEGACY-NONCANONICAL",
        "NO DOCUMENT-LEVEL\nVERDICT",
    ),
    TOMBSTONE: (
        "applied controlled-forgetting specimen",
        "current admission: EXCLUDED",
        "Known loss",
        "2a6e54d81a493623a32521ead5850e3ff7d8b92f",
    ),
    WORKFLOW: (
        "tools/embedded_claims_surface_check.py",
        "test_cli.py",
    ),
}

STALE_MARKERS = (
    "full parser still pending",
    "canonical pipeline is inline",
)


def tracked_paths(root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"],
    )
    return [p.decode("utf-8") for p in out.split(b"\0") if p]


def check(root: Path, paths: list[str] | None = None) -> list[str]:
    errors: list[str] = []

    for rel in RETIRED:
        if (root / rel).exists():
            errors.append(f"RETIRED_SUBJECT_PRESENT:{rel}")

    for rel, markers in REQUIRED.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"REQUIRED_SURFACE_MISSING:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"BOUNDARY_MARKER_MISSING:{rel}:{marker}")

    readme = root / README
    if readme.is_file():
        lower = readme.read_text(encoding="utf-8").lower()
        for marker in STALE_MARKERS:
            if marker in lower:
                errors.append(f"STALE_CURRENT_CLAIM:{README}:{marker}")

    candidates = paths if paths is not None else tracked_paths(root)
    ignored_prefixes = ("reviews/", ".git/")
    ignored_exact = {TOMBSTONE, SELF}
    retired_names = tuple(Path(p).name for p in RETIRED)
    for rel in candidates:
        if rel in ignored_exact or rel.startswith(ignored_prefixes):
            continue
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name in retired_names:
            if name in text:
                errors.append(f"ZOMBIE_REFERENCE:{rel}:{name}")

    tombstone = root / TOMBSTONE
    if tombstone.is_file():
        text = tombstone.read_text(encoding="utf-8")
        for rel, digest in RETIRED.items():
            if rel not in text or digest not in text:
                errors.append(f"TOMBSTONE_SUBJECT_UNBOUND:{rel}")

    return sorted(set(errors))


def write_minimal_tree(root: Path) -> list[str]:
    paths = list(REQUIRED)
    for rel in REQUIRED:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / README).write_text(
        "current operational surface CAPSULE-ONLY manifesto.capsule.v2 "
        "LEGACY-NONCANONICAL NO DOCUMENT-LEVEL\nVERDICT\n",
        encoding="utf-8",
    )
    subjects = "\n".join(f"{p} {d}" for p, d in RETIRED.items())
    (root / TOMBSTONE).write_text(
        "applied controlled-forgetting specimen\n"
        "current admission: EXCLUDED\nKnown loss\n"
        "2a6e54d81a493623a32521ead5850e3ff7d8b92f\n" + subjects,
        encoding="utf-8",
    )
    (root / WORKFLOW).write_text(
        "tools/embedded_claims_surface_check.py\ntest_cli.py\n",
        encoding="utf-8",
    )
    return paths


def selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        paths = write_minimal_tree(root)
        assert check(root, paths) == [], check(root, paths)

        resurrected = next(iter(RETIRED))
        (root / resurrected).parent.mkdir(parents=True, exist_ok=True)
        (root / resurrected).write_text("old bytes", encoding="utf-8")
        assert any(e.startswith("RETIRED_SUBJECT_PRESENT:")
                   for e in check(root, paths + [resurrected]))
        (root / resurrected).unlink()

        zombie = root / "drafts/current.md"
        zombie.parent.mkdir(parents=True, exist_ok=True)
        zombie.write_text(Path(resurrected).name, encoding="utf-8")
        assert any(e.startswith("ZOMBIE_REFERENCE:")
                   for e in check(root, paths + ["drafts/current.md"]))
        zombie.unlink()

        (root / README).write_text("current operational surface\n", encoding="utf-8")
        assert any(e.startswith("BOUNDARY_MARKER_MISSING:")
                   for e in check(root, paths))

    print("ALL PASS (embedded-claims surface mutation controls)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    root = Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS embedded-claims active surface: 5 retired, 0 zombie references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
