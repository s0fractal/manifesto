# CONTROLLED-FORGETTING-0.1 — Забуття як зміна admission, а не стирання минулого

**Статус:** design draft / proposal. Не політика репозиторію, не дозвіл на
масове прибирання і не список файлів-кандидатів.

**Призначення:** описати, як прибирати застарілі патерни, роздуми й стандарти з
активної когнітивної поверхні репозиторію, не вдаючи, що їх ніколи не існувало,
не втрачаючи provenance та не дозволяючи моделі випадково воскресити їх як
чинний precedent.

**Принцип одним реченням:**

> Контрольоване забуття — це типізована зміна admission policy для точного
> артефакту, з явним loss і tombstone у live tree; це не заперечення існування,
> не автоматичне спростування і не гарантія фізичного стирання байтів.

---

## 0. Чому це стало окремою проблемою

Дослідницький репозиторій накопичує не лише результати, а й траєкторію:

- ранні формулювання, що відкрили напрям, але більше не є найкращими;
- експериментальні синтаксиси, які випадково стали precedent;
- моделі, демотовані після контрприкладу;
- чернетки з конфліктуючими версіями одного стандарту;
- корисні помилки, які варто пам'ятати історично, але не підкладати в кожен
  новий контекст;
- завершені гілки думки, чия постійна присутність дорожча за їхню живу цінність.

Зберігати все у HEAD означає не максимальну пам'ять, а максимальну конкуренцію
за увагу. Для людини це створює плутанину. Для моделі — ще гірше: кілька
схожих документів із різними статусами легко зливаються в уявний “узгоджений
стандарт”, якого ніколи не існувало.

Просте видалення теж недостатнє. `git log` може зберегти bytes, але не пояснює:

- чому артефакт зник;
- чи він хибний, замінений, небезпечний або просто більше не потрібний у
  default context;
- що саме було втрачено при заміні;
- чи дозволено використовувати його як історичне джерело;
- що потрібно для легального повернення.

Отже потрібен не “чистильник репозиторію”, а протокол керованої зміни
когнітивної поверхні.

---

## 1. Базове розрізнення: пам'ять, активність і доступ — не одне й те саме

Мінімум три шари мають лишатися окремими.

### 1.1. Active surface

Артефакти, які поточний reader, agent або context builder має право вважати
живими кандидатами на норму, precedent чи основу наступної роботи.

### 1.2. Historical substrate

Попередні Git objects, releases, receipts, discussions та зовнішні архіви. Вони
можуть бути доступні для реконструкції, але сама доступність не повертає їм
активний статус.

### 1.3. Admission policy

Правило, за яким артефакт потрапляє у default context і може ліцензувати нове
рішення. Саме цей шар змінює controlled forgetting.

Тому:

```text
present in Git history  ≠ active
retrievable             ≠ admitted
historically important  ≠ currently normative
restored bytes          ≠ re-adopted meaning
```

---

## 2. Не один `DELETED`: типи retirement

Один статус приховав би різні причини й різні правила повернення.

| Mode | Що означає | Що не означає |
|---|---|---|
| `SUPERSEDED` | є названий replacement, який займає попередню роль | повна семантична еквівалентність без loss |
| `WITHDRAWN` | owner більше не підтримує claim, proposal або стандарт | claim машинно спростований |
| `REFUTED` | існує адресний контрприклад або finding | артефакт історично нецінний або має бути стертий |
| `ARCHIVED` | прибрано з default surface, але збережено для історичного читання | помилка чи відмова від змісту |
| `ABANDONED` | траєкторію припинено через cost, відсутність прогресу або зміну фокусу | логічна неможливість напряму |
| `QUARANTINED` | споживання тимчасово заборонене через невизначений ризик чи provenance | остаточний verdict |
| `REDACTED` | bytes не повинні залишатися доступними у звичайній історії | звичайне видалення з HEAD |

`REDACTED` — окремий security/privacy протокол. Він може вимагати history
rewrite, видалення release artifacts, cache invalidation і key rotation. Його не
можна реалізувати tombstone'ом, що містить digest або цитату секрету: навіть hash
може стати verification oracle для вгадуваного значення.

---

## 3. Основні сутності

### 3.1. Retirement Intent

Заявка прибрати точний subject із active surface. До застосування вона не змінює
статус артефакту.

