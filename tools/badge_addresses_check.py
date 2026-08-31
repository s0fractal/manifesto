#!/usr/bin/env python3
"""Recompute the addresses `ts-sigma/replayable-badge.html` pins.

The page recomputes them in the viewer's browser with Web Crypto. This does it
in Python, from the node layout rather than from the page's own JavaScript, so
the two routes are independent: a serializer bug that agreed with itself would
still be caught here.

Layout, Book I §3.2:  LITERAL = 0x00 0x01 ‖ atom   APPLY = 0x02 0x06 ‖ l ‖ r
"""
import hashlib
import pathlib
import re
import sys

HTML = pathlib.Path(__file__).resolve().parents[1] / "ts-sigma/replayable-badge.html"

sha = lambda data: hashlib.sha256(data).digest()
lit = lambda atom: bytes([0x00, 0x01]) + atom
app = lambda l, r: bytes([0x02, 0x06]) + sha(l) + sha(r)


def main():
    html = HTML.read_text()
    block = re.search(r"const EXPECT\s*=\s*\{(.*?)\n  \};", html, re.S)
    if not block:
        print("the page no longer declares EXPECT in the form this reads",
              file=sys.stderr)
        return 1
    pinned = dict(re.findall(r'"([^"]+)"\s*:\s*"([0-9a-f]{64})"', block.group(1)))

    I, K, S = lit(sha(b"I")), lit(sha(b"K")), lit(sha(b"S"))
    FALSE = app(K, I)
    built = {
        "I": I, "K": K, "S": S,
        "FALSE = K I": FALSE,
        "I K": app(I, K),
        "S I I": app(app(S, I), I),
        "K FALSE I": app(app(K, FALSE), I),
    }
    if set(built) != set(pinned):
        print(f"the page pins {sorted(pinned)}, this checks {sorted(built)}",
              file=sys.stderr)
        return 1

    failed = 0
    for name, node in built.items():
        got = sha(node).hex()
        good = got == pinned[name]
        failed += not good
        print(("  OK    " if good else "  FAIL  ")
              + f"{name:14} {got[:16]}…"
              + ("" if good else f"  pinned {pinned[name][:16]}…"))
    print()
    if failed:
        print(f"BADGE-ADDRESSES: {failed} of {len(built)} do not recompute")
        return 1
    print(f"BADGE-ADDRESSES: ALL PASS ({len(built)}/{len(built)} recomputed "
          f"independently of the page's JavaScript)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
