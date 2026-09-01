# Fixture: unknown capsule field fails closed (phase 2, §13.8)

The arithmetic is true and the verifier is correctly pinned, but the capsule carries
an unknown field. A closed schema (`additionalProperties: false`) must reject it —
never ignore it "for forward compatibility". An old consumer silently dropping a
field that changes meaning is exactly the unknown-field downgrade threat.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:7a678c25452c23f91f6193b68e78cca09faea917b0b2b433cd36ea0878a95c90",
  "surprise": "should fail closed"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
naming the unknown field.
