# Adversarial 16 — two capsules for one local_id (compile layer)

One claim (`{#A}`) and TWO schema-valid capsules that both bind it.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦arith: 74 + 1 = 75⟧{#A}

```json capsule
{"claim_ref": "A", "verifier": "glyph://sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

```json capsule
{"claim_ref": "A", "verifier": "settle-gate://sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}
```

<!-- manifesto-claims:end -->

Expected — COMPILE: `DUPLICATE_CLAIM_REF` — a claim owns at most one capsule; two
capsules referencing local_id `A` is a typed error, not a silent last-wins.
