# Adversarial 09 — the claim lives inside the capsule (T8 dissolved)

The canonical form: the capsule CONTAINS the claim (local_id + class + payload) plus its
verifier and dependency. There is no inline glyph to associate with, so claim↔capsule
association is structural containment — the whole `claim_ref` / `{#local_id}` machinery
is gone.

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{
  "schema_version": "manifesto.capsule.v2",
  "claim": {
    "local_id": "README-THESIS-COUNT",
    "class": "count",
    "payload": "/^## Теза [0-9]+:/ in README.md = 7"
  },
  "verifier": "settle-gate://sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "dep": {"path": "README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

<!-- manifesto-claims:end -->

Expected — PARSE: status VALID, ONE capsule whose raw body slice contains the full
claim object. The compiler (3c) schema-validates this v2 capsule and settles the
contained claim; association is trivial because the claim is inside. `local_id` is a
human name; the content-addressed `claim_id` is derived by the compiler.
