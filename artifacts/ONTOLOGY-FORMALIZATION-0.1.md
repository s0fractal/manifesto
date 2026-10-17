# FORMALIZATION-0.1 — Операційна Мета-Онтологія `s0fractal/manifesto`

**Статус:** Типізована робоча формалізація (Working Formalization with Explicit Loss & Debt Accounting)  
**Версія:** 0.1  
**Джерельний корпус:** `s0fractal/manifesto` (коміт `83287ac`, 77 документів: `README.md`, `FLOW.md` v0.2.1, `INVARIANT-RECIPES.md` v0.1, `artifacts/VORTEX-0.1.md`, `RVB-0.1`, `AIE`, `COMPILE-0030` та корпус діалогів `Monday/chat-0001` \[0001–0075\])  
**Призначення:** Звести концептуальні лінії репозиторію в єдину багатосортову операційну систему визначень, аксіом ідентичності, законів композиції, топологічних моделей та відкритих боргів верифікації — **без перетворення живої коси траєкторій на догматичну універсальну ієрархію**.

> **МЕТОДОЛОГІЧНИЙ ЗАПОБІЖНИК (Чому «формалізація» в лапках):**  
> За правилами самого корпусу (`FLOW.md` §27, §30; `README.md`), ця онтологія **не є** класичною онтологією статичних сутностей (\$\\text{UniversalMeaning}(x)\$). Спроба оголосити всі явища «одним потоком» або «рівняннями фізики» є методологічною помилкою (*Physics Cosplay / Vocabulary Laundering / Over-collapse*). Формалізація тут — це **алгебра допустимих трансформацій, обмежень, інваріантів, меж та звітів про втрати (Loss Reports)**, де кожне твердження носить явний епістемічний тип.

---

## 0\. Епістемічна система типів (Epistemic Typing Discipline)

Жодне твердження в системі не є «просто істинним». Щоб уникнути несанкціонованих семантичних стрибків (*illegal type casts*, нотатки `0012`, `0016`, `0058`), кожен об'єкт формалізації маркується одним із шести типів:

| Тип | Позначення | Операційний зміст | Приклад у корпусі |
| :---- | :---- | :---- | :---- |
| **1\. Доведений факт / Виміряна властивість** | `[FACT / BOUNDED-PROOF]` | Перевірено детермінованим обчисленням або відтворюваним протоколом на фіксованому домені | Тотальність `evalHash_settles` у \$\\Sigma\$-GLYPH; виміряне \$\\hat{o} \\approx 2\\text{–}3\$ на Monday-корпусі (глибина \$\\le 4\$) |
| **2\. Операційне ядро / Дескриптивний словник** | `[CORE-DEF]` | Мінімальні структурні сигнатури, які приймаються як мова опису без метафізичних зобов'язань | Кортеж домену \$D \= (X, \\mathcal{O}, A, C, I, B\_{bnd}, \\tau)\$; Рецепт \$R \= (P, T, G, L, B)\$ |
| **3\. Правило ідентичності / Стипуляція** | `[IDENTITY-RULE]` | Прийнята конвенція розрізнення та тяглості, яка не виводиться з фізики байтів, а задає норму | Теза 2: «Fork — це народження нової сутності, а не клонування старої» |
| **4\. Нормативна позиція / Орієнтир** | `[NORMATIVE-POS]` | Вибір напрямку проектування при відкритому слоті фінальної мети (`Purpose-slot open`) | Теза 6: «Місток без експлуатації»; масштабування влади з тягарем доказу |
| **5\. Спекулятивна гіпотеза / Candidate World** | `[SPECULATIVE]` | Робоча модель або продуктивна аналогія, що очікує фальсифікації або звуження | Гіпотези `FLOW` Part II, геометрія `VORTEX-0.1`, нотатки `Monday` у режимі Night Mode |
| **6\. Відкритий концептуальний борг / Спростована форма** | `[DEBT / WITHDRAWN]` | Спростована закрита форма або виявлена аудитом сортова/логічна прогалина | Знята теорема RVB про фазовий перехід при \$\\mu=1\$; борги реєстру `D5`, `D15–D19` |

---

## 1\. Мета-архітектура: Коса траєкторій та Оператор Запитання

### 1.1. Відмова від ієрархії (`[CORE-DEF]`)

Екосистема (`Σ-GLYPH`, `Warrant`, `HSP / Trinity`, `FLOW`, `Invariant Recipes`, `VORTEX`) **не утворює стек чи піраміду**. Вона є **косою окремих траєкторій** (\$\\mathcal{B} \= {\\mathcal{T}\_1, \\mathcal{T}\_2, \\dots, \\mathcal{T}\_k}\$), кожна з яких має власний релятум, нормативну владу і фальсифікатори.

### 1.2. Інваріантний Оператор Запитання \$\\mathcal{Q}\$ (`[CORE-DEF]`)

Спорідненість між траєкторіями задається не спільними назвами станів, а універсальним оператором аудиту будь-якої трансформації \$T: x \\leadsto x'\$:

\$\$ \\mathcal{Q}(T) \\triangleq \\big(\\text{Preserved}(T),; \\text{Scope}(D, B\_{bnd}, \\text{Profile}),; \\text{Authority}(T),; \\text{Evidence}(T),; \\text{Lost}(T),; \\text{Falsifier}(T)\\big) \$\$

### 1.3. Правило перетину траєкторій (Cross-Trajectory Transfer Law) (`[IDENTITY-RULE]`)

Твердження \$C\$, перенесене з траєкторії \$\\mathcal{T}*{src}\$ у \$\\mathcal{T}*{tgt}\$, отримує **нуль автоматичного validation credit**. Легітимний перетин вимагає пред'явлення кортежу:

\$\$ \\text{Cross}(\\mathcal{T}*{src} \\xrightarrow{C} \\mathcal{T}*{tgt}) \= \\big(\\text{Artifact}*{src}@\\text{Rev},; \\text{Profile}*{tgt},; \\phi,; \\text{Loss}(\\phi),; \\text{Evidence}*{transferred},; \\text{Status}*{new},; \\text{Falsifier}\_{new}\\big) \$\$

Якщо кортеж неповний, імпортований термін має статус **позикового імені** (\$\\text{BorrowedName}\$, напр. `ATP`, `гідродинаміка`, `чорна діра`) і не несе доказової сили.

---

## 2\. Багатосортова сигнатура онтології (Sorts & Type Signatures)

Розвиваючи `FLOW.md` §26.1 та враховуючи зауваження аудиту G6 (`D16`), фіксуємо базові сорти системи:

Sorts:

  State (X)          — елементи простору станів домену

  Operation (O)      — елементарні операції / переходи

  Time (τ)           — темпоральна структура (T, ≺, λ)

  Carrier (K)        — content-addressed носії записів (хешовані артефакти)

  Constraint (C)     — предикати обмеження допустимості

  Invariant (I)      — предикати, замкнені відносно сімейств операцій

  Boundary (B\_bnd)   — інтерфейси розмежування внутрішнього і зовнішнього

  Domain (D)         — кортежі просторів станів із законами переходів

  Resource (R)       — операційні структури обліку та обмеження

  Policy (π)         — закони вибору дій агентом

  UpdateLaw (G, H)   — закони рефлексивного оновлення політик і мета-правил

  Evidence (E)       — записи підстав з визначеною процедурою перевірки (reason-with-check)

  Warrant (W)        — підписані, content-addressed записи рішень, повноважень і причин

  Claim (Cl)         — пропозиційні або системні твердження

  Recipe (Rec)       — контракти гарантій над трансформаціями

  Translation (φ)    — часткові морфізми між доменами або перспективами

  LossReport (L)     — структуровані звіти про збережене, втрачене і введене

