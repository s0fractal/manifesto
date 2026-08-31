// ts-sigma/conformance_test.ts — self-contained Deno conformance test.
//
// The expected hashes below are the Python reference output
// (sigma-glyph/impl/sigma_glyph.py), cross-checked live byte-for-byte on
// 2026-08-31. They are SHA-256 node hashes, hence deterministic: pinning them
// lets a TS/Deno stack run this test with NO Python dependency, while the
// values remain auditable against the reference (re-run ts-sigma/conformance.ts
// beside the Python emitter to re-verify).
//
// run: deno test ts-sigma/conformance_test.ts

import { assertEquals } from "jsr:@std/assert@1";
import { app, genesis, hex, termHash } from "./mod.ts";

const REFERENCE: Record<string, string> = {
  I: "2f33694d09810641fa5b8c47a7c0dc42e1b99eb8c9784a00aaee9a66330f4162",
  K: "bc0c2fe26e44e2aed8ce500a74963bc270fd4a49ec0c2e4837ce7a64bb0a486c",
  S: "887045bc22935aec5cba2dc11400d4e4357bc34d06681a6e92f06e7795b1f8a6",
  FALSE: "65cd957fee7ec9fb310bc9d9712cec1726c78f8026fda679ac8f237938a32098",
  app_I_K: "51d8148feda28f17304c9ed6c34d9d548c83a84c380f4dd1ba0a037ceb9d4d3e",
  app_S_I_I: "77e9c454771af4ea715c07ac91d5472dc10d0eb08605ffba869c22a03885bdf6",
  app_K_FALSE_I:
    "793285f9f0165faf0635309d852402b11e2a7969ece4c5be2fc2f10c463dbef4",
};

Deno.test("ts-sigma identity layer matches the Σ-GLYPH Python reference", async () => {
  const { I, K, S, FALSE } = await genesis();
  assertEquals(hex(await termHash(I)), REFERENCE.I);
  assertEquals(hex(await termHash(K)), REFERENCE.K);
  assertEquals(hex(await termHash(S)), REFERENCE.S);
  assertEquals(hex(await termHash(FALSE)), REFERENCE.FALSE);
  assertEquals(hex(await termHash(app(I, K))), REFERENCE.app_I_K);
  assertEquals(hex(await termHash(app(app(S, I), I))), REFERENCE.app_S_I_I);
  assertEquals(
    hex(await termHash(app(app(K, FALSE), I))),
    REFERENCE.app_K_FALSE_I,
  );
});

// A "verifiable test" in the sense the operator asked for: the assertion is a
// content-addressed identity — the test PASSES iff the term settles to the
// pinned address. Re-executable, deterministic, μ=0 (verification = recompute
// the hash, not "an assert did not throw"). This is the primitive a
// pytest-sigma / deno-test-sigma harness would build on.
Deno.test("verifiable test: FALSE settles to its canonical address", async () => {
  const { I, K } = await genesis();
  const falseAddr = hex(await termHash(app(K, I)));
  // the verdict is not "true-ish" — it is "this construction has THIS address"
  assertEquals(falseAddr, REFERENCE.FALSE);
});
