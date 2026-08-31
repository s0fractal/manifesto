// ts-sigma/mod.ts — TS/Deno identity layer for Σ-GLYPH Book I terms.
//
// SCOPE (honest, v0): this is the CONTENT-ADDRESSING layer only —
// canonical serialization + SHA-256 node hashing + term construction —
// ported to match the Python reference (sigma-glyph/impl/sigma_glyph.py)
// BYTE-FOR-BYTE. It is NOT the ATP-priced lazy evaluator and does NOT
// reduce terms; a TS reducer is future work. Cross-checked against Python
// by ts-sigma/conformance.ts (genesis + application node hashes must match).
//
// Why this alone is useful on a TS/Deno stack: a settlement receipt is
// content-addressed. Reproducing the node hashes lets a TS verifier check
// "does this term hash to this address" and compare two normal-form
// addresses — the equality-by-address substrate — without a full evaluator.

const enc = new TextEncoder();

async function sha256(bytes: Uint8Array): Promise<Uint8Array> {
  // copy into a plain ArrayBuffer-backed view so the type is exactly
  // BufferSource (not a SharedArrayBuffer union) under strict checking.
  const buf = new ArrayBuffer(bytes.length);
  new Uint8Array(buf).set(bytes);
  const d = await crypto.subtle.digest("SHA-256", buf);
  return new Uint8Array(d);
}

/** SHA-256 of a UTF-8 string — matches Python `sha(b"...")`. */
export function shaStr(s: string): Promise<Uint8Array> {
  return sha256(enc.encode(s));
}

// op codes and field flags — identical to the Python reference.
export const OP = { LITERAL: 0x00, REF: 0x01, APPLY: 0x02, DISSONANCE: 0xff };
const F_ATOM = 0x01, F_LEFT = 0x02, F_RIGHT = 0x04;

function concat(...parts: Uint8Array[]): Uint8Array {
  const n = parts.reduce((a, p) => a + p.length, 0);
  const out = new Uint8Array(n);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}

/** Canonical node bytes: [op, flags] followed by present 32-byte fields.
 *  Mirrors Python `ser(op, flags, atom, left, right)`. */
export function ser(
  op: number, flags: number,
  fields: { atom?: Uint8Array; left?: Uint8Array; right?: Uint8Array } = {},
): Uint8Array {
  const parts: Uint8Array[] = [new Uint8Array([op, flags])];
  for (const f of [fields.atom, fields.left, fields.right]) {
    if (f !== undefined) {
      if (f.length !== 32) throw new Error("field must be 32 bytes");
      parts.push(f);
    }
  }
  return concat(...parts);
}

export function nodeHash(b: Uint8Array): Promise<Uint8Array> {
  return sha256(b);
}

// --- term AST (mirrors the Python tuple encoding) --------------------------
export type Term =
  | { t: "lit"; atom: Uint8Array }
  | { t: "app"; left: Term; right: Term };

export function lit(atom: Uint8Array): Term { return { t: "lit", atom }; }
export function app(left: Term, right: Term): Term { return { t: "app", left, right }; }

/** Canonical bytes of a term node (children folded to their hashes for APPLY),
 *  matching Python `term_bytes`. */
export async function termBytes(x: Term): Promise<Uint8Array> {
  if (x.t === "lit") return ser(OP.LITERAL, F_ATOM, { atom: x.atom });
  const l = await termHash(x.left);
  const r = await termHash(x.right);
  return ser(OP.APPLY, F_LEFT | F_RIGHT, { left: l, right: r });
}

/** Content address (SHA-256 of canonical bytes), matching Python `term_hash`. */
export async function termHash(x: Term): Promise<Uint8Array> {
  return nodeHash(await termBytes(x));
}

export function hex(b: Uint8Array): string {
  return Array.from(b).map((x) => x.toString(16).padStart(2, "0")).join("");
}

/** Genesis atoms and the FALSE combinator, for convenience and self-check. */
export async function genesis() {
  const I = lit(await shaStr("I"));
  const K = lit(await shaStr("K"));
  const S = lit(await shaStr("S"));
  const FALSE = app(K, I); // Book I: FALSE = K I
  return { I, K, S, FALSE };
}
