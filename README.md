# AI Agent MultiRole Telegram Bot

Telegram-бот с поддержкой нескольких AI-провайдеров, памятью диалога, сменой ролей, генерацией изображений и видео.

---

> 📐 Архитектурная документация с диаграммами C4, BPMN и UML — в файле [ARCHITECTURE.md](ARCHITECTURE.md)

## Возможности

- Три AI-провайдера: **Z.AI**, **ProxyAPI (OpenAI)**, **GenAPI**
- Выбор модели и температуры при первом запуске и через `/settings`
- Память диалога — последние 10 пар сообщений на пользователя (сохраняется между перезапусками)
- 5 режимов (ролей): помощник, разработчик, писатель, учитель, аналитик — легко расширяются через `prompts.json`
- Генерация изображений (`/image`) — DALL·E, GPT-Image-1, GLM-Image, Flux, Recraft и др.
- Генерация видео (`/video`) — Sora, CogVideoX-3, Kling, LTX, PixVerse и др.
- Подсчёт стоимости каждого запроса в рублях (курс ЦБ РФ)
- Логирование в консоль и файл `bot.log` с ротацией

---

## Структура проекта

```
├── main.py           # Точка входа, все хендлеры бота
├── config.py         # Провайдеры, модели, константы
├── memory.py         # Хранение истории диалогов и настроек
├── prompts.json      # Системные промпты (роли)
├── requirements.txt  # Зависимости
├── .env              # Ключи API (не коммитить!)
├── memory.json       # Автосоздаётся: история диалогов
├── user_settings.json # Автосоздаётся: настройки пользователей
└── bot.log           # Автосоздаётся: лог бота
```

---

## Установка

**Требования:** Python 3.10+

```bash
# 1. Клонировать репозиторий
git clone https://github.com/your/repo.git
cd repo

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Заполнить .env (см. раздел ниже)

# 4. Запустить бота
python main.py
```

---

## Настройка .env

```env
# Токен Telegram-бота (получить у @BotFather)
BOT_TOKEN=your_telegram_bot_token

# Z.AI — https://api.z.ai
ZAI_API_KEY=your_zai_key

# ProxyAPI — https://proxyapi.ru
PROXY_API_KEY=your_proxyapi_key

# Cerebras — https://cloud.cerebras.ai
CEREBRAS_API_KEY=your_cerebras_key

```

Нужен только тот ключ, провайдера которого планируешь использовать.

---

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Первый запуск, выбор провайдера/модели/температуры |
| `/settings` | Изменить провайдера, модель или температуру |
| `/mode` | Сменить роль ИИ (сбрасывает историю) |
| `/reset` | Очистить историю диалога |
| `/image` | Сгенерировать изображение |
| `/video` | Сгенерировать видео |
| `/help` | Список команд |

---

## Провайдеры и модели

### Z.AI

**Текстовые / мультимодальные LLM**

| Модель | Бесплатно | Описание |
|---|:---:|---|
| GLM-4.7-Flash | ✅ | Быстрый и бесплатный. Повседневные задачи, чат |
| GLM-4.5-Flash | ✅ | Бесплатный. Лёгкие задачи, высокая скорость |
| GLM-4.7 | — | Код, рассуждения, агентные задачи |
| GLM-4.5 | — | Флагман для агентов, MoE-архитектура, 128k контекст |
| GLM-4.6 | — | Лучшая модель для кода, 200k контекст |
| GLM-5 | — | Топ-модель: сложный код, архитектура систем |
| GLM-5-Turbo | — | GLM-5 с упором на скорость и агентные цепочки |
| GLM-4.5V | — | Vision: анализ изображений, видео, GUI-агенты |
| GLM-4.6V | — | Vision: понимание изображений + Function Calling |

**Изображения:** GLM-Image (text-to-image)  
**Видео:** CogVideoX-3 (text/image-to-video, до 4K, с аудио)

---

### ProxyAPI (OpenAI)

**Текстовые LLM**

| Модель | Описание |
|---|---|
| GPT-4.1 Nano | Самый дешёвый GPT-4.1. Простые задачи, высокая скорость |
| GPT-4.1 Mini | Баланс цены и качества. Код, тексты, анализ |
| GPT-4.1 | Флагман OpenAI. Сложный код, длинный контекст |
| GPT-4o Mini | Мультимодальный, быстрый. Чат, изображения |
| GPT-4o | Мультимодальный флагман. Текст, код, зрение |

**Изображения:** DALL·E 2, DALL·E 3, GPT-Image-1 (высокое качество)  
**Видео:** Sora, Sora-2 (до 4K, 90 сек)

---

### GenAPI

**Текстовые LLM**

| Модель | Описание |
|---|---|
| GPT-4.1 Mini | Быстрый и экономичный GPT-4.1 для повседневных задач |
| GPT-4.1 | Флагман OpenAI. Сложный код, длинный контекст |
| GPT-5.4 | Топ OpenAI. Глубокий анализ, сложные инструкции |
| GPT-5.4 Mini | GPT-5.4 облегчённый. Быстро и качественно |
| GPT-4o | Мультимодальный флагман. Текст, код, зрение |
| Claude Sonnet 4.5 | Anthropic. Длинные тексты, нюансированный стиль |
| Gemini 2.5 Flash | Google. Быстрый, мультимодальный, длинный контекст |
| Gemini 3.1 Flash Lite | Google. Самый дешёвый Gemini 3.1, высокая скорость |
| DeepSeek Chat | Китайская модель. Код и чат по низкой цене |
| DeepSeek R1 | Reasoning-модель. Математика, логика, сложный анализ |
| GLM-5 | Z.AI топ-модель. Код, архитектура, агентные задачи |
| Qwen 3.5 | Alibaba. Длинный контекст, многоязычность |

