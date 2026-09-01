# Adversarial 11 — unknown region profile (region layer)

The region declares a profile the parser does not implement.

<!-- manifesto-claims:begin profile=some.other.profile.v9 -->

⟦arith: 3 + 6 = 9⟧

<!-- manifesto-claims:end -->

Expected: a typed `UNKNOWN_PROFILE` failure — fail closed. The parser must not fall
back to a default profile or settle the claim under an assumed one; an unrecognized
profile is refused by name, never best-effort.
