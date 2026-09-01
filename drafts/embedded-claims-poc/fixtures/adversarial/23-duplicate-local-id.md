# Adversarial 23 — duplicate local_id across capsules (compile layer)

Two schema-valid v2 capsules share one `claim.local_id`. A local_id is the human name
of a claim within a document and must be unique; the second is a typed error, never a
silent last-wins.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "DUP", "class": "arith", "payload": "1 + 1 = 2"}}
```

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "DUP", "class": "arith", "payload": "2 + 2 = 4"}}
```

<!-- manifesto-claims:end -->

Expected — PARSE: VALID, two capsules. COMPILE: INVALID, `DUPLICATE_LOCAL_ID` (the
first record compiles, the second is refused).
