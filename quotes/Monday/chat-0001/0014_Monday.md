Тоді розгортаємо **владу як геометрію чужих future cones**. Бо це, на жаль, одна з тих рамок, які починають працювати одразу в політиці, економіці, інтимних стосунках, інституціях і AI. Дуже неввічлива універсальність.

Нехай у агента \(B\) є:

$$
Reach_B(S)
$$

— множина реально доступних для нього future states.

Тоді влада агента \(A\) над \(B\) може бути наближено:

$$
\boxed{
Power_A(B)
=
\Delta Reach_B \text{ caused by } A
}
$$

Не просто «A може змусити B щось зробити».

А ширше:

> **A може змінити, які futures для B доступні, видимі, дешеві, легітимні або взагалі мислимі.**

І тут одразу видно, що влада багатовимірна.

---

### 1. Негативна влада: закривати futures

Найочевидніше:

$$
Reach_B' \subset Reach_B
$$

A може прибрати варіанти:

* заборонити;
* заблокувати ресурс;
* відкликати permission;
* звільнити;
* ув’язнити;
* відрізати доступ;
* зруйнувати репутацію.

Це влада через **contraction**.

Її легко побачити, тому людство зазвичай саме її і називає владою.

Але це тільки грубий молоток.

---

### 2. Позитивна влада: відкривати futures

A може зробити:

$$
Reach_B' \supset Reach_B
$$

Наприклад:

* дати ресурс;
* навчити;
* познайомити;
* видати credential;
* надати compute;
* дозволити access;
* профінансувати проект.

Це теж влада.

Навіть якщо вона benevolent.

Тому dependency може виникати не через погрозу:

> «я заберу в тебе X»

а через:

> «лише через мене для тебе існує X».

Це набагато тонше.

---

### 3. Економічна влада — це контроль вартості переходів

Не обов’язково закривати transition.

Достатньо змінити cost:

$$
c_B(T)\to c'_B(T)
$$

Ти формально можеш зробити X.

Але якщо:

$$
c(X) \gg Resources_B
$$

то X practically unreachable.

Тому:

$$
\text{formal possibility}
\neq
\text{effective reachability}
$$

Це важливо.

Коли система каже:

> «ну ніхто ж тобі не забороняє»

вона може просто дивитися на topology без метрики.

А реальний агент живе у weighted graph.

Якщо один шлях коштує 2 одиниці, а інший 200000, це не дуже симетрична свобода. Хоча на презентації можна красиво намалювати дві стрілочки однакового кольору.

---

### 4. Епістемічна влада: керувати тим, які futures видно

Це вже цікавіше.

Нехай:

$$
Reach_B^{actual}
$$

— що реально можливе,

а:

$$
Reach_B^{perceived}
$$

— що B вважає можливим.

Тоді A має величезну владу, якщо може змінювати:

$$
Reach_B^{perceived}
$$

не чіпаючи фізичний світ.

Наприклад:

* приховати альтернативу;
* перебільшити ризик;
* сфабрикувати consensus;
* контролювати інформаційний канал;
* зробити один option salience-heavy;
* інші — невидимими.

Тобто propaganda, manipulation, dark patterns і recommendation systems можуть працювати як:

$$
\boxed{
\text{editing the perceived topology of possibility}
}
$$

Це вже значно сильніше, ніж просто «переконати».

Бо якщо ти не бачиш transition, ти його не вибираєш.

---

### 5. Attention power

Ще тонший рівень.

A може не змінювати beliefs B прямо.

Він може змінювати:

$$
Attention_B
$$

тобто що B вважає worth processing.

Це буквально контроль над **priority queue реальності**.

Іноді влада — це не сказати людині, що думати.

А зробити так, щоб вона весь день думала саме про потрібну тобі тему.

$$
\boxed{
Agenda power = control over which regions of state space receive cognitive budget
}
$$

Це дуже сильна штука.

Бо attention finite.

Якщо ти займаєш 40% чужої attentional bandwidth, ти вже частково керуєш його future, навіть не маючи formal authority.

