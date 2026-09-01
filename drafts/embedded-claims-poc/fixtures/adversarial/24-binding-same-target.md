# Adversarial 24 — same binding target, different claims (compile layer, P0)

Two different claims assert the SAME relation/target/status. Their binding identities
must differ — a binding is bound to its claim, so it cannot be transferred between
claims (composition laundering, architecture §13.11).

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "C1", "class": "arith", "payload": "1 + 1 = 2"}, "binding": {"relation": "measures", "target": "the same prose target", "status": "ASSERTED"}}
```

```json capsule
{"schema_version": "manifesto.capsule.v2", "claim": {"local_id": "C2", "class": "arith", "payload": "2 + 2 = 4"}, "binding": {"relation": "measures", "target": "the same prose target", "status": "ASSERTED"}}
```

<!-- manifesto-claims:end -->

Expected — COMPILE: COMPILED, two records (C1, C2), and their `binding.id` values DIFFER
even though relation/target/status are identical, because each binding record includes
its `claim_id`.
