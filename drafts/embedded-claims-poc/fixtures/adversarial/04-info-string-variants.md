# Adversarial 04 — info-string variants (T4)

Five fenced blocks whose info strings drift from the frozen token. Only the exact
token may be a live-capsule candidate; the rest must be ignored (as ordinary code) or
rejected with a typed reason — never silently treated as capsules.

```json claim
{"note": "architecture doc uses 'json claim'"}
```

``` json capsule
{"note": "leading space before json"}
```

```JSON capsule
{"note": "uppercase"}
```

```json capsule {profile}
{"note": "trailing tokens"}
```

```json capsule
{"note": "the exact frozen token"}
```

Expected — PARSE layer only (schema/compile not yet reached, so the placeholder
bodies are irrelevant here): only the LAST block (`json capsule`, exact) is a capsule
candidate; the four variants are ordinary code blocks. Note the CommonMark subtlety
(Codex P1): CommonMark TRIMS info-string whitespace, so ``` json capsule``` (leading
space) has the same structural info string as the exact token — the AST cannot reject
it. The protocol profile therefore rejects it at the RAW opener-line level (exact
spelling required). Uppercase, trailing `{profile}`, and the `json claim` token are
likewise rejected by the raw-span profile. Freezing the one token is open decision §8.2.
