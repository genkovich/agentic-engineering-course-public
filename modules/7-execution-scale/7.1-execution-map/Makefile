.PHONY: help verify map clean

help:
	@echo "Targets:"
	@echo "  verify   - run the DoD check (pytest -q). RED on a clean checkout (NotImplementedError) - that's the start state."
	@echo "  map      - print the decision tree 'яка задача → який патерн' (the Module 7 map)"
	@echo "  clean    - remove caches (.pytest_cache, __pycache__)"

# DoD probe. On a fresh checkout store/tags/search/dedupe/export are NotImplementedError stubs
# → every test errors out (red). Green only after a story's module is implemented.
verify:
	uv run --with pytest pytest -q

# The Module 7 map: which task shape → which execution pattern.
map:
	@echo "Яка задача → який патерн виконання (мапа Module 7):"
	@echo ""
	@echo "  • Бінарний так/ні критерій «готово», маленька замкнена задача"
	@echo "      → Ralph loop            (7.2)   напр. SNIP-1 store"
	@echo "  • Автономний фініш без саморобної обв'язки (цикл/sentinel руками не пишемо)"
	@echo "      → /goal                 (7.3)   напр. SNIP-2 tags"
	@echo "  • Багато незалежних підзадач (різні файли, не блокують одна одну)"
	@echo "      → dynamic workflow      (7.4)   напр. SNIP-3 search + SNIP-4 dedupe паралельно"
	@echo "  • Робота поза чатом / за розкладом (довгий прогін, AFK)"
	@echo "      → background execution  (7.5)   вісь HOW/WHERE, не окрема story"
	@echo "  • «Готово» треба довести (перевірка результату, а не лише запуск)"
	@echo "      → feedback loops        (7.6)   вісь HOW/WHERE, не окрема story"
	@echo "  • Критична логіка з точними правилами - тест-першим"
	@echo "      → TDD                   (7.7)   напр. SNIP-5 export"
	@echo ""
	@echo "  7.5 (background) і 7.6 (feedback) - це осі ЯК/ДЕ виконується й перевіряється"
	@echo "  робота, а не окремі stories. Будь-яку story можна гнати фоново і під feedback loop."

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
