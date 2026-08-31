// ts-sigma/conformance.ts — emit the node hashes this TS core computes, so a
// harness can compare them BYTE-FOR-BYTE against the Python reference. If any
// line differs from Python, the TS port is non-conformant on identity and the
// discipline says: it is a sibling with zero validation credit until it agrees.
//
// run: deno run --allow-none ts-sigma/conformance.ts   (prints name=hex lines)

import { app, genesis, hex, termHash } from "./mod.ts";

const { I, K, S, FALSE } = await genesis();

const cases: [string, Awaited<ReturnType<typeof genesis>>[keyof Awaited<ReturnType<typeof genesis>>]][] = [
  ["I", I], ["K", K], ["S", S], ["FALSE", FALSE],
];

const out: string[] = [];
for (const [name, term] of cases) {
  out.push(`${name}=${hex(await termHash(term))}`);
}
// a few application nodes (identity-layer only; NOT reduced)
out.push(`app_I_K=${hex(await termHash(app(I, K)))}`);
out.push(`app_S_I_I=${hex(await termHash(app(app(S, I), I)))}`);
out.push(`app_K_FALSE_I=${hex(await termHash(app(app(K, FALSE), I)))}`);

console.log(out.join("\n"));
