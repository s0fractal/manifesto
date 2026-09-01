# Adversarial 21 — capsule body is not strict JSON (compile layer)

The parser extracts the capsule (the fence is well-formed), but its body is not valid
JSON. The compiler must fail closed.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{ this is not valid json }
```

<!-- manifesto-claims:end -->

Expected — PARSE: VALID, one capsule. COMPILE: INVALID, `CAPSULE_NOT_STRICT_JSON`
(caught by the closed scalar profile / JSON parse), no record emitted for it.
