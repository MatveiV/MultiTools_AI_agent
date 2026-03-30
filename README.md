# AI Agent MultiRole Video Bot

Telegram-бот с поддержкой 5 AI-провайдеров, памятью диалога, 8 ролями, генерацией изображений и видео.

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://aiogram.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> 📐 Архитектурная документация с диаграммами C4, BPMN и UML — в файле [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Возможности

- **5 AI-провайдеров:** Z.AI, ProxyAPI (OpenAI), GenAPI, Cerebras, HuggingFace
- Выбор провайдера, модели и температуры при первом запуске и через `/settings`
- Память диалога — последние 10 пар сообщений на пользователя (сохраняется между перезапусками)
- **8 ролей:** помощник, разработчик, писатель, учитель, аналитик, системный архитектор, UI/UX дизайнер, Senior Developer
- Генерация изображений (`/image`) — DALL·E, GPT-Image-1, GLM-Image, FLUX, Recraft, Kling и др.
- Генерация видео (`/video`) — Sora, CogVideoX-3, Kling, LTX, PixVerse и др.
- Подсчёт стоимости каждого запроса в рублях (курс ЦБ РФ)
- Логирование в консоль и файл `bot.log` с ротацией (5 МБ × 3 файла)
- Длинные ответы автоматически разбиваются на части (лимит Telegram 4096 символов)

---

## Структура проекта

```
├── main.py            # Точка входа: хендлеры, FSM, роутинг к провайдерам
├── config.py          # Провайдеры, модели, цены токенов, константы
├── memory.py          # История диалогов и настройки пользователей (JSON)
├── prompts.json       # Системные промпты для ролей
├── requirements.txt   # Зависимости Python
├── ARCHITECTURE.md    # Диаграммы C4, BPMN, UML
├── .env               # Ключи API (не коммитить!)
├── .gitignore
├── memory.json        # Автосоздаётся: история диалогов
├── user_settings.json # Автосоздаётся: настройки пользователей
└── bot.log            # Автосоздаётся: лог бота
```

---

## Установка

**Требования:** Python 3.10+

```bash
# 1. Клонировать репозиторий
git clone https://github.com/MatveiV/MultiTools_AI_agent.git
cd MultiTools_AI_agent

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env и заполнить ключи (см. раздел ниже)

# 4. Запустить бота
python main.py
```

---

## Настройка .env

```env
# Telegram Bot (получить у @BotFather)
BOT_TOKEN=your_telegram_bot_token

# Z.AI — https://api.z.ai
ZAI_API_KEY=your_zai_key

# ProxyAPI — https://proxyapi.ru (OpenAI через российский прокси)
PROXY_API_KEY=your_proxyapi_key

# GenAPI — https://gen-api.ru
GEN_API_KEY=your_genapi_key

# Cerebras — https://cloud.cerebras.ai (есть free tier)
CEREBRAS_API_KEY=your_cerebras_key

# HuggingFace — https://huggingface.co/settings/tokens
# fine-grained token с разрешением "Make calls to Inference Providers"
HF_TOKEN=your_hf_token
```

Нужен только тот ключ, провайдера которого планируешь использовать.

---

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Первый запуск, выбор провайдера / модели / температуры |
| `/settings` | Изменить провайдера, модель или температуру |
| `/mode` | Сменить роль ИИ (сбрасывает историю диалога) |
| `/reset` | Очистить историю диалога |
| `/image` | Сгенерировать изображение |
| `/video` | Сгенерировать видео |
| `/help` | Список команд |

---

## Провайдеры и модели

### 1. Z.AI

