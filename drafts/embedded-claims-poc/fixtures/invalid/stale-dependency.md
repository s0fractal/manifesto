# Fixture: stale dependency — never silently green

The count is correct against the current README, verifier correctly pinned, but
the capsule pins an OLD dependency digest. Freshness wins: STALE, not REPLAYED. A
green result against a changed world is a lie.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "dep": {"path": "README.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
```

Expected: execution=STALE (facts include DEPENDENCY_STALE and RESULT_MATCH).
