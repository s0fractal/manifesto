# Adversarial 02 — multiple claims in one paragraph (T2)

У корені три файли й шість підпапок, разом ⟦arith: 3 + 6 = 9⟧ елементів; діалогів
Monday — ⟦arith: 74 + 1 = 75⟧, що більше за чернетки, тож ⟦cmp: 75 > 8⟧.

Expected: a conformant parser returns THREE live claims in document order
(arith 3+6=9, arith 74+1=75, cmp 75>8), each with its own result — never just the
first. Order is load-bearing (binding environment threads left-to-right).
