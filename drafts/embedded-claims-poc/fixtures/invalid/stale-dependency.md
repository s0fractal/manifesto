# Fixture: stale dependency — never silently green

The count is correct against the current README, verifier correctly pinned, but
the capsule pins an OLD dependency digest. Freshness wins: STALE, not REPLAYED. A
green result against a changed world is a lie.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "dep": {"path": "README.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
```

Expected: execution=STALE (facts include DEPENDENCY_STALE and RESULT_MATCH).
