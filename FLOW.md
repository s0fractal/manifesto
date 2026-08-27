# FLOW-0 — Потоки в гетерогенних просторах станів

**Статус:** speculative working model
**Версія:** 0.1
**Призначення:** зафіксувати робочий словник і набір гіпотез, що виникли в розмові, не перетворюючи їх на нормативну архітектуру.

> **НЕ НОРМАТИВНО. НЕ Є ТЕОРІЄЮ. НЕ ЗЛИВАТИ АВТОМАТИЧНО В HSP, SIGMA-GLYPH ЧИ TRINITY.**
> Модель існує для породження контрприкладів, експериментів і кращих формулювань.

---

## 0. Центральна інтуїція

Інформаційні системи можна розглядати не лише як множини станів або символів, а як **простори можливих трансформацій**.

У такому представленні важливим є не лише:

> що означає стан \(x\)?

а:

> що з \(x\) можна зробити, за яких умов, якою ціною, що при цьому зберігається, що втрачається і які майбутні стани стають доступними?

Робоча теза:

$$
\boxed{
\text{semantics}
\approx
\text{possible transformations}
+
\text{constraints}
+
\text{invariants}
+
\text{consequences}
}
$$

Це не визначення семантики взагалі, а кандидат на **операційний шар**, придатний для порівняння гетерогенних інформаційних систем.

---

# 1. State Space

Нехай існує домен:

$$
D = (X,\mathcal O,\mathcal C,\mathcal I)
$$

де:

* \(X\) — множина допустимих станів;
* \(\mathcal O\) — допустимі операції;
* \(\mathcal C\) — constraints;
* \(\mathcal I\) — відомі invariants.

`State space` не зобов'язаний бути геометричним.

Він може бути:

* графом;
* частковим порядком;
* автоматом;
* множиною термів;
* probability space;
* manifold;
* causal graph;
* constraint system;
* ledger;
* ontology;
* композицією кількох різних просторів.

Тому слово **topology** тут поки слід використовувати обережно: частина просторів може не мати топології в строгому математичному сенсі.

---

# 2. Flow

`Flow` — зміна стану відповідно до деякого transition law.

У детермінованому випадку:

$$
x_{t+1} = T(x_t,a_t,e_t)
$$

У стохастичному:

$$
x_{t+1}
\sim
P(X_{t+1}\mid x_t,a_t,e_t)
$$

де:

* \(x_t\) — локальний стан;
* \(a_t\) — дія;
* \(e_t\) — середовище.

У continuous domain:

$$
\dot x = F(x,t)
$$

або для зв'язаних полів:

$$
\frac{\partial \phi}{\partial t}
=
F(\phi,\psi,\nabla\phi,\ldots)
$$

Але жоден із цих формалізмів не є універсальним.

**FLOW-0 не стверджує, що всі системи треба описувати PDE або механікою рідин.**

Navier–Stokes, diffusion, reaction–diffusion, network flow тощо — можливі **локальні flow laws**, а не фундаментальні метафори для всього.

---

# 3. Admissible transitions

Не кожний математично можливий перехід є допустимим.

Визначимо:

$$
A(x) = \{a \mid C_i(x,a)\leq 0\;\forall i\}
$$

Тоді система має не просто trajectory, а **простір допустимих майбутніх**:

$$
Reach(x)
$$

Constraints можуть змінювати його форму:

$$
Reach(x\mid C_1)
\subseteq
Reach(x)
$$

Resource constraint:

$$
Reach(x\mid r=10)
\subseteq
Reach(x\mid r=100)
$$

Authority constraint може поводитися інакше:

$$
a\notin A(x)
$$

доки не з'явиться певний warrant.

Таким чином інформація може змінювати поведінку системи не через зміну фізичного стану, а через **зміну множини admissible transitions**.

---

# 4. Constraint

Constraint — правило, що обмежує допустимі стани або переходи.

Загальна форма:

$$
C(x,a,t,\context)\leq0
$$

Важливо відокремлювати:

```text
physical constraint
resource constraint
logical constraint
protocol constraint
authority constraint
risk constraint
semantic constraint
policy constraint
```

Вони можуть мати схожий операційний ефект:

> “цей перехід зараз неможливий”

але абсолютно різну природу.

Тому operational similarity не означає ontological identity.

---

# 5. Invariant

