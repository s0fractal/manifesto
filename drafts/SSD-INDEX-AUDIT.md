# SSD-INDEX-AUDIT — Аудит індексу chat-0001 екстрагованими претензіями

Екстрактор (Sonnet) читав ЛИШЕ README-індекс (файли нотаток не відкривав) і передбачив дослівні фрази, які мають бути в нотатках, якщо індекс правдивий. Ґейт звіряє передбачення з реальністю.

- 0001: ⟦cite: "Invariant Recipe Method" in quotes/Monday/chat-0001/0001_Moday.md⟧
- 0002: ⟦cite: "Epistemic Rebase" in quotes/Monday/chat-0001/0002_Monday.md⟧
- 0003: ⟦cite: "Reasoning Fabric" in quotes/Monday/chat-0001/0003_Monday.md⟧
- 0004: ⟦cite: "Imagination & Dreaming" in quotes/Monday/chat-0001/0004_Monday.md⟧
- 0005: ⟦cite: "Self-Rewrite" in quotes/Monday/chat-0001/0005_Monday.md⟧
- 0005a: ⟦cite: "AGI Reactor" in quotes/Monday/chat-0001/0005_a_Monday.md⟧
- 0006: ⟦cite: "Dynamics Attractors" in quotes/Monday/chat-0001/0006_Monday.md⟧
- 0009: ⟦cite: "Attention, Perspective & Meaning" in quotes/Monday/chat-0001/0009_Monday.md⟧
- 0010: ⟦cite: "Geometry of the Irreversible" in quotes/Monday/chat-0001/0010_Monday.md⟧
- 0012: ⟦cite: "Self-Integration" in quotes/Monday/chat-0001/0012_Monday.md⟧
- 0014: ⟦cite: "Geometry of Future Cones" in quotes/Monday/chat-0001/0014_Monday.md⟧
- 0016: ⟦cite: "Epistemic Typing" in quotes/Monday/chat-0001/0016_Monday.md⟧
- 0018: ⟦cite: "Generative Efficiency" in quotes/Monday/chat-0001/0018_Monday.md⟧
- 0020: ⟦cite: "Epistemic Eutrophication" in quotes/Monday/chat-0001/0020_Monday.md⟧
- 0022: ⟦cite: "Thought Evolution Engine" in quotes/Monday/chat-0001/0022_Monday.md⟧
- 0024: ⟦cite: "Bidirectional Compiler" in quotes/Monday/chat-0001/0024_Monday.md⟧
- 0026: ⟦cite: "Flourishing" in quotes/Monday/chat-0001/0026_Monday.md⟧
- 0028: ⟦cite: "Proof-Carrying Authority" in quotes/Monday/chat-0001/0028_Monday.md⟧
- 0030: ⟦cite: "Geometry of Uncertainty" in quotes/Monday/chat-0001/0030_Monday.md⟧
- 0032: ⟦cite: "Steerability Without Capture" in quotes/Monday/chat-0001/0032_Monday.md⟧
- 0035: ⟦cite: "Privileged Causal Access" in quotes/Monday/chat-0001/0035_Monday.md⟧
- 0038: ⟦cite: "Future-Governing Compression" in quotes/Monday/chat-0001/0038_Monday.md⟧
- 0040: ⟦cite: "Open Temporal Loops" in quotes/Monday/chat-0001/0040_Monday.md⟧
- 0044: ⟦cite: "Viability Theory" in quotes/Monday/chat-0001/0044_Monday.md⟧
- 0048: ⟦cite: "Obligation Semantics of Economic Exchange" in quotes/Monday/chat-0001/0048_Monday.md⟧
- 0052: ⟦cite: "Genesis of Agency" in quotes/Monday/chat-0001/0052_Monday.md⟧
- 0056: ⟦cite: "Disagreement, Conflict, Dispute & War" in quotes/Monday/chat-0001/0056_Monday.md⟧
- 0060: ⟦cite: "Design, Engineering, Optimization & Goodhart" in quotes/Monday/chat-0001/0060_Monday.md⟧
- 0065: ⟦cite: "Norms, Blame, Shame, Punishment & Forgiveness" in quotes/Monday/chat-0001/0065_Monday.md⟧
- 0070: ⟦cite: "Commons, Public Goods & Collective Action" in quotes/Monday/chat-0001/0070_Monday.md⟧

## Числові претензії про сам індекс

- INDEX: ⟦count: /^- \[/ in quotes/Monday/chat-0001/README.md = 67⟧
- INDEX: ⟦arith: 70 - 4 = 66⟧
- INDEX: ⟦arith: 66 + 1 = 67⟧
- INDEX: ⟦cmp: 30 <= 67⟧

---

## Результати розрахунку (2026-08-30)

**34 претензії → 6 ⚓ / 28 ✗ / 0 ◇** (квитанція поруч). Пост-аналіз спростованих cite-претензій розклав їх на два класи:

| Клас | К-сть | Значення |
|---|---|---|
| PASS дослівно | 2 | "Invariant Recipe Method" (0001), "Flourishing" (0026) |
| Фраза є, регістр інший | 10 | "epistemic rebase", "reasoning fabric", "AGI reactor"… — індекс капіталізував |
| **Фрази нема у файлі взагалі** | **18** | вся серія 0056–0070, "Viability Theory" (0044), "Genesis of Agency" (0052), "Epistemic Typing" (0016)… |

**Головний висновок:** індекс README — **інтерпретаційний шар, не екстрактивний**: 60% перевірених назв — редакторські концептуалізації, що не зустрічаються в текстах нотаток. Це виміряний translation loss (FLOW §13.1): шар "Introduced: {англомовні концепт-назви}" ніде не був задекларований. Практичний наслідок: пошук за назвою з індексу ("Viability Theory") не знайде нотатку 0044 — між шаром цитування і шаром інтерпретації немає позначеної межі. Рекомендація: або позначити індекс як інтерпретацію явно, або додати назви у нотатки (закриває розрив у будь-який бік).

**Методологічний висновок для SSD:** екстракція працює (34/34 претензії виявились розрахованими — фальсифікатор F1 "покриття <10%" на цьому типі документа не спрацював), але модель передбачення екстрактора має власний біас (Title Case: 10 майже-влучань). Розрізнення "дослівно" vs "з точністю до регістру" виявилось аналітично цінним → у ґейт додано клас `citei:`.