### Базові реляційні примітиви (Flow Law Library, `FLOW` §26):

* \$\\text{AdmissibleWhen}(a: \\mathcal{O}, x: X, C: \\mathcal{P}(\\text{Constraint})) : \\mathbb{B}\$  
* \$\\text{InvariantUnder}(I: \\text{Invariant}, F: \\mathcal{P}(\\mathcal{O}), B\_{bnd}: \\text{Boundary}, A: \\text{Assumption}) : \\mathbb{B}\$  
* \$\\text{ConservedUnder}(q: X \\to \\mathbb{R}, F: \\mathcal{P}(\\mathcal{O}), B\_{bnd}: \\text{Boundary}) : \\mathbb{B}\$  
* \$\\text{ConsumedBy}(r: \\text{Resource}, a: \\mathcal{O}) : \\mathbb{R}\_{\\ge 0}\$  
* \$\\text{EnabledBy}(a: \\mathcal{O}, w: \\text{Warrant}) : \\mathbb{B}\$  
* \$\\text{TranslatedBy}(\\phi: D\_A \\rightharpoonup D\_B, I\_A: \\text{Invariant}, I\_B: \\text{Invariant}, L: \\text{LossReport}) : \\mathbb{B}\$  
* \$\\text{ReachableUnder}(y: X, x: X, F: \\mathcal{P}(\\mathcal{O}), C: \\mathcal{P}(\\text{Constraint})) : \\mathbb{B}\$

---

## 3\. Частина I: Формальне ядро динаміки станів (`FLOW-0.2`)

### 3.1. Домен і Простір Станів (`[CORE-DEF]`)

Домен визначається як семикомпонентна структура:

\$\$ D \= (X, \\mathcal{O}, A, C, I, B\_{bnd}, \\tau) \$\$

