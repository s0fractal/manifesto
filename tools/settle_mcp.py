#!/usr/bin/env python3
"""
settle_mcp.py — Settlement MCP Membrane, Stage 1 (GOAL-001 §4).

A dependency-free MCP stdio server (newline-delimited JSON-RPC 2.0) exposing
the settlement stack to any MCP client (Claude Desktop, Cursor, Antigravity,
Neovim, another agent):

  settle_text(markdown)            -> settled_text + receipt (badges ⚓/✗/◇)
  verify_receipt(markdown,receipt) -> re-settles the text, compares receipts
                                      byte-for-byte (verification = replay)
  check_taint(receipts[])          -> inherited-falsehood report across an
                                      ordered sequence of receipts

The engine is the deterministic layer already measured in this repository:
settle_gate (claim classes arith/cmp/count/cite/citei/sha256/mono; small
arithmetic settles on the real Σ-GLYPH machine, ATP-priced), taint_check
(operand ∩ refuted-claimed-values, propagating through PASS arithmetic).
No LLM anywhere in the loop — the membrane is a judge of bytes, not of style.

Client config example (Claude Desktop / Cursor):
  { "mcpServers": { "settle": {
      "command": "python3",
      "args": ["/path/to/manifesto/tools/settle_mcp.py"] } } }
"""
import hashlib
import json
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import settle_gate  # noqa: E402
import taint_check  # noqa: E402
import receipt_freshness  # noqa: E402

PROTOCOL = "2024-11-05"

TOOLS = [
    {
        "name": "settle_text",
        "description": "Settle every ⟦class: payload⟧ claim in a markdown text "
                       "against the repository and the Σ-GLYPH machine. Returns "
                       "the text with verdict badges (⚓ settled / ✗ REFUTED with "
                       "the measured actual value / ◇ unsettled) plus a "
                       "deterministic receipt. Claim classes: arith, cmp, count, "
                       "cite, citei, sha256, mono.",
        "inputSchema": {"type": "object",
                        "properties": {"markdown": {"type": "string"}},
                        "required": ["markdown"]},
    },
    {
        "name": "verify_receipt",
        "description": "Verification is replay: re-settles the given markdown "
                       "and compares the freshly computed receipt with the "
                       "supplied one byte-for-byte. Returns match: true/false "
                       "with both receipt hashes.",
        "inputSchema": {"type": "object",
                        "properties": {"markdown": {"type": "string"},
                                       "receipt": {"type": "string",
                                                   "description": "receipt JSON as returned by settle_text"}},
                        "required": ["markdown", "receipt"]},
    },
    {
        "name": "check_freshness",
        "description": "Is a settlement receipt still true of the current world? "
                       "A 0.3+ receipt records the digest of every file each "
                       "claim read; this recomputes them NOW and reports FRESH / "
                       "STALE (with the affected claims) / LEGACY — without "
                       "re-running the gate or any LLM. Answers the 'a receipt "
                       "silently goes stale when its inputs change' problem.",
        "inputSchema": {"type": "object",
                        "properties": {"receipt": {"type": "string",
                                                   "description": "receipt JSON from settle_text"}},
                        "required": ["receipt"]},
    },
    {
        "name": "check_taint",
        "description": "Detect inherited falsehood across an ORDERED sequence "
                       "of receipts (earlier -> later): flags later numeric "
                       "claims whose operands equal values claimed by earlier "
                       "REFUTED claims, propagating poison through internally "
                       "valid arithmetic. The per-claim gate verdict cannot see "
                       "this; the taint pass can.",
        "inputSchema": {"type": "object",
                        "properties": {"receipts": {"type": "array",
                                                    "items": {"type": "string"},
                                                    "description": "receipt JSONs in generation order"}},
                        "required": ["receipts"]},
    },
]


def build_receipt(text, results):
    """Delegate to the gate's own minter. This used to be a second copy of that
    block, which is how the 0.3/0.4 shape rule could have been installed in one
    producer and missed in the other."""
    body, receipt_sha, _ = settle_gate.build_receipt(text, results)
    return body + "\nRECEIPT_SHA256: " + receipt_sha + "\n"


def tool_settle_text(args):
    text = args["markdown"]
    settled, results = settle_gate.gate(text)
    return {"settled_text": settled, "receipt": build_receipt(text, results)}


def _split_receipt(s):
    """Return (body, trailer_hash) for a receipt string, or (None, None) if it
    is not in the exact `<body>\\nRECEIPT_SHA256: <hex>\\n` canonical shape."""
    m = re.search(r"\nRECEIPT_SHA256: ([0-9a-f]{64})\n?\Z", s)
    if not m:
        return None, None
    return s[:m.start()], m.group(1)


