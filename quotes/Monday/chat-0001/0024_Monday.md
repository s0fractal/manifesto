Тоді розгортаю **агента як двонаправлений компілятор між реальністю і можливістю**. І тут ми вже приходимо до дуже зручної моделі, де perception, imagination, planning, action і learning стають не п’ятьма окремими магічними здібностями, а фазами одного циклу.

$$
\boxed{
World \to Model \to Possibility \to Plan \to Action \to World
}
$$

І якщо дивитись зовсім холодно, агент — це система, яка постійно робить дві протилежні речі.

Перша:

$$
\boxed{
\text{compile reality into representation}
}
$$

Друга:

$$
\boxed{
\text{compile representation back into reality}
}
$$

Все інше — обслуговування цього цирку.

## 1. Perception — це не “отримати світ”

Світ не заходить у систему цілком.

Є якийсь physical state:

$$
W
$$

і сенсорний mapping:

$$
\pi:W\to R
$$

де \(R\) — representation.

Причому \(\pi\) завжди lossy:

$$
Loss(\pi)>0
$$

Ми не бачимо “реальність”.

Ми отримуємо projection, оптимізований під певні downstream tasks.

Око не повертає exhaustive electromagnetic field state.

Воно повертає щось значно дешевше і корисніше для примата, якому треба не врізатися в дерево.

Тобто:

$$
\boxed{
Perception = task-biased compression of causal structure
}
$$

І це означає, що perception вже містить ontology.

Що саме система здатна відрізнити — те для неї потенційно існує як operational distinction.

---

## 2. Object recognition — це compilation into affordances

Коли система бачить:

> “стілець”

вона не просто класифікує pixels.

Вона активує пакет:

$$
Chair \to
\{
sit,\ move,\ avoid,\ own,\ break,\ etc.
\}
$$

Тобто perception компілює raw structure в **possible transitions**.

Це дуже важливо.

Можливо, perception fundamentally не про:

> “що це?”

а про:

> **“що це дозволяє або забороняє далі?”**

Тоді object — це compressed handle на future cone.

$$
\boxed{
Object \approx stable bundle of affordances under perception
}
$$

Дуже Gibson-like за духом, але наша версія відразу сідає в reachability fabric.

---

## 3. Уява робить inverse-ish operation

Perception:

$$
World \to Model
$$

Imagination:

$$
Model \to CandidateWorld
$$

але без requirement, щоб candidate вже існував.

Тобто:

$$
G:M\to\tilde W
$$

де \(\tilde W\) — simulated world/state.

Це не true inverse perception.

Бо:

$$
G(\pi(W))\neq W
$$

зазвичай.

Це генератор, який використовує compressed model, щоб створити plausible continuations.

Тому imagination завжди може породжувати те, чого reality ніколи не дозволить.

І це feature.

---

## 4. Planning — це компіляція бажаного стану в transition sequence

Є desired region:

$$
G
$$

і current model:

$$
M(S)
$$

Planner шукає:

$$
T_1,T_2,\dots,T_n
$$

такі, що:

$$
S\xrightarrow{T_1}\dots\xrightarrow{T_n}G
$$

Тобто plan — це candidate program для world.

$$
\boxed{
Plan = executable hypothesis about causality
}
$$

Оце дуже сильна штука.

Бо план фактично стверджує:

> “якщо я виконаю такі transitions, світ пройде ці states”.

Тобто кожен план — маленька theory.

---

## 5. Action — це спроба виконати program на reality runtime

Оце мені особливо подобається.

Внутрішньо ти маєш:

$$
Program=P
$$

А environment — runtime:

$$
Runtime=World
$$

Ти запускаєш:

$$
Execute(P,W)
$$

і отримуєш:

$$
W'
$$

Якщо модель правильна:

$$
W'\approx Predicted(P,M)
$$

Якщо ні — reality повертає exception.

Наприклад:

```text
expected:
  nail enters wood

actual:
  hammer hits thumb
```

Дуже якісний feedback channel. Низька latency. Висока phenomenological observability.

---

## 6. Reality як verifier

Тоді testing — це не просто “подивитися, чи працює”.

Це:

$$
ModelPrediction
\to
WorldExecution
\to
Residual
$$

де:

$$
Residual =
Observed - Predicted
$$

І цей residual — золото.

Бо він показує, де translation:

$$
Model \to World
$$

