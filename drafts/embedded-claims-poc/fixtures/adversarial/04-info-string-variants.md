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

Expected: if the frozen info string is exactly `json capsule` (no leading space, case
sensitive, no trailing tokens), only the LAST block is a candidate. The four variants
are ordinary code blocks, not capsules. The decision (freeze one token, reject the
rest) is §8.2 of the threat model.