Ключ: [api.z.ai](https://api.z.ai) → `ZAI_API_KEY`

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

**Изображения:** GLM-Image  
**Видео:** CogVideoX-3 (text/image-to-video, до 4K, с аудио)

---

### 2. ProxyAPI (OpenAI)

OpenAI-модели через российский прокси без VPN.  
Ключ: [proxyapi.ru](https://proxyapi.ru) → `PROXY_API_KEY`

| Модель | Описание |
|---|---|
| GPT-4.1 Nano | Самый дешёвый GPT-4.1. Простые задачи, высокая скорость |
| GPT-4.1 Mini | Баланс цены и качества. Код, тексты, анализ |
| GPT-4.1 | Флагман OpenAI. Сложный код, длинный контекст |
| GPT-4o Mini | Мультимодальный, быстрый. Чат, изображения |
| GPT-4o | Мультимодальный флагман. Текст, код, зрение |

**Изображения:** DALL·E 2, DALL·E 3, GPT-Image-1  
**Видео:** Sora, Sora-2 (до 4K, 90 сек)

---

### 3. GenAPI

Агрегатор моделей с поддержкой оплаты картами РФ.  
Ключ: [gen-api.ru](https://gen-api.ru) → `GEN_API_KEY`

| Модель | Описание |
|---|---|
| GPT-4.1 Mini / GPT-4.1 | OpenAI. Код, длинный контекст |
| GPT-5.4 / GPT-5.4 Mini | Топ OpenAI. Глубокий анализ |
| GPT-4o | Мультимодальный флагман |
| Claude Sonnet 4.5 | Anthropic. Длинные тексты, нюансированный стиль |
| Gemini 2.5 Flash | Google. Быстрый, мультимодальный |
| Gemini 2.5 Flash Lite | Google. Самый дешёвый Gemini 2.5 |
| Gemini 3 Flash | Google. Frontier-класс по цене Flash |
| DeepSeek Chat / R1 | Код, чат, reasoning по низкой цене |
| GLM-5 | Z.AI топ-модель |
| Qwen 3.5 | Alibaba. Длинный контекст, многоязычность |

**Изображения:** GLM-Image, Flux 2 Klein, Recraft v4 Pro, Qwen Image 2/Max, Seedream v5 Lite, Nano Banana 2, Kling Image V3, Hunyuan Image V3, Grok Imagine Image, FireRed Image Edit  
**Видео:** Kling Video O3/V3/v2.6, LTX 2/2.3, PixVerse 5.5, ViduQ3Video, Grok Imagine Video

---

### 4. Cerebras

Самый быстрый инференс в мире — до 3000 tok/s на чипах WSE. Есть бесплатный tier.  
Ключ: [cloud.cerebras.ai](https://cloud.cerebras.ai) → `CEREBRAS_API_KEY`

| Модель | ID | Скорость | Бесплатно | Описание |
|---|---|---|:---:|---|
| Llama 3.1 8B | `llama3.1-8b` | ~2200 tok/s | ✅ | Быстрый и бесплатный. Чат, простые задачи |
| Qwen 3 235B | `qwen-3-235b-a22b-instruct-2507` | ~1400 tok/s | — | Мощная MoE-модель Alibaba. Код, анализ |
| GPT OSS 120B | `gpt-oss-120b` | ~3000 tok/s | — | OpenAI open-source 120B. Самый быстрый |
| Llama 3.3 70B | `llama-3.3-70b` | ~2100 tok/s | — | Мощный Llama для сложных задач |

---

### 5. HuggingFace Inference Providers

Роутер поверх 18+ провайдеров (Groq, Together, Novita, SambaNova и др.).  
Ключ: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → fine-grained token с разрешением "Make calls to Inference Providers" → `HF_TOKEN`

Суффиксы к model ID: `:fastest` — максимальная скорость, `:cheapest` — минимальная цена.

| Модель | Описание |
|---|---|
| `meta-llama/Llama-3.1-8B-Instruct:cheapest` | Быстрый и дешёвый. Чат, простые задачи |
| `meta-llama/Llama-3.3-70B-Instruct:fastest` | Мощный Llama 3.3. Код, анализ |
| `openai/gpt-oss-120b:fastest` | OpenAI open-source 120B |
| `openai/gpt-oss-20b:cheapest` | OpenAI open-source 20B. Самый дешёвый |
| `deepseek-ai/DeepSeek-V3.2:cheapest` | Код, рассуждения, низкая цена |
| `deepseek-ai/DeepSeek-R1:fastest` | Reasoning-модель |
| `Qwen/Qwen3-235B-A22B-Instruct-2507:cheapest` | Мощная Qwen 3 MoE |
| `Qwen/Qwen3-32B:fastest` | Баланс скорости и качества |
| `moonshotai/Kimi-K2.5:cheapest` | Длинный контекст 262k |
| `zai-org/GLM-5:cheapest` | Z.AI GLM-5 |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8:cheapest` | 1M контекст, мультимодальный |

**Изображения** (через `huggingface_hub`): FLUX.1-dev, FLUX.1-schnell, Stable Diffusion 3.5 Large

---

## Роли (режимы)

Переключаются командой `/mode`. При смене роли история диалога сбрасывается.

| Ключ | Название | Назначение |
|---|---|---|
| `assistant` | Обычный помощник | Повседневные задачи, общий чат |
| `developer` | Помощник разработчика | Написание и объяснение кода |
| `writer` | Редактор текстов | Статьи, посты, описания |
| `teacher` | Учитель | Объяснение сложных тем простыми словами |
| `analyst` | Аналитик | Анализ данных, принятие решений |
| `architect` | Системный архитектор | Проектирование систем, выбор технологий |
| `ui_designer` | UI/UX Дизайнер | Проектирование интерфейсов, usability |
| `senior_dev` | Senior Developer | Production-ready код, code review, best practices |

Добавить новую роль — отредактировать `prompts.json`:

```json
"my_role": {
  "name": "Моя роль",
  "description": "Краткое описание.",
  "system_prompt": "Ты — ..."
}
```

---

## Логирование

Логи пишутся одновременно в консоль и `bot.log`.  
Ротация: 5 МБ × 3 файла (`bot.log`, `bot.log.1`, `bot.log.2`).

Изменить уровень в `main.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)   # подробнее
logging.basicConfig(level=logging.WARNING, ...) # только ошибки
```

---

## Зависимости

```
aiogram>=3.7.0
openai>=1.30.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
google-auth>=2.29.0
huggingface_hub>=0.24.0
```
