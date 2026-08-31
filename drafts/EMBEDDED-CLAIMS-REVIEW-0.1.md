# EMBEDDED-CLAIMS-REVIEW-0.1 — ревʼю дизайну + прийняті дельти + план збірки

**Статус:** review-запис і build-план до
[EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md](EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md).
Закриває review-петлю, якої вимагає §16.1 архітектури («спробуй спростувати,
поверни counterexamples, не стилістику»). Не нова онтологія: архітектура-0.1
лишається генералізацією, цей файл — дельти й те, з чого збирати PoC.

**Джерела ревʼю:** внутрішнє (Claude, повний контекст сесії) + зовнішнє
(Kimi, обмежений контекст — бачила лише архітектуру-0.1, припустила ціль
«децентралізована мережа довіри»). Дельти, запозичені у Kimi, атрибутовані нижче.

---

## 1. Перевірка перевірних claim'ів у документі (settlement до самого ревʼю)

Застосовуємо власну дисципліну до документа: спершу перерахунок, потім судження.
Знято на `HEAD = 40d0b0578d83c877b8e4103b351f8aa3f085de3a`.

| Claim документа | Перевірка | Результат |
|---|---|---|
| Всі посилання на локальні файли резолвяться | `test -f` на EMBEDDING-SETTLEMENT, EMBED-FORMAT-DESIGN, INVARIANT-RECIPES, FLOW-GLOSSARY | OK — усі є |
| Запінена ревізія = поточний стан | `git rev-parse HEAD` vs `40d0b05…` | збіг |
| README має 7 тез `## Теза N:` | `grep -cE '^## Теза [0-9]+:'` | 7 |
| README sha256 = `f9be29ece691…` | `shasum -a 256 README.md` | збіг байт-у-байт |

Наслідок: §7.2 «схематична» капсула насправді **повністю replayable** проти
поточного дерева. Єдині дві діри в ній (`UNPINNED-DRAFT` verifier,
`UNADOPTED` epistemic profile) — навмисні й чесні. Документ не підробив власний
приклад. Це рідкість і її варто зберегти як норму.

---

## 2. Вердикт по шести викликах §16.1

Мета була спростувати, не хвалити. Із шести — чотири вистояли, один потребує
корекції, один підтверджую *з причиною*.

1. **Розділення Claim/Binding/Plan/Result/Receipt — вистояло.** Несучий тест —
   Result vs Receipt: два різні Plan можуть дати той самий Result; один Plan
   двічі → два Receipt з одним Result. Злиття зруйнувало б твердження «ці два
   receipt *згодні*». Плюс self-contained шлях адресує Result напряму без
   Receipt. Розділення виправдане.
2. **Workflow поза графом — не знайдено.** Live-URL і model/недетерміновані —
   граф їх тримає, але Receipt дає лише *witness*, не `REPLAY_MATCHED`. Чесно
   позначено, не діра.
3. **Простіша капсула — так, і це actionable.** ~40 полів у §7.2 проти майже
   нуля для self-contained arith. Ризик: важка капсула стає «форматом», легкий
   аліґнутий кейс атрофується. → дельта D1.
4. **Осі статусу ортогональні — часткова корекція.** Осі §5 незалежні (чіпляються
   до різних обʼєктів). Але credits у §5.3 названі ортогональними, а вони
   **вкладені**: `REPLAY_MATCHED ⊃ DEPENDENCIES_RESOLVED ⊃ PARSE_CONFORMANT`.
   Решітка виведення, не вільний добуток. Це рівно наш відстежуваний overclaim
   (licensing-стрілку злито в рівність). → дельта D2.
5. **Coverage-знаменник gameable — спростування стоїть.** `E = atomic ∧
   eligible` вирішує автор; звузив `E` — усі відношення вгору. §12/§13.10
   помʼякшують, але не роблять `E` механічним. → дельта D4.
6. **Executable binding для вузьких класів — підтверджую з причиною.** Binding
   перевірний лише коли зводиться до під-claim'а (schema-conformance для
   `instantiates`, digest-рівність). Щойно відношення справді семантичне
   (`supports`/`measures`/`defines`) — не перевірний; §10.1 сам це доводить
   («7 заголовків» ≠ «7 значущих тез»). Це *підтримує* тезу, не спростовує.

---

## 3. Прийняті дельти (що міняємо в дизайні)

