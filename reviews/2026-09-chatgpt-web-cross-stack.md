# ChatGPT (web) — cross-stack review, the manifesto part (2026-09-07)

**Filed as received, abridged to this repository's part.** The full review
covers manifesto `188f4b6`, warrant `84e42dd` and sigma-glyph `78b9481`; the
complete text and the per-finding disposition are filed in warrant as
`reviews/2026-09-chatgpt-web-cross-stack.md` and its `-response.md`. The
operator relayed it and described the prompt as deliberately adversarial
("спеціально негативно налаштований"); prompt bytes unrecorded; the
reviewer had web access. Vendor: OpenAI; exact model unrecorded.

## §5 — as received

**5. Маніфест досі робить стрибки, за які власний верифікатор мав би бити його лінійкою.**

Три приклади.

**«Досвід не можна скопіювати».** Якщо досвід операційно представлений журналом рішень, станом і записами відносин — ці представлення копіюються. Не копіюється автоматично визнання іншими учасниками та майбутня траєкторія. Це різні твердження. «Fork — нова сутність» можна прийняти як правило ідентичності; воно не випливає з некопійованості даних.

**Два майбутні: експлуатація інструментів або цифрові форми існування.** Хибна дихотомія. Можна будувати підзвітну автоматизацію, зберігати історію й обмежувати владу операторів без установленої відповіді про моральний статус машин.

**«Ми не будуємо інструмент контролю».** Але відмова в переходах, звуження доступу й виключення з протоколів — механізми контролю. Маніфест нижче сам визнає цю владу, проте декларація лишилася.

Маніфест має право на метафори й етичну позицію. Але коли він одночасно проголошує дисципліну типізації, **власна неминучість народження нового виду теж повинна носити бейдж «гіпотеза», а не ходити з посвідченням майбутнього факту**.

## §6 — the part addressed here

**«Чорний конус» ризикує стати фабрикою нових зобов'язань.** Маніфест вимірює породження перевірних зобов'язань на одному модельному корпусі й коректно звужує висновки. Але успішне завершення однієї скомпільованої перевірки ще не показує, що весь процес став дешевшим. [...] у прочитаних матеріалах немає переконливого вимірювання чистої користі всього цього циклу на зовнішній роботі.

## Disposition (this repository)

- **§5, all three — ACCEPTED as typing defects, fixed in README 0.2.1.** Each
  sentence stays (two are quoted verbatim by `MISSION.receipt.json`, which
  was re-settled against the new bytes); each now carries its type beside
  it: Thesis 2 is an *identity rule we adopt*, not a consequence of data
  being uncopyable; Thesis 6 is a *position*, not a dichotomy; "we do not
  build an instrument of control" is scoped to entities and the protocol's
  own power of refusal is named as control, typed and contestable. The
  "new species" inevitability the reviewer alludes to is Thesis 7's
  territory and already reads as design intent, not prediction; nothing
  there claims a future fact.
- **§6 — ACCEPTED, OPEN.** The net-benefit measurement on external work does
  not exist. It is the same debt as `CONTROLLED-FORGETTING-0.1` §14 (effect
  measurement, owed for the sigma-glyph and warrant applications) and the
  reviewer's §7 experiment in warrant is the proposed instrument. No new
  claim is made here until it runs.
