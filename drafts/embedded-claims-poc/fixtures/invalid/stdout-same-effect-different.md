# Fixture: same stdout, different effect (D6 — Kimi)

`echo_and_touch` prints `hello\n` and ALSO writes a file. Its stdout is
byte-identical to `echo_only`. The author addressed by stdout (`addr` is the
stdout digest `5891b5b5…`) and treated the command as pure. Settling on stdout
would call this a MATCH; we settle on the observed post-state digest, so the write
shifts the address and the claim is refuted. "Same output" ≠ "same effect".

⟦effect: echo_and_touch addr=5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03⟧

```json capsule
{
  "verifier": "effect-sandbox://sha256:d36ea017c1564ec924c5d05316549e2ffab5f91911ebbcffb6075f76c10c0915"
}
```

Expected: execution=MISMATCH, with a note that stdout-only WOULD have matched.
