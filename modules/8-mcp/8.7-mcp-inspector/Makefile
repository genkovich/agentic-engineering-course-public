# 8.7 - MCP Inspector. Самодостатній debug-кит: чесний vs зламаний сервер.
# Стандартний API: make build / inspect / inspect-buggy / smoke / contract / clean
.PHONY: install build inspect inspect-buggy smoke contract clean

node_modules: package.json
	npm install

install: node_modules

build: node_modules
	npm run build

# Smoke-перегляд: tools/list через справжній stdio. Підтверджує, що збірка живе,
# discovery повертає схеми, а stdout чистий від сміття.
inspect: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method tools/list

# Той самий межовий виклик на ЗЛАМАНОМУ сервері: complete_task з фейковим id.
# Очікувана правильна поведінка - isError. Фактична - success: true. Це і є баг.
inspect-buggy: build
	npx @modelcontextprotocol/inspector --cli node dist/server.buggy.js \
		--method tools/call --tool-name complete_task --tool-arg id=task-999

# Контракт #1 (discovery): рівно 3 інструменти. exit 0 = ок, інакше pipeline червоніє.
smoke: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method tools/list \
		| jq -e '.tools | length == 3'

# Контракт #2 (чесність): чесний сервер повертає isError на неіснуючий id.
# exit 0 проти dist/server.js, 1 проти dist/server.buggy.js - так баг ловиться у CI.
contract: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js \
		--method tools/call --tool-name complete_task --tool-arg id=task-999 \
		| jq -e '.isError == true'

clean:
	rm -rf node_modules dist
