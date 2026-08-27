# FLOW-0.1 — Потоки в гетерогенних просторах станів

**Статус:** speculative working model  
**Версія:** 0.1 → 0.1-revised  
**Призначення:** зафіксувати робочий словник і набір гіпотез; породжувати контрприклади, експерименти та кращі формулювання. Не перетворюватися на нормативну архітектуру.

> **НЕ НОРМАТИВНО. НЕ Є ТЕОРІЄЮ. НЕ ЗЛИВАТИ АВТОМАТИЧНО В HSP, SIGMA-GLYPH ЧИ TRINITY.**

---

## Структура документа

- **Part I — Descriptive Vocabulary** (§1–§11): що фіксується без додаткових онтологічних припущень.
- **Part II — Hypotheses** (§12–§18): спекуляції, які можуть бути хибними.
- **Part III — Methodology, Risks & Experiments** (§19–§27): як перевіряти, чому не довіряти, що робити далі.
- **Appendix A — Concrete Minimal Example**
- **Appendix B — Anti-Example**

---

# PART I — DESCRIPTIVE VOCABULARY

## 1. Minimal Formal Core

Навіть якщо повної формалізації немає, можна виділити ядро, яке приймається без додаткових метафор:

$$
D = (X, \mathcal{O}, A, C, I, B, 	au)
$$

де:

- $X$ — множина допустимих станів;
- $\mathcal{O}$ — множина операцій;
- $A(x) \subseteq \mathcal{O}$ — допустимі операції в стані $x$;
- $C$ — constraints (предикати над $X 	imes \mathcal{O} 	imes T$);
- $I$ — invariants (предикати над $X$, замкнені відносно допустимих переходів);
- $B$ — boundary (інтерфейс між внутрішнім і зовнішнім);
- $	au$ — temporal domain (часова структура).

Усе інше в документі — розширення цього ядра.

---

## 2. State Space

State space не зобов'язаний бути геометричним. Він може бути графом, частковим порядком, автоматом, множиною термів, probability space, manifold, causal graph, constraint system, ledger, ontology або композицією кількох різних просторів.

Тому слово **topology** тут використовується обережно: частина просторів може не мати топології в строгому математичному сенсі.

---

## 3. Boundary / Interface

Boundary $B$ — first-class об'єкт, а не метафора:

$$
B = (S_{in}, S_{out}, M, F)
$$

де:

- $S_{in}$ — стани, які належать домену;
- $S_{out}$ — стани поза доменом, але з якими можливі взаємодії;
- $M$ — mapping дозволених впливів (що може перетинати межу);
- $F$ — фільтр інформації (що спостерігається ззовні).

Без boundary поняття "transfer" (§5) не має сенсу: transfer — це зміна стану зі збереженням деякої властивості при перетині $B$.

---

## 4. Flow

Flow — зміна стану відповідно до деякого transition law.

У детермінованому випадку:

$$
x_{t+1} = T(x_t, a_t, e_t)
$$

У стохастичному:

$$
x_{t+1} \sim P(X_{t+1} \mid x_t, a_t, e_t)
$$

У continuous domain:

$$
\dot{x} = F(x, t)
$$

Але жоден із цих формалізмів не є універсальним. Navier–Stokes, diffusion, reaction–diffusion, network flow тощо — можливі **локальні flow laws**, а не фундаментальні метафори для всього.

---

## 5. Admissible Transitions

Не кожний математично можливий перехід є допустимим.

$$
A(x) = \{a \mid C_i(x, a) \leq 0 \; orall i\}
$$

Тоді система має не просто trajectory, а **простір допустимих майбутніх**:

$$
Reach(x)
$$

Constraints змінюють його форму:

$$
Reach(x \mid C_1) \subseteq Reach(x)
$$

Resource constraint:

$$
Reach(x \mid r=10) \subseteq Reach(x \mid r=100)
$$

Authority constraint може поводитися інакше: $a \notin A(x)$ доки не з'явиться певний warrant.

Таким чином інформація може змінювати поведінку системи не через зміну фізичного стану, а через **зміну множини admissible transitions**.

---

## 6. Constraint

Constraint — правило, що обмежує допустимі стани або переходи.

Загальна форма:

$$
C(x, a, t, \text{context}) \leq 0
$$

Відокремлюємо:

```
physical constraint
resource constraint
logical constraint
protocol constraint
authority constraint
risk constraint
semantic constraint
policy constraint
```