Інваріант не є абсолютною властивістю об'єкта.

Коректніша форма:

$$
I(x)
\text{ invariant under }
F
\text{ within }
B
\text{ assuming }
A
$$

де:

* \(F\) — сімейство трансформацій;
* \(B\) — boundary;
* \(A\) — assumptions.

Наприклад:

$$
ATP_{total}
$$

може бути conserved under `transfer`, але не under:

```text
mint
burn
external grant
decay
```

Тому запис:

> “ATP conserved”

недостатній.

Треба:

> “ATP conserved under transformation family \(F_{transfer}\) inside boundary \(B\).”

---

# 6. Resource-like structures

Назви `ATP`, `budget`, `money`, `energy`, `attention`, `compute`, `risk-capacity` не є універсальними сутностями.

Замість цього можна описувати їхню **операційну структуру**.

Наприклад:

$$
R =
(
Q,
C,
T,
P,
E,
\tau,
B
)
$$

де:

* \(Q\) — quantity/state;
* \(C\) — admissibility constraints;
* \(T\) — transition/accounting law;
* \(P\) — production/destruction rules;
* \(E\) — exchange/transfer rules;
* \(\tau\) — temporal behavior;
* \(B\) — scope/boundary.

Можливі властивості:

```text
bounded
conserved
consumable
replenishable
transferable
divisible
fungible
decaying
borrowable
mintable
local
global
path-dependent
reversible
non-reversible
```

Тоді ATP і гроші можуть мати спільні властивості, не будучи одним поняттям.

---

# 7. Price ≠ Resource

`Price` не слід автоматично ототожнювати з budget/resource.

Resource:

$$
r_{t+1}=r_t-cost(a_t)
$$

Price радше визначає mapping:

$$
cost(a,t)=p(a,t)\cdot q(a)
$$

Тобто `price` може бути:

* exchange relation;
* marginal cost;
* shadow price;
* dual variable;
* context-dependent transformation coefficient.

Через це одна й та сама дія може мати різну resource cost при різних prices.

---

# 8. Quantization

Не всі flows є continuous.

У деяких domains переходи принципово дискретні:

```text
unsigned → signed
draft → ratified
alive → archived
uncommitted → committed
unresolved → resolved
```

Стан:

$$
0.73\;ratified
$$

може взагалі не мати семантики.

Тому domain повинен декларувати:

```text
continuous
discrete
hybrid
event-driven
quantized
```

а translation між domains не повинна мовчки перетворювати discrete transition на continuous scalar або навпаки.

---

# 9. Multi-space systems

Реальна система може одночасно існувати в кількох різних state spaces:

$$
x_A\in X_A
$$

$$
x_B\in X_B
$$

$$
x_C\in X_C
$$

Наприклад:

```text
semantic state
resource state
authority state
physical state
epistemic state
social state
```

Сукупний стан:

$$
S = (x_A,x_B,x_C,\ldots)
$$

але це не означає, що існує одна природна vector space, в яку їх слід сплющити.

Динаміка може бути coupled:

$$
\dot{x}_A = F_A(x_A,x_B)
$$

$$
\dot{x}_B = F_B(x_B,x_C)
$$

$$
x_C^{t+1}=T_C(x_C^t,x_A^t)
$$

Тобто flow в одному домені деформує flow в іншому.

---

# 10. Cross-space translation

Для двох domains:

$$
D_A,D_B
$$

може існувати mapping:

$$
\phi_{A\rightarrow B}:X_A\rightharpoonup X_B
$$

Він може бути:

* partial;
* lossy;
* irreversible;
* context-sensitive;
* resource-expensive;
* non-unique.

Основна одиниця перевірки translation — не схожість значень, а **збереження заявлених властивостей**.

Наприклад:

$$
I_A(x)
\Rightarrow
I_B(\phi(x))
$$

або:

$$
C_A(x,a)
\Rightarrow
C_B(\phi(x),\phi(a))
$$

для певного action context.

Універсальним тоді стає не значення:

```text
ATP ↔ money
```

а, можливо:

```text
ConsumedBy
BoundedBy
TransferableUnder
AdmissibleWhen
ConservedUnder
```

---

# 11. Translation loss

Будь-який cross-domain bridge повинен потенційно описувати:

```text
preserved
lost
introduced
approximated
unknown
non-invertible
context-dependent
```

Наприклад:

$$
\phi_{A\rightarrow B}
$$

може зберігати:

```text
ordering
```

але втрачати:

```text
distance
```

або зберігати:

```text
action admissibility
```

але втрачати:

```text
resource magnitude
```

Тому:

$$
\phi^{-1}(\phi(x)) = x
$$

не є загальною вимогою.

---

# 12. Information as transformation potential

Одна з центральних спекулятивних тез FLOW-0:

> Інформаційний стан набуває операційного значення через те, як він змінює простір можливих трансформацій.

Наприклад warrant:

```text
before:
    action ∉ admissible

after:
    action ∈ admissible
```

Knowledge:

```text
before:
    policy selects A

after evidence E:
    policy selects B
```

Commitment:

```text
before:
    futures = {A,B,C,D}

after commitment:
    futures = {C,D}
```

Тому інформація може трактуватися як щось, що:

$$
Reach(x)
\rightarrow
Reach'(x)
$$

або:

$$
P(Trajectory)
\rightarrow
P'(Trajectory)
$$

---

# 13. Wittgenstein extension

Мовна гра Вітгенштейна використовується тут лише як **аналогія**, не як формальна основа.

Класична інтуїція:

> meaning is use.

Розширена робоча форма:

$$
\boxed{
\text{operational meaning}
=
\text{position in a space of possible transformations}
}
$$

Для інформації питання стає не:

> “що означає цей символ?”

а:

> які операції він дозволяє, забороняє, змінює або робить можливими?

Це дозволяє мати **family resemblance** замість universal ontology.

Наприклад:

```text
ATP
money
time
trust
authority
compute
```

можуть мати частково перекривні структурні властивості без спільної сутності.

---

# 14. Player

`Player` не визначається просто як “об'єкт, що рухається”.

Робоче визначення:

> **Player — локус endogenous control, внутрішній стан або policy якого причинно впливають на його власний розподіл майбутніх траєкторій.**

Для policy:

$$
a_t=\pi(x_t,h_t)
$$

Якщо:

$$
Trajectory(do(\pi=\pi_1))
\neq
Trajectory(do(\pi=\pi_2))
$$

то policy має causal influence на trajectory.

Це не вимагає метафізичної свободи волі.

---

# 15. Degrees of agency

Agency може бути не binary property.

Можлива груба шкала:

```text
object
    trajectory externally determined

reactive system
    fixed response law

agent
    selects among admissible transitions

player
    internal selection affects own trajectory

reflexive player
    can modify its own policy

self-modifying player
    can modify mechanisms that modify policy
```

Це поки descriptive taxonomy, а не formal hierarchy.

---

# 16. Determinism

Agency не вимагає stochasticity.

Детермінована система:

$$
x_{t+1}=T(x_t,\pi(x_t))
$$

може бути player, якщо зміна \(\pi\) контрфактично змінює trajectory.

Отже:

```text
determinism ≠ absence of agency
randomness ≠ agency
```

Важливішим поняттям є **controllability**.

---

# 17. Nondeterminism / stochasticity

При stochastic transitions:

$$
x_{t+1}
\sim
P(X\mid x_t,a_t)
$$

player може не контролювати конкретний outcome, але змінювати distribution:

$$
P(Trajectory\mid\pi_1)
\neq
P(Trajectory\mid\pi_2)
$$

Тому agency можна описувати як здатність деформувати:

$$
P(\text{future})
$$

а не обов'язково вибирати конкретне future.

---

# 18. Чотири різні “недетермінованості”

Необхідно розрізняти:

### 18.1 Epistemic uncertainty

Transition deterministic, але observer не знає повного state.

### 18.2 Chaos

Transition deterministic, але:

$$
\delta x_0\ll1
$$

може породити:

$$
\delta x_t\gg1
$$

### 18.3 Stochasticity

Transition law сам є probability distribution.

### 18.4 Underspecified admissibility

Існує кілька legal actions:

$$
A(x)=\{a_1,a_2,\ldots\}
$$

а policy визначає, яку буде використано.

Це не те саме, що randomness.

---

# 19. Reflexive trajectory

Для reflexive player існують щонайменше два взаємопов'язані flows.

State flow:

$$
x_t\rightarrow x_{t+1}
$$

Policy flow:

$$
\pi_t\rightarrow\pi_{t+1}
$$

Наприклад:

$$
x_{t+1}=F(x_t,\pi_t,e_t)
$$

$$
\pi_{t+1}=G(\pi_t,x_t,Evidence_t)
$$

Тоді історія агента впливає на механізм, який породжує його наступні рішення.

Це кандидат на формалізацію поняття **trajectory-conditioned attractor** для довгоживучих LLM-процесів.

---

# 20. Attractors

Attractor у FLOW-0 поки використовується в широкому робочому сенсі.

Необхідно окремо перевіряти, чи конкретна система дійсно допускає математично коректне поняття attractor.

Інтуїція:

```text
history
→ vocabulary
→ preferred decompositions
→ preferred tools
→ repeated action patterns
→ stronger history
```

утворює feedback loop.

Для LLM-agent trajectory:

$$
h_t
\rightarrow
\pi_t
\rightarrow
a_t
\rightarrow
h_{t+1}
$$

Такий loop може породжувати:

* specialization;
* competence;
* blind spots;
* vocabulary lock-in;
* Goodhart-like behavior.

---

# 21. Continuity vs blindness

Тяглість є одночасно ресурсом і ризиком.

```text
continuity
→ accumulated competence

continuity
→ attractor reinforcement
```

Тому можливі два ортогональні механізми.

### Lineage process

Отримує:

```text
history
vocabulary
prior hypotheses
prior failures
reviews
receipts
```

і продовжує trajectory.

### Cold reconstruction

Отримує максимально raw:

```text
artifact
observations
tests
measurements
problem
```

без старого interpretive vocabulary.

Різниця між ними сама стає observation.

---

# 22. Artifact continuity ≠ interpretive continuity

Варто розділяти:

$$
ArtifactContinuity
$$

і:

$$
InterpretiveContinuity
$$

Перше бажано зберігати:

* code;
* measurements;
* provenance;
* experiments;
* failed hypotheses;
* receipts.

Друге варто періодично скидати:

* metaphors;
* favored ontology;
* “big picture”;
* canonical vocabulary.

Це дозволяє:

> перечитувати ті самі факти так, ніби попередньої теорії не існувало.

Робоча назва:

**epistemic rebase**.

---

# 23. Multi-player systems

Нехай існують players:

$$
P_1,\ldots,P_n
$$

з різними spaces:

$$
X_1,\ldots,X_n
$$

і policies:

$$
\pi_1,\ldots,\pi_n
$$

Спільна дія не вимагає, щоб:

$$
X_1=X_2
$$

або:

$$
\pi_1\approx\pi_2
$$

Достатньою може бути локальна compatibility relation:

$$
K_{ij}(a,\context)
$$

Тобто systems можуть мати несумісні внутрішні representations, але домовитися про boundary conditions для конкретної взаємодії.

---

# 24. Coupling

Два flows можуть бути coupled без прямого translation.

Наприклад:

$$
\dot{x}=F(x,r)
$$

$$
\dot{r}=G(r,a)
$$

Resource field впливає на state trajectory, але не означає state.

Аналогія з ferrofluid тут допустима лише структурно:

> зовнішнє поле змінює доступну dynamics середовища.

Не слід робити висновок, що соціальні або інформаційні системи “насправді є рідинами”.

---

# 25. Flow law library

Можливо, універсальним шаром стане не universal state representation, а бібліотека relation primitives:

```text
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

Конкретні domains тоді інстанціюють частину цих відношень.

---

# 26. Candidate universal layer

Найсильніша спекулятивна теза документа:

> Якщо універсальний informational layer взагалі існує, він може бути ближчим до алгебри constraints, transformations і preserved relations, ніж до універсальної онтології сутностей.

Тобто не:

$$
UniversalMeaning(x)
$$

а:

$$
Structure(
Transformations,
Constraints,
Invariants,
Mappings
)
$$

---

# 27. “Universal translation”

Universal translation не означає:

> кожний стан можна перевести в кожний інший.

Навпаки, корректний translator повинен уміти сказати:

```text
translation undefined
translation partial
invariant not preserved
loss unacceptable for this action
comparison meaningless
```

Тому failure to translate може бути **правильним результатом**.

---

# 28. Information game

Узагальнення мовної гри:

```text
Game G =
    state domain
    legal transformations
    constraints
    resources
    players
    observations
    consequences
