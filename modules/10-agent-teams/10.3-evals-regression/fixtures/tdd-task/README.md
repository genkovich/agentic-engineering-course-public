# tdd-task fixture

Стартовий стан для golden-task `tdd-three-commits`: стаб `src/slug.js` + story з AC
(`tasks/story.md`). Тестів ще немає — їх пише агент у фазі RED.

Кейс регресить **TDD-дисципліну** (порт скіла 7.7 на `node:test`): агент має зробити
рівно 3 атомарні коміти `test(`/`feat(`/`refactor(`, не змінювати `test/` після RED і
довести `node --test` до зеленого. `check.py` асертить саме цей процес, а не зміст тестів.