**D1 — self-contained inline-recompute лишається першокласним (не «sugar»).**
Центр ваги між EMBEDDING-SETTLEMENT §0 і архітектурою-0.1 зсунувся з trustless
inline-перерахунку (**CAS не потрібен**, repo-незалежно) до важкого
receipt-граф + CAS + verifier-identity + governance. Важка рама повертає саме ту
довіру (резолвний CAS, запінений verifier, adoption), яку inline-шлях уникав.
Обидва валідні для своїх класів, але inline-кейс має бути fixture #1, не §7.1.

**D2 — §5.3: credits — частковий порядок (DAG), не одна вкладена шкала.**
*(уточнено Codex.)* Моє перше формулювання («вкладені, не ортогональні») теж
неточне. `PARSE_CONFORMANT → DEPENDENCIES_RESOLVED → REPLAY_MATCHED` справді
ланцюг (спина). Але `KERNEL_DERIVED`, `COUNTERMODELED`,
`IMPLEMENTATION_CONFORMANT` одне одному **непорівнювані** — це бічні кредити, не
рівні тієї ж шкали. Тобто credits = DAG: replay-спина + непорівнювані бічні
вузли. Ортогональною лишається пара execution↔authority (§5.2↔§5.4).

**D3 — verifier identity = `glyph://<hash>` для sigma-glyph-рантайму.**
*(запозичено у Kimi.)* Якщо glyph identity вже містить toolchain digest, весь
§8.4 (source/binary/runtime/profile/deps) для sigma-glyph зводиться до одного
`glyph://<hash>`. Закриває відкриту розвилку §17 #7 для цього рантайму — без
дублювання онтології між капсулою і гліфом. Для warrant аналогічно: identity =
warrant-CID.

**D4 — coverage лишається governance, НЕ вимірювання; ATP — лише cost-телеметрія.**
*(моя ідея «ATP як вага coverage» РЕТРАГОВАНА — Codex спростував.)* Kimi вірно
показала, *чому* знаменник gameable (агент оптимізує найдешевшу вісь). Я
запропонував важити компоненти вектора ATP-вартістю replay — це **помилка**:
ATP міряє *обчислювальну* вартість, не *семантичну* важливість. Можна згенерувати
дорогі тривіальні claim'и й роздути «вагу», нічого не довівши. Тому: ATP лишається
cost-телеметрією (корисна, окрема вісь), а НЕ вагою epistemic coverage.
Cost-функція на семантичну важливість — невирішена; поки що чесна відповідь —
публікувати метод atomization, профіль eligibility, exclusions (§12) і не робити
з coverage єдиного числа. Це шоста інстанція нашого overclaim-патерну (злиття
«дорого порахувати» з «важливо»).

**D5 — 2 осі статусу на фазах 0–2, решта в non-blocking sidecar.**
*(запозичено у Kimi.)* Замість добутку 4 осей одразу:
- `execution: DECLARED | REPLAYED | MISMATCH`
- `binding: UNTIED | ASSERTED`

Authority / epistemic profile / credit taxonomy → **sidecar governance-записи,
що НЕ блокують execution pipeline.** Статусний автомат кожного claim'а тоді 3×2,
а не добуток чотирьох. Це механізм проти state-soup (Kimi #1: чотири осі без
діаграми переходів → кожен downstream-агент робить ad-hoc інтерпретацію). Повний
ledger (§5) лишається метою фаз 4+, але не гейтить ядро.

**D6 — side effect ≠ детермінований вихід: enforcement, не декларація.**
*(запозичено у Kimi, найгостріше.)* «Перевиконувані консольні команди покриють
усе» має дірку: команда може дати той самий stdout, але писати в `/tmp`, чіпати
`mtime`, лізти в мережу через `LD_PRELOAD`. §9.2 декларує *намір* (network
denied, file-write denied крім staging) — але це декларація, не enforcement. Для
warrant replay «той самий вивід» ≠ «той самий ефект на замкненому state».
Наслідок: чим ми *міряємо* ефект? Відповідь не «stdout збігся», а **digest
замкненого state after execution**. Для sigma-glyph проблеми нема (замкнений
ATP-світ). Для console-effect рантайму — центральне питання, і його треба зловити
негативним fixture з першого дня (див. build-план §5).

---

## 4. Що відкидаємо (ціль не наша)

Kimi бачила обмежений контекст і припустила «екосистема автономних агентів без
центрального gatekeeping». Ця ціль **явно знята** оператором (проєкт існує, бо
значущий для оператора; зовнішнє прийняття — не критерій успіху). Тому:

- **Kimi #6 (консенсус розбіжних верифікаторів), #7 (fail-closed = централізований
  gatekeeper), #10 (темпоральна модель / vector clocks)** та підсумок — усі
  припускають BFT-мережу довіри. Для одного оператора з детермінованими рантаймами
  (sigma-glyph, warrant) розбіжність верифікаторів = баг у рантаймі, не візантійська
  проблема. Не будуємо BFT під мету, якої нема.
- **Kimi #2 (Markdown — тупик, канон має бути CRDT-граф)** — документ це вже
  враховує (§4.2/§6: канон = граф records, Markdown = проєкція). CRDT —
  over-engineering для сольного проєкту. Пропускаємо.

---

## 5. Чесна межа ревʼю

Це **два прочитання одного документа** (Claude + Kimi), що збіглись на
«governance перебудована відносно execution-ядра». **Збіг двох прочитань ≠
зовнішнє підтвердження** — валідаційного кредиту не дає (наша дисципліна:
рекуренція в межах одного корпусу = нуль). Як сигнал *куди різати* — надійний,
бо збігається ще й із наміром оператора. Як доказ *правильності* — ні.

---

## 6. З чого збирати PoC (build-план, не нова онтологія)

Джерело збірки = три тонкі шари, кожен зі своєю роллю:

1. **ARCHITECTURE-0.1** — генералізація (незмінна, референс сутностей).
2. **цей файл §3** — прийняті дельти поверх неї.
3. **цей §6** — що саме кодимо у фазі 1.

**Working core first (проти bootstrap-paralysis, Kimi #8).** Ключове
спостереження: перший fixture НЕ потребує запінених §17 #1/#2/#4
(canonicalization/hash/info-string) — вони кусають на фазі 2 (загальний парсер).
Self-contained arith на sigma-glyph використовує **власний term-hash гліфа** як
адресу, не JSON-record-canonicalization. Тому ядро будується вже, а три розвилки
відкладаються до парсера.

### Фаза 1 PoC — scope

```
drafts/embedded-claims-poc/
  README.md              — що це, межі, що НЕ доведено
  fixtures/valid/
    arith-self.md        — ⟦arith⟧ self-contained, адреса = glyph term-hash
    repo-count.md        — ⟦count⟧ repo-observation (README 7 тез, вже replayable)
  fixtures/invalid/
    stdout-same-effect-different.md   — D6: той самий stdout, запис у /tmp / touch mtime
    expected-mismatch.md              — actual ≠ expected → MISMATCH + receipt
    stale-dependency.md               — README змінено → інший digest → STALE
    unpinned-verifier.md              — немає glyph://hash → не дає REPLAY_MATCHED
    wrong-binding.md                  — правильний replay + навмисно хибний binding
  verify.py              — тонка обгортка над settle_gate/glyphlib (без нового рантайму)
```

Статус кожного claim'а — **2 осі (D5)**: `execution` + `binding`. Authority/
epistemic/credit — не в цьому колі.

Verifier identity — **`glyph://<hash>` / warrant-CID (D3)**, без §8.4-онтології.

### Definition of done фази 1

1. `arith-self.md` перераховується будь-де без CAS (D1);
2. `repo-count.md` дає STALE при зміні README, не тихо-зелене;
3. кожен invalid-fixture падає з typed reason;
4. **`stdout-same-effect-different.md` ловиться** — вердикт спирається на
   state-digest, не на stdout (D6);
5. `wrong-binding.md`: правильний execution НЕ фарбує binding у зелене — рендер
   показує два рядки (`execution: REPLAYED` / `binding: UNTIED`);
6. документуємо, що лишилось unproven (semantic adequacy, §17 #1/#2/#4).

### Що НЕ робимо у фазі 1

- не пінимо canonicalization/hash/info-string (фаза 2);
- не будуємо browser extension / CAS / MCP (фаза 6);
- не чіпаємо MYC/Trinity;
- не мігруємо README;
- не ставимо жодного «verified manifesto» бейджа.

---

## 7. Що лишається рішенням оператора

- **§17 #1 canonicalization** (JCS/RFC 8785 vs власний closed JSON) — кусає на
  фазі 2, не раніше; але вибереш не те — всі `record_id` доведеться викинути.
- **§17 #2 hash** (SHA-256 для Warrant-сумісності vs domain-separated BLAKE3).
- **§17 #4 info-string** (`json claim` vs `claim+json`).

Рекомендація: не пінити їх зараз. Зібрати фазу 1 на native-hash рантаймів,
побачити чистий цикл, і пінити #1/#2/#4 разом із фазою-2 парсером — коли вони
реально знадобляться.
