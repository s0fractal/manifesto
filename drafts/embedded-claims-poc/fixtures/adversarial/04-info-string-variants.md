# Adversarial 04 — info-string variants (T4)

Five fenced blocks in a live region whose info strings drift from the frozen token.
Only the exact raw opener may be a live capsule; the rest are ordinary code.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

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

<!-- manifesto-claims:end -->

Expected — PARSE: exactly ONE live capsule (the last block). The others have a
different RAW opener line (`json claim`, `​``` json capsule` with leading space that
CommonMark trims from `info` but the raw-span check rejects, `JSON capsule`,
`json capsule {profile}`) and are ordinary code blocks. Placeholder bodies are
irrelevant at PARSE — schema runs later.
