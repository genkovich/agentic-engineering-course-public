# 8.5 - Claude як MCP-сервер. Скрипт-кит навколо вбудованого `claude mcp serve`.
# Власного коду немає: сервер - це сам Claude Code. Потрібен встановлений `claude`.
.PHONY: serve-help tools no-resources read clean

# Дві опції і нуль налаштувань транспорту: це stdio-процес, який запускає клієнт.
serve-help:
	claude mcp serve --help

# Поглянути на сервер очима клієнта: Inspector робить initialize + tools/list.
# Побачиш внутрішній тулбокс Claude Code (Read, Edit, Write, Bash, ...). Порахуй,
# скільки інструментів у твоїй версії (у 2.1.177 їх 33 - у тебе може відрізнятись).
tools:
	npx @modelcontextprotocol/inspector --cli claude mcp serve --method tools/list

# Сервер реалізує лише примітив tools: resources/list повертає -32601 Method not found.
no-resources:
	npx @modelcontextprotocol/inspector --cli claude mcp serve --method resources/list

# Виклик інструмента Read БЕЗ моделі: вміст serve-demo.txt повертається миттєво,
# без жодного токена і - головне - без жодного підтвердження.
read:
	npx @modelcontextprotocol/inspector --cli claude mcp serve --method tools/call --tool-name Read --tool-arg file_path=$(PWD)/serve-demo.txt

clean:
	@echo "нічого прибирати: ні node_modules, ні dist - сервер це сам claude"