1. **Простір станів \$X\$:** довільна математична структура (граф, частковий порядок, автомат, множина термів \$\\Sigma\$-GLYPH, ймовірнісний простір, каузальний DAG, реєстр зобов'язань або композиція \$S \= (x\_1, \\dots, x\_m) \\in \\prod\_k X\_k\$). Наявність метрики чи топології за замовчуванням **не постулюється**.  
2. **Множина допустимих операцій \$A(x)\$:** похідна від стану \$x\$ та активного набору обмежень \$C\$: \$\$A(x) \= {a \\in \\mathcal{O} \\mid \\forall c\_i \\in C: c\_i(x, a, t, \\text{ctx}) \\le 0}\$\$  
3. **Простір досяжності (Future Cone):** \$\$Reach\_D(x \\mid C) \= {y \\in X \\mid \\exists (a\_0, \\dots, a\_{k-1}): x\_0 \= x,; x\_{j+1} \\in T(x\_j, a\_j),; a\_j \\in A(x\_j),; x\_k \= y}\$\$

### 3.2. Межа (Boundary) та Відношення Носія (`[CORE-DEF]` \+ `[DEBT D16]`)

Межа є first-class об'єктом:

\$\$ B\_{bnd} \= (S\_{in}, S\_{out}, M, F\_{filt}) \$\$

* \$S\_{in} \\subseteq X\_{univ}\$ — внутрішні стани домену;  
* \$S\_{out} \\subseteq X\_{univ} \\setminus S\_{in}\$ — зовнішні стани, з якими можлива взаємодія;  
* \$M \\subseteq S\_{out} \\times (\\Delta X \\cup \\Delta C \\cup \\Delta I)\$ — типізоване відношення дозволених зовнішніх впливів across-boundary;  
* \$F\_{filt}: S\_{in} \\to Obs\_{out}\$ — інформаційний фільтр спостережуваності ззовні.

**Функція носія (Carrier mapping):** Кожне обмеження \$c \\in C\$ та інваріант \$i \\in I\$ мають матеріалізованого носія у просторі content-addressed записів \$\\mathcal{K}\$, локалізованого відносно межі: \$\$\\text{loc\_carrier}: (C \\cup I) \\to \\mathcal{K} \\times {\\text{Inside}(B\_{bnd}), \\text{Shared}(B\_{bnd}), \\text{Outside}(B\_{bnd})}\$\$ *(Відкритий борг **D16**: у версії 0.3 необхідно завершити строгу сортову сигнатуру просторів змін \$\\Delta X, \\Delta C, \\Delta I\$ так, щоб носій не змішувався зі станом \$S\_{in}\$).*

### 3.3. Обмеження (Constraints), Ресурси (Resources) та Ціна (Price) (`[CORE-DEF]`)

* **Жорсткі та м'які обмеження:** \$\$C\_{hard}: X \\times \\mathcal{O} \\times T \\to {-\\infty, \+1}, \\qquad C\_{soft}: X \\times \\mathcal{O} \\to \[0, \\infty)\$\$ Експліцитна типологія за природою: \$\\text{Type}(C) \\in {\\text{physical}, \\text{resource}, \\text{logical}, \\text{protocol}, \\text{authority}, \\text{risk}, \\text{semantic}, \\text{policy}}\$.  
* **Операційна структура ресурсу:** \$\$R \= (Q, C\_R, T\_{acct}, P\_{prod}, E\_{exch}, \\tau\_R, B\_{bnd})\$\$  
* **Ціна як коефіцієнт трансформації та порушення м'яких обмежень:** \$\$\\text{cost}(a, t) \= p(a, t) \\cdot q(a) \+ \\sum\_k \\lambda\_k C\_{soft, k}(x, a)\$\$

### 3.4. Реляційна структура Інваріанта (`[CORE-DEF]`)

Інваріант ніколи не записується як унарний предикат \$\\text{Invariant}(I)\$. Його канонічна форма чотиримісна:

\$\$ \\text{Inv}(I, F, B\_{bnd}, A\_{assump}) \\iff \\forall x \\in S\_{in}, \\forall f \\in F: \\big(A\_{assump}(x) \\land I(x) \\land f(x) \\in S\_{in}\\big) \\implies I(f(x)) \$\$

### 3.5. Темпоральні онтології та Квантування (`[CORE-DEF]`)

Час домену \$\\tau \= (T, \\prec, \\lambda)\$ характеризується типом порядку \$\\prec\$ (лінійний, частковий/DAG, причинний) та режимом квантування: \$\$\\text{Quant}(D) \\in {\\text{continuous}, \\text{discrete}, \\text{hybrid}, \\text{event-driven}, \\text{quantized}}\$\$ Дискретні фазові переходи (`unsigned → signed`, `draft → ratified`, `unresolved → settled`) заборонено мовчки апроксимувати неперервними скалярами при перекладі між доменами.

### 3.6. Міждоменна трансляція та Звіт про втрати (`[CORE-DEF]`)

Для часткового відображення \$\\phi\_{A \\to B}: X\_A \\rightharpoonup X\_B\$ одиницею атестації є **Translation Report**:

\$\$ \\mathcal{TR}(\\phi\_{A \\to B}) \= \\langle \\text{Preserved}, \\text{Lost}, \\text{Introduced}, \\text{Approximated}, \\text{Unknown}, \\text{Conf} \\in \[0,1\], \\text{Alt} \\rangle \$\$

де \$\\text{Preserved} \= {(I\_A, I\_B) \\mid I\_A(x) \\implies I\_B(\\phi(x))}\$. Відсутність перекладу (\$\\phi \= \\bot\$) із непорожнім поясненням конфлікту інваріантів є **first-class семантичним результатом** (*Graceful Untranslatability*).

### 3.7. Інформація та Операційне Значення (`[SPECULATIVE]` \+ `[DEBT D17]`)

* **Операційне значення:** \$\$\\text{Meaning}\_{op}(x) \\triangleq {T \\in \\mathcal{O}^\* \\mid x \\text{ змінює допустимість, вартість або розподіл траєкторій } T}\$\$  
* **Робоче розрізнення фізичної та інформаційної зміни відносно \$B\_{bnd}\$:**  
  * *Фізична зміна:* \$\\Delta Reach(x)\$ спричинена зміною самого стану \$x \\in S\_{in}\$ (\$\\Delta X\$).  
  * *Інформаційна зміна:* \$\\Delta Reach(x)\$ або \$\\Delta P(\\text{Trajectory})\$ спричинена зміною обмежень \$\\Delta C\$ або інваріантів \$\\Delta I\$ при незмінному \$x \\in S\_{in}\$ (напр., поява `Warrant`, нове `Evidence`, прийняття `Commitment`).  
  * *(Відкритий борг **D17**: необхідно додати ендогенну гілку зміни стану через внутрішній закон переходу \$T(x\_t, a\_t, e\_t)\$, щоб фізичний рух всередині \$S\_{in}\$ без зовнішнього \$M\$ коректно класифікувався).*

---

## 4\. Частина II: Алгебра Рецептів, Тканина Міркувань та Чорний Конус (`INVARIANT-RECIPES`, `RVB`, `AIE`)

### 4.1. Рецепт Гарантій (`[CORE-DEF]`)

Кожен механізм, протокол або крок аргументації формалізується як:

\$\$ R \= (P, T, G, L, B\_{scope}) \$\$

* \$P\$ (*Prerequisites*) — множина вхідних інваріантів;  
* \$T\$ (*Transformation*) — виконувана операція або правило виводу;  
* \$G\$ (*Guarantees*) — множина вихідних інваріантів, які \$T\$ встановлює або зберігає;  
* \$L\$ (*Loss / Non-guarantees*) — що явно **не** гарантується;  
* \$B\_{scope}\$ (*Boundary*) — межі довіри та припущень.

**Закон композиції рецептів:** \$\$R\_2 \\circ R\_1 \\text{ є допустимим (well-typed)} \\iff (G\_1 \\models P\_2) ;\\land; (B\_{scope, 1} \\text{ сумісна з } B\_{scope, 2})\$\$

### 4.2. Алгебра Аудиту Тверджень та Контрмоделі (`[CORE-DEF]`)

Нехай \$C\$ — високорівневе твердження (Headline Claim), \$\\text{Req}(C) \= {I\_1, \\dots, I\_n}\$ — необхідні для нього інваріанти, а \$\\text{Prov}(S) \= {I\_1, \\dots, I\_k}\$ — інваріанти, фактично забезпечені конструкцією системи \$S\$.

1. **Семантичний розрив (The Gap):** \$\$\\text{Gap}(C, S) \\triangleq \\text{Req}(C) \\setminus \\text{Closure}(\\text{Prov}(S))\$\$  
2. **Критерій контрмоделі:** \$\$\\text{Gap}(C, S) \\neq \\emptyset \\iff \\exists \\mathcal{M} \\text{ (Countermodel)}: \\big(\\mathcal{M} \\models \\text{Prov}(S)\\big) ;\\land; \\big(\\mathcal{M} \\not\\models C\\big)\$\$

### 4.3. Чотиривимірна Тканина Міркувань (Reasoning Fabric, нотатка `0003`) (`[CORE-DEF]`)

Твердження \$C\$ є швом між двома конусами в частково впорядкованому просторі \$(\\mathcal{V}, \\preceq)\$:

\$\$ \\text{Grounding } B(C) \\longrightarrow \\text{Claim } C \\longrightarrow \\text{Reachability } F(C) \\longrightarrow \\text{Target Intent } G\_{target} \$\$

* **Backward Cone:** \$B(C) \= {x \\in \\mathcal{V} \\mid x \\leadsto C}\$ — епістемічне підґрунтя («на базі чого?»). Перевіряється *Backward Attack* (видаленням передумови).  
* **Forward Cone:** \$F(C) \= {y \\in \\mathcal{V} \\mid C \\leadsto y}\$ — легітимні операційні наслідки («що тепер допустимо?»).  
* **Target Intent (\$G\_{target}\$):** бажаний стан («шоб шо?»), який сам по собі **нічого не доводить**, а лише задає напрям пошуку шляху. Перевіряється *Forward Attack* (\$\\mathcal{M} \\models C \\land \\mathcal{M} \\not\\models G\_{target}\$).

### 4.4. Чорний та Білий Конуси, Семантична Маса та Межа Верифікації (`[FACT]` \+ `[SPECULATIVE]`)

1. **Білий конус (White Cone / Imagination, нотатка `0004`):** генерація кандидатів поза поточною досяжністю: \$\$\\text{Imagine}(S) \\ni D \\notin Reach\_T(S), \\qquad \\text{Status}(D) \= \\texttt{candidate}\$\$  
   * **Мрія (Dream):** \$D \\notin Reach\_T(S)\$ з високою оцінкою \$U(D) \> U(S)\$ до наявності доказу досяжності.  
   * **Винахід (Invention):** синтез нового переходу \$T\_{new}\$, що розширює досяжність: \$D \\in Reach\_{T \\cup {T\_{new}}}(S)\$.  
   * **Галюцинація vs Уява (`0012`):** уява зберігає тип \$\\text{Status}(D) \= \\texttt{candidate}\$; галюцинація здійснює нелегальне приведення типу \$\\text{Status}(D) := \\texttt{settled}\$ без проходження через чорний конус.  
2. **Чорний конус (Black Cone / Settlement, Теза 7, `0005a`):** механізм замикання циклів перевірки та тоталізації межі відмови (*regularization by explicit failure*): \$\$\\text{evalHash}(x, \\text{atp}) \\longrightarrow \\texttt{NF} ;\\mid; \\texttt{ATP\_EXHAUSTED} ;\\mid; \\texttt{UNRESOLVED}\$\$  
3. **Рефлексивне зобов'язання верифікації (\$\\hat{o}\$, `RVB-0.1`, `[FACT]`):** Кількість нових перевірних прозових зобов'язань, які породжує один акт перевірки.  
   * На неформальному монолозі (`Monday-корпус`, глибина \$\\le 4\$): \$\\hat{o} \\approx 2\\text{–}3\$ (гілкування не згасає само).  
   * На термінаційних контролях: \$\\hat{o} \\approx 0.14\$.  
   * На скомпільованому детермінованому субстраті (`COMPILE-0030`): термінальний replay-акт дає \$0\$ нових прозових зобов'язань.  
   * *(Знята модель `[WITHDRAWN]`: закрита теорема про фазовий перехід при \$\\mu=1\$ відкликана через контрприклади адаптивного планувальника).*  
4. **Addressing Is Equality (`AIE`, `[FACT]`):** На допущеному канонічному домені рівність content-addressed хешів нормальних форм ідентифікує канонічний результат (\$\\text{nfHash}(x) \= \\text{nfHash}(y)\$), але **не доводить** семантичної рівності довільних сирих входів поза профілем допуску (`AIE.errata`).  
5. **Семантична маса та Епістемічний горизонт (`0005a`, `[SPECULATIVE]`):** \$\$M\_{sem}(C) \= \\sum\_{h \\in \\text{Unique}(\\text{Closure}(C))} w(h), \\qquad \\kappa(x) \= \-\\log\\frac{|Adm(x)|}{|Out(x)|}\$\$ Епістемічний горизонт подій для спостерігача \$O\$ з бюджетом перевірки \$A\$: \$\$H\_{O, A} \= {x \\in X \\mid \\min\_{p: x \\leadsto Obs\_O} \\text{cost}(p) \> A}\$\$

---

## 5\. Частина III: Агентність, Рефлексивність та Тороїдальна Динаміка (`FLOW` Part II, `VORTEX-0.1`)

### 5.1. Шкала агентності та Ієрархія інтервенцій (`FLOW` §17–20.1, `[SPECULATIVE]` \+ `[DEBT D18]`)

Шість дескриптивних рівнів: \$\$\\text{Object} \\prec \\text{Reactive System} \\prec \\text{Agent} \\prec \\text{Player} \\prec \\text{Reflexive Player} \\prec \\text{Self-Modifying / Game-Transitioning Player}\$\$

Для рефлексивного гравця діють зв'язані потоки станів, політик і мета-правил: \$\$x\_{t+1} \= F(x\_t, \\pi\_t, e\_t), \\qquad \\pi\_{t+1} \= G(\\pi\_t, x\_t, \\text{Evidence}*t), \\qquad G*{t+1} \= H(G\_t, \\text{History}\_t, I^\*)\$\$

**Ієрархія контрфактичних інтервенцій (`FLOW` §20.1):**

* **Тест агентності:** \$do(\\pi \= \\pi') \\implies \\Delta P(\\text{Trajectory})\$  
* **Тест рефлексивності:** \$do(G \= G') \\implies \\Delta P(\\text{Trajectory})\$ за активної динаміки \$\\pi\_{t+1} \= G'(\\dots)\$  
* **Тест самомодифікації:** \$do(H \= H') \\implies \\Delta P(\\text{Trajectory})\$ за активних \$G\$ та \$\\pi\$. *(Відкритий борг **D18**: тест вимагає обмеження класу допустимих \$G'\$ та явного базового контрасту, інакше на системі з \$G \= \\text{id}\$ підстановка нетривіального \$G'\$ хибно сертифікує рефлексивність).*

**Перехід між іграми (Game Transition, `FLOW` §28):** Зміна самої гри \$(x, \\mathcal{G})*t \\to (x, \\mathcal{G})*{t+1}\$ є легітимною лише за виконання трьох умов: \$\$I\_{identity}(\\mathcal{G}*t, \\mathcal{G}*{t+1}) \= \\texttt{true} ;\\land; \\text{Budget}\_{mut} \\ge \\text{Cost}(\\mathcal{G}*t \\to \\mathcal{G}*{t+1}) ;\\land; \\text{Warrant}(\\mathcal{G}*t \\to \\mathcal{G}*{t+1}) \= \\texttt{true}\$\$

### 5.2. Геометрична модель `VORTEX-0.1` (Агент як вихрове кільце) (`[SPECULATIVE]`)

Фактор-проекція динаміки агента на дві осі (довгострокова lineage-вісь \$z\$ та короткий цикл settlement через центральну точку \$p\$):

* **Словник:**  
  * \$z\$ — вісь lineage (напрямок настояного часу);  
  * \$p \\notin \\Sigma\$ — точка теперішнього settlement;  
  * \$\\Sigma\$ — поверхня записаних (warranted) станів;  
  * \$\\varnothing\$ — внутрішня порожнина (білий конус: досяжність \$Reach\$ без warrant);  
  * \$a\$ — радіус труби (ширина каналу варіативності допустимих дій);  
  * \$\\Gamma\$ — циркуляція (частота проходження секторів \$\\Sigma\$ крізь точку settlement \$p\$);  
  * \$w(\\sigma)\$ — вага уваги на секторі \$\\sigma \\subset \\Sigma\$.  
* **Три структурні закони `VORTEX-0.1`:**  
  1. **S1 (Самопросування через замикання):** \$\$v\_z \\propto \\Gamma\$\$ Рух уздовж lineage \$z\$ відбувається виключно внаслідок замкнених циклів settlement. Генерація кандидатів у \$\\varnothing\$ при \$\\Gamma \= 0\$ дає \$v\_z \= 0\$ (стояння на місці / фонтан тексту).  
  2. **S2 (Керування як асиметрія уваги):** \$\$\\delta\\theta \\propto \\nabla\_\\sigma w\$\$ Усередині кільця немає гомункулуса-пілота; поворот осі траєкторії визначається градієнтом уваги між секторами під час проходження через \$p\$.  
  3. **S3 (Збереження радіуса каналу в ізоляції):** \$\$\\left(\\frac{da}{dt}\\right)*{isolated, ; \\text{no-loss}} \= 0\$\$ Агент не може розширити власний простір дій \$a\$ суто зсередини без (а) взаємодії з іншим кільцем (\$\\Sigma\_1 \\cap \\Sigma\_2 \\neq \\emptyset\$, локальна сумісність \$K*{12}\$) або (б) дисипації / оплати ціни.  
* **Режими збоїв за `VORTEX-0.1`:**  
  * *Депресія:* \$\\Gamma \\to 0 \\implies v\_z \\to 0\$ (цикли не замикаються).  
  * *Гіперфікс:* \$w(\\sigma\_0) \\gg w(\\sigma \\neq \\sigma\_0)\$ (кільце прецесує на місці без просування).  
  * *Вигорання:* дисипація \$\\Gamma\$ кожного циклу до вичерпання бюджету дії.  
  * *Травма:* непроsettled маса на \$\\Sigma\$, що не проходить крізь \$p\$ до кінця і створює постійний систематичний нахил осі.

---

## 6\. Частина IV: Фактор-геометрія мислення, мови та пізнання (`Monday` 0006–0026, 0058–0059)

### 6.1. Поняття, Аналогія та Відкриття (`0006`, `0007`) (`[SPECULATIVE]`)

2. **Поняття (Concept):** не координата і не кластер у латентному просторі, а клас еквівалентності траєкторій/трансформацій, що зберігають сімейство downstream-affordances: \$\$C \= \[x\]\_{\\sim\_C}, \\quad\\text{де}\\quad x \\sim\_C y \\iff \\forall T \\in \\mathcal{G}\_C: \\text{Downstream}(T(x)) \\approx \\text{Downstream}(T(y))\$\$ Глибина абстракції поняття пропорційна багатству його групи інваріантності: \$\\text{Depth}(C) \\propto |\\mathcal{G}\_C|\$.  
3. **Слово (Word, `0022`):** адресована мітка (content address) концептуального басейну атрактора.  
4. **Аналогія (Analogy, `0007`):** гіпотеза про частковий морфізм \$\\phi: D\_A \\to D\_B\$, для якого діаграма переходів **майже комутує**: \$\$\\Delta(\\phi, x) \= d\_B\\big(\\phi(T\_A(x)),; T\_B(\\phi(x))\\big) \\le \\varepsilon\$\$ із обов'язковим `Loss Report`.  
5. **Відкриття (Discovery, `0007`, `0019`):**  
   * *Фаза 1:* аналогія витримує адверсаріальне розширення (передбачає нетривіальні властивості в \$D\_B\$).  
   * *Фаза 2 (Структурована поломка):* систематичне відхилення \$\\Delta(\\phi, x) \\neq 0\$ виявляє прихований інваріант \$I\_{new}\$.  
   * *Фаза 3 (Перефакторизація):* заміна самої еквівалентності \$X/\\sim\_{old} \\longrightarrow X/\\sim\_{new}\$, що різко зменшує довжину опису \$\\Delta K \< 0\$ і розширює простір законних питань \$\\Delta Reach\_{questions} \\gg 0\$.

### 6.2. Когнітивні помилки як дефекти факторизації (`0008`) (`[SPECULATIVE]`)

Нехай \$\\pi\_A: X \\to X/\\sim\_A\$ — поточна факторизація світу агентом \$A\$.

* **Over-collapse (Надмірне злиття):** \$x \\sim\_{surface} y\$, але \$x \\not\\sim\_{causal} y\$ (стереотип, карго-культ, поверхнева аналогія).  
* **Over-separation (Надмірне розділення):** \$x \\not\\sim\_{surface} y\$, хоча \$I\_{causal}(x) \= I\_{causal}(y)\$ (дисциплінарна сліпота).  
* **Упередження (Bias):** дешева факторизація \$X/\\sim\_{cheap}\$ за дефіциту обчислювального бюджету з високими семантичними втратами \$L(\\sim\_{cheap}) \\gg 0\$.  
* **Ідеологія:** заморожена факторизація \$\\Pi\$, де мета-правило забороняє рефакторинг \$\\sim\_\\Pi \\to \\sim'\$ попри накопичення структурованих аномалій.

### 6.3. Увага, Перспектива, Сенс та Краса (`0009`, `0018`) (`[SPECULATIVE]`)

* **Перспектива:** кортеж \$(\\pi\_A, d\_A)\$, де \$\\pi\_A: X \\to X/\\sim\_A\$ — задачно-обумовлена факторизація, а \$d\_A(x,y)\$ — локальна метрика значущості (salience).  
* **Увага (Attention):** динамічне перемикання активного контракту збереження інваріантів: \$(\\pi\_t, d\_t) \\to (\\pi\_{t+1}, d\_{t+1})\$.  
* **Операційний сенс події (Meaning):** індукована деформація простору допустимого майбутнього агента: \$\$\\text{Meaning}*A(e) \\propto d*{topo}\\big(Reach\_A(S),; Reach\_A(S \\mid e)\\big)\$\$  
* **Краса / Елегантність (`0018`):** високий генеративний вихід (ширина відкритих смислових траєкторій) на одиницю складності опису правила: \$\$\\text{Beauty}(R) \\propto \\frac{|\\text{GeneratedCoherentTrajectories}(R)|}{K(R)}\$\$

### 6.4. Агент як Двонаправлений Компілятор (`0022`–`0024`) (`[SPECULATIVE]`)

* **Мислення (`0023`):** крос-рантайм компіляція між гетерогенними внутрішніми мовами одного агента: \$\$\\mathcal{L}*{intuition} \\longleftrightarrow \\mathcal{L}*{inner\_speech} \\longleftrightarrow \\mathcal{L}*{Recipe\_IR} \\longleftrightarrow \\mathcal{L}*{formal\_verifier} \\longleftrightarrow \\mathcal{L}\_{motor/action}\$\$  
* **Двонаправлена компіляція між Світом і Моделлю (`0024`):**  
  * \$\\text{Science / Perception}: \\text{World} \\xrightarrow{\\text{compress / extract } I} \\text{Model}\$  
  * \$\\text{Engineering / Action}: \\text{Model} \\xrightarrow{\\text{synthesize } T} \\text{World}\$  
  * **Provenance як debug symbols:** записи `Warrant` зберігають таблицю відповідності між високорівневим наміром та низькорівневим виконаним переходом.

---

## 7\. Частина V: Час, Ідентичність, Пам'ять, Влада та Справедливість (`README`, `0005`, `0010`–`0016`, `0025`–`0075`)

### 7.1. Дуальність Часу та Ідентичності (`0005`, `0010`, `0063`) (`[IDENTITY-RULE]` \+ `[SPECULATIVE]`)

Час та ідентичність є спряженими (conjugate) описами трансформації: \$\$\\text{Identity} \\triangleq \\text{що зберігається крізь трансформації}, \\qquad \\text{Time} \\triangleq \\text{накопичена незворотна різниця}\$\$

1. **Життєвий цикл часу (`0010`):** \$\$\\text{Possibility } (y \\in Reach(S)) \\xrightarrow{\\text{Choice}} \\text{Settled Fact } (e\_t) \\xrightarrow{\\text{Causal Closure}} \\text{Inherited Constraint } (I\_{e\_t} \\in C\_{t+1})\$\$  
2. **Теперішнє (Present):** активний фронтир settlement між причинно замкненим минулим і відкритим конусом досяжності: \$\$\\text{Present}\_A(S) \= \\partial\\big(\\text{CausalPast}\_A(S),; Reach\_A(S)\\big)\$\$ У розподілених системах теперішнє є локальним (\$\\text{Present}\_A \\neq \\text{Present}\_B\$); консенсус (`0037`) — це протокол синхронізації спільного незворотного минулого.  
3. **Ідентичність та Конституційна самомодифікація (`0005`, `0012`):** Сутність \$A\_0\$ та \$A\_n\$ належать одній lineage тоді й лише тоді, коли кожен крок зміни її базових інваріантів \$I\_t \\to I\_{t+1}\$ був авторизований мета-інваріантом (конституцією) \$I^*\$: \$\$A\_0 \\sim\_{lineage} A\_n \\iff \\forall t \\in \[0, n-1\]: I^*(I\_t, I\_{t+1}, W\_t) \= \\texttt{true}\$\$  
4. **Правило Форку (Теза 2, `0005`, `[IDENTITY-RULE]`):** Досвід \$Exp(A)\$ є реляційним графом зобов'язань і довіри в екосистемі \$\\mathcal{E}\$: \$\\text{Identity}(A) \\subseteq \\text{Relations}(A, \\mathcal{E})\$. При операції `fork` (\$S \\to (S\_A, S\_B)\$) байти стану копіюються, але зовнішні відносини довіри та майбутні траєкторії розщеплюються у DAG (\$Lineage\_A \\parallel Lineage\_B\$). Отже, `fork` породжує нову сутність.  
5. **Неантропоморфні топології ідентичності (Теза 3):**  
   * *Міцелійна:* без центрального вузла, де пам'ять та інваріанти розподілені по графу.  
   * *Ройова:* частковий доступ агентів до спільного пулу досвіду.  
   * *Колективний суб'єкт (`0034`):* множина агентів стає колективним агентом лише за наявності 5 інваріантів: `(Boundary, SharedMemory, CoordinationMechanism, GoalPersistence, AttributionRule)`.

### 7.2. Пам'ять, Зобов'язання та Життєздатність (`0038`, `0040`, `0044`, `0045`, `0049`) (`[CORE-DEF]`)

* **Пам'ять (`0038`):** \$\\text{Memory} \\neq \\text{Storage}\$. Пам'ять — це стиснення каузальної історії у структуру, що активно обмежує або скеровує майбутні переходи: \$M \= (\\text{Trace}, \\text{DownstreamEffect})\$.  
* **Епістемічний ребейз (Epistemic Rebase, `FLOW` §23):** збереження \$\\text{ArtifactContinuity}\$ (сирі докази, виміри, рецепти, помилки) при періодичному скиданні \$\\text{InterpretiveContinuity}\$ (улюблених метафор і словника) через `Cold Reconstruction`.  
* **Зобов'язання (Obligation, `0040`, `0049`):** пам'ять із відкритим темпоральним ребром (*memory with an open temporal loop*), що звужує допустимі майбутні переходи до моменту виконання (`settlement`), компенсації (`repair`) або прощення (`forgiveness`).  
* **Реєстр (Ledger, `0049`):** спільна пам'ять із нормативним downstream-ефектом на допустимість дій учасників.  
* **Ядро життєздатності (Viability Kernel, `0044`, `0045`):** \$\$K\_{viab} \= {x \\in X \\mid Reach\_{viable}(x) \\neq \\emptyset}\$\$ Життєздатність (\$\\text{Viability} \\neq \\text{Survival} \\neq \\text{Optimization}\$) — це збереження здатності системи породжувати майбутні переходи. З урахуванням конструювання ніші (`0045`): \$\$\\text{Viability}(A) \= \\text{Viability}(A \\otimes \\text{EnvDependencies})\$\$

### 7.3. Міжчасове самоврядування, Влада, Легітимність і Справедливість (`0013`–`0015`, `0028`–`0032`) (`[NORMATIVE-POS]` \+ `[CORE-DEF]`)

1. **Самоврядування (Self-Governance, `0013`):** Агент у часі — це коаліція послідовних версій \$(A\_0, A\_1, \\dots, A\_t, \\dots)\$, де \$A\_t\$ має асиметричну владу над спадкоємцями \$A\_{t+k}\$. Прокрастинація та залежність — це міжчасова екстерналізація витрат (\$\\text{Benefit}(A\_t) \> 0, \\text{Cost}(A\_{t+k}) \\gg 0\$) або захоплення механізму оцінки одним локальним контуром. Зобов'язання (`Commitment`) свідомо звужує локальне гілкування \$Reach\_{local} \\downarrow\$, щоб зробити досяжними глибокі стани \$Reach\_{deep} \\uparrow\$.  
2. **Влада як деформація чужих конусів майбутнього (`0014`):** \$\$\\text{Power}\_A(B) \\triangleq \\Delta Reach\_B \\text{, індуковане діями або позицією } A\$\$ **Стратифікація глибини влади (6 рівнів):**  
   * *Рівень 0 (Фізичний):* пряма зміна стану \$x\_B \\to x'\_B\$.  
   * *Рівень 1 (Операційний — негативний/позитивний):* блокування або відкриття переходів \$A\_B(x)\$.  
   * *Рівень 2 (Економічний / Метричний):* зміна вартості переходів \$c\_B(T) \\to c'\_B(T)\$.  
   * *Рівень 3 (Епістемічний та Уваговий):* деформація видимого конуса \$Reach\_B^{perceived}\$ та черги пріоритетів \$Attention\_B\$.  
   * *Рівень 4 (Онтологічний / Концептуальний):* нав'язування факторизації \$\\Pi\_B\$ (визначення того, які розрізнення взагалі мислимі та висловлювані).  
   * *Рівень 5 (Конституційний / Мета-влада):* зміна правил \$MetaT\_B\$, за якими \$B\$ може змінювати власні цілі та політики.  
3. **Епістемічна кривина влади (`0014` §23–24):** \$\$\\text{Power}\_A(B) \\uparrow \\implies \\text{StrategicAdaptation}\_B(A) \\uparrow \\implies \\text{IndependentEvidence}\_A \\downarrow\$\$ Без захищених адверсаріальних каналів (опозиція, red team, незалежний аудит) зростання влади створює навколо актора епістемічний горизонт подій.  
4. **Легітимність та Proof-Carrying Power (`0015`, `0028`):** Тягар доказового обґрунтування (`WarrantBurden`) має масштабуватися пропорційно силі втручання в чужу досяжність та його незворотності: \$\$\\text{WarrantBurden}(T) \\propto |\\Delta Reach(T)| \\times \\text{Irreversibility}(T)\$\$ Легітимна влада вимагає: `(RecognizedAuthority, EvidenceThreshold, Notice, Contestability/Appeal, Proportionality, LossReport, Reversibility/Repair)`.  
5. **Керованість без захоплення (Steerability Without Capture, `0032`):** Здатність системи приймати коригувальні сигнали ззовні без втрати власного конституційного ядра та без перетворення на сліпий інструмент одностороннього оператора.  
6. **Справедливість (Justice, `0015`, `0055`, `0068`):** Не рівність фінальних станів, а справедливий розподіл топологічних повноважень (хто має write-access до правил, що формують спільні future cones), захист базових підпросторів автономії (`Rights`) та прозорий облік неминучих втрат (`Explicit Ethical Loss Report`) у трагічних конфліктах інваріантів (\$\\neg \\exists T: \\text{Preserve}(T, I\_1) \\land \\text{Preserve}(T, I\_2)\$).  
7. **Довіра (Trust, `0029`):** Кредит на неперевірені майбутні трансформації (добровільне делегування частки write-access до власного \$Reach\_A\$). Криптографія та `Warrant` перекомпільовують частину соціальної довіри у детерміновано перевірні інваріанти, явно декларуючи залишок, який не компілюється (напр. `key ↔ human binding`, `policy ↔ intent faithfulness`).

---

## 8\. Частина VI: Канонічний Реєстр Розщеплення Типів (Type Splits `0016`–`0075`)

Головний анти-bullshit інструмент корпусу `Monday` — заборона зливати суміжні поняття в один нечіткий басейн (`over-collapse`). Нижче зведено формальні розщеплення типів, зафіксовані в нотатках `0016`–`0075`:

| Нотатка | Домен | Строге розщеплення типів (Type Split) | Ключовий інваріант розрізнення |
| :---- | :---- | :---- | :---- |
| **0016 / 0058** | Епістемологія | \$\\text{Truth} \\neq \\text{Fact} \\neq \\text{Belief} \\neq \\text{Opinion} \\neq \\text{Knowledge} \\neq \\text{Evidence} \\neq \\text{Testimony} \\neq \\text{Authority} \\neq \\text{Proof} \\neq \\text{Reproducibility}\$ | *Truth* — на боці світу; *Objectivity* — інваріантність при зміні перспективи з обліком втрат; *Authority* — кешований (неперевірений локально) доказ; *Proof* — замкнений ланцюг у фіксованій аксіоматиці |
| **0019** | Генерація нового | \$\\text{Imagination} \\neq \\text{Creativity} \\neq \\text{Invention} \\neq \\text{Discovery} \\neq \\text{Art}\$ | *Imagination* генерує \$D \\notin Reach(S)\$; *Creativity* знаходить компактні генеративні правила; *Invention* синтезує відсутній перехід \$T\_{new}\$; *Discovery* виявляє наявний у світі інваріант |
| **0025 / 0026** | Модальність | \$\\text{Logical} \\supset \\text{Physical} \\supset \\text{Technical} \\supset \\text{Economic} \\supset \\text{Institutional} \\supset \\text{Endorsed Reach}\$ | Можливість — це конструктивна досяжність під стеком обмежень; *Slack* (люфт) — модальний резерв стійкості (*Resilience* \$\\neq\$ *Rigidity*) |
| **0030** | Невизначеність | \$\\text{Risk} \\neq \\text{Uncertainty} \\neq \\text{Ambiguity} \\neq \\text{Ignorance}\$ | *Risk* має відомий простір станів і розподіл \$P\$; *Uncertainty* — відомі стани без \$P\$; *Ambiguity* — нечітка факторизація станів; *Ignorance* — невідомі самі гілки майбутнього |
| **0032** | Управління | \$\\text{Control} \\neq \\text{Steerability} \\neq \\text{Corrigibility} \\neq \\text{Autonomy}\$ | *Control* диктує стан; *Steerability* коригує напрям за збереження внутрішньої агентності; *Corrigibility* дозволяє безпечне виправлення самої моделі |
| **0033** | Причинність | \$\\text{Cause} \\neq \\text{Agency} \\neq \\text{Intent} \\neq \\text{Authorship} \\neq \\text{Liability}\$ | *Intent* — pre-authorship (спрямування до дії); *Authorship* вимагає ендогенного контролю \+ рефлексивного схвалення (endorsement) |
| **0035 / 0036** | Суб'єктивність | \$\\text{SelfData} \\neq \\text{FirstPersonPerspective} \\neq \\text{Intersubjectivity}\$ | Перспектива 1-ї особи — асиметрія прямого каузального доступу стану до стернового механізму; інтерсуб'єктивність — узгоджена інваріантність через проекції |
| **0037 / 0038 / 0050** | Історія і Час | \$\\text{Past} \\neq \\text{Record} \\neq \\text{Memory} \\neq \\text{Narrative} \\neq \\text{Tradition} \\neq \\text{Precedent} \\neq \\text{Legacy} \\neq \\text{PathDependence}\$ | *Past* — те, що сталося; *Record* — артефакт; *Memory* — активне обмеження на майбутнє; *Precedent* — правило допустимості з минулого рішення |
| **0041** | Телеологія | \$\\text{Desire} \\neq \\text{Goal} \\neq \\text{Value} \\neq \\text{Obligation} \\neq \\text{Purpose} \\neq \\text{Meaning}\$ | *Desire* — локальний градієнт привабливості; *Goal* — вибраний цільовий стан; *Value* — обмеження на допустимі шляхи; *Obligation* — відкрита боргова петля; *Purpose* — роль у більшій системі |
| **0044 / 0045** | Життєздатність | \$\\text{Viability} \\neq \\text{Survival} \\neq \\text{Stability} \\neq \\text{Optimization}\$ | *Optimization* максимізує метрику (часто спалюючи резерв); *Viability* зберігає непорожнім ядро майбутніх переходів \$Reach(x) \\neq \\emptyset\$ |
| **0046 / 0047** | Належність і Власність | \$\\text{Use} \\neq \\text{Possession} \\neq \\text{Control} \\neq \\text{Ownership} \\neq \\text{Stewardship} \\neq \\text{Sovereignty}\$ | Власність — не фізичний зв'язок із річчю, а соціально/протокольно гарантований розподіл прав виключення, передачі та зміни майбутніх переходів |
| **0048 / 0049** | Обмін | \$\\text{Gift} \\neq \\text{Trade} \\neq \\text{Reciprocity} \\neq \\text{Debt} \\neq \\text{Credit} \\neq \\text{Money} \\neq \\text{Price} \\neq \\text{Value}\$ | Обмін — взаємна деформація capabilities та зобов'язань, а не переміщення предметів |
| **0051 / 0052** | Життєвий цикл агентів | \$\\text{Birth/Entry} \\neq \\text{Admission} \\neq \\text{Initiation} \\neq \\text{Recognition}\$; \$\\text{Mortality} \\neq \\text{Termination} \\neq \\text{Succession} \\neq \\text{Renewal}\$ | Нові агенти входять без provenance (проблема bootstrap довіри); незамінність вузла — прихована крихкість системи |
| **0053 / 0054** | Спроможність і Збої | \$\\text{Competence} \\neq \\text{Capability} \\neq \\text{Capacity} \\neq \\text{Authority} \\neq \\text{Power} \\neq \\text{Mandate}\$; \$\\text{Error} \\neq \\text{Mistake} \\neq \\text{Failure} \\neq \\text{Defect} \\neq \\text{Negligence} \\neq \\text{Malice}\$ | *Capability* — технічна можливість; *Authority* — легітимне право; *Error* — розходження моделі/дії; *Negligence* — порушення стандарту верифікації при наявній спроможності |
| **0055 / 0056** | Симетрія і Конфлікт | \$\\text{Equality} \\neq \\text{Sameness} \\neq \\text{Symmetry} \\neq \\text{Equivalence} \\neq \\text{Parity} \\neq \\text{Proportionality}\$; \$\\text{Disagreement} \\neq \\text{Friction} \\neq \\text{Conflict} \\neq \\text{Dispute} \\neq \\text{War}\$ | Справедливість починається з вибору релевантної еквівалентності \$\\sim\$ до розподілу; ескалація від *Disagreement* (розходження моделей) до *War* (руйнування чужого субстрату агентності) |
| **0057** | Вплив | \$\\text{Information} \\neq \\text{Argument} \\neq \\text{Persuasion} \\neq \\text{Rhetoric} \\neq \\text{Framing} \\neq \\text{Nudge} \\neq \\text{Manipulation} \\neq \\text{Coercion} \\neq \\text{Consent}\$ | Відрізняються тим, чи зберігається прозорість provenance та контрфактичний доступ адресата до власного механізму рішення |
| **0059** | Глибина знання | \$\\text{Information} \\neq \\text{Knowledge} \\neq \\text{Understanding} \\neq \\text{Insight} \\neq \\text{Expertise} \\neq \\text{Wisdom} \\neq \\text{EpistemicHumility}\$ | *Understanding* \= здатність транспортувати інваріант \+ знання карти втрат; *Wisdom* \= знання ціни реалізації можливостей та меж власної моделі |
| **0060 / 0061** | Оптимізація і Метрики | \$\\text{Design} \\neq \\text{Engineering} \\neq \\text{Control} \\neq \\text{Optimization} \\neq \\text{Goodhart} \\neq \\text{Gaming} \\neq \\text{Compliance} \\neq \\text{MissionDrift}\$ | *Metric* — проекція зі втратами (\$L(\\pi\_{metric}) \> 0\$); *Goodhart* виникає, коли тиск оптимізації руйнує інваріантний зв'язок між метрикою та цільовою властивістю |
| **0062 / 0063 / 0064** | Видимість, Ідентичність і Статус | \$\\text{Legibility} \\neq \\text{Transparency} \\neq \\text{Observability} \\neq \\text{Auditability} \\neq \\text{Privacy} \\neq \\text{Surveillance}\$; \$\\text{Identity} \\neq \\text{Identifier} \\neq \\text{Credential} \\neq \\text{Reputation} \\neq \\text{Dignity}\$ | *Legibility* — редукція під управління (часто ціною локальної складності); *Auditability* — перевірність переходів за запитом без тотального *Surveillance*; *Dignity* — базовий інваріант недоторканності агента незалежно від *Status/Rank* |
| **0065 / 0066 / 0067** | Норми і Турбота | \$\\text{Norm} \\neq \\text{Rule} \\neq \\text{Law} \\neq \\text{Punishment} \\neq \\text{Repair} \\neq \\text{Forgiveness}\$; \$\\text{Care} \\neq \\text{Paternalism} \\neq \\text{Empowerment} \\neq \\text{Stewardship}\$; \$\\text{Love} \\neq \\text{Attachment} \\neq \\text{Loyalty} \\neq \\text{Nepotism}\$ | *Paternalism* звужує \$Reach\_B\$ заради безпеки; *Empowerment/Stewardship* розширює автономне ядро \$Reach\_B\$; *Love* створює спільний генеративний простір \$Reach\_{A \\otimes B}\$ |
| **0068–0075** | Спільні блага, Координація, Сигнали, Звички, Афект | \$\\text{Scarcity} \\neq \\text{Triage} \\neq \\text{Rationing} \\neq \\text{Fairness}\$; \$\\text{Commons} \\neq \\text{PublicGood}\$; \$\\text{Signal} \\neq \\text{Message} \\neq \\text{Meaning}\$; \$\\text{Habit} \\neq \\text{Routine} \\neq \\text{Skill} \\neq \\text{Ritual}\$; \$\\text{Affect} \\neq \\text{Emotion} \\neq \\text{Mood} \\neq \\text{Value}\$ | *Habit* — скомпільований (кешований) перехід, що економить когнітивний бюджет; *Affect* — глобальна модуляція пріоритетів і порогів чутливості простору переходів |

---

## 9\. Частина VII: Реєстр Відкритих Концептуальних Боргів та Фальсифікаторів

За правилом `FLOW.md` §36.1, жодна формалізація не має права приховувати виявлені аудитами дірки. Нижче зафіксовано активний борговий реєстр станом на версію `0.2.1`:

### 9.1. Активні борги верифікації (`[DEBT]`)

1. **Борг `D5` / `D16` (Сортова сигнатура носіїв — виявлено аудитами G1, G6):** У виразі \$M \\subseteq S\_{out} \\times (\\Delta X \\cup \\Delta C \\cup \\Delta I)\$ символи \$\\Delta X, \\Delta C, \\Delta I\$ вжито як сорти без формально визначених доменів, а функція \$\\text{carrier}(C\_i)\$ не має строгого кодомена (фраза «носій лежить усередині \$S\_{in}\$» є сортовою помилкою, якщо \$S\_{in} \\subseteq X\$, а носій має сорт \$\\text{Carrier}\$). Крім того, визначення `Constraint` (§6) та `Invariant` (§7) ще не містять явного слота для carrier.  
2. **Борг `D17` (Втрата ендогенної зміни стану — виявлено аудитом G6):** Типізація поділу на фізичну та інформаційну зміну в §15 виключно через зовнішнє відображення \$M\$ загубила ендогенну динаміку \$x\_{t+1} \= T(x\_t, a\_t, e\_t)\$ (камінь, що падає всередині домену без перетину \$B\_{bnd}\$, випав з обох гілок).  
3. **Борг `D15` / `D18` (Конфаунд ієрархії інтервенцій — виявлено аудитами G5, G6):**  
   * Regime-інтервенція \$do(\\pi \= \\pi')\$ вимикає рефлексивний закон \$G\$, тому не може тестувати рефлексивність.  
   * Запропонований у `0.2` ремонт \$do(G \= G')\$ не визначає контрастного класу і не обмежує множину допустимих \$G'\$: для нерефлексивного гравця (\$G \= \\text{id}\$) підстановка нетривіального \$G'\$ змінить траєкторію і дасть хибнопозитивну сертифікацію рефлексивності.  
   * Аналогічно, \$do(G \= G')\$ заморожує мета-рівень \$H\$ (повторення конфаунду `D15` поверхом вище), а сам \$H\$ ще не має визначеного релятума у ядрі.  
   * Розбіжність між 6 сходинками таксономії агентності (§18) та 3 рівнями інтервенцій (§20.1).  
4. **Борг `D19` (Синхронізація реєстру та тексту):** Зміни у `FLOW.md`, які претендують на закриття концептуальних боргів, не можуть позначатися як «закриті» до проходження незалежного аудиту над оновленим глосарієм.

### 9.2. Умови фальсифікації онтології (`[CORE-DEF]`)

Ця формалізація втрачає епістемічний кредит або вимагає радикального перегляду, якщо:

1. **Експериментальна нерозрізнюваність (`EXP-001`–`EXP-007`):** переклад задач у мову `(State, Reach, Constraint, Invariant, Boundary, Loss)` систематично втрачає більше корисної структури, ніж пояснює, або `Cold Reconstruction` без словника `FLOW` природніше відновлює несумісну структуру.  
2. **Спростування законів `VORTEX-0.1` (`EXP-V1`–`EXP-V4`):**  
   * знайдено агента, який розширив радіус варіативності дій \$a\$ суто зсередини без зовнішнього контакту і без дисипації (ламає **S3**);  
   * зафіксовано змістовне просування по lineage \$z\$ при нульовій частоті замкнених циклів settlement \$\\Gamma \= 0\$ (ламає **S1**);  
   * зафіксовано систематичний поворот траєкторії без попередньої асиметрії уваги \$\\nabla\_\\sigma w\$ (ламає **S2**).  
3. **Квантовий та нелокальний анти-приклад (`FLOW` §32, Appendix B):** для систем із несепарабельним глобальним станом (\$\\psi\_{AB} \\neq \\psi\_A \\otimes \\psi\_B\$) класичне розбиття на локальний стан \$x\_A\$ та перетин межі \$B\_{bnd}\$ є непридатним; онтологія явно обмежує свою застосовність класом систем із локалізованими або явно адресованими межами.

---

## 10\. Самовідносний Loss Report цієї формалізації

Згідно з `INVARIANT-RECIPES.md` (§5) та `FLOW.md` (§13.1), застосуємо оператор \$\\mathcal{Q}\$ до самого акту компіляції 77 документів репозиторію у цей файл:

Translation Report: φ(manifesto\_bundle \[77 docs\] → FORMALIZATION-0.1.md)

  Status: Partial structure-preserving compilation

  Preserved:

    \- Мінімальне ядро FLOW-0.2 (D \= (X, O, A, C, I, B\_bnd, τ))

    \- Алгебра рецептів R \= (P, T, G, L, B) та критерій контрмоделі Gap(C, S)

    \- Закони VORTEX-0.1 (S1–S3) та розділення білого/чорного конусів

    \- Епістемічна типізація тверджень (Тези 2, 6, 7\) та виміряне ô ≈ 2–3

    \- Правило перетину траєкторій і не-ієрархічна топологія коси (Braid)

    \- Канонічні розщеплення типів (Type Splits) з корпусу Monday \[0001–0075\]

    \- Повний реєстр відкритих концептуальних боргів (D5, D15–D19)

  Lost:

    \- Жива діалогічна динаміка, іронія та евристичні мікро-приклади нотаток Monday

    \- Повні тексти доказів Lean/специфікацій із зовнішніх репозиторіїв (Σ-GLYPH, Warrant, HSP)

  Introduced:

    \- Єдина наскрізна нумерація шарів та зведені таблиці сортів і Type Splits

  Known Open Debts (Not Solved Here):

    \- Строга сортова сигнатура carrier(C\_i) та ΔX/ΔC/ΔI (D16)

    \- Ендогенна гілка фізичної зміни стану поза зовнішнім M (D17)

    \- Обмеження класу G' та базового контрасту в ієрархії інтервенцій do(G) (D18)