### 3.2. Impact Report

Результат read-only аналізу до зміни:

- exact paths і content digests;
- active inbound references;
- generated outputs та receipts, які залежать від subject;
- cross-repository links;
- replacement candidates;
- прогнозований loss;
- reversible та irreversible частини операції.

### 3.3. Retirement Plan

Точний план переходу: що видаляється, що оновлюється, який tombstone лишається,
які postconditions мають упасти при неповному прибиранні.

### 3.4. Retirement Receipt

Запис фактичного переходу між двома станами дерева. Receipt не доводить, що
retirement був мудрим; він лише адресує виконану трансформацію та її результат.

### 3.5. Tombstone

Мінімальний live record, який повідомляє майбутньому reader'у або моделі:

```text
цей subject існував;
він більше не admitted за замовчуванням;
ось mode і причина;
ось replacement, якщо він є;
ось known loss;
ось умови історичного доступу та re-adoption.
```

Tombstone не копіює весь retired artifact. Інакше він сам стає каналом його
неявного повернення в context.

### 3.6. Re-adoption Record

Окреме рішення, що повертає історичний subject або його похідну в active
surface. `git show`, checkout старого commit або копіювання bytes не є
re-adoption.

---

## 4. Машина станів

```text
                         ┌──────────────┐
                         │ QUARANTINED  │
                         └──────┬───────┘
                                │ resolve / review
                                ▼
ACTIVE ────────┬────────▶ SUPERSEDED
               ├────────▶ WITHDRAWN
               ├────────▶ REFUTED
               ├────────▶ ARCHIVED
               └────────▶ ABANDONED

historical state ──explicit Re-adoption Record──▶ ACTIVE-derived revision

REDACTED  — окрема гілка; не обіцяє recoverability
```

Повернення не переписує старий RetirementReceipt. Воно створює новий causal
record і, бажано, нову revision артефакту. Це дозволяє сказати не “ми передумали
й минулого не було”, а “після нового evidence ми знову admitted цю конструкцію
за такими умовами”.

---

## 5. Мінімальні інваріанти

### I1. Exact subject

Retirement адресує не назву і не “цей старий файл”, а repository identity,
revision, path та content digest. Інакше між review та apply можна прибрати вже
інший artifact.

### I2. Default exclusion

Після retirement subject не входить до default active indexes, context manifests
і normative links. Його історична доступність не змінює цього.

### I3. No implicit resurrection

Старий blob, знайдений через Git history, завжди переносить retirement status.
Він не може стати current precedent лише тому, що його bytes знову прочитані.

### I4. Loss is first-class

`SUPERSEDED` не заявляє безвтратну заміну. Known loss, unmapped concepts,
зламані workflows та несумісні assumptions записуються до apply.

### I5. Retirement is not refutation

Вилучення з active surface не змінює truth value claim'ів автоматично. Якщо є
контрприклад — він адресується окремо. Якщо його немає — mode не називається
`REFUTED`.

### I6. No borrowed authority

Green impact scan або виконаний recipe не роблять рішення легітимним. Хто має
право retire конкретний normative artifact — окрема governance/ownership межа.

### I7. Git is best-effort memory

Shallow clone, source archive, mirror policy, garbage collection або зникнення
remote можуть зробити старі objects недоступними. Tombstone не повинен обіцяти
“завжди можна відновити”; він називає preservation policy і перевірену на момент
receipt retrieval path.

### I8. Composition remains non-transitive

Прибирання кількох конфліктуючих документів не робить автоматично істинним той,
що залишився. Воно лише змінює admission surface. Replacement потребує власного
evidence і warrant.

---

## 6. Схематичний RetirementRecord

Не прийнята schema, лише форма для review:

