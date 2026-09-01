# Adversarial 05 — unclosed capsule fence (T4)

A capsule fence that is opened but never closed (truncated document, edit accident).

```json capsule
{"verifier": "glyph://sha256:deadbeef...", "note": "no closing fence follows"}

Expected: the current regex simply fails to match and drops the block SILENTLY — the
worst outcome, because an author who wrote a capsule sees no error and assumes it was
read. A conformant parser emits a typed error (UNCLOSED_FENCE) and fails closed, never
a silent skip.
