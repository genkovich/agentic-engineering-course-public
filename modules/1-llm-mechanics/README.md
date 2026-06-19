# Module 1 - LLM Mechanics

Як LLM реально працює зсередини: токени, контекстне вікно, латентність, ціна, embeddings, агентний loop. Цей модуль не про Claude Code, а про модель під капотом - щоб ти міг свідомо приймати рішення про prompt design, цінову економіку, і архітектуру агента.

## Лекції модуля

- 1.1 Що таке LLM - загальний огляд
- 1.2 Що таке токен і чому це важливо
- 1.3 Контекстне вікно
- 1.4 Як модель пише відповідь (autoregression, sampling)
- 1.5 Системний промпт vs користувацький
- 1.6 Параметри генерації (temperature, top_p, stop sequences)
- 1.7 Stateless природа моделі і як це впливає на агентів
- 1.8 Latency: першим токеном vs повна відповідь
- 1.9 Embeddings - що це і коли треба
- 1.10 Multi-modal входи (зображення, документи)
- 1.11 Безпека: prompt injection на рівні моделі
- 1.12 Опенсорс vs пропрієтарні моделі
- 1.13 Як обирати модель під задачу

## Артефакти модуля

Модуль концептуальний, але дві ключові концепції простіше зрозуміти через runnable demo:

| Demo | Що показує | Лекції |
|---|---|---|
| [1.2-token-counter](./1.2-token-counter) | Як рахуються токени, чому UA дорожча за EN, ціна input vs output | 1.1, 1.2 |
| [1.3-context-window](./1.3-context-window) | Як вигорає контекстне вікно під час сесії, коли треба `/compact` | 1.3, 1.7 |
| [1.4-stochasticity](./1.4-stochasticity) | Той самий промпт через T=0/0.5/1.0, чому промпт це теж "ручка temperature" | 1.4 |
| [1.9-embeddings](./1.9-embeddings) | Cosine similarity для слів, king-man+woman ≈ queen, семантичний пошук | 1.9 |

Demos самостійні: `cd modules/1-llm-mechanics/<N.M-demo> && pip install -r requirements.txt && make run`.

## Pre-requisites

- Python 3.10+
- ANTHROPIC_API_KEY (отримати на console.anthropic.com)

## Додаткові ресурси

- **Anthropic Academy: AI Fluency** - безкоштовний курс від Anthropic про роботу з LLM на концептуальному рівні. Покриває все, що тут лекціях, плюс ширший контекст. https://www.anthropic.com/ai-fluency
- **Anthropic Cookbook** - збірник Jupyter notebook прикладів по фічах SDK. https://github.com/anthropics/anthropic-cookbook

## Що робити після цього модуля

Module 2 (Ecosystem) розкаже як ці концепції збираються у працюючі агенти: tool use, agentic loop, fine-tuning vs RAG, prompt injection захисти. Module 3 (Claude Code Setup) покаже як використовувати готовий агент (Claude Code) для свого проекту.
