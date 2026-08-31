# Fixture: stale dependency — never silently green

The count is correct against the current README, verifier correctly pinned, but
the capsule pins an OLD dependency digest. Freshness wins: STALE, not REPLAYED. A
green result against a changed world is a lie.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:b4f33ca1ba18b005de4eeba34a550cd65e4481e54a3ce5885831cd6d239636cd",
  "dep": {"path": "README.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
```

Expected: execution=STALE (facts include DEPENDENCY_STALE and RESULT_MATCH).
