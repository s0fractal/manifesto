# Adversarial 15 — dangling claim_ref (compile layer)

The region has one claim (`{#A}`) and a schema-valid capsule whose `claim_ref` names a
claim that does not exist.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

⟦arith: 74 + 1 = 75⟧{#A}

```json capsule
{"claim_ref": "Z", "verifier": "glyph://sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

<!-- manifesto-claims:end -->

Expected — COMPILE: the capsule is schema-valid (so the compiler reaches association),
then fails with `DANGLING_CLAIM_REF` — `claim_ref: "Z"` matches no claim (only `A`
exists). A capsule may not reference a claim that is not present.
