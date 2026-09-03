# Fixture: unknown capsule field fails closed (phase 2, §13.8)

The arithmetic is true and the verifier is correctly pinned, but the capsule carries
an unknown field. A closed schema (`additionalProperties: false`) must reject it —
never ignore it "for forward compatibility". An old consumer silently dropping a
field that changes meaning is exactly the unknown-field downgrade threat.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:dfd20c29d6366da6e78ae6ef5639d2ff7cf343e6eebaca7ac8a6af3ab955feb0",
  "surprise": "should fail closed"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
naming the unknown field.
