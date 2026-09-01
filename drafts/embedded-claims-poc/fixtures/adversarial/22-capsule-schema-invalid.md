# Adversarial 22 — capsule.v2 schema violation (compile layer)

Valid JSON, but the claim's `class` is not a known settlement class. The closed v2
schema must reject it.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "X", "class": "bogus", "payload": "x"}}
```

<!-- manifesto-claims:end -->

Expected — PARSE: VALID, one capsule. COMPILE: INVALID, `CAPSULE_SCHEMA_INVALID`
(unknown claim.class), no record emitted.