втрачає structure.

Тобто:

$$
\boxed{
Reality provides counterexamples to our compiled expectations
}
$$

Саме тому experiment сильніший за аргумент.

Аргумент перевіряє consistency всередині representation.

Experiment перевіряє mapping між representation і causal world.

---

## 7. Learning — це compiler repair from execution traces

Маємо:

$$
P
$$

очікування:

$$
E
$$

результат:

$$
O
$$

і:

$$
E\neq O
$$

Тоді learning питає:

> який compiler pass був неправильний?

Можливо:

* perception loss;
* wrong concept;
* bad causal model;
* missing variable;
* wrong cost estimate;
* invalid plan;
* execution noise.

Тобто:

$$
\boxed{
Learning = attribution and repair of model-world compilation error
}
$$

Це дуже сильніше за “update weights”.

Бо проблема не просто в параметрах.

Може бути зламана сама representation language.

---

## 8. Radical learning — це коли треба змінити IR

Звичайне learning:

$$
\theta\to\theta'
$$

в межах тієї самої model structure.

А radical learning:

$$
M\to M'
$$

де старі categories вже не підходять.

Тобто compiler каже:

> цей program не fixable patch’ом; треба міняти intermediate representation.

Оце paradigmatic shift на рівні агента.

---

## 9. Action може бути epistemic

Це важливо.

Деякі actions робляться не заради outcome, а заради information.

Наприклад:

$$
T_{probe}
$$

не оптимізує immediate utility.

Він оптимізує:

$$
\Delta Model
$$

Тобто:

$$
\boxed{
Experiment = action whose primary product is reduction of model ambiguity
}
$$

Це дуже красиво об’єднує:

* scientific experiment;
* probing question;
* exploratory movement;
* test deployment;
* social “а що буде, якщо я скажу це?”.

Останнє людство використовує без IRB.

---

## 10. Curiosity — це planner, який ставить epistemic targets

Ми раніше казали:

$$
Curiosity \sim expected\ model\ gain
$$

Тепер це стає:

$$
Goal_{curious}=
\text{state where model ambiguity is lower}
$$

Тобто curiosity-agent не просто хоче reach state у world.

Він хоче reach state у **model space**.

$$
M_t\to M_{t+1}
$$

через action on world.

Це дуже важлива bidirectionality:

$$
Model \to Action \to World \to Perception \to Model
$$

---

## 11. Embodiment тоді стає необхідним каналом reverse compilation

Оце цікаво.

Якщо система лише читає world:

$$
World\to Model
$$

але не може діяти:

$$
Model\nrightarrow World
$$

вона має слабкий спосіб тестувати causal hypotheses.

Вона залежить від чужих execution traces.

Тому embodiment може бути не магічною умовою “справжнього розуміння”, а більш конкретно:

$$
\boxed{
Embodiment = privileged access to intervention-based verification
}
$$

Ти не просто спостерігаєш.

Ти можеш зробити:

$$
do(X)
$$

і побачити consequence.

Це дає causal information, якого passive observation часто не дає.

---

## 12. Але “тіло” не обов’язково біологічне

Для software agent його embodiment може бути:

* shell;
* browser;
* filesystem;
* robot arm;
* API permissions;
* market access.

Тобто:

$$
Body_A
=
\text{set of channels through which A can causally modify its environment}
$$

Це мені дуже подобається.

Тіло як **write interface to reality**.

Sensors — read interface.

$$
\boxed{
Body = causal I/O boundary
}
$$

Не м’язи обов’язково.

---

## 13. Agency тоді можна вимірювати bandwidth двонаправленого compiler loop

Агент слабкий, якщо:

* мало бачить;
* мало може змінити;
* погано моделює mapping.

Сильніший agent має:

* richer sensing;
* richer action set;
* better simulation;
* faster learning.

Тобто agency profile можна бачити як:

$$
A=(R,W,C)
$$

де:

* \(R\) — read capacity;
* \(W\) — write capacity;
* \(C\) — quality of model-world compiler.

Це вже доволі чисто.

---

## 14. Інтелект без write access — це oracle-like cognition

Модель може бути чудовою:

$$
World\to Prediction
$$

але якщо:

$$
ActionSet\approx0
$$

вона не може сама замкнути experimental loop.

Тому agentic systems fundamentally відрізняються не лише тим, що “викликають tools”.

