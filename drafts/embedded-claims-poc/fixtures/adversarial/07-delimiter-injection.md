# Adversarial 07 — delimiter injection (T7)

Two payloads that try to terminate their own container.

A cite whose quoted text contains the closing glyph ⟧:
⟦cite: "he said ⟧ and left" in NOTES.md⟧

A capsule whose JSON string value contains a code fence:

```json capsule
{"verifier": "glyph://sha256:deadbeef...", "note": "ends with ``` inside a string"}
```

Expected: the glyph claim's `[^⟧]+` payload grammar stops at the FIRST `⟧`, so the
cite is truncated to `"he said ` — wrong. The capsule's embedded ```` ``` ```` closes
the fence early for a naive scanner. A conformant parser needs an escaping rule or a
structural (not first-delimiter) parse, decided in §8.5. Until then, a payload
containing its own delimiter must be a typed error, not a silent truncation.
