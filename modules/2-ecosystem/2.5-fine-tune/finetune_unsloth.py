"""
Fine-tune Demo — QLoRA з Unsloth
Лекція 2.5: Fine-tuning vs Prompting vs RAG

Запуск на Google Colab (безкоштовна T4 GPU):
  1. Runtime → Change runtime type → T4 GPU
  2. Запустіть код по комірках

Після тренування модель можна скачати і юзати локально — див. Крок 8.
"""

# ── Встановлення (запустіть першою коміркою в Colab) ──────────────────
# !pip install unsloth                                # фреймворк для швидкого fine-tuning
# !pip install --no-deps trl peft accelerate bitsandbytes  # залежності без конфліктів версій

# ── Імпорти ───────────────────────────────────────────────────────────

from unsloth import FastLanguageModel  # обгортка Unsloth для завантаження моделей з QLoRA
import torch                           # PyTorch — основна бібліотека для ML
import json                            # для читання JSONL тренувальних даних

# ── Крок 1: Завантажуємо маленьку модель ─────────────────────────────

MODEL_NAME = "unsloth/tinyllama-chat"  # TinyLlama 1.1B параметрів — маленька модель для демо
MAX_SEQ_LENGTH = 2048                  # максимальна довжина тексту в токенах (вхід + вихід)
LORA_RANK = 16                         # розмір LoRA патчу: більше = якісніше, але повільніше і більше памʼяті

print("📦 Завантажуємо модель...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,       # яку модель завантажити з HuggingFace
    max_seq_length=MAX_SEQ_LENGTH,  # обмеження довжини тексту
    dtype=None,                  # автовизначення типу даних (float16 для T4 GPU)
    load_in_4bit=True,           # QLoRA: стискаємо модель до 4-біт — в 4 рази менше памʼяті
)
print(f"✅ Модель {MODEL_NAME} завантажена (4-bit)")

# ── Крок 2: Додаємо LoRA адаптери ────────────────────────────────────
#
# Ось тут відбувається те, що ми вивчали в лекції:
# - Базова модель ЗАМОРОЖЕНА (її ваги не змінюються)
# - Додаємо маленький LoRA "патч" (rank=16)
# - Тренуємо ТІЛЬКИ цей патч (~1% параметрів моделі)

print("🎯 Додаємо LoRA адаптери...")
model = FastLanguageModel.get_peft_model(
    model,                         # базова модель до якої додаємо патч
    r=LORA_RANK,                   # rank — розмір патчу (16 = хороший баланс якість/швидкість)
    target_modules=[               # які шари моделі патчимо (attention + feed-forward)
        "q_proj", "k_proj",        # query і key проєкції в attention механізмі
        "v_proj", "o_proj",        # value і output проєкції в attention механізмі
        "gate_proj", "up_proj",    # feed-forward шари (вхідні)
        "down_proj",               # feed-forward шар (вихідний)
    ],
    lora_alpha=16,                 # масштабуючий коефіцієнт LoRA (зазвичай = rank)
    lora_dropout=0,                # dropout 0 = не викидаємо випадкові нейрони (Unsloth оптимізація)
    bias="none",                   # не тренуємо bias параметри (економія памʼяті)
    use_gradient_checkpointing="unsloth",  # Unsloth-оптимізація: менше памʼяті при тренуванні
)
print(f"✅ LoRA додано (rank={LORA_RANK})")

# Скільки параметрів тренуємо? Порівнюємо з загальною кількістю
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)  # тільки LoRA параметри
total = sum(p.numel() for p in model.parameters())                         # всі параметри моделі
print(f"📊 Тренуємо: {trainable:,} / {total:,} параметрів ({100*trainable/total:.2f}%)")

# ── Крок 3: Готуємо тренувальні дані ─────────────────────────────────

def format_prompt(instruction: str, response: str = "") -> str:
    """Форматує дані в чат-формат TinyLlama.
    Кожна модель має свій формат — TinyLlama використовує <|system|>, <|user|>, <|assistant|> теги.
    """
    text = f"<|system|>\nТи — бот підтримки TeamHub. Відповідай коротко, конкретно, українською.</s>\n"
    text += f"<|user|>\n{instruction}</s>\n"   # питання користувача
    text += f"<|assistant|>\n{response}</s>"   # ідеальна відповідь (те чому ми вчимо модель)
    return text

