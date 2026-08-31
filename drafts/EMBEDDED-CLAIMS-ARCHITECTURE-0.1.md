# EMBEDDED-CLAIMS-0.1 — Вбудовані claim'и як межа між прозою і розрахунком

**Статус:** design draft / proposal. Не специфікація, не прийнятий формат і не
дозвіл на масову міграцію текстів.

**Призначення:** дати наступному розробнику або моделі достатньо контексту,
щоб спроєктувати мінімальний, fail-closed механізм явних claim-блоків у
Markdown, не перевинаходячи рецепти MYC/Trinity і не перетворюючи весь
manifesto на псевдоформальну мову.

**Головна пропозиція:** перевірні твердження можуть добровільно виноситися в
явні fenced code blocks. Блок є **авторською заявкою на перевірку**, а не
вердиктом. Канонічний машинний шар — граф окремих записів
`Claim → Binding → VerificationPlan → Dependencies → Receipt`; Markdown-блок —
лише переносна людсько-машинна проєкція цього графа.

**Неочевидна межа:** механічно перевірити результат обчислення ще не означає
перевірити, що саме це обчислення підтримує сусідню прозу. Формат має зробити
цей розрив видимим, але не може оголосити його закритим самою наявністю JSON.

---

## 0. Чому цей документ існує

Поточні дослідження в manifesto вже мають кілька частин майбутнього механізму:

- inline-розмітку `⟦class: payload⟧` і `settle_gate.py`;
- dependency-bound receipts;
- поділ `PASS / REFUTED / UNSETTLED`;
- content-addressed результати Σ-GLYPH;
- Warrant-записи з replay;
- Lean-ядро для обмеженої формальної частини глосарію;
- статуси `Defined / Stipulated / Speculative`;
- Invariant Recipe Method для пошуку семантичного розриву.

Паралельно виникла ідея вбудувати в будь-який текст claim разом із адресою
перевірки, а згодом дати браузеру або моделі змогу його перерахувати. Перші
драфти — [EMBEDDING-SETTLEMENT.md](EMBEDDING-SETTLEMENT.md) та
[EMBED-FORMAT-DESIGN.md](EMBED-FORMAT-DESIGN.md) — правильно відділили raw
claim від читацького вердикту і побачили різницю між self-contained та
world-dependent твердженнями.

Але вони почали проєктування з поверхні — гліфа, CID, browser extension — раніше,
ніж була зафіксована модель сутностей. Через це кілька різних речей ризикують
злитися в один “зелений claim”:

```text
твердження
≠ процедура перевірки
≠ виконання процедури
≠ квитанція виконання
≠ відповідність твердження сусідній прозі
≠ право автора або спільноти прийняти висновок
```

Цей документ опускається на один шар нижче. Він не скасовує попередні драфти,
а визначає, що саме майбутній гліф, CLI, receipt або browser overlay мають
представляти.

---

## 1. Проблема: проза має кілька режимів, а checker бачить лише операнди

У manifesto поруч природно живуть:

- метафори й образи;
- визначення та стипуляції;
- нормативні позиції;
- спекулятивні траєкторії;
- емпіричні твердження;
- твердження про стан репозиторію;
- формальні теореми;
- результати детермінованих обчислень;
- маркетингово-подібні сильні формулювання, які потребують декомпозиції.

Змушувати весь текст говорити однією машинною мовою означало б не усунути
семантичний розрив, а приховати його під синтаксисом. Речення “цінність виникає
у відношенні” не стає точнішим від того, що `Value` отримало поле `type`.
Натомість речення “у цьому файлі сім тез” має ясний операнд, процедуру і
контрприклад; його природно винести в перевірний блок.

Тому базова одиниця тут — не все речення і не весь Markdown. Базова одиниця —
**явно виділене атомарне зобов'язання**, для якого автор готовий назвати:

1. що саме стверджується;
2. у якому домені та на якому snapshot;
3. яка процедура може дати спостережуваний результат;
4. які входи, параметри й контекст ця процедура реально використовує;
5. чого позитивний результат не встановлює;
6. до якого фрагмента прози автор намагається перенести validation credit.

Якщо хоча б одна з цих частин невідома, це не робить текст незаконним. Це лише
означає, що claim поки не скомпільований до replayable-форми.

---

## 2. Цілі та не-цілі

### 2.1. Цілі

Формат має:

1. **Розрізняти авторське очікування і отриманий вердикт.** Raw-блок не має
   права сам собі видати `PASS`.
2. **Бути видимим у звичайному Markdown.** Людина повинна зрозуміти основний
   зміст без спеціального renderer'а.
3. **Бути однозначно виділеним для машини.** На першому етапі — лише fenced
   code blocks, без евристичного полювання на всі речення.
4. **Фіксувати dependency closure.** World-claim без зафіксованих байтів,
   snapshot або способу їх отримання не може стати `MATCH`.
5. **Описувати capabilities, payload policy, side effects і resource limits до
   execution.** Це пряме успадкування MYC.
6. **Розділяти ідентичність плану, результату і receipt.** Це пряме
   успадкування SPORE.
7. **Зберігати різні validation credits ортогонально.** Kernel-derived,
   replayed, implementation-conformant, domain-adequate й normatively-adopted
   не складаються в один badge.
8. **Робити невідповідність між прозою і claim'ом окремим об'єктом аудиту.**
9. **Дозволяти поступове застосування.** Один claim-блок не створює вимоги
   переписати весь manifesto.
10. **Мати негативні fixtures і падаючого споживача.** Формат живе лише тоді,
    коли порушення межі реально зупиняє відповідний consumer.