Вони можуть мати схожий операційний ефект — "цей перехід зараз неможливий" — але абсолютно різну природу. Operational similarity не означає ontological identity.

### 6.1 Soft Constraints

Не всі обмеження бінарні. **Soft constraint** відображає:

$$
C_{soft}: X \times \mathcal{O} \rightarrow [0, \infty)
$$

де $0$ = жорстко заборонено, а скінченні значення = допустимо з ціною. Це дозволяє говорити про graceful degradation і про price (§8) як про вартість порушення, а не лише як про обмінний курс.

---

## 7. Invariant

Інваріант не є абсолютною властивістю об'єкта. Коректніша форма:

$$
I(x) \text{ invariant under } F \text{ within } B \text{ assuming } A
$$

де:

- $F$ — сімейство трансформацій;
- $B$ — boundary;
- $A$ — assumptions.

Наприклад, величина $R_{total}$ може бути conserved under `transfer`, але не under `mint`, `burn`, `external grant`, `decay`.

Тому запис "ATP conserved" недостатній. Треба: "$R_{total}$ conserved under transformation family $F_{transfer}$ inside boundary $B$."

---

## 8. Resource-like Structures

Назви `budget`, `compute`, `attention`, `risk-capacity` не є універсальними сутностями. Замість цього описуємо їхню **операційну структуру**:

$$
R = (Q, C, T, P, E, \tau, B)
$$

де:

- $Q$ — quantity/state;
- $C$ — admissibility constraints;
- $T$ — transition/accounting law;
- $P$ — production/destruction rules;
- $E$ — exchange/transfer rules;
- $	au$ — temporal behavior;
- $B$ — scope/boundary.

Можливі властивості:

```
bounded, conserved, consumable, replenishable, transferable,
divisible, fungible, decaying, borrowable, mintable,
local, global, path-dependent, reversible, non-reversible
```

Тоді різні ресурси можуть мати спільні властивості, не будучи одним поняттям.

---

## 9. Price

Price не слід автоматично ототожнювати з budget/resource.

Resource:

$$
r_{t+1} = r_t - \text{cost}(a_t)
$$

Price радше визначає mapping:

$$
\text{cost}(a, t) = p(a, t) \cdot q(a)
$$

Price може бути:

- exchange relation;
- marginal cost;
- shadow price;
- dual variable;
- context-dependent transformation coefficient;
- **вартість порушення soft constraint**.

Одна й та сама дія може мати різну resource cost при різних prices.

---

## 10. Temporal Domains

Різні домени мають різний час. Wall-clock, logical (Lamport), event-driven, causal — це не різні "реалізації" одного часу, а різні **темпоральні онтології**.

Temporal domain:

$$
\tau = (T, \prec, \lambda)
$$

де:

- $T$ — носій (множина часових міток);
- $\prec$ — порядок (частковий або повний);
- $\lambda$ — функція "тривалості" (може бути undefined).

При translation між domains зміна темпоральної онтології — це не просто дискретизація, а зміна самої структури flow.

---

## 11. Quantization

Не всі flows є continuous. У деяких domains переходи принципово дискретні:

```
unsigned → signed
draft → ratified
alive → archived
uncommitted → committed
unresolved → resolved
```

Стан $0.73 \; \text{ratified}$ може взагалі не мати семантики.

Domain повинен декларувати:

```
continuous / discrete / hybrid / event-driven / quantized
```

Translation між domains не повинна мовчки перетворювати discrete transition на continuous scalar або навпаки.

---

## 12. Multi-space Systems

Реальна система може одночасно існувати в кількох різних state spaces:

$$
x_A \in X_A, \quad x_B \in X_B, \quad x_C \in X_C
$$

Наприклад: semantic state, resource state, authority state, physical state, epistemic state, social state.

Сукупний стан $S = (x_A, x_B, x_C, \ldots)$, але це не означає, що існує одна природна vector space.

Динаміка може бути coupled:

$$
\dot{x}_A = F_A(x_A, x_B)
$$

$$
\dot{x}_B = F_B(x_B, x_C)
$$

$$
x_C^{t+1} = T_C(x_C^t, x_A^t)
$$

Flow в одному домені деформує flow в іншому.

---

## 13. Cross-space Translation

Для двох domains $D_A, D_B$ може існувати mapping:

