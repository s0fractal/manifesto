# Fixture: dependency pin names the wrong path (P0, rev 3)

The claim reads README.md, and the pinned digest even matches README's bytes — but
the pinned `path` says NOT-README.md. A pin whose path does not match what was
actually read does not describe the dependency; it must not confer replay credit,
however convincing the digest looks.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "dep": {"path": "NOT-README.md", "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"}
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_PATH_MISMATCH).
