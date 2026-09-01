# Adversarial 09 — claim ↔ capsule association (T8)

Two claims and two capsules in one live region. Association is by explicit
`local_id`/`claim_ref`, never adjacency. The capsule bodies are SHAPE-VALID under the
closed schema (64-hex placeholders), so the compiler reaches the association check
instead of rejecting on schema first (Codex P1: separate parse from compile).

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

First claim ⟦arith: 74 + 1 = 75 #A⟧ and second claim ⟦count: /Теза/ in README.md = 8 #B⟧.

```json capsule
{"claim_ref": "B", "verifier": "settle-gate://sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "dep": {"path": "README.md", "sha256": "2222222222222222222222222222222222222222222222222222222222222222"}}
```

```json capsule
{"claim_ref": "A", "verifier": "glyph://sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

<!-- manifesto-claims:end -->

Expected — PARSE: two claims (local_id A, B) and two capsules found in the region.
Expected — COMPILE: capsule 1 binds claim B, capsule 2 binds claim A, by `claim_ref` —
NOT by document order/adjacency (the capsules are deliberately out of order). A
`claim_ref` matching no claim, or two capsules referencing one local_id, is a typed
error. `#A`/`#B` here sketch a local_id syntax; the exact spelling is an open decision,
but the mechanism (explicit reference) is decided.
