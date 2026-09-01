# Fixture: dependency pin names the wrong path (P0, rev 3)

The claim reads README.md, and the pinned digest even matches README's bytes — but
the pinned `path` says NOT-README.md. A pin whose path does not match what was
actually read does not describe the dependency; it must not confer replay credit,
however convincing the digest looks.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:7a678c25452c23f91f6193b68e78cca09faea917b0b2b433cd36ea0878a95c90",
  "dep": {"path": "NOT-README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_PATH_MISMATCH).
