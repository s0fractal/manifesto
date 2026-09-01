# Fixture: a real effect the observer CANNOT see (P1-5, honest limit)

This fixture is neither "valid" nor a caught "invalid" — it is a LIMIT. It settles
to REPLAYED even though the command had a side effect, because the effect was
write-then-delete: nothing survives in the observed tree, so the post-state digest
equals `echo_only`'s. The same blindness applies to writes outside the temp dir,
network calls, and metadata changes.

The lesson is exactly what the credit name says: `effect` establishes "observed
post-state differs", NOT "all side effects were enforced or observed". A real
effect runtime needs OS-level confinement, not a TemporaryDirectory.

⟦effect: echo_then_delete addr=af876bae98fc8a8eb8c5d13e9adcf8912f952995c9c92e2299c6736cbd2751d5⟧

```json capsule
{
  "verifier": "effect-sandbox://sha256:6e93ada00ce7473c09f0cee2039d771a6c2183c114615d447b5980d7b75ca1b9"
}
```

Expected: execution=REPLAYED — and this is a DEMONSTRATED BLIND SPOT, not a
success. The write-then-delete side effect is invisible to post-state observation.
