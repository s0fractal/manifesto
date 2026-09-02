# INTENT-VOCABULARY-EVOLUTION-0.1 — інтенти й словник, які можуть змінюватися без тихого переписування себе

**Статус:** extraction draft / не прийнята специфікація / не schema.  
**Джерело extraction:** BOS `feat/observer-relative-assessments@ee4034c` і
Monday-корпус Manifesto.  
**Призначення:** зберегти вузькі інваріанти BOS перед його архівацією, не
переносячи в Manifesto загальний typed decision graph, genesis-машинерію або
онтологію кожної думки.

Цей документ не визначає універсальні `Intent`, `Value`, `Risk` чи `Meaning`.
Він визначає, що треба заявити, аби конкретна scoped-версія такого терма або
інтенту могла змінитися без прихованої підміни значення, доказу чи влади.

Коротко:

> Зберігати треба не незмінний словник цінностей, а перевірні правила його
> легітимної еволюції.

---

## 0. Чому BOS можна прибрати, а ця проблема лишається

BOS намагався зробити першокласними claims, assessments, decisions, actions,
context cuts, trajectories, status axes та їхні relations. Це принесло кілька
корисних розрізнень, але сам загальний граф не отримав зовнішнього consumer'а і
почав платити за власну онтологію більше, ніж за рішення.

Його stop-rule передбачив саме цей випадок: заморозити ontology work, якщо нові
версії schema не додають consumer query, mechanical countervector або зовнішній
decision use case. Архівація BOS виконує цей rule, а не спростовує весь його
зміст.

Проблема, яку варто зберегти, вужча:

```text
actor uses vocabulary V_t
  → forms intent I_t
  → selects or refuses transformations
  → later changes vocabulary or intent

Question:
Which invariants make V_t → V_t+1 and I_t → I_t+1 a legible evolution
rather than silent replacement, semantic collapse, or authority laundering?
```

---

## 1. Monday-корекція: словник не нейтральний

Слово створює quotient: багато різних випадків відображаються в одну назву, а
частина відмінностей перестає бути видимою. Тому помилки виникають симетрично:

- **over-collapse** — назва склеїла випадки з різною downstream dynamics;
- **over-separation** — різні назви приховали спільний invariant pattern.

У виміряному term graph слово `Value` має найбільше сусідніх розрізнень у
корпусі. Але це **діагноз небезпечної змішаності**, не доказ єдиного значення і
не джерело `Value@v1`.

Звідси перший закон цього draft:

> Версія терма — це versioned scoped partition із заявленими збереженими та
> втраченими відмінностями, а не нова редакція універсального definition.

---

## 2. Розрізнення, які не можна схлопувати

### 2.1. Grounding ≠ Claim ≠ Reachability ≠ Intent

- **Grounding** відповідає, чому claim має певний credit.
- **Claim** формулює те, що можна підтримати, спростувати або лишити unsettled.
- **Reachability** обмежує, що з claim'а легітимно випливає у заявленому домені.
- **Intent** називає desired region або напрям пошуку шляху.

Intent сам по собі не є evidence для claim'а і не розширює його forward cone.
Те, що актору потрібно `X`, не робить `X` істинним, досяжним чи дозволеним.

### 2.2. Intent ≠ Decision ≠ Action ≠ Outcome

- intent може існувати без обраного шляху;
- decision вибирає напрям лише в межах названої authority;
- action є фактичною або запропонованою mutation конкретного target;
- outcome є спостереженим наслідком із власним evidence.

Модель може породжувати інтенти, оцінки, claims і proposals. Їхня форма не дає
їм влади змінювати shared state. Матеріальна mutation потребує окремого
authority record і залишає receipt або чесно позначену відсутність receipt.

### 2.3. Subject ≠ Assessment lens

`risk`, `opportunity`, `error`, `growth_signal` і `constraint` — не intrinsic
kinds subject'а. Це attributable lenses щонайменше над:

```text
subject
  + assessed_by
  + stakeholder
  + objective
  + context_cut
  + horizon
  + evidence / assumptions
  → assessment
```

Одна умова може бути одночасно risk для одного stakeholder'а й opportunity для
іншого. Спільний subject не дозволяє deduplicate такі records, а вибір одного з
них як reason for action не робить цю lens універсально істинною.

### 2.4. Value-term ≠ observed invariant ≠ normative authority

Monday запропонувала продуктивну, але поки speculative операціоналізацію:
цінності можуть бути властивостями, які агент систематично намагається зберігати
під широким класом transformations.

Навіть якщо pattern спостережено, з нього не випливає:

- що агент назвав би його своєю цінністю;
- що invariant морально правильний;
- що він має перевагу над іншими invariants;
- що хтось уповноважений нав'язати його іншому actor'у;
- що та сама лексема `Value` має цей сенс в іншому домені.