### 2.2. Не-цілі

Перша версія не має:

- формалізувати всі значення природної мови;
- оголошувати metaphoric, normative або speculative текст “невалідним”;
- доводити semantic adequacy вибраного verifier'а;
- перетворювати receipt на authority;
- автоматично виконувати довільний код із Markdown;
- надавати file-write, network, model-call або git-write за замовчуванням;
- створювати глобальний trust score автора;
- робити MYC, Trinity, Warrant або Σ-GLYPH модулями одного нового стека;
- одразу будувати IPFS/CAS, browser extension, badge service чи MCP;
- мігрувати весь README або вимагати “100% речень у claims”.

---

## 3. Походження конструкції: що беремо і звідки

Цей дизайн не є чистим винаходом manifesto. Він складає вже відкриті механізми,
але не переносить їхню нормативну владу або validation credit автоматично.

Snapshot, використаний для цього драфту:

| Джерело | Ревізія | Що звідти беремо | Чого не імпортуємо |
|---|---|---|---|
| manifesto | `40d0b0578d83c877b8e4103b351f8aa3f085de3a` | inline claims, receipts, status distinctions, semantic-gap discipline | твердження, що поточні checker'и вже реалізують цей дизайн |
| MYC | `b1e94b03df9d0a34df693380b6bdeea9b970e2dc` | `RecipeDescriptor`, dry-run, payload/path/effect/proof/output contracts, Markdown + canonical block | MYC authority, descriptor namespace або дозвіл на виконання |
| Trinity | `52b98e29e4303a72cd4a5b55f7f9256192bff68b` | causal closure, exact mutator identity, `record → resolve → apply → receipt`, recipe як projection | Trinity ledger ontology як обов'язковий storage layer |
| SPORE draft у Trinity | та сама ревізія | окремі identity для apply-record і output; EXPECT/CAPS/DEPENDS; fail-closed unknowns | заяву, що manifesto є SPORE-conformant або отримує його proof status |

Першоджерела:

- [MYC Recipe Draft Spec](https://github.com/s0fractal/myc/blob/b1e94b03df9d0a34df693380b6bdeea9b970e2dc/protocols/recipes/SPEC.draft.md)
- [MYC RecipeDescriptor](https://github.com/s0fractal/myc/blob/b1e94b03df9d0a34df693380b6bdeea9b970e2dc/public/objects/h/53396d6c498b/h.53396d6c498b.classify-intent.recipe.myc.md)
- [MYC JAZZ recipe example](https://github.com/s0fractal/myc/blob/b1e94b03df9d0a34df693380b6bdeea9b970e2dc/protocols/jazz/examples/recipe.classify.h.12f026ff.raw.myc.md)
- [MYC policy dry-run](https://github.com/s0fractal/myc/blob/b1e94b03df9d0a34df693380b6bdeea9b970e2dc/src/x01A0_policy_services.ts)
- [MYC quarantine counterexample](https://github.com/s0fractal/myc/blob/b1e94b03df9d0a34df693380b6bdeea9b970e2dc/protocols/recipes/myc-quarantine-policy.function.myc.md)
- [Trinity: Recipe As Spore](https://github.com/s0fractal/trinity/blob/52b98e29e4303a72cd4a5b55f7f9256192bff68b/src/x3300_t20260511000847_codex_recipe-as-spore-ledger-native-mutators.myc.md)
- [Trinity: Ledger Records, Not Recipes](https://github.com/s0fractal/trinity/blob/52b98e29e4303a72cd4a5b55f7f9256192bff68b/src/x4d00_t20260513211717_codex_ledger-records-not-recipes.myc.md)
- [SPORE v0 draft](https://github.com/s0fractal/trinity/blob/52b98e29e4303a72cd4a5b55f7f9256192bff68b/contracts/SPORE.v0.draft.md)
- [Invariant Recipe Method](../INVARIANT-RECIPES.md)
- [FLOW glossary](FLOW-GLOSSARY.md)

### 3.1. MYC: хороший мінімум до виконання

MYC вимагає, щоб recipe ще **до запуску** називав:

```text
function
params
context_policy
payload_policy
allowed_paths
forbidden_paths
side_effects
proof_mode
output_contract
dry_run
```

Найцінніше тут не назви полів, а інваріант: процедура має бути explainable до
execution. `side_effects: ["none"]` означає не “майже read-only”, а відсутність
file, network, model і git writes. Recipe draft — review target, не authority.

Розширений JAZZ-приклад додає `input_commitment`, `context_commitment`,
`params_commitment`, очікувані outputs і точні privacy permissions. Саме ці
поля захищають від непомітної зміни операнда.

Обмеження спадщини теж важливе: наявний MYC audit переважно перевіряє форму, а
наявний `recipeDryRun` проєктує поля дескриптора. Це ще не доказ, що function
існує, capabilities достатні, execution відповідає dry-run або результат має
заявлене значення. Ми беремо контракт, але не називаємо field-presence
verification.

### 3.2. Trinity: recipe як causal packet, а потім як view

Початкова конструкція Trinity розклала portable transition так:

```text
recipe_hash = H(prev_state, mutator, params, input)
next_state  = apply(recipe, prev_state)
receipt     = H(recipe, next_state, trace, provenance)
```

Вона принесла чотири інваріанти, потрібні й claim-системі:

- точна, addressable версія функції;
- повна залежність від входів і контексту;
- expected result, відмінний від actual result;
- receipt, відмінний і від плану, і від результату.

Пізніша нотатка `Ledger Records, Not Recipes` зробила ще важливішу корекцію:
recipe не обов'язково є фундаментальним типом. Машинний субстрат може зберігати
граф записів, а “recipe” бути людською проєкцією apply-chain.

Для цього дизайну наслідок прямий:

```text
Markdown claim block = capsule / projection
canonical machine state = linked records
```

Не можна робити identity claim'а залежною від того, скільки пробілів навколо
code fence або де блок стоїть у документі.

### 3.3. SPORE: transition identity не є result identity

SPORE розрізняє `spore_id` запису `apply(...)` і `output_hash`. Так само тут:

```text
claim_id        ≠ verification_plan_id
plan_id         ≠ result_id
result_id       ≠ receipt_id
receipt_id      ≠ prose_document_id
```

SPORE також резервує окремі commitments для expected output, capabilities і
dependency manifest та відхиляє невідомі flags. Ми не копіюємо wire format, але
переносимо fail-closed правило: невідомий verifier, profile, schema field або
нерозв'язна dependency не дає “best effort PASS”.

### 3.4. Три різні “recipe”, які не можна зливати

| Назва | Значення | Роль тут |
|---|---|---|
| **Invariant Recipe** у manifesto | аналітичний контракт `(P,T,G,L,B)` для claim'а | допомагає знайти передумови, гарантії, втрати й boundary |
| **MYC RecipeDescriptor** | контрольована reusable transformation | дає execution-policy envelope |
| **Trinity recipe-view** | людська проєкція графа apply/receipt records | дає правильний статус Markdown capsule |

Тому канонічний тип нового об'єкта не слід називати просто `Recipe`. Робочі
назви: `ClaimDescriptor`, `VerificationPlan`, `VerificationReceipt` і
`SemanticBinding`. Слово recipe може залишитися назвою людського view або
методом декомпозиції, але не має приховувати різницю сутностей.

---

## 4. Основні сутності

### 4.1. Prose Fragment

Фрагмент людського тексту. Може бути метафоричним, нормативним, спекулятивним
або перевірним. Сам по собі не зобов'язаний мати machine-readable форму.

### 4.2. Claim

Атомарне твердження з явним релятумом. Claim описує, **що автор бере на себе як
зобов'язання**, але не містить отриманого verdict.

### 4.3. Semantic Binding

Окрема авторська заява, що Claim має певне відношення до Prose Fragment:

```text
supports | refutes | defines | instantiates | measures
```

Саме тут живе головний залишковий розрив. Механічний verifier може підтвердити
результат claim'а і водночас нічого не знати про адекватність binding'а.

### 4.4. Verification Plan

Пінована процедура, яка називає verifier/profile, inputs, params, context,
capabilities, effects, limits, proof mode і expected result. Це план перевірки,
не факт її виконання.

### 4.5. Dependency Manifest

Повна або явно обмежена множина байтів/артефактів, від яких залежить результат.
Path без digest не є identity. URL без captured response не є replayable input.
Ambient clock, environment, filesystem або network response мають бути
перетворені на зафіксований artifact або чесно марковані як live observation.

### 4.6. Result

Канонічний результат виконання verifier'а над конкретними inputs. Result може
бути `true/false`, normal form, countermodel, count, digest або typed error.

### 4.7. Verification Receipt

Запис про фактично виконаний Plan:

- які exact bytes були використані;
- який verifier/runtime/profile був запущений;
- які capabilities реально надавалися;
- який result отримано;
- скільки ресурсів витрачено;
- чи збігся actual result з expected;
- що не було перевірено.

Receipt описує виконання. Він не є verifier binary, dependency artifact,
semantic adequacy proof або governance adoption.

### 4.8. Rendered Verdict

Локальне представлення receipt для читача: `MATCH`, `MISMATCH`, `STALE`,
`UNRESOLVED` тощо. Badge/overlay є cache або projection і не отримує більшого
credit, ніж receipt, який читач реально перевірив.

---

## 5. Не одна шкала статусу, а ортогональний ledger

Одна позначка `✓` неминуче переобіцяє. Мінімум чотири координати мають жити
окремо.

### 5.1. Epistemic / language status

Це статус змісту за явно названим профілем, наприклад:

```json
{
  "profile": "manifesto/FLOW-GLOSSARY-0.6",
  "value": "Stipulated"
}
```

`Defined`, `Stipulated` і `Speculative` не треба перетворювати на універсальну
глобальну enum: це словник конкретного профілю.

### 5.2. Execution state

```text
DECLARED
→ PARSED
→ RESOLVED
→ EXECUTED
→ MATCH | MISMATCH
```

Бічні стани:

```text
UNSUPPORTED_SCHEMA
UNKNOWN_VERIFIER
UNRESOLVED_DEPENDENCY
STALE
BUDGET_EXCEEDED
CAPABILITY_DENIED
TRAPPED
NONDETERMINISTIC
```

Жоден із них не є синонімом `false`. Наприклад, `STALE` означає, що заявлений
world snapshot не збігається з поточним; істинність для старого snapshot може
залишатися відкритою або вже підтвердженою.

### 5.3. Validation credit

Receipt може надати лише конкретні кредити:

```text
PARSE_CONFORMANT
DEPENDENCIES_RESOLVED
REPLAY_MATCHED
KERNEL_DERIVED
IMPLEMENTATION_CONFORMANT
COUNTERMODELED
```

Окремо залишаються, і не виводяться автоматично:

```text
DOMAIN_ADEQUATE
EMPIRICALLY_GROUNDED
SEMANTIC_BINDING_REVIEWED
NORMATIVELY_ADOPTED
```

### 5.4. Authority / lifecycle

```text
draft | candidate | accepted | superseded | withdrawn
```

Це рішення конкретного owner/governance process. Верифікатор не має права
перетворити `draft` на `accepted`, навіть якщо всі байти збіглися.

---

## 6. Архітектура: граф унизу, capsule нагорі

```text
                           ┌──────────────┐
                           │ ProseFragment│
                           └──────┬───────┘
                                  │ SemanticBinding
                                  ▼
┌───────────┐      ┌──────────────────┐      ┌────────────────────┐
│   Claim   │─────▶│ VerificationPlan │─────▶│ DependencyManifest │
└───────────┘      └─────────┬────────┘      └────────────────────┘
                             │ execute
                             ▼
                       ┌──────────┐
                       │  Result  │
                       └────┬─────┘
                            │ observed by
                            ▼
                    ┌───────────────────┐
                    │VerificationReceipt│
                    └─────────┬─────────┘
                              │ projected as
                              ▼
                     badge / overlay / report
```

Markdown codeblock може переносити authoring-проєкцію кількох вузлів разом,
бо це зручно людині. Compiler має розкласти capsule на окремо адресовані
records. Це дозволяє:

- одному Claim мати кілька VerificationPlan;
- одному Plan перевірятися кількома runtime implementations;
- одному Prose Fragment мати кілька claims із різними типами credit;
- замінити renderer, не змінюючи identity claim'а;
- supersede binding, не переписуючи історичний receipt;
- не хешувати whitespace або весь Markdown як сутність claim'а.

---

## 7. Авторська форма: fenced claim capsule

### 7.1. Чому fenced block, а не розмітка всього тексту

На першому етапі consumer читає лише code fences з exact info string:

````text
```json claim
{ ... }
```
````

Переваги:

- межа між прозою й машинним contract видима;
- Markdown лишається валідним без plugin;
- JSON отримує звичайне syntax highlighting;
- парсер не вгадує, чи `Value`, формула або стрілка є executable claim;
- автор свідомо бере verification obligation;
- можна поступово додавати по одному блоку.

Inline `⟦…⟧` може залишитися компактним authoring sugar для вже підтриманих
локальних класів, але не має бути єдиним канонічним форматом. Compiler може
перетворювати inline form на той самий graph, якщо mapping повний і явний.

### 7.2. Мінімальна authoring capsule

Нижче — **схематичний приклад**, не канонічний record і не settled claim:

```json claim
{
  "format": "manifesto.claim-capsule.v0",
  "lifecycle": "draft",
  "claim": {
    "local_id": "README-T7-COUNT-001",
    "text": "README.md містить сім основних тез",
    "kind": "repository-observation",
    "epistemic_status": {
      "profile": "UNADOPTED-CLAIM-STATUS-DRAFT",
      "value": "Observed"
    },
    "scope": {
      "repository": "manifesto",
      "revision": "40d0b0578d83c877b8e4103b351f8aa3f085de3a"
    }
  },
  "binding": {
    "document": "README.md",
    "selector": {
      "heading": "MANIFESTO: Протоколи для Цифрового Існування"
    },
    "relation": "measures",
    "asserted_by": "document-author",
    "limitations": [
      "Підрахунок заголовків не оцінює істинність змісту тез"
    ]
  },
  "verification": {
    "class": "repo.heading-count",
    "verifier": {
      "name": "manifesto-claim-verifier",
      "identity": "UNPINNED-DRAFT"
    },
    "inputs": [
      {
        "path": "README.md",
        "sha256": "f9be29ece691c7e9f19490cd6c95923fc9dfc9eb5585697508aa9165117db084"
      }
    ],
    "params": {
      "pattern": "^## Теза [0-9]+:"
    },
    "expected": {
      "type": "integer",
      "value": 7
    },
    "context_policy": "public",
    "payload_policy": "descriptor-only",
    "capabilities": ["read:repository"],
    "allowed_paths": ["README.md"],
    "forbidden_paths": ["private/", "sealed/"],
    "side_effects": ["none"],
    "limits": {
      "max_read_bytes": 8388608,
      "max_runtime_ms": 2000
    },
    "proof_mode": "deterministic",
    "output_contract": "manifesto.verification-receipt.v0",
    "dry_run": true
  }
}
```

`UNADOPTED-CLAIM-STATUS-DRAFT` і `UNPINNED-DRAFT` навмисні: FLOW-глосарій не
містить claim-статусу `Observed`, а verifier цього формату ще не існує. Документ
не позичає першому чужий profile і не вигадує другому hash. Такий блок може
lintитися як draft, але не може отримати `REPLAY_MATCHED`.

### 7.3. Чого raw capsule не містить

Raw authoring form не повинна містити:

- готовий зелений badge;
- `actual_result`, якщо виконання ще не відбулося;
- receipt hash, обчислений над неповним receipt;
- validation credits як авторське самоприсвоєння;
- підпис “community accepted” без governance record;
- semantic adequacy як наслідок `MATCH`.

Expected result є легальним: це фальсифікована ставка автора. Actual result
з'являється лише у receipt.

---

## 8. Канонічні records та addressing

### 8.1. Authoring JSON не дорівнює canonical bytes

Сказати “hash JSON” недостатньо. Потрібен запінений canonicalization profile,
exact schema version і domain separation. Кандидат для PoC — JCS/RFC 8785 із
додатковою забороною floating-point значень у identity-bearing body. Але це
рішення має бути окремо прийняте і перевірене conformance vectors; сам цей
драфт його не приймає.

Мінімальна формула:

```text
record_id = HASH(domain_separator || canonical(record_body))
```

де `domain_separator` різний для:

```text
manifesto.claim.v0
manifesto.semantic-binding.v0
manifesto.verification-plan.v0
manifesto.dependency-manifest.v0
manifesto.result.v0
manifesto.verification-receipt.v0
```

### 8.2. Commitment не хешує сам себе

Envelope може містити:

```json
{
  "type": "ClaimDescriptor",
  "schema_version": "manifesto.claim.v0",
  "commitment": {
    "algorithm": "sha256",
    "canonicalization": "<pinned-profile>",
    "covers": "descriptor.body",
    "value": "<digest>"
  },
  "body": {}
}
```

`commitment.value` не входить до `descriptor.body`; інакше виникає
self-reference. Parser має відхиляти невідоме `covers`, а не вгадувати.

### 8.3. Exact dependency closure

Для кожного input потрібен один із режимів:

1. `inline-bytes` — bytes прямо в capsule/sidecar;
2. `content-addressed` — digest + resolvable locator;
3. `repository-snapshot` — repo identity + exact revision + path + file digest;
4. `live-observation` — timestamp, fetch policy, response digest і чесний
   non-replayable/freshness статус.

Голий path, branch `main`, непінований URL або “latest” не може бути strict
replay dependency.

### 8.4. Verifier identity

Verifier identity має включати або посилатися на:

- source/binary digest;
- entrypoint;
- runtime identity та версію;
- profile/domain;
- transitive code dependencies або sealed environment identity;
- canonicalization rules;
- resource model, якщо результат від нього залежить.

Receipt, який містить лише назву скрипта, не закриває replay.

---

## 9. Dry-run і execution

### 9.1. Dry-run — це policy explanation, не фальшиве виконання

До запуску consumer повинен уміти відповісти:

```text
який verifier буде запущено?
які inputs він прочитає?
які capabilities запросить?
які side effects можливі?
які resource bounds діють?
який output contract очікується?
які частини plan нерозв'язні?
execution enabled чи ні?
```

`dry_run: true` у JSON саме по собі нічого не гарантує. Dry-run consumer має
перерахувати policy projection, перевірити resolvability і повернути
`execution_enabled: false` за замовчуванням.

### 9.2. Виконання дозволяється окремим актом

Для першого PoC дозволений лише профіль:

```text
filesystem: read-only under repository root
network: denied
model-call: denied
file-write: denied, крім явно вказаної output staging directory
git-write: denied
bounded bytes/time/output
```

Поява `side_effects != ["none"]` не означає автоматичний дозвіл. Вона лише
робить запит видимим; capability policy може його відхилити.

### 9.3. Expected mismatch

Як у SPORE `HAS_EXPECT`, deterministic plan порівнює actual canonical result з
expected:

```text
actual == expected → MATCH
actual != expected → MISMATCH + receipt, без зміни source document
```

MISMATCH — цінний результат, а не аварія, яку треба приховати. Саме він ловить
authorial overclaim.

---

## 10. Semantic Binding: головний продукт, а не службове поле

### 10.1. Чому replay недостатньо

Нехай verifier правильно встановив:

```text
README.md має 7 заголовків виду "## Теза N"
```

З цього не випливає:

```text
маніфест має лише 7 значущих тверджень;
усі 7 тези істинні;
тези незалежні;
структура маніфесту повна;
зміст є етично прийнятним.
```

Технічний result підтримує лише обмежене відношення. SemanticBinding має
називати це відношення і його loss report.

### 10.2. Binding як окремий claim

Binding не слід вкладати в receipt як нібито доведений факт. Його мінімальна
форма:

```text
source fragment identity
target claim identity
claimed relation
scope/profile
introduced assumptions
known losses
falsifier or review procedure
binding status
```

Початковий `binding status` має бути `AUTHOR_ASSERTED`. Пізніше незалежний
review може додати `REVIEWED`, `CONTESTED` або `REFUTED`, не переписуючи
початковий запис.

### 10.3. Стабільний prose selector

Номер рядка нестабільний, а heading може повторюватися. Кандидатний selector:

```json
{
  "document_digest": "sha256:...",
  "heading_path": ["Теза 7: Чорний конус"],
  "quoted_text_digest": "sha256:...",
  "occurrence": 1
}
```

Людська quote може зберігатися для читабельності, але identity має спиратися на
bytes/digest. Після редагування прози старий binding стає `STALE`; він не
переїжджає мовчки до “схожого” абзацу.

### 10.4. Semantic-gap report

Для сильних claims binding повинен мати форму, споріднену з Invariant Recipe
Method:

```text
Prerequisites / Assumptions
Transformation / Check
Guarantees actually obtained
Loss / Non-guarantees
Boundary / Scope
Countermodel or falsifier
```

Це місце, де manifesto може додати власний внесок до успадкованого recipe
envelope: не лише “чи виконалася процедура?”, а “який саме forward cone вона
ліцензує?”.

---

## 11. Які claims варто і не варто компілювати першими

### 11.1. Добрі кандидати

- арифметичні й порівняльні твердження;
- counts/digests над pinned repository snapshot;
- exact quotations і source presence;
- schema conformance;
- детерміновані інваріанти над explicit inputs;
- Lean theorem/countermodel за pinned toolchain і axiom policy;
- Warrant replay над повною dependency closure;
- твердження про конкретний experiment result із captured dataset;
- negative claims, для яких існує executable counterexample.

### 11.2. Claims, які потребують декомпозиції

- “система безпечна”;
- “ідентичність не копіюється”;
- “це форма життя”;
- “протокол справедливий”;
- “verification завершується” без scheduler/root-selection assumptions;
- “Lean довів значення терміна”;
- “receipt доводить правильність рішення”.

Їх не треба забороняти. Треба або лишити typed speculation/normative position,
або розкласти на кілька claims і окремий binding, який не приховує gap.

### 11.3. Claims, які не треба насильно компілювати

- поетичні образи;
- запрошення уявити можливе;
- етичні позиції як позиції;
- відкриті питання;
- слова на кшталт Value, Dignity, Love або Meaning без операційної претензії;
- свідомо Speculative-конектори та trajectory sketches.

Їхня чесність походить від типу й контексту, не від фіктивного verifier'а.

---

## 12. Coverage: не “який процент тексту в claims”, а вектор меж

Один загальний відсоток створить Goodhart-пастку: автор почне дробити легкі
claims, уникати складних або оголошувати метафору “не claim”, щоб підняти
показник.

Мінімальний coverage report повинен мати кілька знаменників:

```text
E = atomic claims, визнані eligible для поточного verification profile
D = E, що мають ClaimDescriptor
B = D, що мають явний SemanticBinding
P = D, що мають resolvable VerificationPlan
R = P, replay яких успішно виконано на pinned dependencies
F = R, receipts яких fresh відносно обраного target snapshot
```

Тоді звіт — вектор:

```text
descriptor coverage = D / E
binding coverage    = B / D
plan coverage       = P / D
replay coverage     = R / P
fresh coverage      = F / R
```

Обов'язково публікуються:

- метод atomization;
- профіль eligibility;
- snapshot документа;
- excluded categories;
- unresolved disagreements щодо знаменника.

`R/P = 100%` може означати лише, що всі три вибрані легкі claims replayed. Воно
не означає, що “manifesto на 100% verified”.

Для першого етапу правильна мета не відсоткова. Правильна мета:

> три різні класи claims проходять повний цикл, один навмисно refuted, один
> stale, а semantic binding не отримує автоматичного credit.

---

## 13. Threat model і failure signals

### 13.1. Структурне laundering

JSON повний, schema green, але verifier не виконує заявлену семантику.

**Контроль:** behavioral fixtures, known-answer tests, negative/mutation tests,
verifier identity та conformance suite.

### 13.2. Semantic laundering

Тривіальний true claim прив'язаний до сильного абзацу і візуально робить його
“доведеним”.

**Контроль:** binding окремий, credit не переходить автоматично, renderer
показує “claim replayed / binding author-asserted”.

### 13.3. Authority laundering

Receipt використовується як warrant на дію або governance acceptance. Старий
MYC quarantine draft показує, що формально повний recipe може описувати
авторитарну дію.

**Контроль:** authority/lifecycle поза execution verdict; no side effects by
default; capability grant окремий від декларації.

### 13.4. Dependency substitution

Plan називає path або URL, а verifier читає інші bytes.

**Контроль:** digest фактично прочитаних bytes у receipt; containment;
download/read-back; strict comparison із manifest.

### 13.5. Stale green

Історичний receipt показується біля зміненого тексту чи файла.

**Контроль:** prose/document/input digests; `STALE` як окремий verdict;
renderer ніколи не переносить green між snapshots.

### 13.6. Receipt forgery або partial comparison

Перевіряються лише кілька полів receipt, а решта можуть бути змінені.

**Контроль:** canonical receipt body hash; exact closed schema;
`additionalProperties: false`; порівняння всіх identity-bearing полів.

### 13.7. Path escape, symlink escape, ReDoS, resource exhaustion

**Контроль:** resolved-path containment, symlink policy, allowlisted roots,
bounded bytes, regex policy/timeouts, output limits, ATP/gas або wall-time
policy там, де це лише implementation-local diagnostic.

### 13.8. Unknown-field downgrade

Старий consumer ігнорує нове поле, яке змінює semantics.

**Контроль:** closed versioned schemas; unknown fields/profiles/flags fail
closed; explicit migration.

### 13.9. Self-reference laundering

Документ каже, що сам відповідає формату, використовуючи власну незавершену
схему як доказ.

**Контроль:** bootstrap status. Design draft не може бути першим conformance
certificate власного дизайну.

### 13.10. Coverage gaming

Легкі claims масово розмічаються, складні лишаються в prose, а загальний badge
росте.

**Контроль:** coverage vector, declared eligibility profile, claim inventory і
окремий список high-impact uncompiled claims.

---

## 14. Мінімальна схема receipt

Схематично, не як уже прийнята JSON Schema:

```json
{
  "type": "VerificationReceipt",
  "schema_version": "manifesto.verification-receipt.v0",
  "body": {
    "claim_id": "sha256:...",
    "binding_ids": ["sha256:..."],
    "verification_plan_id": "sha256:...",
    "dependency_manifest_id": "sha256:...",
    "verifier": {
      "artifact_id": "sha256:...",
      "runtime_id": "sha256:...",
      "profile_id": "sha256:..."
    },
    "observed_inputs": [
      {
        "declared_id": "sha256:...",
        "observed_id": "sha256:...",
        "match": true
      }
    ],
    "execution": {
      "capabilities_granted": ["read:repository"],
      "side_effects_observed": ["none"],
      "resource_model": "implementation-local",
      "resource_spent": {
        "wall_ms": 12,
        "bytes_read": 8142
      }
    },
    "result_id": "sha256:...",
    "expected_match": true,
    "verdict": "MATCH",
    "credits": [
      "DEPENDENCIES_RESOLVED",
      "REPLAY_MATCHED"
    ],
    "not_established": [
      "SEMANTIC_BINDING_REVIEWED",
      "DOMAIN_ADEQUATE",
      "NORMATIVELY_ADOPTED"
    ]
  },
  "commitment": {
    "algorithm": "sha256",
    "covers": "descriptor.body",
    "value": "sha256:..."
  }
}
```

Для `MISMATCH` receipt все одно зберігається. Для `UNRESOLVED` допустимий error
receipt, але він не повинен вигадувати `result_id`. Runtime-specific error text
може бути diagnostic, але downstream semantics не має branch-итися на його
довільному формулюванні.

---

## 15. Поступове застосування до manifesto

### Phase 0 — Design freeze, без production schema

Артефакти:

- цей design draft;
- таблиця відкритих рішень;
- inventory трьох значень “recipe”;
- явний список non-goals.

Gate:

- review погоджується хоча б із розділенням сутностей;
- жоден checker або README не заявляє conformance.

### Phase 1 — Три hand-written capsules і counterexamples

Обрати лише три claims:

1. self-contained deterministic claim;
2. repository-snapshot claim;
3. formal/kernel або Warrant-replay claim.

Поруч створити щонайменше:

- expected mismatch;
- stale dependency;
- unknown verifier;
- forbidden path;
- extra field;
- valid replay із deliberately wrong semantic binding.

Gate:

- людина може прочитати capsule;
- negative cases виражають головні межі;
- ще немає automatic execution.

### Phase 2 — Parser + schema/lint consumer

Consumer:

- використовує Markdown parser, а не regex по всьому тексту;
- читає лише exact fenced info string;
- валідовує closed schema;
- нормалізує capsule у graph records;
- обчислює commitments за pinned canonicalization profile;
- видає dry-run policy report;
- нічого не виконує.

Gate:

- усі malformed/unknown-field fixtures fail closed;
- whitespace Markdown не змінює record identity;
- зміна identity-bearing body змінює commitment;
- parser не чіпає звичайні codeblocks і метафоричну прозу.

### Phase 3 — Bounded verifier

Спочатку лише наявні deterministic класи, адаптовані з `settle_gate.py`, із
повною dependency closure та explicit runtime/verifier identity.

Gate:

- dry-run і execution capabilities збігаються;
- path containment, byte/time limits і closed receipt comparison мають
  негативні тести;
- replay у clean environment дає той самий canonical result;
- mutation tests ламають consumer там, де очікується.

### Phase 4 — Semantic binding report

Renderer показує щонайменше два незалежні рядки:

```text
claim execution: MATCH
semantic binding: AUTHOR_ASSERTED / REVIEWED / CONTESTED
```

Gate:

- green execution не фарбує весь абзац у green;
- навмисно неправильний binding лишається видимо неправильним попри replay;
- зміна prose fragment робить binding stale.

### Phase 5 — Обмежена міграція manifesto

Почати з Тези 7 та технічних додатків, де вже існують receipts/checkers. Не
починати з Value/Dignity/Life/Identity.

Gate:

- migration diff невеликий і reviewable;
- source prose не переписується під метрику;
- coverage report називає знаменники й exclusions;
- старий inline format або має explicit compiler mapping, або лишається legacy;
- rollback полягає у видаленні capsules/sidecars, а не відновленні переписаної
  онтології.

### Phase 6 — Лише після стабільного локального циклу

Можливі:

- CLI `lint / dry-run / verify / render`;
- MCP tool для моделей;
- hosted verifier;
- browser extension/bookmarklet;
- CAS/IPFS publication;
- server badge як чесно позначений cache/view.

Жоден із них не потрібен, щоб перевірити основну архітектурну гіпотезу.

---

## 16. Конкретне завдання наступному виконавцю

Цей розділ можна використати як handoff для Клода.

### 16.1. Спочатку — review дизайну

Потрібно спробувати спростувати:

1. чи справді Claim, Binding, Plan, Result і Receipt мусять бути окремими;
2. чи існує workflow, який не виражається графом цих records;
3. чи authoring capsule може бути простішою без втрати critical boundary;
4. чи запропоновані status axes ортогональні;
5. чи coverage vector не має невизначеного або gameable знаменника;
6. чи semantic binding можна зробити executable для вузьких класів, не
   оголошуючи загальну semantic adequacy.

Результат review має містити counterexamples, а не лише стилістичні поради.

### 16.2. Потім — найменший PoC

Якщо розділення витримало review, створити ізольований draft/PoC, не змінюючи
README і не торкаючись Trinity/MYC:

```text
drafts/embedded-claims-poc/
  README.md
  schemas/
  fixtures/valid/
  fixtures/invalid/
  receipts/
  verifier or linter entrypoint
```

Рекомендовані команди майбутнього інтерфейсу:

```text
claims lint <markdown>
claims dry-run <markdown>
claims verify <markdown> --out <staging-dir>
claims render <markdown> --receipts <dir>
```

Назви не нормативні; behavior важливіший.

### 16.3. Обов'язкові fixtures

Positive:

- один self-contained claim;
- один pinned repository claim;
- один claim із receipt, що replayed у clean checkout.

Negative:

- malformed JSON;
- unknown schema version;
- unknown extra field;
- missing payload policy;
- `side_effects: ["none"]` при фактичному write/network attempt;
- path traversal і out-of-tree symlink;
- dependency digest mismatch;
- stale prose selector;
- expected mismatch;
- unpinned verifier;
- receipt body mutation;
- valid claim із intentionally invalid/unsupported semantic binding;
- budget exhaustion;
- unsupported nondeterminism.

### 16.4. Заборонені shortcuts

- не оголошувати schema green semantic verification;
- не використовувати receipt як executable artifact;
- не хешувати лише кілька вибраних receipt fields;
- не приймати branch name як immutable revision;
- не дозволяти unknown fields “для forward compatibility” у v0;
- не будувати browser extension раніше за negative fixtures;
- не робити full-document parser, який намагається сам знайти всі claims;
- не змінювати MYC/Trinity, щоб вони “підтримали” manifesto;
- не називати shared LLM review незалежною validation;
- не ставити загальний “verified manifesto” badge.

### 16.5. Definition of done для PoC

PoC завершений не тоді, коли valid example зелений. Він завершений, коли:

1. valid example replayed у чистому середовищі;
2. кожна negative fixture падає з typed reason;
3. зміна dependency дає `STALE/MISMATCH`, а не silent green;
4. receipt перевіряється повністю;
5. execution не може вийти за capability boundary;
6. renderer показує межу validation credit;
7. wrong semantic binding не отримує credit від правильного result;
8. документуємо, що лишилося unproven.

---

## 17. Відкриті рішення

1. **Canonicalization:** JCS/RFC 8785 чи простіший власний closed JSON profile?
2. **Hash:** SHA-256 для сумісності з manifesto/Warrant чи domain-separated
   BLAKE3 для нових records? Змішування потребує явного multihash profile.
3. **Authoring form:** чи capsule містить inline Plan, чи лише reference на
   окремий Plan record?
4. **Info string:** `json claim`, `claim+json` чи інший exact token?
5. **Selectors:** як стабільно адресувати prose fragment після нормальних
   редакцій?
6. **Binding vocabulary:** який мінімальний closed set relations не створює
   псевдоточності?
7. **Runtime closure:** source digest + runtime version достатні для v0 чи
   потрібен sealed environment/container/wheel digest?
8. **Live claims:** чи входять вони у v0, чи перша версія підтримує лише pinned
   snapshots?
9. **Nondeterministic/model checks:** чи завжди це `witnessed`, а не replayed?
10. **Signatures/authorship:** окремий record одразу чи поза першим PoC?
11. **Legacy inline syntax:** compiler target, authoring sugar чи окрема
    застаріла система?
12. **Ownership:** чи schema живе в manifesto, чи згодом стає окремим профілем;
    cross-repo adoption не можна припустити наперед.

---

## 18. Фальсифікатори всього дизайну

Цей напрям слід зупинити або суттєво змінити, якщо:

1. люди систематично не можуть відрізнити raw claim від verified receipt;
2. machine parser потребує розуміння довільної прози, щоб виконати базову
   перевірку;
3. claim capsule неможливо нормалізувати без втрати заявленої semantics;
4. semantic binding знову редукується до adjacency або “автор так сказав” і
   renderer приховує це;
5. повна dependency closure дорожча за саму перевірку настільки, що для
   вибраних класів механізм не використовується;
6. coverage metrics стимулюють більше шуму, ніж закритих obligations;
7. дві незалежні implementations не погоджуються щодо canonical records або
   receipts;
8. capability policy неможливо звірити з фактичними effects;
9. формат стає authority token або приводом автоматичної дії;
10. найсильніші claims manifesto не стають точнішими, а лише отримують
    декоративний JSON.

---

## 19. Самозастосування цього документа

Цей драфт написаний мовою меж, які сам пропонує, але **не заявляє conformance
власному майбутньому формату**.

Що тут уже є:

- exact source revisions;
- provenance механізмів;
- відокремлення proposal від adopted specification;
- явні non-goals;
- loss/limitations;
- open decisions;
- falsifiers;
- schematic capsule із навмисно непінованим verifier'ом.

Чого тут немає:

- прийнятої schema;
- canonicalization vectors;
- compiler із capsule до records;
- pinned verifier identity;
- executable receipt цього документа;
- незалежного semantic-binding review;
- governance adoption.

Тому правильний статус цього файла:

```text
DESIGN_DRAFT
structure argued, not conformance-proven
source provenance pinned, implementation absent
semantic adequacy open
adoption open
```

Це не недолік, який треба замаскувати fake badge. Це bootstrap boundary.

---

## 20. Стисла теза

Не треба перетворювати весь manifesto на код. Треба дати окремим сильним і
перевірним твердженням явну форму, в якій:

```text
автор формулює Claim і expected result;
VerificationPlan називає exact procedure, inputs, context і effects;
DependencyManifest фіксує світ, проти якого твердження перевіряється;
execution породжує окремий Result і Receipt;
SemanticBinding чесно описує, що цей result підтримує у прозі;
renderer показує кожен validation credit окремо;
authority та adoption лишаються окремими рішеннями.
```

MYC уже дав discipline до execution. Trinity вже показала causal closure і
понизила recipe з онтології до view. SPORE вже розвів transition identity та
output identity. Manifesto може додати те, чого цим механізмам бракує саме для
природної мови: явний SemanticBinding, loss report і вимірюваний розрив між
правильно виконаним claim'ом та тим, що текст намагається з нього вивести.

Тобто новизна не в `claim+json` і не в гліфі. Новизна — у тому, щоб зробити
перехід

```text
prose → claim → computation → receipt → licensed prose consequence
```

настільки ж видимим і фальсифікованим, як саме обчислення.