# Читаємо тренувальні дані з JSONL файлу (кожен рядок = окремий JSON обʼєкт)
with open("training_data.jsonl", "r", encoding="utf-8") as f:
    raw_data = [json.loads(line) for line in f]  # парсимо кожен рядок як JSON

# Перетворюємо в формат який розуміє модель
train_data = []
for item in raw_data:
    train_data.append({
        "text": format_prompt(item["instruction"], item["response"])  # "запит → відповідь" пара
    })

print(f"📄 Тренувальних прикладів: {len(train_data)}")

# ── Крок 4: Тест ДО fine-tuning ──────────────────────────────────────
# Запитаємо модель ДО тренування — побачимо що вона не знає про TeamHub

print("\n" + "="*50)
print("🔍 ТЕСТ ДО FINE-TUNING:")
print("="*50)

test_questions = [
    "Як підключити Slack?",
    "Скільки коштує Pro план?",
    "Як налаштувати SSO?",
]

FastLanguageModel.for_inference(model)  # переводимо модель в режим генерації (не тренування)
for q in test_questions:
    prompt = format_prompt(q)                       # форматуємо питання в чат-формат
    prompt = prompt.rsplit("</s>", 1)[0]            # прибираємо останню </s> — модель має згенерувати відповідь сама
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")  # токенізуємо і відправляємо на GPU
    outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)  # генеруємо до 100 токенів
    result = tokenizer.decode(outputs[0], skip_special_tokens=False)  # декодуємо токени назад в текст
    answer = result.split("<|assistant|>")[-1].replace("</s>", "").strip()  # витягуємо тільки відповідь
    print(f"\n❓ {q}")
    print(f"🤖 {answer[:200]}")  # показуємо перші 200 символів відповіді

# ── Крок 5: Тренування ───────────────────────────────────────────────

from trl import SFTTrainer             # Supervised Fine-Tuning тренер з HuggingFace TRL
from transformers import TrainingArguments  # конфігурація тренування
from datasets import Dataset           # формат даних HuggingFace

print("\n" + "="*50)
print("🏋️ ТРЕНУВАННЯ (QLoRA з Unsloth)")
print("="*50)

dataset = Dataset.from_list(train_data)  # перетворюємо наш список в HuggingFace Dataset

trainer = SFTTrainer(
    model=model,                         # модель з LoRA адаптерами
    tokenizer=tokenizer,                 # токенізатор для обробки тексту
    train_dataset=dataset,               # наші тренувальні дані
    dataset_text_field="text",           # яке поле в dataset містить текст
    max_seq_length=MAX_SEQ_LENGTH,       # максимальна довжина послідовності
    args=TrainingArguments(
        per_device_train_batch_size=2,   # скільки прикладів обробляємо за раз (2 = економія памʼяті)
        gradient_accumulation_steps=4,   # накопичуємо градієнти за 4 кроки (ефективний batch = 2*4 = 8)
        warmup_steps=5,                  # перші 5 кроків — плавне збільшення learning rate
        num_train_epochs=3,              # скільки разів проходимо по всіх даних (3 = достатньо для демо)
        learning_rate=2e-4,              # швидкість навчання (0.0002 — стандарт для LoRA)
        fp16=not torch.cuda.is_bf16_supported(),  # float16 якщо GPU не підтримує bfloat16
        bf16=torch.cuda.is_bf16_supported(),      # bfloat16 якщо підтримується (краще для тренування)
        logging_steps=1,                 # логувати прогрес кожен крок
        output_dir="outputs",            # папка для чекпоінтів тренування
        optim="adamw_8bit",              # оптимізатор в 8-біт форматі (менше памʼяті)
    ),
)

print("🚀 Починаємо тренування...")
stats = trainer.train()                  # запускаємо тренування — це може зайняти кілька хвилин
print(f"✅ Тренування завершено за {stats.metrics['train_runtime']:.0f} секунд")

# ── Крок 6: Тест ПІСЛЯ fine-tuning ───────────────────────────────────
# Ті самі питання — але тепер модель натренована на наших даних