Отже `Value@v1` може бути scoped stipulation або hypothesis. Сам суфікс версії
не підвищує її до `DOMAIN_ADEQUATE`, `EMPIRICALLY_GROUNDED` чи
`NORMATIVELY_ADOPTED`.

### 2.5. Decoder compatibility ≠ semantic continuity

Стара schema може лишатися декодовною після появи нової. Це доводить лише
syntactic recoverability старих bytes. Воно не доводить, що:

- нова версія зберігає значення старої;
- старі records можна використати як current reasons;
- `v2` є безвтратним successor `v1`;
- однакове поле має однаковий domain і authority effect.

---

## 3. Мінімальні інваріанти еволюції

### I1. Scoped identity

Кожна терм-версія називає owner, domain, version і exact bytes. Голий `Value`
не є portable identity.

### I2. Immutable historical meaning

Після використання `Term@v1` його bytes і stipulation не редагуються заднім
числом. Зміна створює `Term@v2` та transition record.

### I3. Explicit partition delta

Transition заявляє:

- які distinctions v2 зберігає;
- що v2 розділяє з того, що v1 склеював;
- що v2 об'єднує з того, що v1 розрізняв;
- які known cases більше не класифікуються;
- які нові cases стали representable.

Без цього `supersedes` є лише авторською заявою про назву successor'а.

### I4. Illegal casts survive versioning

Нова версія не може мовчки легалізувати старий illegal cast. Наприклад:

```text
Intent     ⇏ Evidence
Assessment ⇏ IntrinsicProperty
Proposal   ⇏ Decision
Decision   ⇏ Truth
ObservedInvariant ⇏ NormativeValue
Decodable ⇏ SemanticallyCompatible
Supersedes ⇏ EquivalentTo
```

Якщо version transition хоче змінити одну з цих меж, це окремий explicit claim
із falsifier'ом та authority, а не побічний ефект schema migration.

### I5. Attribution completeness

Intent або assessment, що претендує на portable use, називає actor/assessor,
stakeholder, objective, bounded source context і horizon. Невідоме лишається
`UNKNOWN`; validator не підставляє автора, beneficiary, мету чи час за
замовчуванням.

### I6. Plurality without forced reconciliation

Кілька несумісних intents або assessments можуть співіснувати. Зведений view
не має права перетворити plurality на consensus, вибрати winner або створити
середній scalar `value`, якщо цього не зробив названий authority/process.

### I7. Authority is orthogonal

Епістемічна, формальна, емпірична та governance-осі не утворюють одну шкалу.
Зокрема:

```text
FORMALIZED
KERNEL_DERIVED
COUNTERMODELED
IMPLEMENTATION_CONFORMANT
DOMAIN_ADEQUATE
EMPIRICALLY_GROUNDED
NORMATIVELY_ADOPTED
```

можуть змінюватися незалежно. Ні compiled schema, ні green validator, ні model
agreement не створюють adoption.

### I8. Context and horizon bind use

Історичний context cut не “протухає” як опис минулого, але його придатність як
current reason може завершитися. Freshness є projection над source commitment,
validity interval та later refutation/supersession; поле `current` не може саме
себе зробити актуальним.

### I9. Evolution is governed by meta-invariants

Складна система може змінювати власні intents і values. Continuity не вимагає
заморозити їх назавжди; вона вимагає заявити meta-invariants переходу. Candidate
family:

- не фальсифікувати provenance;
- не стирати external commitments без disposition;
- не розширювати authority мовчки;
- не приховувати known loss;
- не видавати нову назву за доказ нової adequacy;
- лишати оскаржуваний шлях до predecessor і competing branch.

Цей список — proposal, не універсальна моральна конституція.

### I10. Active attention is bounded

Addressability не означає, що кожен record має входити в default context.
Versioned terms, historical intents і losing branches можуть бути доступними в
Git/history, але excluded із current working set через controlled forgetting.

Новий kind або axis допускається лише після конкретного counterexample, який
показує втрату потрібної семантики в наявній формі. “Було б красиво мати” не є
consumer.

---

## 4. Candidate records — форма для review, не schema

### 4.1. TermRevision

```yaml
type: TermRevision
schema: manifesto.term-revision.v0

term: Value
version: 1
owner: <canonical-owner>
domain: <bounded-domain>
status:
  formalized: false
  domain_adequate: unknown
  empirically_grounded: unknown
  normatively_adopted: false

stipulation: <what this owner means here>
discriminators:
  - <case that must remain distinct>
forbids:
  - ObservedInvariant => NormativeValue

source:
  revision: <exact-revision>
  digest: sha256:<digest>
```

Це ілюстрація форми. Вона **не реєструє** `Value@v1` і не робить Manifesto
власником значення `Value` для інших протоколів.

### 4.2. IntentRecord

