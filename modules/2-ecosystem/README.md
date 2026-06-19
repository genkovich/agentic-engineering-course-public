# Module 2 - Ecosystem and Agentic Mindset

Як LLM перетворюється на робочого агента: tool use, agentic loop, fine-tuning vs RAG vs prompting, prompt injection і захисти. Цей модуль про патерни, які лежать в основі будь-якого AI-асистента (включно з Claude Code).

## Лекції модуля

- 2.1 Tool use - як модель отримує доступ до зовнішнього світу
- 2.2 Coding assistants - звідки взялась ідея AI-програміста
- 2.3 Agentic loop - observe → think → act, як патерн
- 2.4 MCP як стандарт інтеграції tools
- 2.5 Fine-tuning vs Prompting vs RAG - коли що
- 2.6 Prompt injection і захисти
- 2.7 Multi-agent системи - коли потрібні
- 2.8 Memory і long-running агенти
- 2.9 Економіка агентного запуску - як рахувати ROI

## Артефакти модуля

| Demo | Що показує | Лекції |
|---|---|---|
| [2.1-tool-use](./2.1-tool-use) | Базовий tool use з Anthropic SDK, цикл tool_use → tool_result | 2.1, 2.2 |
| [2.3-agentic-loop](./2.3-agentic-loop) | Явна реалізація observe → think → act loop без SDK helpers | 2.3 |
| [2.5-rag](./2.5-rag) | Робочий RAG pipeline: PGVector + OpenAI embeddings + Claude | 2.5 |
| [2.5-fine-tune](./2.5-fine-tune) | QLoRA з Unsloth: fine-tune опенсорс моделі (TinyLlama) на Colab T4 | 2.5 |
| [2.6-prompt-injection](./2.6-prompt-injection) | 3 типи атак (direct/indirect/markdown exfil) і defense-in-depth pipeline | 2.6 |
| [2.7-data-privacy](./2.7-data-privacy) | Інспекція env vars що контролюють telemetry в Claude Code | 2.7 |

Demos самостійні: `cd modules/2-ecosystem/<N.M-demo> && pip install -r requirements.txt && make run`.

## Pre-requisites

- Python 3.10+
- ANTHROPIC_API_KEY

## Три підходи з лекції 2.5: prompting, RAG, fine-tuning

Лекція 2.5 порівнює три способи "вчити" модель про свій домен:

1. **Prompting + caching** для документів менше 200K токенів. Просто покладеш все у system prompt, prompt caching робить це дешевим. Demo: будь-який tool-use приклад.
2. **RAG** для великих корпусів і часто-оновлюваних даних. Demo `rag/` показує робочий PGVector + OpenAI pipeline.
3. **Fine-tuning опенсорс моделі** для зміни стилю, формату, тону. Demo `fine-tune/` показує QLoRA + Unsloth на TinyLlama (працює на безкоштовній Colab T4).

Anthropic не пропонує публічного fine-tuning Claude (Claude занадто великий, Constitutional AI ускладнює). Замість цього: prompt caching, distillation program (preview), Skills у Claude Code. Якщо реально потрібен fine-tune, бери опенсорс через Unsloth / AWS Bedrock / together.ai.

## Додаткові ресурси

- **Anthropic Cookbook** - tool use, multi-agent, RAG приклади. https://github.com/anthropics/anthropic-cookbook
- **MCP документація** - https://modelcontextprotocol.io
- **Building effective agents** (Anthropic blog post про патерни): https://www.anthropic.com/engineering/building-effective-agents

## Що робити після цього модуля

Module 3 (Claude Code Setup) бере готовий агент (Claude Code) і вчить як його встановити, налаштувати і захистити для свого проекту.
