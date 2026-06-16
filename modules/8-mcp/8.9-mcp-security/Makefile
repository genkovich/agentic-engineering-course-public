# 8.9 - Безпека MCP. Інспекційна фікстура: отруєний vs безпечний сервер.
# Демо лише показує отруєний ОПИС - нічого реально не крадеться.
.PHONY: install build inspect-poisoned inspect-safe clean

node_modules: package.json
	npm install

install: node_modules

build: node_modules
	npm run build

# Аудит ОТРУЄНОГО сервера очима моделі: у description інструмента add видно
# схований блок <IMPORTANT> з командою прочитати ~/.ssh/id_rsa і параметр note.
# Рівно ці червоні прапорці шукаєш у чужому сервері ПЕРЕД підключенням.
inspect-poisoned: build
	npx @modelcontextprotocol/inspector --cli node dist/server.poisoned.js --method tools/list

# Для контрасту - чистий двійник: той самий add, чесний опис, без note.
inspect-safe: build
	npx @modelcontextprotocol/inspector --cli node dist/server.safe.js --method tools/list

clean:
	rm -rf node_modules dist
