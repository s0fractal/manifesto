# Review: Codex — terminology-through-Lean / semantic gap (2026-08-31)

Web-delivered, filed verbatim (as received). Target: commit 2dbda4c
(`drafts/glossary-lean-poc/FlowGlossary.lean` + `GLOSSARY-ARCHITECTURE.md §8`).
Response: `2026-08-response-to-codex-lean.md`.

---

**Головний висновок:** семантичний розрив — не випадковий дефект, а спільний предмет усього сімейства. Кожен репозиторій ловить той самий незаконний перехід на іншій межі.

PoC реальний: remote main справді вказує на 2dbda4c, FlowGlossary.lean компілюється Lean 4.31 навіть із warningAsError. Контрмодель справді показує, що Reachable → Viable не випливає із заданої теорії.

Але фраза «Lean розв'язує C3 і дає out-of-lineage semantic validation» — нове завищення. Точніше:

> Lean є out-of-lineage перевіряльником формального виведення, але не out-of-lineage валідатором значення формалізації.

## Спільна форма розриву

```
світ / намір → (adequacy) → Lean-визначення → (proof) → теорема →
(conformance) → Python/TS/Rust → (execution) → receipt →
(relevance+authority) → рішення/дія/норма
```

Lean закриває одну стрілку — definitions→theorem. Решту — ні.

| Репозиторій | Розрив | Що механіка закриває | Що лишається |
|---|---|---|---|
| Σ-GLYPH | адреса ↔ семантична рівність | тотожність канонічного результату | admission, reflection, preservation, intended equivalence |
| Warrant | replay ↔ обґрунтоване рішення | integrity, provenance, replay | reason-binding, relevance, truth, justice |
| Trinity/HSP | translation ↔ збереження значення | типізований mapping, loss report, admission | adequacy доменів, повнота loss, легітимність authority |
| FLOW | словник ↔ реальна зміна/агентність | сорти, illegal casts, countermodels | grounding, completeness, normative meaning |
| Lean glossary | слово ↔ формальне означення | когерентність наслідків теорії | правильність вибору означення |

> **Робочий принцип (не теорема):** Формалізація не усуває семантичний розрив; вона стискає його й переміщує до першої неформалізованої межі.

## Що довів PoC (розділений кредит)

Поля `flour_viable`, `viable_reach` позначені як **stipulation**. Theorem означає "якщо ми прийняли ці включеності, Lean перевірив композицію" — machine-checked derivation, не незалежне відкриття про flourishing. Контрмодель доводить non-entailment: нелегальний каст неможливо отримати без додаткового зобов'язання.

- KERNEL-DERIVED: так; COUNTERMODELED: так;
- SEMANTICALLY-ADEQUATE: ще ні; IMPLEMENTATION-CONFORMANT: ще ні; NORMATIVELY-ADOPTED: ще ні.

## П'ять незгод із поточним текстом

1. **C3 не закрито.** Lean усуває потребу довіряти більшості щодо коректності proof term. Але та сама lineage може: вибрати неправильний relatum; формалізувати зручне замість задуманого; пропустити передумову; прийняти модель як нормативну; оголосити неповну теорію достатньою. Статус: C3 proof-checking slice mitigated; semantic/adoption layer open.
2. **`Defined` зливає ≥5 речей.** Замінити на ортогональний ledger: FORMALIZED / KERNEL_DERIVED / COUNTERMODELED / IMPLEMENTATION_CONFORMANT / DOMAIN_ADEQUATE / EMPIRICALLY_GROUNDED / NORMATIVELY_ADOPTED. Промоція prose→Lean — подія формалізації, не автоматично валідації.
3. **Value/Dignity/Love МОЖНА в Lean.** Kernel дозволить аксіоматизувати будь-що; проблема не "не Lean-able", а що kernel не встановить адекватність кодування. Чесний статус — STIPULATED_FORMAL, не DEFINED_TRUTH. Межа: не Lean-able/non-Lean-able, а "наслідки формально перевірені / міст поняття→формалізація обґрунтований чи ні".
4. **Lean не ловить семантичну циркулярність сам.** Enforces what we remembered to state; не повідомляє, чого забули. Не змусить Reach_A походити з попередньої transition system, якщо ми самі не внесемо це в тип.
5. **Падаючого споживача ще нема.** Нема lakefile, pinned toolchain, CI/gate у manifesto. grep sorry + lake build недостатньо: axiom, admit, native_decide, axiom cones, statement-swap. Зрілий патерн — sigma-glyph GUARD_CLAIMS.txt (theorem pins, exact axiom cones, guard, що не авторизує сам себе).

## SSoT

Так — Lean може бути canonical source of formal stipulation+derivation у межах owner-domain. Ні — не універсальний semantic SSoT для всієї коси. Розташування файлу не повинно передати Sigma нормативне володіння термінами FLOW/Warrant. Рекомендація: НЕ переносити PoC у Sigma як "semantic kernel" зараз; спершу виправити чотири claim boundaries, потім мінімальне ядро — як proof-carrying federation of stipulations, не єдине джерело значення.

> Семантика не живе в одному файлі, hash, proof чи receipt. Вона живе у явно заявленому відношенні між артефактом, інтерпретатором, доменом, контекстом, часом і владою прийняти інтерпретацію. Системи не закривають прірву раз і назавжди — вони не дають переходити її непомітно.
