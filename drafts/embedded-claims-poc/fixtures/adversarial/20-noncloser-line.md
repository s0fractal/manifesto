# Adversarial 20 — a line that only looks like a closer (Codex P1)

The capsule's "closing" line is ```` ```not-a-closer ````, which is NOT a valid closing
fence (backticks followed by text). A `startswith("```")` check would wrongly call the
fence closed; the exact closing-fence rule rejects it, so the fence is unclosed.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"verifier": "glyph://sha256:deadbeef..."}
```not-a-closer

<!-- manifesto-claims:end -->

Expected — PARSE: status INVALID, `UNCLOSED_FENCE` (the fence is never validly closed).
Since the unclosed fence then runs to EOF and swallows the `end` marker, `MISSING_END`
is also reported. Never a silent "closed".
