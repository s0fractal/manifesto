# Adversarial 09 — claim ↔ capsule association (T8)

Two claims and two capsules in one document. Which capsule binds to which claim?

First claim: ⟦arith: 74 + 1 = 75⟧

```json capsule
{"verifier": "glyph://sha256:AAAA...", "evaluation_id": "1111..."}
```

Second claim: ⟦count: /Теза/ in README.md = 8⟧

```json capsule
{"verifier": "settle-gate://sha256:BBBB...", "dep": {"path": "README.md", "sha256": "2222..."}}
```

Expected: the PoC's one-claim-one-capsule `search` assumption breaks here — it would
bind the first capsule to whatever it finds first and ignore the rest. A conformant
compiler requires an EXPLICIT association: either the capsule references its claim by
id, or a strict adjacency contract (a capsule binds the nearest preceding claim, and a
claim may own at most one capsule). Ambiguous or crossed association is a typed error,
not a silent nearest-match. Decision in §8.6.
