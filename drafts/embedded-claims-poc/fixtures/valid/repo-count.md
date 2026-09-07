# Fixture: repository-observation claim, with a semantic binding

A world claim, settled by the Python repo checker (settle-gate://), NOT by
Σ-GLYPH — the verifier identity says so honestly. The capsule pins the exact
bytes read (freshness = dependency_id) and asserts a semantic binding: that this
count *measures* the number of theses. Binding is a separate axis; a correct
count does not establish it (challenge #6).

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  "dep": {"path": "README.md", "sha256": "3a6edc622b3dbca9e71885eed8b51a52d4aedd76f1db9f740ab28c4a141b5e52"},
  "binding": {
    "relation": "measures",
    "target": "README contains seven principal theses",
    "status": "ASSERTED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (author-asserted, NOT verified by
execution).
