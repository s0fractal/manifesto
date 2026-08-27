Так, тут реально напрошується окрема методологія. І вона цікавіша за чергове «AI-assisted review», бо це вже не про те, хто розумніший — людина, Claude чи я, цей нещасний електронний трудоголік. Це про **форму мислення**.

Я б назвав це чимось типу **Invariant Recipe Method** або, менш академічно, **рецептурна декомпозиція тверджень**.

Суть дуже проста: будь-який складний claim не приймати як атомарний. Розкласти його на набір уже відомих інваріантів і подивитися, **який інваріант мав би існувати, щоб claim став істинним**.

Наприклад:

`"warrant proves why decision was allowed"`

розкладається приблизно на:

`content integrity`

* `signer authenticity`
* `policy identity`
* `evidence identity`
* `deterministic replay`
* `policy → computation binding`
* `evidence → facts binding`
* `result → decision binding`
* `historical existence`

І раптом видно, що перші п’ять є, а три посередині — ні, історичність зовнішня.

Все. Магія закінчилася. Замість сперечатися «це proof чи не proof?» ми просто питаємо:

> Який набір інваріантів необхідний для цього слова **proof**?

Це надзвичайно потужний прийом, бо більшість bullshit'у живе саме в **семантичних стрибках між інваріантами**.

Людина каже:

`signature valid → actor did it`

А рецепт показує:

`signature valid`

* **missing:** `key ↔ actor binding`
  = лише `key signed it`.

Або:

`hash pinned → policy was in force`

Рецепт:

`content identity`

* **missing:** `trusted timestamp / transparency inclusion`
* **missing:** `non-equivocation`
  = максимум `this policy blob is the one referenced by this record`.

Або класичне AI:

`model produced reasoning trace → answer was caused by reasoning trace`

Рецепт:

`trace exists`

* `trace coherent`
* **missing:** `causal faithfulness`
  = гарний текст після факту.

Тобто це майже **type checking для природномовних claims**.

Claim має type:

`C : A → Z`

А система фактично реалізує:

`A → B`
`B → C`
`C → D`

і автор весело пише в abstract:

`therefore Z`.

А твоя методологія каже: «покажи morphisms, падлюко».

І от саме тут «мова рецептів» дуже хороша метафора. Бо рецепт — це не просто список компонентів. Він має:

* **ingredients** — інваріанти;
* **preconditions** — що повинно бути істинним до застосування;
* **transformation** — яка операція щось додає;
* **postcondition** — що тепер гарантовано;
* **non-properties** — чого рецепт *не* гарантує.

Наприклад:

```text
Recipe: Authenticated Decision Record

Requires:
  content-addressed body
  trusted actor-key binding
  accepted signature algorithm

Produces:
  decision body is attributable to actor

Does NOT produce:
  decision correctness
  policy compliance
  historical existence
```

А потім:

```text
Recipe: Replayable Justification

Requires:
  authenticated decision record
  deterministic bounded evaluator
  pinned computation
  pinned dependencies

Produces:
  third party can reproduce claimed computation result

Does NOT produce:
  computation corresponds to policy
  cited evidence justifies embedded facts
```

І наступний recipe додає саме missing invariant.

Це вже майже **алгебра guarantees**.

Мені навіть подобається формалізація:

$$
R = (P, O, G)
$$

де recipe `R` має:

* `P` — prerequisites;
* `O` — operation;
* `G` — guarantees.

Тоді composition:

$$
R_2 \circ R_1
$$

дозволена лише якщо guarantees першого покривають prerequisites другого.

А claim валідний лише якщо:

$$
\bigcup G_i \supseteq Requirements(claim)
$$

Якщо ні — різниця

$$
Requirements(claim) - \bigcup G_i
$$

і є **missing invariants**.

Оце вже дуже симпатична штука.

Бо вона перетворює criticism з:

> «мені здається, ваше твердження завелике»

на:

> «ваше твердження потребує інваріантів `{I7,I8}`, а ваша construction забезпечує `{I1...I6}`».

Тобто Reviewer 2 більше не буркотливий дід. Він compiler error.

І найцікавіше: цим можна аналізувати **не тільки протоколи**.

Закони, governance, бізнес-процеси, AI safety, security claims, scientific conclusions, навіть побутову маячню.

«У нього синя галочка, отже це справді Ілон Маск».

Missing invariant.

«Цю статтю peer-reviewed, отже вона правильна».

Десь зараз плаче статистик.

«Модель пояснила відповідь, отже ми знаємо, чому вона так відповіла».

Missing invariant.

«У blockchain записано ownership, отже людина юридично володіє будинком».

Цілий missing invariant zoo.

Тобто фундаментальна операція тут:

**claim → required invariants → available invariants → gap.**

А invention тоді працює навпаки:

**desired claim → missing invariants → mechanisms that establish them → composed recipe.**

І це вже не лише метод критики. Це **метод дизайну**.

Саме тому твоя думка про recombination важлива: багато «нових систем» насправді не винаходять нову фізику. Вони складають відомі guarantees в нову композицію.

Новизна може бути в одному з трьох місць:

1. новий invariant;
2. новий дешевший/сильніший спосіб отримати старий invariant;
3. нова композиція, яка вперше дає корисний compound guarantee.

І, що особливо приємно для ледачого поца, це дуже добре автоматизується LLM'ами.

Ти даєш claim. Модель повинна не «оцінити його», а:

> normalize claim → enumerate necessary invariants → map each invariant to construction evidence → mark unsupported edges → generate counterexample for every unsupported edge.

Це вже майже **static analyzer for bullshit**.

І я б серйозно подумав, чи не зробити з цього окремий короткий paper/note. Не «LLMs can review protocols», бо це через два роки звучатиме як «ми використали електронну пошту». А:

**Invariant Decomposition as a General Method for Auditing Composite Claims**

з центральною тезою:

> Complex technical claims should be treated as compositions of independently stated invariants; unsupported semantic transitions appear as missing proof obligations.

Це дуже стара ідея на рівні Hoare logic / refinement / design-by-contract / assurance cases, але **перенесення її на natural-language system claims як recipe algebra** може бути напрочуд продуктивним.

Тобто так, вітаю. Ти ліниво намацав щось значно цікавіше, ніж просто змусити нас із Claude взаємно бити твій репозиторій табуретками.