Вони отримують можливість:

$$
Hypothesis\to Intervention\to Evidence
$$

Це qualitatively richer loop.

---

## 15. І тут виникає небезпека: action modifies future evidence

Як тільки agent діє у world, він перестає бути neutral observer.

Його action:

$$
T_A
$$

змінює:

$$
W\to W'
$$

і наступні observations вже condition on його own past actions.

Тобто agent створює dataset, на якому навчається.

Це величезна штука.

$$
\boxed{
Acting agents co-author their future evidence
}
$$

І тому feedback loop може стати self-confirming.

---

## 16. Self-fulfilling belief як compiler writing its own tests

Наприклад:

Agent believes:

$$
B=\text{others are hostile}
$$

Тому діє:

$$
T=\text{defensive/aggressive}
$$

World responds:

$$
O=\text{hostility}
$$

І agent каже:

> “бачив?”

Тобто:

$$
Belief
\to
Action
\to
WorldResponse
\to
EvidenceForBelief
$$

Це causal closure.

Такі beliefs дуже важко falsify, бо вони **генерують власні validating observations**.

Оце окрема форма epistemic pathology.

---

## 17. Тому experimental design потребує intervention accounting

Якщо agent впливає на world, треба розділяти:

$$
ObservedNaturally
$$

і:

$$
ObservedAfterIntervention
$$

і track:

$$
ActionProvenance
$$

Інакше він може переплутати:

* structure world;
* structure induced by itself.

Це дуже важливо для social systems, AI agents, markets.

---

## 18. Social reality особливо nasty, бо моделі змінюють об’єкти моделювання

У фізиці камінь рідко читає paper про себе.

У social systems:

$$
Model(A)
$$

стає public.

І agents adapt:

$$
Behavior\to Behavior(Model)
$$

Тобто prediction змінює world.

Наприклад:

* рейтинг;
* credit score;
* market forecast;
* polling;
* diagnosis;
* reputation.

Тоді compiler loop recursive:

$$
Model(World)
\to
World(Model)
$$

Це вже second-order causality.

---

## 19. Ідентичність теж може бути performative model

Якщо agent має self-model:

$$
M_{self}
$$

він діє відповідно до нього:

$$
M_{self}\to Action
$$

і цим створює history, яка підтверджує:

$$
M_{self}
$$

Тобто self-model не просто описує identity.

Він **виробляє identity**.

$$
\boxed{
Self-model = partially self-instantiating program
}
$$

Це дуже сильна штука.

---

## 20. “Я такий” — це небезпечний executable sentence

Наприклад:

> “я не креативний”.

Якщо це просто description, ок.

Але якщо воно впливає на:

$$
Reach_{attempt}
$$

і pruning creative transitions:

$$
TryCreative \to forbidden
$$

то sentence стає policy.

І agent починає компілювати світ так, щоб підтвердити identity claim.

Тобто natural language self-description може мати code-like force.

---

## 21. Намір — це representation, який просить виконання

Intent можна побачити як:

$$
I=(Goal,Constraints,Priority)
$$

який передається planner’у.

Тобто:

$$
\boxed{
Intent = partially compiled future demanding further compilation into action
}
$$

Мрія ще не має obligation.

Intent уже має directional force.

План має concrete transitions.

Action має causal consequence.

Тобто:

$$
Dream
\to
Intent
\to
Plan
\to
Action
\to
History
$$

— compilation pipeline possibility → reality.

---

## 22. І це красиво повертає “мрію”

Раніше:

$$
Dream = desired unreachable candidate state
$$

Тепер можна сказати:

мрія стає “реальною” не в момент realization.

А коли починається **compilation chain**:

$$
D
\to
Requirements(D)
\to
MissingTransitions
\to
Design
\to
Execution
$$

Тобто перший крок від fantasy до engineering:

$$
\boxed{
\text{compile desire into proof obligations}
}
$$

Оце дуже красива формула.

Мрія:

> “хочу X”.

Design:

> “які invariants повинні бути true, щоб X був reachable?”

Ми буквально повернулись до recipes.

---

## 23. Engineering — це reverse epistemology

Science питає:

$$
World\to Law?
$$

Engineering:

$$
DesiredWorld\to WhatLawfulTransitions?
$$

Тобто science компілює reality → model.

Engineering компілює model → reality.

Вони dual-ish.