$$
\phi_{A \rightarrow B}: X_A \rightharpoonup X_B
$$

Він може бути partial, lossy, irreversible, context-sensitive, resource-expensive, non-unique.

Основна одиниця перевірки translation — не схожість значень, а **збереження заявлених властивостей**:

$$
I_A(x) \Rightarrow I_B(\phi(x))
$$

або:

$$
C_A(x, a) \Rightarrow C_B(\phi(x), \phi(a))
$$

для певного action context.

Універсальним стає не значення ("resource X ↔ resource Y"), а, можливо:

```
ConsumedBy, BoundedBy, TransferableUnder, AdmissibleWhen,
ConservedUnder, EnabledBy, ForbiddenBy
```

### 13.1 Graceful Untranslatability

Translator повинен уміти сказати не просто "не вдається", а видавати структурований звіт:

```
Translation report:
  φ: partial mapping
  Preserved: {ordering, action admissibility}
  Lost: {distance, resource magnitude}
  Introduced: {approximation error}
  Confidence: [0,1]
  Alternative: {φ', φ''} або "none found"
```

Failure to translate — це **first-class результат**, а не поразка.

---

## 14. Translation Loss

Будь-який cross-domain bridge повинен потенційно описувати:

```
preserved, lost, introduced, approximated,
unknown, non-invertible, context-dependent
```

Наприклад, $\phi_{A \rightarrow B}$ може зберігати ordering, але втрачати distance; або зберігати action admissibility, але втрачати resource magnitude.

Тому $\phi^{-1}(\phi(x)) = x$ не є загальною вимогою.

---

# PART II — HYPOTHESES

> Усе, що нижче, — свідомі спекуляції. Вони можуть бути хибними.

---

## 15. Information as Transformation Potential

**Центральна спекулятивна теза FLOW-0.1:**

> Інформаційний стан набуває операційного значення через те, як він змінює простір можливих трансформацій.

**Уточнення щодо тавтологічності:** зміна $Reach(x)$ сама по собі ще не є інформацією. Камінь падає — його $Reach$ змінюється, але він не "отримує інформацію". Різниця:

- **Фізична зміна** змінює $Reach(x)$ через зміну самого $x$.
- **Інформаційна зміна** змінює $Reach(x)$ без зміни фізичного стану — через зміну $A(x)$, $C$ або $I$.

Приклади:

```
Warrant:
  before: action ∉ admissible
  after:  action ∈ admissible

Knowledge:
  before: policy selects A
  after evidence E: policy selects B

Commitment:
  before: futures = {A,B,C,D}
  after:  futures = {C,D}
```

Тому інформація трактується як те, що:

$$
Reach(x) \rightarrow Reach'(x)
$$

або:

$$
P(\text{Trajectory}) \rightarrow P'(\text{Trajectory})
$$

**але лише коли зміна відбувається через зміну constraints, а не через зміну фізичного стану.**

---

## 16. Operational Meaning

Розширена робоча форма:

$$
\boxed{
\text{operational meaning}
=
\text{position in a space of possible transformations}
}
$$

Для інформації питання стає не "що означає цей символ?", а "які операції він дозволяє, забороняє, змінює або робить можливими?"

Це дозволяє мати **family resemblance** замість universal ontology.

Наприклад, `budget`, `trust`, `authority`, `compute` можуть мати частково перекривні структурні властивості без спільної сутності.

---

## 17. Player

**Робоче визначення:**

> **Player — локус endogenous control, внутрішній стан або policy якого причинно впливають на його власний розподіл майбутніх траєкторій, і який має representational capacity (стан, що функціонально відіграє роль моделі ситуації).**

Для policy:

$$
a_t = \pi(x_t, h_t)
$$

Якщо:

$$
\text{Trajectory}(do(\pi=\pi_1)) \neq \text{Trajectory}(do(\pi=\pi_2))
$$

то policy має causal influence на trajectory.

**Уточнення:** за цим визначенням складний термостат може бути borderline player, але він не має representational capacity у сенсі моделі альтернатив. Це не вимагає метафізичної свободи волі.

---

## 18. Degrees of Agency

Agency — не binary property. Груба шкала:

```
object
    trajectory externally determined

reactive system
    fixed response law

agent
    selects among admissible transitions

player
    internal selection affects own trajectory
    + representational capacity

reflexive player
    can modify its own policy

self-modifying player
    can modify mechanisms that modify policy
```

