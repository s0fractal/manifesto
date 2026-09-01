# Fixture: unknown capsule field fails closed (phase 2, §13.8)

The arithmetic is true and the verifier is correctly pinned, but the capsule carries
an unknown field. A closed schema (`additionalProperties: false`) must reject it —
never ignore it "for forward compatibility". An old consumer silently dropping a
field that changes meaning is exactly the unknown-field downgrade threat.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "surprise": "should fail closed"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
naming the unknown field.