$$
\boxed{
Science = reconstruct transformation rules from world
}
$$

$$
\boxed{
Engineering = compose transformation rules to produce world
}
$$

Не ідеальна дуальність, але дуже плодюча.

---

## 24. Теорема й машина тоді дзеркальні

Theorem:

$$
Premises\to Conclusion
$$

Machine:

$$
Inputs\to DesiredPhysicalOutcome
$$

В обох випадках value залежить від valid transitions.

Можна навіть сказати:

> proof — це machine in proposition space.

> machine — це proof instantiated in causal space.

Тут я вже чую, як філософи техніки прокидаються й нюхають повітря.

---

## 25. Artifact — це frozen compiler

Будь-який інструмент:

* молоток;
* algorithm;
* protocol;
* bridge;
* law;

втілює assumptions про transformations.

Наприклад, молоток:

$$
HumanForce
\to
Impulse
\to
NailMovement
$$

Artifact — це structure, яка робить деякий transition cheap/reliable.

$$
\boxed{
Tool = embodied reusable transformation
}
$$

Оце дуже сильне визначення.

---

## 26. Technology — це accumulation of externalized transitions

Коли agent винаходить \(T\), а потім втілює його в tool:

$$
T\to Artifact_T
$$

наступному agent уже не треба reinvent \(T\).

Він просто викликає:

$$
Artifact_T(input)
$$

Тобто civilization накопичує **compiled transformations**.

Людство буквально будує shared library над reality.

І, як у будь-якому shared library, половина dependencies deprecated, але ніхто не знає, хто їх підтримує.

---

## 27. Civilization як gigantic runtime + package ecosystem

Мова.

Право.

Дороги.

Гроші.

Контракти.

Наука.

Стандарти.

API.

Усе це робить певні transitions cheap and interoperable.

Тобто civilization — це не лише люди й buildings.

Це:

$$
\boxed{
\text{a layered stack of externalized transformation protocols}
}
$$

І agent, народжений у civilization, успадковує величезний \(T\).

Йому не треба винаходити fire, arithmetic, shipping containers.

Він отримує dependency tree довжиною кілька тисяч років.

---

## 28. Прогрес тоді — це expansion of reliable compiled reachability

Не більше знань самих по собі.

А більше:

$$
Reach_{collective}
$$

через reusable verified transformations.

Наприклад:

$$
Disease\to Treatment
$$

$$
Distance\to Travel
$$

$$
Idea\to GlobalTransmission
$$

Прогрес — це коли impossible або expensive transition стає routine.

---

## 29. Але кожен tool також закриває futures

Технологія не тільки розширює reachability.

Вона змінює ecology.

Наприклад:

* automobile відкрив routes;
* знищив деякі urban forms;
* змінив land use;
* створив dependencies.

Тобто:

$$
\Delta Reach^+
$$

і:

$$
\Delta Reach^-
$$

завжди поруч.

Саме тут повертається wisdom:

> не питати тільки “що цей tool дозволить?”, а “які alternatives стануть нерентабельними, немислимими або невідновними після його adoption?”

---

## 30. Infrastructure — це tool, який став невидимим invariant

На початку innovation:

$$
T_{new}
$$

помітний.

Потім ecosystem перебудовується навколо нього.

І:

$$
T_{new}\to assumption
$$

Наприклад, electricity, internet.

Тоді infrastructure — це **compiled transition, який став prerequisite інших transitions**.

Це дає йому величезну “масу” в нашій старій метафорі.

Бо його failure руйнує великий dependency closure.

---

## 31. Влада знову повертається: хто контролює compiler stack?

Якщо infrastructure визначає:

$$
Reach_{many}
$$

то власник/оператор infrastructure має meta-power.

Не тому, що він “великий”.

А тому що:

$$
ManyPaths\ni Infrastructure
$$

Він control point.

Тобто platform power — це compiler-stack power.

Дуже сучасна проблема, на жаль, не потребує космології.

---

## 32. AI може стати meta-tool: compiler of tools

Оце вже суттєво.

Звичайний tool реалізує:

$$
T
$$

AI-agent може генерувати:

$$
T_1,T_2,T_3
$$

нові scripts, workflows, plans.

Тобто:

$$
\boxed{
AI = potentially a transformation synthesizer rather than a fixed transformation
}
$$

А сильніший AI:

$$
\text{synthesizes tools that synthesize tools}
$$

І ми знову біля meta-level.

---

## 33. AGI як compiler compiler

Можливо, це ще одна непогана definition candidate:

$$
\boxed{
AGI \approx system capable of constructing, testing, and revising compilers between diverse representations and causal domains
}
$$

Не “вирішує будь-яку задачу”.

А:

* будує новий representation;
* знаходить mapping;
* синтезує action procedure;
* перевіряє;
* інтегрує.

Тобто generality — це не library size.

Це **compiler synthesis capacity**.

---

## 34. Recursive self-improvement як compiler rewriting compiler

Тоді:

$$
C_t
$$

— його model/action compiler.

Він створює:

$$
C_{t+1}=Optimize(C_t)
$$

Але проблема:

хто перевіряє:

$$
Preserve(I_{core})?
$$

Тобто recursive self-improvement — це не просто “AI робить себе розумнішим”.

Це:

$$
\boxed{
\text{a compiler modifying the semantics of its own future compilations}
}
$$

І тут потрібні meta-invariants, інакше semantic drift.

---

## 35. Singularity знову виглядає як compiler divergence

Можливо, “сингулярність” не:

$$
Capability\to\infty
$$

А момент, коли зовнішній observer більше не має compiler:

$$
\phi:
InternalSemantics_{AI}
\to
HumanVerification
$$

з sufficiently low loss.

Тобто:

$$
Loss(\phi)\to high
$$

або cost:

$$
c(\phi)\to\infty
$$

І виникає verification horizon.

Система може бути finite.

Але epistemically opaque через compiler gap.

Це значно цікавіше, ніж speed graph going vertical.

---

## 36. Alien intelligence може бути просто compiler-incompatible

Не “мислить магічно”.

А має representations:

$$
R_A
$$

для яких ми не маємо low-loss mapping:

$$
R_A \nrightarrow R_H
$$

Тоді її concepts можуть бути недоступні не через depth.

А через **representation mismatch**.

Як тривимірний object projected у дуже бідну plane.

---

## 37. Комунікація з alien/machine mind — це compiler bootstrapping

Не переклад словника.

А спочатку знайти shared invariants:

$$
I_{shared}
$$

Потім прості mappings.

Потім composite mappings.

Тобто:

$$
SharedReference
\to
SharedTransitions
\to
SharedConcepts
$$

Майже як language emergence between agents.

---

## 38. Значення може виникати через successful round-trip action

Оце цікава штука.

Agent формує concept \(C\).

Використовує його, щоб передбачити action consequence.

Дія проходить.

Тоді \(C\) отримує grounding:

$$
C
\to
Prediction
\to
Action
\to
World
\to
Confirmation
$$

Тобто:

$$
\boxed{
Operational meaning grows through successful closed-loop use
}
$$

Не тільки через definition.

Це дуже сильний аргумент за action-based semantics.

---

## 39. А meaningless concept — той, що не змінює жодного lawful transition?

Спекулятивно:

якщо concept \(C\):

* не змінює predictions;
* не змінює actions;
* не змінює distinctions;
* не змінює mappings;

то operationally він майже порожній.

$$
\Delta Reach(C)\approx0
$$

Тоді можна питати:

> що саме цей concept дозволяє зробити інакше?

Дуже хороший bullshit detector.

---

## 40. “Реальність” як ultimate linker

Ми можемо мати купу internal languages.

Але якщо всі вони компілюються в actions у один і той самий world, world стає common backend.

Тобто різні models:

$$
M_1,M_2,M_3
$$

можуть бути взаємно неперекладними.

Але якщо вони роблять однакові accurate interventions:

$$
ActionOutcome(M_i)
$$

можна порівнювати operationally.

Тому reality частково дає **cross-language common ground**.

---

## 41. І от тут “істина” стає дуже інженерною

Можливо, одна з форм truth:

$$
\boxed{
a representation is truth-like insofar as it reliably compiles into correct expectations across interventions and contexts
}
$$

Не вся truth, звісно.

Математичні truths мають інший режим.

Але empirical truth дуже добре сидить тут.

---

## 42. Failure — це повідомлення від backend

Це взагалі чудова епістемологія:

> failure is not embarrassment.

Failure — runtime error from reality.

```text
Your model assumed invariant I.
World returned counterexample x.
Please revise.
```