Це descriptive taxonomy, а не formal hierarchy.

---

## 19. Determinism, Stochasticity, Nondeterminism

### 19.1 Determinism ≠ absence of agency

Детермінована система $x_{t+1} = T(x_t, \pi(x_t))$ може бути player, якщо зміна $\pi$ контрфактично змінює trajectory.

### 19.2 Stochasticity

При $x_{t+1} \sim P(X \mid x_t, a_t)$ player може не контролювати outcome, але змінювати distribution:

$$
P(\text{Trajectory} \mid \pi_1) \neq P(\text{Trajectory} \mid \pi_2)
$$

Agency — здатність деформувати $P(\text{future})$, а не обов'язково вибирати конкретне future.

### 19.3 Чотири різні "недетермінованості"

1. **Epistemic uncertainty** — transition deterministic, але observer не знає повного state.
2. **Chaos** — transition deterministic, але $\delta x_0 \ll 1$ породжує $\delta x_t \gg 1$.
3. **Stochasticity** — transition law сам є probability distribution.
4. **Underspecified admissibility** — існує кілька legal actions $A(x) = \{a_1, a_2, \ldots\}$, а policy визначає, яку буде використано. Це не те саме, що randomness.

---

## 20. Reflexive Trajectory

Для reflexive player існують щонайменше два взаємопов'язані flows:

State flow:

$$
x_t \rightarrow x_{t+1}
$$

Policy flow:

$$
\pi_t \rightarrow \pi_{t+1}
$$

Наприклад:

$$
x_{t+1} = F(x_t, \pi_t, e_t)
$$

$$
\pi_{t+1} = G(\pi_t, x_t, \text{Evidence}_t)
$$

Історія агента впливає на механізм, який породжує його наступні рішення. Кандидат на формалізацію **trajectory-conditioned attractor** для довгоживучих процесів.

---

## 21. Attractors

Attractor у FLOW-0.1 використовується в широкому робочому сенсі. Необхідно окремо перевіряти, чи конкретна система дійсно допускає математично коректне поняття attractor.

**Застереження:** це психологічна/епістемічна метафора, а не динамічна система, доки не доведено існування відповідної метрики.

Інтуїція:

```
history → vocabulary → preferred decompositions
       → preferred tools → repeated action patterns
       → stronger history
```

утворює feedback loop. Для LLM-agent trajectory:

$$
h_t \rightarrow \pi_t \rightarrow a_t \rightarrow h_{t+1}
$$

Такий loop може породжувати specialization, competence, blind spots, vocabulary lock-in, Goodhart-like behavior.

---

## 22. Continuity vs Blindness

Тяглість є одночасно ресурсом і ризиком:

```
continuity → accumulated competence
continuity → attractor reinforcement
```

Два ортогональні механізми:

### Lineage process
Отримує: history, vocabulary, prior hypotheses, prior failures, reviews, receipts — і продовжує trajectory.

### Cold reconstruction
Отримує максимально raw: artifact, observations, tests, measurements, problem — без старого interpretive vocabulary.

Різниця між ними сама стає observation.

---

## 23. Artifact Continuity ≠ Interpretive Continuity

Варто розділяти $\text{ArtifactContinuity}$ і $\text{InterpretiveContinuity}$.

Перше бажано зберігати: code, measurements, provenance, experiments, failed hypotheses, receipts.

Друге варто періодично скидати: metaphors, favored ontology, "big picture", canonical vocabulary.

Це дозволяє **перечитувати ті самі факти так, ніби попередньої теорії не існувало**.

Робоча назва: **epistemic rebase**.

---

## 24. Multi-player Systems

Нехай існують players $P_1, \ldots, P_n$ з різними spaces $X_1, \ldots, X_n$ і policies $\pi_1, \ldots, \pi_n$.

Спільна дія не вимагає $X_1 = X_2$ або $\pi_1 \approx \pi_2$. Достатньою може бути локальна compatibility relation:

$$
K_{ij}(a, \text{context})
$$

Systems можуть мати несумісні внутрішні representations, але домовитися про boundary conditions для конкретної взаємодії.

---

## 25. Coupling

Два flows можуть бути coupled без прямого translation.

Наприклад:

$$
\dot{x} = F(x, r)
$$

$$
\dot{r} = G(r, a)
$$

Resource field впливає на state trajectory, але не означає state.