```yaml
type: RetirementRecord
schema_version: manifesto.retirement.v0

subject:
  repository: s0fractal/manifesto
  revision: <exact-commit>
  path: drafts/OLD-PATTERN.md
  content_digest: sha256:<digest>

mode: SUPERSEDED
reason:
  summary: >
    Inline claims змішували prose та verification eligibility.
  evidence:
    - kind: review-finding
      locator: reviews/<exact-file-or-record>

replacement:
  repository: s0fractal/manifesto
  revision: <exact-commit>
  path: drafts/embedded-claims-poc/
  relation: replaces-active-role

known_loss:
  - compact inline authoring
  - compatibility with legacy settle_gate fixtures

preservation:
  policy: git-history-best-effort
  locator:
    revision: <exact-commit>
    path: drafts/OLD-PATTERN.md
  verified_retrievable_at: <timestamp>

admission:
  default: EXCLUDED
  historical_review: ALLOWED_WITH_STATUS
  normative_use: FORBIDDEN_WITHOUT_READOPTION

authority:
  owner: <declared-owner-or-process>
  warrant: <decision-record>

applied:
  before_tree: <tree-id>
  after_tree: <tree-id>
  receipt: <retirement-receipt-id>
```

Для `WITHDRAWN` replacement може бути відсутній. Для `REFUTED` evidence має
містити counterexample/finding. Для `ARCHIVED` reason не повинен симулювати
негативний verdict. Для `REDACTED` ця публічна форма може бути неприйнятною.

---

## 7. Retirement як executable recipe

### 7.1. Discover — read-only

```text
resolve exact subject
verify revision/path/digest
enumerate active inbound references
enumerate generated artifacts and receipts
enumerate cross-repo references where available
classify references: replace / retire / retain-as-historical / unresolved
produce Impact Report
```

На цьому етапі нічого не видаляється. Важлива властивість: рішення про mode і
loss приймається до того, як active surface змінилася і стало психологічно
зручніше раціоналізувати втрату.

### 7.2. Plan

Plan називає closed set змін:

```text
subjects_to_remove
indexes_to_update
references_to_rewrite
tombstones_to_add
generated_outputs_to_refresh_or_retire
expected_remaining_references
postconditions
rollback / recovery boundary
```

Невирішений active reference робить plan `BLOCKED` або вимагає явного
`known_broken_reference`; він не зникає зі звіту через best effort.

### 7.3. Apply

Apply працює лише проти exact before-tree. Якщо subject digest або reference set
змінився після Impact Report, потрібен новий plan або typed `STALE`.

### 7.4. Verify

Мінімальні postconditions:

- subject відсутній у live path;
- tombstone присутній та schema-valid;
- active indexes не рекламують retired subject;
- кожен declared reference transition відбувся;
- replacement references pinned, якщо replacement заявлено;
- repository checks не стали vacuously green через зникнення fixture scope;
- історичний retrieval перевірений, якщо preservation це обіцяє;
- before/after trees і фактичний changed-path set записані.

### 7.5. Receipt

```text
RetirementReceipt =
  intent_id
  plan_id
  exact before_tree / after_tree
  removed subject ids
  added tombstone ids
  reference-impact result
  postcondition results
  unresolved loss
  actor/tool identities
  timestamp
```

Receipt не містить `wise: true`, `ethically_correct: true` або
`replacement_equivalent: true`, якщо для цього немає окремих claims.

---

## 8. Поведінка моделей і context builders

Controlled forgetting працює лише тоді, коли його бачить споживач.

### 8.1. Default mode

Для звичайної роботи модель отримує:

- active files;
- current indexes;
- tombstones як короткі status records;
- replacement pointers;
- не отримує retired blobs автоматично.

### 8.2. Historical mode

Коли старий artifact потрібен для археології рішення, він завантажується разом
із незнімним envelope:

```text
HISTORICAL ARTIFACT
retirement mode: WITHDRAWN
retired at: <revision>
current admission: EXCLUDED
replacement: <pointer or none>
DO NOT TREAT AS CURRENT PRECEDENT
```

### 8.3. Citation rule

Модель може цитувати retired artifact як історичне джерело, але має переносити
його status. Формулювання “manifesto визначає X” нелегальне, якщо єдине джерело
— withdrawn revision; коректно: “withdrawn revision визначала X; current surface
цього більше не adopts”.

### 8.4. No automatic re-adoption

Схожість із новою задачею, висока retrieval score або краса старої ідеї не є
підставою повернення. Модель може запропонувати Re-adoption Intent, але не
підвищити admission самостійно.

---

## 9. Cross-repository retirement

Сцепка Manifesto, Warrant, Sigma-Glyph, Trinity або інших репозиторіїв робить
локальне видалення потенційно нелокальним переходом.

Impact Report для cross-repo subject має, наскільки practically можливо,
назвати:

