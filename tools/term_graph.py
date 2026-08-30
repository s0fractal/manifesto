#!/usr/bin/env python3
"""
term_graph.py — deterministic extraction of the distinction graph from the
Monday corpus.

The notes' ≠-chains ($A \neq B \neq C \neq ...$) are machine decompositions of
mixed human terms: each chain asserts pairwise distinctness of concepts that
one natural-language word habitually fuses. This tool makes that layer a
first-class, checkable object:

  node   = term (normalized LaTeX identifier)
  edge   = an asserted distinction between two terms (all pairs of a chain)
  weight = number of independent chain-assertions of that distinction

Reports (all deterministic, sorted):
  - mixing degree: how many distinct concepts the corpus had to peel off a
    term — a proxy for how overloaded the human word is;
  - cross-file terms: concepts re-distinguished in many notes (glossary
    candidates: highest amortization value per RVB §5.4);
  - repeated edges: the same distinction re-derived in several files
    (redundancy that a glossary entry would collapse);
  - components: islands of the decomposition.

No LLM, no network, no clocks: grep-grade parsing only. Same input bytes →
same output bytes.
"""
import collections
import hashlib
import json
import os
import re
import sys

CORPUS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "quotes", "Monday", "chat-0001")

MATH_SPAN = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
NEQ_SPLIT = re.compile(r"\\neq|\\ne\b|≠")
CLEAN = [
    (re.compile(r"\\text\s*\{([^}]*)\}"), r"\1"),
    (re.compile(r"\\math[a-z]+\s*\{([^}]*)\}"), r"\1"),
    (re.compile(r"[\\{}$]"), ""),
    (re.compile(r"\s+"), ""),
]
TERM_OK = re.compile(r"^[A-Za-zА-Яа-яЇїІіЄєҐґ][A-Za-zА-Яа-яЇїІіЄєҐґ0-9_'\-]{1,40}$")

def clean_term(raw):
    t = raw
    for pat, rep in CLEAN:
        t = pat.sub(rep, t)
    t = t.strip("_-'")
    return t if TERM_OK.match(t) else None

def extract_chains(text):
    for m in MATH_SPAN.finditer(text):
        span = m.group(1) or m.group(2)
        if not NEQ_SPLIT.search(span):
            continue
        parts = [clean_term(p) for p in NEQ_SPLIT.split(span)]
        chain = [p for p in parts if p]
        if len(chain) >= 2:
            yield chain

def main():
    edges = collections.Counter()          # frozenset({a,b}) -> assertion count
    edge_files = collections.defaultdict(set)
    term_files = collections.defaultdict(set)
    chains_per_file = collections.Counter()

    for fname in sorted(os.listdir(CORPUS)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(CORPUS, fname), encoding="utf-8") as f:
            text = f.read()
        for chain in extract_chains(text):
            chains_per_file[fname] += 1
            uniq = sorted(set(chain))
            for t in uniq:
                term_files[t].add(fname)
            for i in range(len(uniq)):
                for j in range(i + 1, len(uniq)):
                    e = frozenset((uniq[i], uniq[j]))
                    edges[e] += 1
                    edge_files[e].add(fname)

    # adjacency + degree
    adj = collections.defaultdict(set)
    for e in edges:
        a, b = sorted(e)
        adj[a].add(b)
        adj[b].add(a)
    degree = {t: len(ns) for t, ns in adj.items()}

    # connected components
    seen, components = set(), []
    for t in sorted(adj):
        if t in seen:
            continue
        stack, comp = [t], set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(adj[u] - comp)
        seen |= comp
        components.append(sorted(comp))
    components.sort(key=lambda c: (-len(c), c[0]))

    top_mixed = sorted(degree.items(), key=lambda kv: (-kv[1], kv[0]))[:25]
    cross_file = sorted(((t, sorted(fs)) for t, fs in term_files.items()
                         if len(fs) >= 3), key=lambda kv: (-len(kv[1]), kv[0]))[:25]
    repeated_edges = sorted(((sorted(e), n, sorted(edge_files[e]))
                             for e, n in edges.items()
                             if len(edge_files[e]) >= 2),
                            key=lambda x: (-len(x[2]), x[0]))[:25]

    report = {
        "stats": {
            "files_with_chains": len(chains_per_file),
            "chains_total": sum(chains_per_file.values()),
            "terms": len(adj),
            "distinctions": len(edges),
            "components": len(components),
            "largest_component": len(components[0]) if components else 0,
        },
        "top_mixed_terms": [{"term": t, "peeled_off": d} for t, d in top_mixed],
        "cross_file_terms": [{"term": t, "files": fs} for t, fs in cross_file],
        "repeated_distinctions": [{"pair": p, "assertions": n, "files": fs}
                                  for p, n, fs in repeated_edges],
        "component_sizes_top10": [len(c) for c in components[:10]],
    }
    # ---- collision detector: does the corpus obey its own distinctions? ----
    # A collision candidate: a pair asserted A != B somewhere, while some math
    # span elsewhere asserts A = B or A <=> B (identity/equivalence, not
    # inequality). Deterministic, string-level: candidates for human review,
    # not verdicts.
    ident_split = re.compile(r"=|\\iff|⟺|\\equiv|≡")
    neq_terms = {t for e in edges for t in e}
    collisions = []
    for fname in sorted(os.listdir(CORPUS)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(CORPUS, fname), encoding="utf-8") as f:
            text = f.read()
        for m in MATH_SPAN.finditer(text):
            span = m.group(1) or m.group(2)
            if NEQ_SPLIT.search(span):
                continue
            body = re.sub(r"\\boxed\s*\{(.*)\}", r"\1", span.strip(), flags=re.S)
            sides = ident_split.split(body)
            if len(sides) != 2:
                continue
            # a genuine identification: each side is exactly one ≠-term
            a, b = clean_term(sides[0]), clean_term(sides[1])
            if not a or not b or a == b:
                continue
            pair = frozenset((a, b))
            if a in neq_terms and b in neq_terms and pair in edges:
                collisions.append({
                    "pair": sorted(pair),
                    "identified_in": fname,
                    "span": " ".join(span.split())[:120],
                    "distinguished_in": sorted(edge_files[pair]),
                })
    # dedupe identical collision records
    seen_c, dedup = set(), []
    for c in collisions:
        key = (tuple(c["pair"]), c["identified_in"], c["span"])
        if key not in seen_c:
            seen_c.add(key)
            dedup.append(c)
    report["collision_candidates"] = dedup[:40]
    report["stats"]["collision_candidates"] = len(dedup)

    out = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)
    print(out)
    print("\nREPORT_SHA256:", hashlib.sha256(out.encode()).hexdigest())

if __name__ == "__main__":
    sys.exit(main())