**Изображения:** GLM-Image, Flux 2 Klein, Recraft v4 Pro, Qwen Image 2/Max, Seedream v5 Lite, Nano Banana 2, Kling Image V3, Hunyuan Image V3, Grok Imagine Image, FireRed Image Edit  
**Видео:** Kling Video O3/V3/v2.6, LTX 2/2.3, PixVerse 5.5, ViduQ3Video, Grok Imagine Video

---

### Cerebras

Самый быстрый инференс в мире — до 3000 tok/s на собственных чипах WSE.  
Ключ: [cloud.cerebras.ai](https://cloud.cerebras.ai) → API Keys → `CEREBRAS_API_KEY` в `.env`  
Есть бесплатный tier (Llama 3.1 8B).

| Модель | ID | Скорость | Бесплатно | Описание |
|---|---|---|:---:|---|
| Llama 3.1 8B | `llama3.1-8b` | ~2200 tok/s | ✅ | Быстрый и бесплатный. Чат, простые задачи |
| Qwen 3 235B | `qwen-3-235b` | ~1400 tok/s | — | Мощная модель Alibaba. Код, анализ (Preview) |
| GPT OSS 120B | `gpt-oss-120b` | ~3000 tok/s | — | OpenAI open-source 120B. Самый быстрый |
| GLM-4.7 (ZAI) | `glm-4.7` | ~1000 tok/s | — | Z.AI GLM-4.7 через Cerebras (Preview) |

---

### HuggingFace Inference Providers

Роутер поверх 18+ провайдеров (Groq, Together, Novita, SambaNova, Fireworks и др.) — единый API, автовыбор провайдера.  
Ключ: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → fine-grained token с разрешением "Make calls to Inference Providers" → `HF_TOKEN` в `.env`

Суффиксы к model ID: `:fastest` — максимальная скорость, `:cheapest` — минимальная цена.

| Модель | ID | Описание |
|---|---|---|
| Llama 3.1 8B | `meta-llama/Llama-3.1-8B-Instruct:cheapest` | Быстрый и дешёвый. Чат, простые задачи |
| Llama 3.3 70B | `meta-llama/Llama-3.3-70B-Instruct:fastest` | Мощный Llama 3.3. Код, анализ, 131k контекст |
| GPT OSS 120B | `openai/gpt-oss-120b:fastest` | OpenAI open-source 120B. Высокая скорость |
| GPT OSS 20B | `openai/gpt-oss-20b:cheapest` | OpenAI open-source 20B. Самый дешёвый |
| DeepSeek V3.2 | `deepseek-ai/DeepSeek-V3.2:cheapest` | Код, рассуждения, низкая цена |
| DeepSeek R1 | `deepseek-ai/DeepSeek-R1:fastest` | Reasoning-модель. Математика, логика |
| Qwen 3 235B | `Qwen/Qwen3-235B-A22B-Instruct-2507:cheapest` | Мощная Qwen 3 MoE. Код, многоязычность |
| Qwen 3 32B | `Qwen/Qwen3-32B:fastest` | Баланс скорости и качества |
| Kimi K2.5 | `moonshotai/Kimi-K2.5:cheapest` | Moonshot. Длинный контекст 262k |
| GLM-5 | `zai-org/GLM-5:cheapest` | Z.AI GLM-5. Код, агентные задачи |
| Llama 4 Maverick | `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8:cheapest` | 1M контекст, мультимодальный |

**Изображения** (через `huggingface_hub`): FLUX.1-dev, FLUX.1-schnell, Stable Diffusion 3.5 Large

---

## Добавление новых ролей

Открой `prompts.json` и добавь новый объект в `prompts`:

```json
"coder": {
  "name": "Senior Developer",
  "description": "Пишет production-ready код.",
  "system_prompt": "Ты — senior-разработчик. Пиши чистый, хорошо документированный код."
}
```

Перезапуск бота не нужен — промпты загружаются при старте.

Доступные роли по умолчанию:

| Ключ | Название | Назначение |
|---|---|---|
| `assistant` | Обычный помощник | Повседневные задачи, общий чат |
| `developer` | Помощник разработчика | Написание и объяснение кода |
| `writer` | Редактор текстов | Статьи, посты, описания |
| `teacher` | Учитель | Объяснение сложных тем простыми словами |
| `analyst` | Аналитик | Анализ данных, принятие решений |
| `architect` | Системный архитектор | Проектирование систем, выбор технологий, архитектурные решения |
| `ui_designer` | UI/UX Дизайнер | Проектирование интерфейсов, usability, UX-паттерны |

---

## Логирование

Логи пишутся одновременно в консоль и файл `bot.log`.  
Ротация: максимум 5 МБ на файл, хранится 3 последних файла (`bot.log`, `bot.log.1`, `bot.log.2`).

Уровень логирования можно изменить в `main.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)  # подробнее
logging.basicConfig(level=logging.WARNING, ...) # только ошибки
```