```text
source revision
known consumers and their pinned revisions
relation type: developed_with / imports / validates / cites / supersedes
compatibility surface
transferred evidence
known unscanned consumers
```

Видалення authoring pattern із Manifesto не змінює автоматично historical
fixtures Trinity. Superseding Warrant profile не робить старий Sigma-Glyph build
“неіснуючим”. Кожен consumer або пінить historical dependency, або приймає
окремий migration/retirement record.

Цикл tombstones між репозиторіями не є preservation. Хоча б один locator має
вести до реально перевіреного artifact або чесно мати статус `UNAVAILABLE`.

---

## 10. Failure modes

### F1. Deletion laundering

Незручний, але чинний counterargument видаляється під назвою “cleanup”.

**Контроль:** mode, reason, authority, impact report і historical access.

### F2. Refutation laundering

`WITHDRAWN` або `ARCHIVED` показується як доказ хибності.

**Контроль:** truth status і admission status ортогональні.

### F3. Supersession laundering

Replacement називається еквівалентним, хоча переносить лише зручну частину.

**Контроль:** mapping + known loss; “replaces active role” не означає semantic
equivalence.

### F4. Zombie precedent

Модель знаходить old blob у Git і змішує його з current standard.

**Контроль:** tombstone-aware retrieval та historical envelope.

### F5. Tombstone eutrophication

Тисячі verbose tombstones самі забруднюють context.

**Контроль:** маленький indexed ledger; default loader отримує лише релевантні
status summaries, повний record — on demand.

### F6. Vacuous green after deletion

Падаючий fixture або consumer видалений разом із implementation, і CI стає
зеленим через нульовий scope.

**Контроль:** non-empty scope assertions, before/after test inventory, explicit
retirement of obligations.

### F7. False recoverability

Tombstone обіцяє `git show`, але користувач має shallow clone або object уже
недоступний.

**Контроль:** best-effort wording, checked retrieval at receipt time, optional
release/archive preservation для важливих artifacts.

### F8. Forgetting as censorship

Owner authority технічно дозволяє retirement, але стирає dissent із доступної
історії.

**Контроль:** `REDACTED` відокремлений від звичайного retirement; для публічних
нормативних рішень зберігаються reason, dissent pointer та appeal path, якщо це
не суперечить safety/privacy.

### F9. Secret-preserving tombstone

Після security deletion у tombstone лишається filename, quote або unsalted hash,
який розкриває чи підтверджує секрет.

**Контроль:** окремий redaction profile із мінімальною або нульовою публічною
метаданою; security review.

### F10. Retirement becomes the project

Більше часу йде на класифікацію старого, ніж на створення нового.

**Контроль:** retire лише те, що реально конфліктує з active reasoning,
збільшує retrieval ambiguity або підтримує мертвий obligation. Історична
неохайність сама по собі не є достатньою причиною.

---

## 11. Мінімальний rollout

### Phase 0 — Design only

Цей документ. Нічого не retire. Не будувати універсальний garbage collector.

### Phase 1 — Один добровільний specimen

Вибрати один малий, очевидно superseded authoring pattern із:

- точним replacement;
- малим reference graph;
- відсутністю privacy/security вимог;
- живим негативним тестом на zombie precedent.

Спочатку вручну написати Impact Report і RetirementPlan. Лише потім виконати
зміну.

### Phase 2 — Falling consumer

Додати checker, який падає, якщо:

- active index посилається на retired subject як current;
- tombstone не має exact subject/reason/admission;
- `SUPERSEDED` не має replacement або loss;
- historical artifact імпортується без status envelope;
- test scope став порожнім після cleanup.

### Phase 3 — Context policy

Навчити repo-local tooling або agent instructions розділяти default та
historical retrieval. Це момент, коли retirement починає реально покращувати
когнітивну якість, а не лише оформлює Git hygiene.

### Phase 4 — Cross-repo лише після локального specimen

Перевірити один exact consumer link. Не робити repo sweep і не заявляти, що всі
невідомі consumers мігровані.

---

## 12. Кандидатний CLI, не implementation promise

```text
forget inspect <path> --at <revision>
forget plan <impact-report> --mode SUPERSEDED --replacement <locator>
forget apply <plan> --dry-run
forget apply <plan> --write
forget verify <retirement-receipt>
forget history <tombstone> --with-status-envelope
forget readopt <tombstone> --proposal-only
```