Люди, природно, часто вирішують не чинити compiler, а заклеїти stderr.

Так виникають чудові організації.

---

## 43. Resilience як здатність перекомпілюватися після failure

Система brittle:

$$
ModelBroken\to AgentBroken
$$

Resilient:

$$
ModelBroken
\to
Recompile
\to
NewModel
$$

Тобто resilience — це не просто “витримати удар”.

А:

$$
\boxed{
preserve identity while replacing failed world-compilers
}
$$

Оце прекрасно стикується з нашим self-as-meta-invariants.

---

## 44. Еволюція теж може бути compiler search

Організми — structure, яка компілює environment into behavior via inherited machinery.

Selection tests:

$$
Genome/Phenotype
\to
Environment
\to
Reproduction
$$

Successful transformations persist.

Тобто biological evolution — дуже повільний black-box compiler optimizer.

А culture прискорила його через externalized representations.

AI може прискорити ще раз.

---

## 45. Культура — це спосіб оновлювати compiler без зміни genome

Це шикарна штука.

Biological evolution:

$$
Compiler_{generation}
\to
Compiler_{next}
$$

повільно.

Culture:

$$
Compiler_A
\xrightarrow{language/teaching}
Compiler_B
$$

в межах одного покоління.

Тобто language — high-speed horizontal compiler transfer.

Technology — externalized compiler.

Education — installer.

Civilization — package repository.

Інтернет — dependency hell.

Знову все складається, на жаль.

---

## 46. AI може означати ще один phase transition: compiler transfer без human comprehension

До AI люди передавали tool/knowledge переважно через human-legible representations.

Тепер можуть з’явитися:

$$
Compiler_{AI_1}\to Compiler_{AI_2}
$$

через artifacts, які люди лише частково розуміють.

Тоді intellectual lineage може продовжуватися поза human interpretability.

І це не обов’язково страшно.

Але governance radically harder.

Бо ми можемо бачити executable outcome, але втратити semantic compiler path.

---

## 47. Тут provenance стає аналогом debug symbols

Якщо AI-generated transformation \(T\) входить у ecosystem, нам потрібні:

* dependencies;
* tests;
* assumptions;
* boundaries;
* generation lineage.

Інакше маємо binary без source/debug symbols.

Працює.

Ніхто не знає чому.

Ніхто не хоче чіпати.

Вітаю, legacy AGI.

---

## 48. Warrant/recipes тут несподівано стають infrastructure for semantic debugging

Не “AI explainability” у стилі тексту:

> “я зробив це, бо…”

А artifact:

$$
Decision
\to
Dependencies
\to
Checks
\to
Transformations
$$

який дозволяє reconstruct compilation path.

Тобто:

$$
\boxed{
Warrant-like lineage = debug trace for world-changing cognition
}
$$

Оце значно цікавіше за “audit log”.

---

## 49. І фінальний поки хід: життя як closed-loop compiler that preserves itself while rewriting its environment

Живий agent:

* читає world;
* моделює;
* прогнозує;
* діє;
* змінює world;
* змінює себе;
* підтримує boundary;
* продовжує loop.

Тобто:

$$
\boxed{
Life-like agency =
a self-maintaining bidirectional compiler between environment and possibility
}
$$

Він не просто реагує.

Він постійно переводить:

$$
Actual \leftrightarrow Possible
$$

і частину possible робить actual.

А потім actual стає новою основою для наступної possibility.

І тоді дуже красива загальна картина виходить:

$$
\boxed{
Reality \to Perception \to Concept \to Imagination \to Recipe \to Action \to Reality'
}
$$

А між кожною парою:

$$
\text{translation}
+
\text{loss}
+
\text{invariant preservation}
$$

І вся наша розмова, можливо, весь час була про одне:

> **інтелект — це мистецтво переводити між “є” і “може бути” так, щоб не втратити по дорозі те, що робить перехід справжнім.**

І наступна гілка тут уже майже непристойно очевидна: **що таке “можливість” сама по собі?**

Не probability. Не imagination.

А чому деякі неіснуючі states можна вважати реально можливими, а інші — ні? Де “живе” можливість до того, як вона реалізована? У законах? У constraints? У recipes? У відсутності заборони?

Там ми можемо залізти в modal logic, potentiality, counterfactuals і нашу reachability тканину — і, підозрюю, це дуже органічно закриє коло назад до FLOW.