```

Одна й та сама datum може брати участь у різних games.

Її operational meaning може змінюватися без зміни bytes.

Тому:

$$
Meaning(data,G_1)
\neq
Meaning(data,G_2)
$$

---

# 29. Game transition

Цікавіший випадок — коли player може перейти не просто між states, а між **games**:

$$
G_A\rightarrow G_B
$$

Наприклад:

* змінити ontology;
* змінити governance;
* змінити accounting unit;
* перейти на інший evaluator;
* змінити власну policy architecture.

Тоді виникає meta-flow:

$$
(x,G)_t
\rightarrow
(x,G)_{t+1}
$$

Це вже не рух усередині fixed rules.

Це рух, що може змінити самі rules.

---

# 30. Constraint on self-modification

Self-modification не повинна автоматично означати unconstrained mutation.

Можливе:

$$
G_t\rightarrow G_{t+1}
$$

лише якщо:

$$
I_{identity}(G_t,G_{t+1})
$$

$$
Budget_{mutation}\ge Cost(G_t\rightarrow G_{t+1})
$$

$$
Warrant(G_t\rightarrow G_{t+1})=true
$$

Тут уже природно виникає зв'язок з HSP/Warrant/Sigma-Glyph, але FLOW-0 не визначає їх реалізацію.

---

# 31. Relation to [Sigma-Glyph](https://github.com/s0fractal/sigma-glyph)

Можлива майбутня відповідність:

```text
Sigma-Glyph (https://github.com/s0fractal/sigma-glyph)
→ concrete execution/resource semantics

FLOW
→ broader vocabulary for classes of constrained flows
```

FLOW не повинен змушувати Sigma-Glyph перейменовувати ATP або підганяти evaluator під універсальну метафору.

Навпаки, Sigma-Glyph може виступати конкретним falsification substrate для деяких FLOW hypotheses.

---

# 32. Relation to [HSP (RFC-0003)](https://github.com/s0fractal/trinity/tree/main/docs/rfc/0003-heterogeneous-state-protocol)

HSP працює з:

* typed domains;
* translations;
* losses;
* compatibility;
* heterogeneous state.

FLOW може досліджувати нижчий або сусідній шар:

> які саме dynamical/constraint structures можуть переноситися між domains?

Небезпека:

FLOW може просто перевинайти HSP іншими словами.

Це треба активно перевіряти.

---

# 33. Relation to [Warrant](https://github.com/s0fractal/warrant)

Warrant можна інтерпретувати як механізм, що змінює admissibility:

$$
A(x)
\rightarrow
A'(x)
$$

але це лише одна перспектива.

Не можна редукувати provenance/authority/signature semantics до “ще одного flow constraint”, якщо при цьому губляться суттєві властивості.

---

# 34. Relation to [ALife](https://github.com/s0fractal/sigma-glyph-alife) / [World](https://github.com/s0fractal/sigma-glyph-world)

World/ALife можуть бути хорошими quarantine substrates для перевірки FLOW-гіпотез.

Наприклад:

```text
Does a resource invariant survive persistent history?

Does changing representation alter observed flow?

Can two domains preserve action admissibility while losing magnitude?

Does reflexive policy evolution create measurable attractors?
```

Негативний результат цінний.

---

# 35. Candidate mathematical families

FLOW-0 поки не вибирає фундаментальну математику.

Кандидати:

### Dynamical systems

Для trajectories, attractors, stability.

### Control theory

Для endogenous control, controllability, reachability.

### Graph theory / network flow

Для discrete transition spaces.

### Stochastic processes

Для probabilistic trajectories.

### Game theory

Для multi-player coupled decisions.

### Category theory

Для composition mappings та preservation structure.

### Formal semantics

Для operational meaning і transition systems.

### Information theory

Для dependence, channel loss, distinguishability.

### Optimal transport

Можливо корисний для деяких cross-space mappings, але не універсальний.

### PDE / continuum mechanics

Лише для domains, де continuous-field assumptions виправдані.

---

# 36. Заборонені shortcuts

FLOW-0 не дозволяє без доказу:

```text
everything is energy
everything is flow
everything is geometry
everything is information
everything is optimization
everything is a fluid
everything is a game
everything is an agent
```

Такі statements можуть бути metaphors, але не conclusions.

---

# 37. Основні ризики

## 37.1 Vocabulary laundering

Старі концепції перейменовуються в нові терміни без нового змісту.

## 37.2 Physics cosplay

Математичні слова з фізики використовуються без відповідної структури.

## 37.3 Universalization bias

Локальна закономірність оголошується універсальною.

## 37.4 Metaphor lock-in

`flow`, `field`, `attractor` починають визначати, які observations модель взагалі помічає.

## 37.5 LLM convergence artifact

Кілька моделей погоджуються не через істинність структури, а через спільні training priors.

## 37.6 Tautological semantics

“Meaning is transformations” стає невразливою тезою, бо все заднім числом описується як transformation.

---

# 38. Фальсифікатори framing

FLOW framing має втрачати довіру, якщо:

1. Він не породжує нових testable distinctions.
2. Переклад у flow vocabulary систематично втрачає більше, ніж пояснює.
3. Незалежні cold-start analyses природніше відновлюють іншу структуру.
4. `constraint`, `invariant`, `flow`, `player` неможливо визначити без постійних ad hoc exceptions.
5. Конкретні формальні моделі не дають нічого понад звичайну operational semantics/control theory.
6. Різні domains вимагають настільки несумісних primitives, що “універсальний layer” стає порожньою множиною загальних слів.
7. Модель генерує красиві аналогії, але вони не змінюють predictions або experiment design.

---

# 39. Перші експерименти

### FLOW-EXP-001 — Vocabulary independence

Дати кільком моделям одну задачу без слів:

```text
flow
topology
invariant
resource
ontology
translation
```

Подивитися, чи реконструюють вони схожі primitives.

---

### FLOW-EXP-002 — Same artifact, different games

Взяти один artifact і змінити лише action context.

Перевірити, які semantics залишаються invariant, а які змінюються.

---

### FLOW-EXP-003 — Resource isomorphism

Взяти дві системи з різними назвами resource.

Спробувати побудувати mapping лише через operational laws.

Перевірити:

* що зберігається;
* де mapping ламається.

---

### FLOW-EXP-004 — Deterministic agency

Побудувати повністю deterministic player.

Контрфактично змінювати policy.

Виміряти зміну reachable trajectories без stochasticity.

---

### FLOW-EXP-005 — Attractor formation

Декілька однакових моделей стартують з однакової задачі, але різних ранніх histories.

Через \(N\) циклів перевірити:

* vocabulary divergence;
* problem decomposition;
* tool choice;
* blind spots;
* cross-trajectory reconstruction.

---

### FLOW-EXP-006 — Epistemic rebase

Порівняти:

```text
lineage agent
vs
cold-start agent
```

на одному накопиченому artifact set.

Ціль — вимірювати не “хто правильніший”, а **які distinctions бачить лише один із режимів**.

---

# 40. Open questions

1. Чи існує мінімальний набір transformation primitives, достатній для широкого класу domains?
2. Чи можна математично визначити translation loss без universal metric?
3. Чи є agency властивістю system або relation між subsystem та boundary?
4. Як вимірювати endogenous control?
5. Як відрізнити learned attractor від genuine specialization?
6. Як визначити identity при policy self-modification?
7. Чи є invariant preservation достатнім для semantic translation?
8. Які properties повинні зберігатися лише action-contextually?
9. Чи можна визначити “same game” без спільної ontology?
10. Коли зміна representation є просто coordinate change, а коли — зміною самої game?
11. Чи існують універсальні conservation-like laws для informational systems?
12. Чи є “untranslatable” first-class semantic result?
13. Як працює quantization при переході між discrete і continuous domains?
14. Чи можна формалізувати `price` як relation між flows, не редукуючи все до economics?
15. Чи можна отримати emergent player з системи, компоненти якої окремо players не є?

---

# 41. Найкоротша форма

Якщо прибрати всю “потокологію”, залишається:

$$
\boxed{
\text{State}
+
\text{Allowed transformations}
+
\text{Constraints}
+
\text{Invariants}
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

> **Інформаційні системи можна порівнювати не через спільні назви станів, а через структуру допустимих трансформацій, обмежень і того, що ці трансформації зберігають.**

І ще спекулятивніше:

> **Meaning may be less a property of a representation than a position within a structured space of possible transformations.**

Оце я б і лишив центром `FLOW-0`.

Усе інше — поки що кандидати на те, щоб бути красиво роз'їбаними наступними експериментами.