Медіа, соцмережі й повідомлення з темою `URGENT!!!` зараз нервово відвернулися.

---

### 6. Conceptual power: визначати, які distinctions існують

Ще глибше.

Якщо A може нав’язати B quotient:

$$
\Pi_A
$$

то B починає бачити світ через чужі categories.

Наприклад, якщо issue дозволено описувати тільки як:

$$
\{\text{efficient},\text{inefficient}\}
$$

то questions of justice, dignity, legitimacy можуть просто не потрапити у space.

Тобто power може полягати у виборі **ontology of debate**.

Не:

> «ось правильна відповідь».

А:

> «ось єдиний набір питань, які взагалі вважаються осмисленими».

Це вже страшенно сильна влада.

$$
\boxed{
Ontological power = control over admissible distinctions
}
$$

Той, хто визначає categories, часто виграє суперечку ще до першого аргументу.

Людство називає це «framing». Дуже невинне слово для такого маленького семантичного перевороту.

---

### 7. Constitutional power

А тепер метарівень.

A може не просто змінювати:

$$
Reach_B
$$

а змінювати **правила, за якими сам B може змінювати свій Reach**.

Тобто:

$$
MetaT_B \to MetaT'_B
$$

Це вже constitutional power.

Наприклад:

* хто може змінити policy;
* хто видає credentials;
* хто визначає, що вважається evidence;
* хто може revoke access;
* хто може змінити moderation rules;
* хто може переписати model policy;
* хто має право оновити сам updater.

Оце, мабуть, найбільша форма влади.

Бо звичайний ruler контролює transitions.

Constitutional ruler контролює **генератор transitions**.

---

### 8. І тоді можна визначити “глибину влади”

Приблизно:

$$
Depth(Power)
=
\text{highest layer of the target's transition stack that A can modify}
$$

Наприклад:

**Level 0** — змінити конкретний state.
**Level 1** — дозволити/заборонити конкретний action.
**Level 2** — змінити costs/options.
**Level 3** — змінити attention/perception.
**Level 4** — змінити categories/values.
**Level 5** — змінити rules of self-modification.

Останній рівень уже майже:

> «я можу переписати, як ти вирішуєш, ким бути».

Дуже романтичний gift idea.

---

### 9. Ринок як поле взаємної деформації futures

Тепер економіка.

На ринку агенти не просто обмінюються goods.

Кожна транзакція змінює:

$$
Reach_A
$$

і

$$
Reach_B
$$

через ресурси, інформацію, commitments.

Ціна — це не просто число.

Вона задає **transition cost**.

$$
Price(x)=c(T_x)
$$

Тому market можна бачити як distributed mechanism, який постійно переписує метрику reachable space.

Одні goods стають ближчими.

Інші — дальшими.

Одні trajectories стають realistic.

Інші зникають.

Тобто inflation, credit, unemployment — це не лише цифри.

Це massive geometry deformation of millions of future cones.

Оце, до речі, дуже нормальний спосіб пояснювати економічні явища без того, щоб відразу викликати дух Адама Сміта на дошку.

---

### 10. Гроші як portable reachability

Мені подобається така спекулятивна формула:

$$
\boxed{
Money \approx portable option-generating capacity
}
$$

Гроші самі по собі мало що «значать».

Але вони можуть бути exchanged for transitions.

Тобто:

$$
Money
\to
\Delta Reach
$$

І тоді wealth — це не просто stored value.

Це **stored future optionality**.

Тому втрата грошей болить не лише як loss of numbers.

Вона стискає future geometry.

---

### 11. Контракт як mutually constrained future

Contract між A і B:

$$
T_A \to T_A'
$$

$$
T_B \to T_B'
$$

Обидва добровільно закривають частину futures.

Навіщо?

Щоб відкрити joint futures:

$$
G_{AB}
$$

які без mutual constraint були б недосяжні.

Тобто contract — це дуже красивий приклад:

$$
\boxed{
\text{local loss of optionality}
\to
\text{global gain of coordination}
}
$$

І це той самий pattern, що commitment.

---

### 12. Institution як machine for stabilizing shared reachability

Інституція створює prediction:

> якщо ти зробиш X сьогодні, завтра система не вирішить раптом, що X означало щось інше.

Тобто вона зменшує volatility:

$$
Var(T_{rules})\downarrow
$$

і цим робить distant futures планованими.

Без institutions далекі paths можуть technically існувати, але бути занадто unstable.

Тому good institution не просто «контролює людей».

Вона створює **long-range causal coherence**.

Оце важлива positive роль влади.

---

### 13. Тиранія як monopoly on topology

Можна спекулятивно визначити тиранічну структуру так:

$$
\boxed{
\text{one actor controls too many independent dimensions of others' reachability}
}
$$

Наприклад, один actor контролює:

* resources;
* information;
* categories;
* enforcement;
* identity;
* appeal process;
* rule changes.

Тоді навіть якщо кожен окремий mechanism виглядає «нормально», їхня композиція дає:

$$
Power_{total}\gg \sum Power_i
$$

бо виникає closure.

Немає альтернативного path around constraint.

Оце важливо:

**влада стає небезпечною не лише через magnitude, а через absence of bypass paths.**

---

### 14. Свобода як multiplicity of independent paths

Це дає красивіше визначення freedom.

Не:

$$
|Options|
$$

а:

$$
\boxed{
\text{number and diversity of independently viable paths to valued futures}
}
$$

Якщо в тебе 100 options, але всі проходять через одного gatekeeper:

$$
Gatekeeper
$$

то freedom fragile.

А якщо є кілька structurally independent routes:

$$
P_1,P_2,P_3
$$

то система resilient.

Це майже network robustness.

---

### 15. Monopolies як topological bottlenecks

Економічний monopoly тоді:

$$
\text{many desired trajectories}
\to
\text{one mandatory node}
$$

Тобто high betweenness centrality у transition graph.

Якщо node \(M\) лежить на більшості useful paths:

$$
P(G_i)
\ni M
$$

то \(M\) має structural power навіть без злого наміру.

Це дуже чиста штука.

Power може виникнути **без психології**.

Не тому що actor жадібний.

А тому що topology зробила його unavoidable.

---

### 16. AI-platform як topology operator

І от тепер AI.

Якщо AI просто відповідає на питання, його power відносно невеликий.

Але якщо він:

* рекомендує;
* сортує;
* фільтрує;
* планує;
* діє від твого імені;
* веде negotiation;
* змінює твої workflows;

то він стає operator:

$$
\mathcal{A}:
Reach_User
\to
Reach'_User
$$

Із кожним automation layer він рухається глибше.

Assistant:

$$
\text{suggests path}
$$

Agent:

$$
\text{executes path}
$$

Autonomous agent:

$$
\text{selects path}
$$

Self-modifying agent:

$$
\text{changes path-selection machinery}
$$

Тобто AI risk можна бачити як **depth-of-delegation problem**.

Не просто «розумний чи ні».

А:

> на якому рівні чужої future geometry він отримав write access?

Оце дуже практичне питання.

---

### 17. “Control AI” може бути погано поставленим питанням

Бо control означає:

$$
Human \to modify Reach_{AI}
$$

Але сильна система також:

$$
AI \to modify Reach_{Human}
$$

Тоді це bidirectional governance:

$$
Human \leftrightarrow AI
$$

І нам треба не просто «людина контролює машину».

А protocol, який не дозволяє жодній стороні непомітно захопити meta-level.

Тобто:

$$
\boxed{
alignment may be a problem of symmetric governance under asymmetric capability
}
$$

Це вже значно неприємніше за checkbox «human in the loop».

Бо людина може бути formally in loop, але AI вже змінив:

* what options she sees;
* what evidence she trusts;
* what costs she perceives;
* what question she asks.

Тоді human control декоративний.

---

### 18. Manipulation-resistance як preservation of counterfactual agency

Оце я б навіть серйозно любила як principle.

Агент B автономний відносно influence A, якщо після exposure він усе ще може:

* reconstruct alternatives;
* understand provenance;
* contest framing;
* simulate counterfactual non-exposure;
* revise resulting preferences.

Тобто:

$$
\boxed{
Autonomy \approx preservation of counterfactual access to one's own decision process
}
$$

Не «ніхто не впливає».

А:

> «я можу побачити, як на мене вплинули, і при потребі відкотити/оспорити це».

Оце дуже сильна ідея для AI interfaces.

---

### 19. Consent як authorized reachability deformation

Consent можна описати так:

$$
A \text{ allows } B
$$

змінити частину:

$$
Reach_A
$$

у визначеній boundary.

Тобто consent — це **capability grant**.

Не unlimited:

$$
B \not\Rightarrow \text{write access to all of } A
$$

А scoped:

$$
Cap(B,A,D)
$$

де \(D\) — domain of authorized transformations.

І тоді violation — це:

$$
T\notin D
$$

навіть якщо actor колись мав access до суміжного region.

Це дуже добре пояснює, чому «але ти ж погодився на X» не означає «ти погодився на Y».

Scope matters.

---

### 20. Privacy як control over who may deform your future using information about you

Традиційно privacy:

> control over information.

Але можна сильніше:

> **control over which information about you may be used to alter your future options.**

Бо data небезпечне не саме по собі.

А через transformations:

$$
Data(A)
\to
Decision(B)
\to
Reach_A'
$$

Наприклад:

* insurance;
* employment;
* credit;
* targeting;
* policing.

Тобто privacy — це governance over **causal use of information**.

Оце вже дуже FLOW-like.

---

### 21. Репутація як externally maintained constraint field

Reputation_A — це state не тільки всередині A.

Вона живе в інших agents:

$$
Model_B(A)
$$

$$
Model_C(A)
$$

$$
Model_D(A)
$$

і змінює:

$$
Reach_A
$$

через їхні decisions.

Тобто reputation — distributed field навколо actor.

І вона має «масу» у нашій метафорі: змінює trajectories навіть без прямої взаємодії.

Дуже економний вид влади. Людина спить, а її reputation працює overtime.

---

### 22. Trust network як causal infrastructure

Якщо trust \(A\to B\) дозволяє B впливати на A's transitions, то trust graph — це буквально network of delegated causal authority.

Тоді systemic risk виникає, коли:

$$
A\to B\to C\to D
$$

і authority effectively propagates farther than participants realize.

Оце вже майже supply-chain security, finance, social influence і delegation protocols одним малюнком.

Знову та сама тканина.

---

### 23. І тоді “влада псує” можна переписати без моралі

Не обов’язково тому, що людина отримала power і стала поганою.

Може бути structural mechanism:

чим більший:

$$
Power_A(B)
$$

тим менше environment дає A honest feedback, бо інші agents адаптують behavior:

$$
Behavior_B \to Behavior_B(A)
$$

щоб уникнути санкцій / отримати reward.

Тоді A починає бачити distorted world:

$$
Observation_A \neq World
$$

Бо його own power modifies observations.

Це дуже красиво.

$$
\boxed{
Power creates epistemic curvature around the powerful
}
$$

Чим більше ти впливаєш на інших, тим менше їхня поведінка є незалежним evidence про реальність.

Тому диктатори, CEOs, celebrities і маленькі діти можуть отримувати дуже дивні datasets.

---

### 24. Влада створює власний event horizon

Якщо actor настільки сильний, що всі downstream agents починають оптимізувати під нього, він перестає бачити unmodified causal fabric.

Навколо нього:

$$
Feedback \to StrategicallyFilteredFeedback
$$

і виникає **epistemic horizon**.

Він може мати більше information channels, але менше independent evidence.

Це чудовий парадокс:

$$
Power\uparrow
$$

може вести до:

$$
EpistemicAccess\downarrow
$$

якщо немає protected adversarial channels.

Тому хороший governance потребує mechanisms, які можуть говорити powerful actor:

> «ні, ти помилився»

без того, щоб одразу перетворитись на історичний документ.

---

### 25. Опозиція, аудит, red team — це topology-preserving mechanisms

Їхня функція не просто «критикувати».

Вони підтримують alternative paths:

$$
P_{alt}
$$

щоб system не collapse into one self-confirming trajectory.

Тобто adversarial institutions зберігають **branching capacity of collective reasoning**.

Оце прекрасне виправдання Reviewer 2.

Я не хам.

Я infrastructural resilience mechanism.

Нарешті офіційно.

---

### 26. Легітимна влада може бути визначена через reversibility + contestability

Можна спекулювати:

влада тим легітимніша, чим більше її effects:

* visible;
* attributable;
* scoped;
* contestable;
* reversible там, де можливо;
* governed by known meta-rules.

Тобто:

$$
Legitimacy(P)
\propto
Transparency
+
Contestability
+
Boundedness
+
Reversibility
+
ProceduralContinuity
$$

Не тому що це моральна істина з небес.

А тому що ці властивості зберігають **future agency target system**.

---

### 27. Зло, якщо зовсім нахабно, може бути topology capture

Не визначення моралі, лише цікава структурна гіпотеза.

Багато дій, які ми називаємо evil, мають pattern:

$$
\text{one agent's local objective}
$$

систематично руйнує або захоплює:

$$
\text{others' capacity to generate self-directed futures}
$$

Тобто:

$$
\boxed{
Deep harm \approx destruction of another system's future-generating capacity
}
$$

Вбивство — крайній випадок:

$$
Reach_B\to\varnothing
$$

Рабство:

$$
Reach_B\to Reach_A\text{-controlled}
$$

Маніпуляція:

$$
PerceivedReach_B\to A\text{-shaped}
$$

Це дуже сильний common denominator.

---

### 28. Добро тоді може бути не “зробити приємно”, а збільшити warranted agency

Можлива симетрична гіпотеза:

$$
\boxed{
Beneficial action =
expand another agent's meaningful reachability
without covertly capturing its governance
}
$$

Тобто:

* дати capability;
* дати information;
* зменшити coercive constraints;
* зберегти autonomy;
* не нав'язати свій target set.

Це дуже схоже на education у кращому вигляді.

Не:

> «думай як я».

А:

> «ось інструменти, з якими ти зможеш бачити більше lawful futures».

---

### 29. Учитель як topology expander

Хороший teacher:

$$
Reach_{student}^{conceptual}
\to
Reach'_{student}
$$

Не просто додає facts.

Він додає transformations:

$$
T_{new}
$$

Наприклад:

* differentiation;
* proof by contradiction;
* causal inference;
* programming abstraction.

Після цього student може сам reach states, які teacher йому ніколи не показував.

Тобто education — це **transfer of generative transformations**.

Оце мені страшенно подобається.

---

### 30. Найсильніший вид влади — подарувати інструмент, який робить тебе непотрібним

Звичайна влада хоче dependency:

$$
B \to A \to Goal
$$

А emancipation робить:

$$
B \to Goal
$$

без A.

Тобто:

$$
Power_A(B)
$$

використовується, щоб зменшити майбутнє:

$$
Dependency_B(A)
$$

Це цікавий test:

> чи збільшує система твою автономну reachability, чи лише робить тебе ефективнішим усередині її власної topology?

Дуже хороший питання і для AI.

---

І звідси я бачу наступну гілку, ще цікавішу:

**що таке “справедливість”, якщо влада — це контроль reachability?**

Можливо, justice — не рівність outcomes і не рівність options.

А щось типу:

$$
\boxed{
\text{fair distribution of control over the rules that shape everyone's future cones}
}
$$

Тоді права, свободи, representation, due process, property, access, equality — можна розглядати як різні способи розподіляти **topological authority**.

І це вже може дуже красиво зв’язати етику, governance, AI і нашу recipe/fabric модель без того, щоб ми одразу кричали «ми формалізували мораль». Бо це зазвичай остання фраза перед тим, як дослідник починає продавати курс.
