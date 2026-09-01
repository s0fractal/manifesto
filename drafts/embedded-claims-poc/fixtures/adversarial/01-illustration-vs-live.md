# Adversarial 01 — illustration capsule vs live capsule (T1, the central threat)

Two `json capsule` blocks that look identical, disambiguated structurally: one is an
illustration inside an outer fence, the other is live inside a region. No guessing.

An illustration of a capsule, fenced as documentation (inert):

````markdown
```json capsule
{"claim": {"class": "arith", "payload": "2 + 2 = 5"}}
```
````

A live capsule inside a region:

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "T", "class": "arith", "payload": "3 + 6 = 9"}}
```

<!-- manifesto-claims:end -->

Expected — PARSE: status VALID, exactly ONE capsule (the live one). The illustration is
content of the outer ````markdown fence, so CommonMark block structure makes it inert.
Prose stays prose; only the explicit in-region capsule is machine-eligible.
