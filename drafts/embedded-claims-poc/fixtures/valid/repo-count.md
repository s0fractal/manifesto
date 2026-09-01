# Fixture: repository-observation claim, with a semantic binding

A world claim, settled by the Python repo checker (settle-gate://), NOT by
Σ-GLYPH — the verifier identity says so honestly. The capsule pins the exact
bytes read (freshness = dependency_id) and asserts a semantic binding: that this
count *measures* the number of theses. Binding is a separate axis; a correct
count does not establish it (challenge #6).

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "dep": {"path": "README.md", "sha256": "259f54a6367bec54644b2574baacff712a8db5a06a291d798416d8d1b0a62d52"},
  "binding": {
    "relation": "measures",
    "target": "README contains seven principal theses",
    "status": "ASSERTED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (author-asserted, NOT verified by
execution).
