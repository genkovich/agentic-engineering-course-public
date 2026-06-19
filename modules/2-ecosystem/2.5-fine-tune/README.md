# Demo: Fine-tuning (QLoRA з Unsloth)

**Module:** 2 - Ecosystem
**Lectures:** 2.5

## Що показує

Третій з трьох підходів які порівнює лекція 2.5: fine-tuning опенсорс моделі через QLoRA (Quantized Low-Rank Adaptation) на безкоштовній Google Colab T4 GPU. Скрипт демонструє:

1. Завантажує TinyLlama-1.1B у 4-bit квантизації (QLoRA), щоб модель влізла в обмежену VRAM.
2. Додає LoRA адаптери (rank=16) до attention і feed-forward шарів. Базова модель заморожена, тренуємо тільки ~1% параметрів.
3. Тестує модель ДО тренування на трьох питаннях про вигаданий продукт TeamHub. Видно що модель не знає специфіки і відповідає узагальнено.
4. Тренує 3 епохи на ~50 прикладах з training_data.jsonl (стиль support бота TeamHub).
5. Тестує модель ПІСЛЯ тренування на тих самих питаннях. Видно що відповіді стали конкретні і відповідають style guide.
6. Merge LoRA з базовою моделлю → одна звичайна модель без overhead.
7. Інструкції як скачати з Colab і запустити локально через Ollama (GGUF формат).

Ключове розуміння: fine-tuning не для додавання знань (це дорого і нестабільно, краще RAG), а для зміни стилю, формату, тону. Тренуємо маленьку модель замість величезної бо рахуємо вартість inference.

Чому Anthropic не пропонує fine-tuning Claude публічно: Claude занадто великий щоб ефективно файнтюнити під одну задачу, і architectural choice (Constitutional AI) ускладнює це. Anthropic натомість пропонує prompt caching, system prompts, distillation через окрему програму, і Skills у Claude Code.

## Pre-requisites

- Google акаунт (для безкоштовної Colab T4 GPU)
- Або локальна NVIDIA GPU з 8+ ГБ VRAM

Запустити локально на CPU або Apple Silicon неможливо. CUDA toolkit і Unsloth потрібні.

## Як запустити

```bash
make help     # покаже інструкції для Colab
```

Кроки:

1. Відкрити https://colab.research.google.com
2. New notebook, потім Runtime → Change runtime type → T4 GPU.
3. Завантажити `finetune_unsloth.py` і `training_data.jsonl` у файловий менеджер Colab (зліва).
4. Скопіювати код з `finetune_unsloth.py` у комірки notebook.
5. Запустити по комірках. Тренування на T4 займає ~5-10 хвилин на 50 прикладах і 3 епохи.

## Очікуваний output

- Скільки параметрів тренуємо: `~16M / 1.1B (1.45%)`.
- ТЕСТ ДО FINE-TUNING: відповіді на 3 питання, видно що TinyLlama не знає TeamHub.
- Прогрес тренування: loss падає по кроках.
- ТЕСТ ПІСЛЯ FINE-TUNING: ті самі 3 питання, відповіді тепер у style guide бота TeamHub.
- Збереження merged моделі у `teamhub-bot-merged/` (~2.2 ГБ float16).
- Інструкції для трьох варіантів deployment: ZIP з Colab, HuggingFace Hub, GGUF для Ollama.

## Source

- Lecture 2.5 у курсі "Agentic Engineering з Claude"
- Unsloth документація: https://docs.unsloth.ai
- LoRA paper (Hu et al, 2021): https://arxiv.org/abs/2106.09685
- QLoRA paper (Dettmers et al, 2023): https://arxiv.org/abs/2305.14314
- TinyLlama: https://github.com/jzhang38/TinyLlama
