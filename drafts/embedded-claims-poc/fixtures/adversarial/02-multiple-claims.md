# Adversarial 02 — multiple capsules in one region (T2, capsule form)

A region may carry several explicit capsules. Each is a separate machine-eligible bet;
the surrounding prose is untouched.

Звичайна проза може говорити про сім тез, цінність і білий конус — і це лишається
прозою.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "A", "class": "arith", "payload": "3 + 6 = 9"}}
```

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "B", "class": "count", "payload": "/^## Теза [0-9]+:/ in README.md = 7"}}
```

<!-- manifesto-claims:end -->

Expected — PARSE: status VALID, TWO capsules in document order, each with its own raw
byte span. The prose sentence about theses is inert. Claims live INSIDE the capsules —
the parser never scans the sentence.