**Застереження:** аналогія з ferrofluid допустима лише структурно — "зовнішнє поле змінює доступну dynamics середовища". Не слід робити висновок, що соціальні або інформаційні системи "насправді є рідинами".

---

## 26. Flow Law Library

Можливо, універсальним шаром стане не universal state representation, а бібліотека relation primitives:

```
BoundedBy(...)
ConservedUnder(...)
ConsumedBy(...)
ProducedBy(...)
TransferredBy(...)
EnabledBy(...)
ForbiddenBy(...)
MonotoneUnder(...)
InvariantUnder(...)
ReversibleWithin(...)
DecaysWith(...)
CoupledTo(...)
TranslatedBy(...)
LosesUnder(...)
QuantizedBy(...)
ReachableUnder(...)
```

Конкретні domains інстанціюють частину цих відношень.

### 26.1 Sorts (Typing)

Щоб ці primitives були більше, ніж слова, потрібні сорти:

```
Sorts:
  State, Action, Observation, Policy, Boundary,
  Time, Evidence, Warrant, Constraint, Invariant,
  Resource, Player, Domain, Translation
```

Тоді $\text{ConservedUnder}(x, F)$ — це well-formed предикат, який можна перевірити на коректність типів, а не довільна фраза.

---

## 27. Candidate Universal Layer

**Найсильніша спекулятивна теза:**

> Якщо універсальний informational layer взагалі існує, він може бути ближчим до алгебри constraints, transformations і preserved relations, ніж до універсальної онтології сутностей.

Тобто не:

$$
\text{UniversalMeaning}(x)
$$

а:

$$
\text{Structure}(
  \text{Transformations},
  \text{Constraints},
  \text{Invariants},
  \text{Mappings}
)
$$

---

## 28. Game Transition

Цікавіший випадок — коли player може перейти не просто між states, а між **games**:

$$
G_A \rightarrow G_B
$$

Наприклад: змінити ontology, governance, accounting unit, evaluator, policy architecture.

Тоді виникає meta-flow:

$$
(x, G)_t \rightarrow (x, G)_{t+1}
$$

Це вже не рух усередині fixed rules. Це рух, що може змінити самі rules.

### 28.1 Constraint on Self-Modification

Self-modification не повинна автоматично означати unconstrained mutation.

Можливе $G_t \rightarrow G_{t+1}$ лише якщо:

```
I_identity(G_t, G_{t+1}) — збереження ідентичності
Budget_mutation ≥ Cost(G_t → G_{t+1})
Warrant(G_t → G_{t+1}) = true
```

---

# PART III — METHODOLOGY, RISKS & EXPERIMENTS

---

## 29. Relation to Other Frameworks

FLOW-0.1 не повинен змушувати інші системи перейменовувати свої поняття або підганяти evaluator під універсальну метафору.

Навпаки, конкретні фреймворки можуть виступати falsification substrate для FLOW hypotheses.

**Позикові імена:** коли використовуються терміни на кшталт "ATP" або "Warrant", це — **позикові імена** ($R_{example}$, $W_{example}$), які не несуть онтологічних зобов'язань. Вони служать лише для конкретності прикладів.

---

## 30. Risks

### 30.1 Vocabulary Laundering
Старі концепції перейменовуються в нові терміни без нового змісту.

### 30.2 Physics Cosplay
Математичні слова з фізики використовуються без відповідної структури.

### 30.3 Universalization Bias
Локальна закономірність оголошується універсальною.

### 30.4 Metaphor Lock-In
`flow`, `field`, `attractor` починають визначати, які observations модель взагалі помічає.

### 30.5 LLM Convergence Artifact
Кілька моделей погоджуються не через істинність структури, а через спільні training priors.

### 30.6 Tautological Semantics
"Meaning is transformations" стає невразливою тезою, бо все заднім числом описується як transformation.

### 30.7 Methodological Risk: Universalization Through Metaphor
"Заборонені shortcuts" (усе є енергією, flow, геометрією тощо) — це не стільки помилки, скільки **методологічний ризик**: спокуса пояснити різне одним і тим самим інструментом, втрачаючи distinctions.

---

## 31. Falsificators

FLOW framing має втрачати довіру, якщо:

1. Він не породжує нових testable distinctions.
2. Переклад у flow vocabulary систематично втрачає більше, ніж пояснює.
3. Незалежні cold-start analyses природніше відновлюють іншу структуру.
4. `constraint`, `invariant`, `flow`, `player` неможливо визначити без постійних ad hoc exceptions.
5. Конкретні формальні моделі не дають нічого понад звичайну operational semantics / control theory.
6. Різні domains вимагають настільки несумісних primitives, що "універсальний layer" стає порожньою множиною загальних слів.
7. Модель генерує красиві аналогії, але вони не змінюють predictions або experiment design.

---

## 32. Anti-Example

**Система, де FLOW framing дає trivial або misleading result:**

Квантова заплутаність. Два ентангльовані частинки $A$ і $B$.

- "Стан" $A$ не є локальним — він не належить $X_A$ окремо.
- "Transformation" над $A$ — це не операція над підсистемою, а глобальна зміна стану $A \otimes B$.
- $Reach(x_A)$ не визначається незалежно від $x_B$.
- Boundary $B$ між $A$ і $B$ пропускає кореляції, які не є "transfer" у жодному класичному сенсі.

FLOW vocabulary тут або мовчить, або вводить в оману, намагаючись застосувати "state", "flow" і "transfer" до контексту, де ці поняття вимагають радикальної переінтерпретації.

**Висновок:** FLOW-0.1 не претендує на універсальність. Він претендує на корисність для певного класу систем.

---

## 33. Experiments

### EXP-001 — Vocabulary Independence
Дати кільком моделям одну задачу без слів: flow, topology, invariant, resource, ontology, translation. Подивитися, чи реконструюють вони схожі primitives.

### EXP-002 — Same Artifact, Different Games
Взяти один artifact і змінити лише action context. Перевірити, які semantics залишаються invariant, а які змінюються.

### EXP-003 — Resource Isomorphism
Взяти дві системи з різними назвами resource. Спробувати побудувати mapping лише через operational laws. Перевірити: що зберігається, де mapping ламається.

### EXP-004 — Deterministic Agency
Побудувати повністю deterministic player. Контрфактично змінювати policy. Виміряти зміну reachable trajectories без stochasticity.

### EXP-005 — Attractor Formation
Декілька однакових моделей стартують з однакової задачі, але різних ранніх histories. Через $N$ циклів перевірити: vocabulary divergence, problem decomposition, tool choice, blind spots, cross-trajectory reconstruction.

### EXP-006 — Epistemic Rebase
Порівняти lineage agent vs cold-start agent на одному накопиченому artifact set. Ціль — вимірювати не "хто правильніший", а **які distinctions бачить лише один із режимів**.

### EXP-007 — Boundary Violation
Система з чітко визначеним $B$. Намисно порушити boundary (змінити $M$ або $F$). Виміряти, які invariants руйнуються негайно, а які — з запізненням. Це тест на те, чи boundary є дійсно first-class.

---

## 34. Open Questions

1. Чи існує мінімальний набір transformation primitives, достатній для широкого класу domains?
2. Чи можна математично визначити translation loss без universal metric?
3. Чи є agency властивістю system або relation між subsystem та boundary?
4. Як вимірювати endogenous control?
5. Як відрізнити learned attractor від genuine specialization?
6. Як визначити identity при policy self-modification?
7. Чи є invariant preservation достатнім для semantic translation?
8. Які properties повинні зберігатися лише action-contextually?
9. Чи можна визначити "same game" без спільної ontology?
10. Коли зміна representation є просто coordinate change, а коли — зміною самої game?
11. Чи існують універсальні conservation-like laws для informational systems?
12. Чи є "untranslatable" first-class semantic result?
13. Як працює quantization при переході між discrete і continuous domains?
14. Чи можна формалізувати `price` як relation між flows, не редукуючи все до economics?
15. Чи можна отримати emergent player з системи, компоненти якої окремо players не є?

---

## 35. Найкоротша форма

Якщо прибрати всю "потокологію", залишається:

$$
\boxed{
\text{State}
+
\text{Allowed transformations}
+
\text{Constraints}
+
\text{Invariants}
+
\text{Boundary}
}
$$

Для interaction між domains:

$$
\boxed{
\text{Mapping}
+
\text{Preservation}
+
\text{Loss}
+
\text{Temporal ontology}
}
$$

Для player:

$$
\boxed{
\text{Internal policy}
\rightarrow
\text{change in future trajectory}
}
$$

Для reflexive player:

$$
\boxed{
\text{trajectory}
\leftrightarrow
\text{policy evolution}
}
$$

А можлива загальна теза:

> **Інформаційні системи можна порівнювати не через спільні назви станів, а через структуру допустимих трансформацій, обмежень, меж і того, що ці трансформації зберігають.**

І ще спекулятивніше:

> **Meaning may be less a property of a representation than a position within a structured space of possible transformations.**

Оце — центр FLOW-0.1. Усе інше — кандидати на те, щоб бути красиво роз'їбаними наступними експериментами.

---

# APPENDIX A — Concrete Minimal Example

## Три домени: Compute, Attention, Budget

### Domain C (Compute)
- $X_C = \{(c, t) \mid c \in \mathbb{R}_{\geq 0}, t \in \mathbb{N}\}$ — доступні обчислювальні одиниці та часові тики.
- $\mathcal{O}_C = \{\text{run}, \text{idle}, \text{delegate}\}$
- $A_C(x) = \{\text{run} \mid c \geq \text{cost}(\text{run})\} \cup \{\text{idle}, \text{delegate}\}$
- $I_C$: $c$ conserved under `delegate` within $B_C$ (передача іншому агенту зберігає суму).
- $B_C$: межа між локальним compute pool і мережею.
- $	au_C$: discrete ticks.

### Domain A (Attention)
- $X_A = \{(a_1, a_2, \ldots, a_n) \mid a_i \in [0, 1], \sum a_i \leq 1\}$ — розподіл уваги.
- $\mathcal{O}_A = \{\text{focus}(i), \text{distribute}, \text{withdraw}\}$
- $I_A$: $\sum a_i$ conserved under `focus` (переміщення, не знищення).
- $	au_A$: event-driven.

### Domain B (Budget)
- $X_B = \{(b, r) \mid b \in \mathbb{R}, r \in \mathbb{R}_{\geq 0}\}$ — баланс і ставка.
- $\mathcal{O}_B = \{\text{spend}, \text{earn}, \text{borrow}\}$
- $C_B$: soft constraint — `borrow` дозволено, але з $\text{cost} = r \cdot \text{amount}$.
- $	au_B$: continuous.

### Translation Attempts

**$\phi_{C \rightarrow A}$: Compute → Attention**
- Partial: $c \geq \text{threshold} \Rightarrow$ можливість `focus`.
- Lost: exact magnitude of $c$ (attention не розрізняє "багато" і "дуже багато" compute).
- Preserved: ordering (більше compute → більше attention capacity).
- Translation report: partial, confidence 0.6.

**$\phi_{A \rightarrow B}$: Attention → Budget**
- Lost: structural property (attention розподіляється, budget — накопичується).
- Preserved: scarcity (обмежена сумарна кількість).
- Translation report: partial, heavy loss, confidence 0.3.

**$\phi_{C \rightarrow B}$: Compute → Budget**
- Mapping: $c \cdot \text{price}_t \rightarrow b$.
- Context-dependent: price залежить від $t$ і market state.
- Preserved: ordering, additivity.
- Lost: temporal granularity (compute вимірюється в ticks, budget — continuously).
- Translation report: partial, temporal ontology mismatch.

**Висновок:** жодна translation не є invertible або lossless. Кожна зберігає інший набір властивостей. Це демонстрація §13–§14.

---

# APPENDIX B — Anti-Example

*(Дублікат §32 для наголосу)*

**Система:** квантово-заплутані частинки.

**Чому FLOW-0.1 тут не працює:**

1. **State:** $\psi_{AB}$ не розкладається на $\psi_A \otimes \psi_B$. Поняття "локального стану $x_A$" — approximation, а не first-class entity.
2. **Boundary:** $B$ між $A$ і $B$ не фільтрує інформацію класичним чином. Кореляції "протікають" крізь boundary без "transfer" у сенсі §3.
3. **Flow:** Operation на $A$ (наприклад, вимірювання) миттєво змінює $\psi_{AB}$, але це не "transition $x_A \rightarrow x'_A$" — це колапс глобального стану.
4. **Invariant:** "Збереження заплутаності" — не invariant у сенсі §5, бо заплутаність не є локальною величиною.
5. **Reach:** $Reach(x_A)$ не визначається незалежно від $x_B$.

**Мораль:** FLOW-0.1 — інструмент для певного класу систем. Його обмеження такі ж важливі, як і його твердження.
