# 8.2 - MCP примітиви. Крихітний read-only сервер для інспекції трьох примітивів.
# Стандартний API: make build / make inspect* / make clean
.PHONY: install build inspect inspect-resources inspect-prompts clean

node_modules: package.json
	npm install

install: node_modules

# Збірка TS -> dist. Inspector запускає сервер як справжній процес (node dist/server.js).
build: node_modules
	npm run build

# Примітив 1 - TOOLS (model-controlled): список інструментів, які модель викликає сама.
inspect: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method tools/list

# Примітив 2 - RESOURCES (app-controlled): дані за URI, які читає додаток.
inspect-resources: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method resources/list

# Примітив 3 - PROMPTS (user-controlled): шаблони, які запускає людина.
inspect-prompts: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method prompts/list

clean:
	rm -rf node_modules dist
