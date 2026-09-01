# Fixture: stale dependency — never silently green

The count is correct against the current README, verifier correctly pinned, but
the capsule pins an OLD dependency digest. Freshness wins: STALE, not REPLAYED. A
green result against a changed world is a lie.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:017d215b3af2c8f1f4475c7030a5a0559fa6d6cdafe3a77e1c0b1d73452b4acd",
  "dep": {"path": "README.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
```

Expected: execution=STALE (facts include DEPENDENCY_STALE and RESULT_MATCH).
