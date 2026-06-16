# 8.1 - Що таке MCP. Конфіг-кит без власного коду.
# Підключаємось до публічного zero-key сервера і дивимось його очима клієнта.
.PHONY: inspect help

# Inspector тут сам виступає MCP-КЛІЄНТОМ: робить initialize + tools/list -
# це кроки 1-3 з 12-крокового flow з лекції. У відповіді видно інструменти
# Context7 (resolve-library-id, query-docs) - той самий ListTools.
# Ключа не треба: Context7 публічний.
inspect:
	npx @modelcontextprotocol/inspector --cli npx -y @upstash/context7-mcp --method tools/list

help:
	@echo "make inspect - tools/list публічного Context7 (без ключа), щоб побачити ListTools"
