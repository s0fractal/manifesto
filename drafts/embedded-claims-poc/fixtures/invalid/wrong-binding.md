# Fixture: correct result, bogus semantic binding (D1/D2, challenge #6)

The arithmetic replays perfectly, verifier correctly pinned. The author then binds
it to a prose claim it does NOT support: that 74+1=75 "defines" human dignity. A
correct execution must NOT launder a false binding. The two axes stay apart:
execution green, binding merely AUTHOR-ASSERTED — never upgraded by the replay.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:45395bf77f4d731565b47a5845853928a4625f20bea439e489863c152817eaa4",
  "binding": {
    "relation": "defines",
    "target": "Human dignity is established by this identity",
    "status": "ASSERTED"
  }
}
```

Expected: execution=REPLAYED, binding=ASSERTED (not established by execution).