def tool_verify_receipt(args):
    """Verification is replay AND self-consistency (P0 fix, Codex F1).
    A forged body carrying a copied trailer must NOT verify: we recompute the
    digest of the SUPPLIED body and reject any trailer/body mismatch BEFORE
    comparing against a fresh replay."""
    given = args["receipt"]
    given_body, given_trailer = _split_receipt(given)
    if given_body is None:
        return {"match": False, "reason": "supplied receipt is not in canonical "
                "`<body>\\nRECEIPT_SHA256: <hex>` form"}
    recomputed = hashlib.sha256(given_body.encode()).hexdigest()
    if recomputed != given_trailer:
        return {"match": False, "reason": "supplied body does not hash to its own "
                "trailer (forged or corrupted receipt)",
                "supplied_trailer": given_trailer, "recomputed": recomputed}
    fresh = tool_settle_text({"markdown": args["markdown"]})["receipt"]
    _, fresh_trailer = _split_receipt(fresh)
    return {"match": fresh == given,
            "fresh_receipt_sha256": fresh_trailer,
            "given_receipt_sha256": given_trailer,
            "note": "verification = self-consistency (body hashes to trailer) "
                    "AND replay (fresh settlement recomputed from the markdown "
                    "reproduces the receipt byte-for-byte)"}


def tool_check_taint(args):
    poison, tainted, total_later = set(), [], 0
    for i, rtxt in enumerate(args["receipts"]):
        cut = rtxt.rfind("RECEIPT_SHA256")
        rec = json.loads(rtxt[:cut].strip() if cut != -1 else rtxt)
        for c in rec["claims"]:
            if i > 0:
                ops = taint_check.operands(c)
                if ops:
                    total_later += 1
                    hit = sorted(set(ops) & poison)
                    if hit:
                        tainted.append({"payload": c["payload"],
                                        "poisoned_operands": hit,
                                        "receipt_index": i})
                        if c["class"] == "arith" and c["verdict"] == "PASS":
                            poison.add(ops[-1])
            if c["verdict"] == "REFUTED":
                v = taint_check.claimed_value(c)
                if v is not None:
                    poison.add(v)
    return {"tainted": tainted, "tainted_count": len(tainted),
            "downstream_numeric_claims": total_later,
            "poison_set": sorted(poison)}


def tool_check_freshness(args):
    s = args["receipt"]
    cut = s.rfind("RECEIPT_SHA256")
    rec = json.loads(s[:cut].strip() if cut != -1 else s)
    deps = rec.get("deps")
    if deps is None:
        return {"verdict": "legacy", "reason": "no deps recorded (pre-0.3 receipt)"}
    stale = []
    for path, settled in deps.items():
        now = receipt_freshness.current_digest(path)
        if now is None:
            stale.append({"path": path, "why": "missing/unresolvable"})
        elif now not in settled:
            stale.append({"path": path, "why": "changed",
                          "settled": settled[0][:12], "now": now[:12],
                          "affected": [c.get("payload") for c in rec.get("claims", [])
                                       if c.get("dep", {}).get("path") == path]})
    return {"verdict": "fresh" if not stale else "stale",
            "dependencies": len(deps), "stale": stale}


HANDLERS = {"settle_text": tool_settle_text,
            "verify_receipt": tool_verify_receipt,
            "check_freshness": tool_check_freshness,
            "check_taint": tool_check_taint}


def reply(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        method, msg_id = msg.get("method"), msg.get("id")
        if method == "initialize":
            reply(msg_id, {"protocolVersion": PROTOCOL,
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "settle-mcp",
                                          "version": "0.1.0"}})
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            reply(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            name = msg["params"]["name"]
            args = msg["params"].get("arguments", {})
            if name not in HANDLERS:
                reply(msg_id, error={"code": -32602, "message": f"unknown tool {name}"})
                continue
            try:
                result = HANDLERS[name](args)
                reply(msg_id, {"content": [{"type": "text",
                                            "text": json.dumps(result, ensure_ascii=False, indent=2)}]})
            except Exception as e:  # tool errors are results, not crashes
                reply(msg_id, {"content": [{"type": "text",
                                            "text": f"tool error: {e!r}"}],
                               "isError": True})
        elif msg_id is not None:
            reply(msg_id, error={"code": -32601, "message": f"unknown method {method}"})


if __name__ == "__main__":
    main()
