.PHONY: help verify matrix demo clean

help:
	@echo "Targets:"
	@echo "  verify   - run the DoD check (pytest -q). GREEN on a clean checkout: snippets store is implemented."
	@echo "             It's the concrete target a /loop recipe polls ('poll until pytest is green')."
	@echo "  matrix   - print the 3-level schedule comparison table (the heart of this demo)"
	@echo "  demo     - print the matrix + the invocation for each level; emphasize the cloud trap"
	@echo "  clean    - remove caches (.pytest_cache, __pycache__)"

# DoD probe. GREEN here by design - the snippets store is implemented.
# This demo is NOT a red-on-checkout build; its artifacts are recipes + the matrix.
# The green 'make verify' is the concrete target a /loop recipe polls.
verify:
	pytest -q

# The heart of the demo: three schedule levels, what must be ON for each,
# and whether each sees your local files.
matrix:
	@echo "Три рівні розкладу - матриця:"
	@echo ""
	@echo "| Рівень            | Де крутиться            | Бачить локальні файли?    | Що має бути ввімкнено        | Найменший інтервал |"
	@echo "|-------------------|-------------------------|---------------------------|------------------------------|--------------------|"
	@echo "| /loop             | локально, у відкритій сесії | так                    | відкрита сесія Claude        | 1 хвилина          |"
	@echo "| desktop scheduled | локально, без сесії     | так                       | увімкнена машина (сесія не потрібна) | за розкладом ОС    |"
	@echo "| cloud /schedule   | інфраструктура Anthropic | ні (свіжа копія з git)   | нічого свого (машина може бути вимкнена) | 1 година           |"
	@echo ""
	@echo "Головна пастка: cloud /schedule бере свіжу копію з git, тож НЕ бачить"
	@echo "локальних файлів - усе під .gitignore, незакомічене чи поза git для неї не існує."

# Print the matrix + the concrete invocation for each level.
# Slash commands run INSIDE 'claude' (not plain shell), so we print the steps.
demo: matrix
	@echo ""
	@echo "Запуск кожного рівня:"
	@echo ""
	@echo "1) /loop - локально, всередині відкритої сесії (бачить локальні файли):"
	@echo "   claude"
	@echo "     # /loop 30m реалізуй наступну todo-story і зупинись, коли pytest зелений"
	@echo "     # /loop стеж за make verify і доповідай, коли зелено   (self-paced, без інтервалу)"
	@echo "   Помре на новій розмові - живе лише поки сесія відкрита. Деталі: recipes/loop.md"
	@echo ""
	@echo "2) desktop scheduled task - локально, без відкритої сесії (машина ввімкнена):"
	@echo "   claude"
	@echo "     # /schedule create local \"щодня 09:00\" \"прожени make verify і поклади звіт у reports/\""
	@echo "   Кожен запуск - свіжа сесія; переживає перезапуск машини. Локальні файли бачить."
	@echo ""
	@echo "3) cloud /schedule - на інфраструктурі Anthropic (твоя машина може бути вимкнена):"
	@echo "   claude"
	@echo "     # /schedule create \"щодня 03:00\" \"підбий дайджест змін у репозиторії за добу\""
	@echo "     # /schedule list      переглянути рутини"
	@echo "     # /schedule run <id>  прогнати рутину негайно"
	@echo "   Найменший інтервал - 1 година. Деталі і пастка: routines/README.md"
	@echo ""
	@echo "ПАСТКА (наголос): хмарна рутина НЕ бачить локальних файлів."
	@echo "   Рутина «підсумуй drafts/» поверне порожньо - drafts/ під .gitignore,"
	@echo "   тож у свіжій копії з git цієї теки немає. Worked-приклад: routines/README.md"

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
