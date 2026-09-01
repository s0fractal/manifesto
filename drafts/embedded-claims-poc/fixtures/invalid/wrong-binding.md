# Fixture: correct result, bogus semantic binding (D1/D2, challenge #6)

The arithmetic replays perfectly, verifier correctly pinned. The author then binds
it to a prose claim it does NOT support: that 74+1=75 "defines" human dignity. A
correct execution must NOT launder a false binding. The two axes stay apart:
execution green, binding merely AUTHOR-ASSERTED — never upgraded by the replay.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:59786891d9840de5712c50f63edea774aeff1e81e4105b67cfc81b36c3df084e",
  "binding": {
    "relation": "defines",
    "target": "Human dignity is established by this identity",
    "status": "ASSERTED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (not established by execution).