Назва `forget` людськи виразна, але canonical records краще називати
`RetirementIntent`, `RetirementPlan`, `RetirementReceipt`, `Tombstone` і
`ReAdoptionRecord`. Це захищає від хибного overclaim “інформацію стерто”.

---

## 13. Відношення до наявних дисциплін manifesto

### [Operator as Hypothesis](OPERATOR-AS-HYPOTHESIS.md)

Вказівка “це старе, видали” є hypothesis про live state та impact, доки exact
subject і references не перевірені. Воля owner'а може бути легітимним мандатом,
але factual передумови retirement все одно розраховуються до дії.

### [Reflexive Verification Bound](RVB-0.1-REFLEXIVE-VERIFICATION-BOUND.md)

Retirement може зменшувати генеративний backlog і conflict surface, але кожен
tombstone/receipt сам додає records. Якщо протокол забуття породжує більше
мета-зобов'язань, ніж прибирає, він програє власній меті.

### [Embedded claims](EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md)

Retirement status, execution receipt і truth status не зливаються. Green
retirement recipe доводить лише, що exact transition відбувся. Він не доводить,
що removed claims були хибними або replacement адекватний.

### Composition laundering

Кілька правильних retirements не роблять залишкову онтологію когерентною.
Композиція active surface потребує окремого review; cleanup не карбує semantic
credit.

---

## 14. Фальсифікатори дизайну

Дизайн треба спростити або відкинути, якщо:

1. моделі з tombstone-aware context не зменшують частоту zombie precedents і
   конфліктуючих стандартів;
2. Impact Report майже завжди дорожчий за наслідки помилкового retirement;
3. tombstones створюють стільки ж retrieval noise, скільки removed artifacts;
4. типи `SUPERSEDED/WITHDRAWN/ARCHIVED/ABANDONED` на практиці систематично
   використовуються як декоративні синоніми;
5. historical envelope не переживає копіювання/citation і status знову губиться;
6. re-adoption настільки дорога, що retirement стає фактично незворотним навіть
   для звичайних non-security artifacts;
7. owner або agents використовують cleanup для приховування dissent/failures;
8. repository checks зеленіють через видалення obligations;
9. Git preservation регулярно недоступне, а зовнішнього archive policy немає;
10. протокол спонукає обслуговувати минуле замість будувати наступне.

---

## 15. Відкриті рішення

1. Один ledger `retirements/` чи tombstone поруч із колишнім path?
2. Чи має tombstone бути Markdown, canonical JSON record або projection обох?
3. Які artifacts достатньо важливі для release/archive preservation поза Git?
4. Хто може retire normative documents, fixtures, reviews і generated evidence?
5. Як переносити retirement status у cross-repo retrieval без спільного runtime?
6. Чи потрібен expiry/review date для `QUARANTINED`?
7. Який мінімальний dissent/appeal record потрібен для governance artifacts?
8. Чи має replacement freshness перевірятися автоматично?
9. Як виміряти когнітивний ефект: менше конфліктів, менше stale citations,
   коротший context, вища точність вибору current standard?

Ці рішення не треба закривати до першого ручного specimen. Реальний retirement
краще покаже, які поля несучі, а які лише церемонія.

---

## 16. Самозастосування

Цей документ сам є `DESIGN_DRAFT`. Він не adopted policy і не ліцензує
видалення жодного файла. Якщо його пізніше supersede, правильний тест дизайну —
чи зможемо ми retire саме цей драфт без втрати причин, меж і фальсифікаторів,
але й без постійного завантаження всіх його bytes у default context.

У цьому сенсі controlled forgetting не протилежне пам'яті. Це здатність пам'яті
мати форму, вагу й напрямок доступу.

---

## 17. Найкоротша форма

```text
forget ≠ erase
forget ≠ refute
forget ≠ hide

forget = exact retirement
       + impact-before-action
       + explicit loss
       + tombstone in live surface
       + historical status on retrieval
       + no resurrection without re-adoption
```

Якісна пам'ять — це не корпус, у якому нічого не зникає. Це корпус, у якому
минуле можна знайти, але воно не отримує права непомітно керувати теперішнім.
