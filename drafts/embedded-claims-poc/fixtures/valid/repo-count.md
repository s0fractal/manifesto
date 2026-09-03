# Fixture: repository-observation claim, with a semantic binding

A world claim, settled by the Python repo checker (settle-gate://), NOT by
Σ-GLYPH — the verifier identity says so honestly. The capsule pins the exact
bytes read (freshness = dependency_id) and asserts a semantic binding: that this
count *measures* the number of theses. Binding is a separate axis; a correct
count does not establish it (challenge #6).

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "dep": {"path": "README.md", "sha256": "0c9e3eddf93a12acfaa15a6b9b91a161e3d7275b3a3110202bc0e0c218144ae2"},
  "binding": {
    "relation": "measures",
    "target": "README contains seven principal theses",
    "status": "ASSERTED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (author-asserted, NOT verified by
execution).