print("\n" + "="*50)
print("🔍 ТЕСТ ПІСЛЯ FINE-TUNING:")
print("="*50)

FastLanguageModel.for_inference(model)  # знову переводимо в режим генерації
for q in test_questions:
    prompt = format_prompt(q)
    prompt = prompt.rsplit("</s>", 1)[0]
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
    result = tokenizer.decode(outputs[0], skip_special_tokens=False)
    answer = result.split("<|assistant|>")[-1].replace("</s>", "").strip()
    print(f"\n❓ {q}")
    print(f"🤖 {answer[:200]}")

# ── Крок 7: Merge LoRA з базовою моделлю ─────────────────────────────

print("\n" + "="*50)
print("🔗 MERGE — зливаємо LoRA патч з моделлю")
print("="*50)

# Merge: нові ваги = старі ваги + LoRA патч (додавання чисел)
# Після merge модель працює без LoRA — патч вбудований назавжди, нуль overhead
model.save_pretrained_merged(
    "teamhub-bot-merged",        # папка куди зберегти злиту модель
    tokenizer,                   # зберігаємо і токенізатор
    save_method="merged_16bit",  # зберігаємо в float16 (стандартний формат для inference)
)
print("✅ Модель збережена в teamhub-bot-merged/")
print("   Це звичайна модель яка працює без LoRA — патч вбудований назавжди")

# ── Крок 8: Як скачати і юзати локально ──────────────────────────────
#
# Натренована модель лежить в папці teamhub-bot-merged/
# Ось як її скачати з Colab і запустити на своєму компʼютері:
#
# === Варіант 1: Скачати як ZIP з Colab ===
#
# В Colab виконайте:
#   !zip -r teamhub-bot.zip teamhub-bot-merged/
#
# Потім у файловому менеджері Colab (зліва) знайдіть teamhub-bot.zip
# і натисніть "Download". Файл ~2-3 ГБ.
#
# === Варіант 2: Завантажити на HuggingFace Hub ===
#
# model.push_to_hub_merged(
#     "your-username/teamhub-bot",    # ваш HuggingFace repo
#     tokenizer,
#     save_method="merged_16bit",
#     token="hf_...",                 # HuggingFace API token
# )
#
# Потім на іншому компʼютері:
#   pip install transformers torch
#   model = AutoModelForCausalLM.from_pretrained("your-username/teamhub-bot")
#
# === Варіант 3: Конвертувати в GGUF для Ollama ===
#
# GGUF — формат для запуску моделей через Ollama (найпростіший спосіб локально):
#
# model.save_pretrained_gguf(
#     "teamhub-bot-gguf",            # папка для GGUF файлу
#     tokenizer,
#     quantization_method="q4_k_m",  # квантизація 4-біт (маленький файл, гарна якість)
# )
#
# Потім скачуємо .gguf файл і створюємо Modelfile для Ollama:
#
#   # Modelfile
#   FROM ./teamhub-bot-q4_k_m.gguf
#   SYSTEM "Ти — бот підтримки TeamHub. Відповідай коротко, конкретно, українською."
#
# Запускаємо:
#   ollama create teamhub-bot -f Modelfile
#   ollama run teamhub-bot
#
# Все! Тепер модель працює локально через Ollama без інтернету і без GPU.

print("\n" + "="*50)
print("📥 ЯК СКАЧАТИ І ЮЗАТИ ЛОКАЛЬНО:")
print("="*50)
print("""
Варіант 1 — ZIP з Colab:
  !zip -r teamhub-bot.zip teamhub-bot-merged/
  → скачати через файловий менеджер Colab

Варіант 2 — HuggingFace Hub:
  model.push_to_hub_merged("your-username/teamhub-bot", tokenizer, ...)
  → потім pip install transformers && python -c "from transformers import ..."

Варіант 3 — GGUF для Ollama (рекомендовано для локального юзу):
  model.save_pretrained_gguf("teamhub-bot-gguf", tokenizer, quantization_method="q4_k_m")
  → ollama create teamhub-bot -f Modelfile
  → ollama run teamhub-bot

Деталі в коментарях вище 👆
""")