```yaml
type: IntentRecord
schema: manifesto.intent.v0

actor: <attributed-actor>
target_region: <desired condition, not asserted fact>
context_cut: <bounded supplied world>
horizon: <bounded | open | unknown>
constraints_or_invariants:
  - <scoped term revision or explicit prose>
assumptions:
  - <claim/hypothesis reference>
authority_effect: none
```

Intent може бути корисним без claim-verdict. Його structured form потрібна для
відстеження напряму та змін, а не для позичання verification credit.

### 4.3. VocabularyTransition

```yaml
type: VocabularyTransition
schema: manifesto.vocabulary-transition.v0

from: <TermRevision identity>
to: <TermRevision identity>
relation: supersedes-active-role
preserved_invariants: []
partition_split: []
partition_merge: []
known_loss: []
newly_representable: []
illegal_cast_changes: []
counterexamples: []
authority: <decision or null>
```

Якщо `authority` відсутня, transition може існувати як proposal, але не змінює
default admission.

---

## 5. Що має падати

Цей draft вартий schema лише тоді, коли з'явиться consumer, для якого порушення
межі має спостережний наслідок. Мінімальний майбутній gate повинен відмовляти:

1. ті самі `term + owner + version` із різними bytes;
2. `v2`, що заявляє supersession без partition delta і known loss;
3. intent, використаний як evidence або authority;
4. intrinsic `risk/opportunity/value` без attribution і domain;
5. migration, що змінює illegal cast без окремого claim/decision;
6. semantic compatibility, виведену лише з decoder compatibility;
7. status promotion без названого evidence чи governance act;
8. current view, що мовчки deduplicate plural assessments;
9. retired term, повернений у default context без re-adoption;
10. generated glossary, чий source closure змінився.

До такого consumer'а документ лишається prose design constraint і не отримує
власну ontology implementation.

---

## 6. Source → invariant → disposition

| Source | Витягнутий invariant | Disposition після BOS |
|---|---|---|
| BOS §1, §11 | proposal/intent не створює authority; material action потребує зовнішнього акту | preserved here; authority implementation лишається Warrant/Git-owner boundary |
| BOS §7.3, observer-relative branch | assessment lens не є intrinsic property; assessor, stakeholder, objective, cut, horizon розділені | preserved as I5–I6; BOS assessment schema не переноситься |
| BOS §7.1 | status не є одним scalar | preserved as I7; конкретний BOS registry не переноситься |
| BOS §9 | semantic relations contestable; `supersedes` не дорівнює equivalence або current selection | preserved as I3–I4 |
| BOS §13 | freshness є projection, не self-asserted field | preserved as I8 |
| BOS §15 | completeness завжди відносна до declared universe | inherited by any future generated term/intent view |
| BOS §21 | ontology росте лише після consumer counterexample | preserved as I10 і stopping rule |
| Monday 0003 | Intent задає desired region, не доказ | preserved as §2.1 |
| Monday 0005 | values можуть проявлятися як persistent constraints | retained as Speculative, not definition |
| Monday 0008 | naming creates quotient; over-collapse/over-separation | preserved as §1 and partition delta |
| Monday 0012 | важливі правила admissible value evolution, а не frozen list | preserved as I9 |
| Manifesto glossary work | scoped stipulations, illegal casts, orthogonal credit ledger | canonical successor direction |
| CONTROLLED-FORGETTING-0.1 | historical availability ≠ active admission | preserved as I10 and transition disposition |

Exact BOS source points:

- active `main` before retirement: `e9b8ab775aef18542ff37842f6fa67e7020161f4`;
- unmerged observer-relative research head:
  `ee4034c16866db68d2adcbf439c46d49c357a655`;
- the latter passed `BOS-VALIDATE: ALL PASS` and 34/34 unit tests during this
  extraction; that establishes bounded validator behaviour, not adoption or
  semantic adequacy.

---

## 7. Deliberately not transferred

- BOS as a global source of portfolio meaning;
- one universal graph of every claim, thought, risk, decision and trajectory;
- the full BOS atom-kind and scope registries;
- self-contained genesis governance machinery;
- the assumption that making a distinction first-class means loading it into
  every context;
- `Value`, `Meaning`, `Intent` or `Risk` as universally fixed definitions;
- the BOS validator as a Manifesto dependency;
- any adoption credit from the unmerged observer-relative branch.

The loss is real: Manifesto will not offer BOS's general query surface or
reconstruct every actor trajectory. The retained result is smaller: a set of
constraints against silent semantic and authority mutation.

---

## 8. Stopping rule

Do not implement `manifesto.term-revision.v0`, `manifesto.intent.v0` or
`manifesto.vocabulary-transition.v0` merely because candidate shapes now exist.

Implementation begins only when one real operation needs to distinguish two
versions or two lenses and current Manifesto artifacts cannot express the
failure. The first implementation must include that counterexample, a negative
mutation, an exact owner, and a bounded consumer.

Until then, the better memory is this compact extraction plus the retired BOS
history — not a replacement BOS hidden inside Manifesto.
