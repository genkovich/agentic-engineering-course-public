# 8.3 - Підключення MCP серверів. Конфіг-кит: приклади .mcp.json + одне живе підключення.
.PHONY: demo help

# Єдиний сервер з прикладів, який працює без ключа - Context7 (stdio).
# Решта (github=http з Bearer, slack=stdio з env, playwright=stdio) у
# .mcp.json.example показують транспорти і env-expansion, але потребують токенів.
demo:
	npx @modelcontextprotocol/inspector --cli npx -y @upstash/context7-mcp --method tools/list

help:
	@echo "make demo - підключити Context7 без ключа і подивитись tools/list"
