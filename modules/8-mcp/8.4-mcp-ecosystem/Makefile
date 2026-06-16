# 8.4 - Екосистема MCP. Конфіг-кит: куровані конфіги + DECISION.md.
.PHONY: inspect help

# Найдешевший мешканець конфігу - Context7 (~тисяча токенів definitions, без ключа).
# Підключаємось і дивимось два його tools: resolve-library-id, query-docs.
inspect:
	npx @modelcontextprotocol/inspector --cli npx -y @upstash/context7-mcp --method tools/list

help:
	@echo "make inspect - tools/list Context7 (без ключа)"
	@echo "DECISION.md  - чек-лист довіри і матриця MCP vs CLI"
