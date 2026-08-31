# Fixture: short effect digest is rejected (P1, rev 3)

An identity-bearing effect commitment must be a full 64-hex digest. Here the author
supplies an 8-hex prefix. It must NOT settle: the claim is malformed, earns no
result and no replay credit. Protects the regression Codex flagged (an 8-hex prefix
used to reach RESULT_MATCH).

⟦effect: echo_only addr=af876bae⟧

Expected: execution=UNVERIFIED; execution_facts include RESULT_UNSETTLED (malformed
effect: needs a full 64-hex digest).
