"""
config.py — конфигурация бота: провайдеры, модели, переменные окружения.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ["BOT_TOKEN"]

# ─── Провайдеры и модели (те же, что в ai_direct.py) ─────────────────────────
PROVIDERS: dict = {
    "1": {
        "name": "Z.AI",
        "api_key_env": "ZAI_API_KEY",
        "api_key": os.environ.get("ZAI_API_KEY", ""),
        "base_url": "https://api.z.ai/api/paas/v4/",
        # ── Текстовые / мультимодальные LLM ──────────────────────────────
        "models": {
            "1": {"id": "glm-4.7-flash", "label": "GLM-4.7-Flash",     "free": True,  "temp_range": (0.0, 1.0), "max_tokens": 4096,  "desc": "Быстрый и бесплатный. Повседневные задачи, чат"},
            "2": {"id": "glm-4.5-flash", "label": "GLM-4.5-Flash",     "free": True,  "temp_range": (0.0, 1.0), "max_tokens": 4096,  "desc": "Бесплатный. Лёгкие задачи, высокая скорость"},
            "3": {"id": "glm-4.7",       "label": "GLM-4.7",           "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Код, рассуждения, агентные задачи"},
            "4": {"id": "glm-4.5",       "label": "GLM-4.5",           "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Флагман для агентов, MoE-архитектура, 128k контекст"},
            "5": {"id": "glm-4.6",       "label": "GLM-4.6",           "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Лучшая модель для кода, 200k контекст"},
            "6": {"id": "glm-5",         "label": "GLM-5",             "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Топ-модель: сложный код, архитектура систем"},
            "7": {"id": "glm-5-turbo",   "label": "GLM-5-Turbo",       "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "GLM-5 с упором на скорость и агентные цепочки"},
            # Мультимодальные (vision)
            "8": {"id": "glm-4.5v",      "label": "GLM-4.5V",          "free": False, "temp_range": (0.0, 1.0), "max_tokens": 16000, "desc": "Vision: анализ изображений, видео, GUI-агенты"},
            "9": {"id": "glm-4.6v",      "label": "GLM-4.6V",          "free": False, "temp_range": (0.0, 1.0), "max_tokens": 16000, "desc": "Vision: понимание изображений + Function Calling"},
        },
        # ── Генерация изображений (endpoint: /images/generations) ─────────
        "image_models": {
            "1": {"id": "glm-image", "label": "GLM-Image", "desc": "Авторегрессия + диффузия. Постеры, иллюстрации", "price": "~$0.06/изобр."},
        },
        # ── Генерация видео (endpoint: /videos/generations, async) ────────
        "video_models": {
            "1": {"id": "cogvideox-3", "label": "CogVideoX-3", "desc": "Text/image-to-video, до 4K, с аудио", "price": "~$0.10/сек"},
        },
    },
    "2": {
        "name": "ProxyAPI (OpenAI)",
        "api_key_env": "PROXY_API_KEY",
        "api_key": os.environ.get("PROXY_API_KEY", ""),
        "base_url": "https://api.proxyapi.ru/openai/v1",
        # ── Текстовые LLM ─────────────────────────────────────────────────
        "models": {
            "1": {"id": "gpt-4.1-nano",  "label": "GPT-4.1 Nano",  "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Самый дешёвый GPT-4.1. Простые задачи, высокая скорость"},
            "2": {"id": "gpt-4.1-mini",  "label": "GPT-4.1 Mini",  "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Баланс цены и качества. Код, тексты, анализ"},
            "3": {"id": "gpt-4.1",       "label": "GPT-4.1",       "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Флагман OpenAI. Сложный код, длинный контекст"},
            "4": {"id": "gpt-4o-mini",   "label": "GPT-4o Mini",   "free": False, "temp_range": (0.0, 2.0), "max_tokens": 16384, "desc": "Мультимодальный, быстрый. Чат, изображения"},
            "5": {"id": "gpt-4o",        "label": "GPT-4o",        "free": False, "temp_range": (0.0, 2.0), "max_tokens": 16384, "desc": "Мультимодальный флагман. Текст, код, зрение"},
        },
        # ── Генерация изображений (endpoint: /images/generations) ─────────
        "image_models": {
            "1": {"id": "dall-e-3",    "label": "DALL·E 3",       "desc": "Высокое качество, точное следование промпту", "price": "$0.04/изобр."},
            "2": {"id": "dall-e-2",    "label": "DALL·E 2",       "desc": "Быстрый и дешёвый, базовое качество",          "price": "$0.02/изобр."},
            "3": {"id": "gpt-image-1", "label": "GPT-Image-1",    "desc": "Флагман OpenAI. Фотореализм, детали",          "price": "$0.17/изобр."},
        },
        # ── Генерация видео (endpoint: /videos/generations, async) ────────
        "video_models": {
            "1": {"id": "sora",   "label": "Sora",   "desc": "Text-to-video от OpenAI",              "price": "$0.03/сек"},
            "2": {"id": "sora-2", "label": "Sora-2", "desc": "До 4K, 90 сек, улучшенная физика",     "price": "$0.05/сек"},
        },
    },
    "3": {
        "name": "GenAPI",
        "api_key_env": "GEN_API_KEY",
        "api_key": os.environ.get("GEN_API_KEY", ""),
        "base_url": "https://proxy.gen-api.ru/v1",
        # ── Текстовые LLM ─────────────────────────────────────────────────
        "models": {
            "1":  {"id": "gpt-4-1-mini",                    "label": "GPT-4.1 Mini",         "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Быстрый и экономичный GPT-4.1 для повседневных задач"},
            "2":  {"id": "gpt-4-1",                         "label": "GPT-4.1",              "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Флагман OpenAI. Сложный код, длинный контекст"},
            "3":  {"id": "gpt-5.4",                         "label": "GPT-5.4",              "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "Топ OpenAI. Глубокий анализ, сложные инструкции"},
            "4":  {"id": "gpt-5.4-mini",                    "label": "GPT-5.4 Mini",         "free": False, "temp_range": (0.0, 2.0), "max_tokens": 32768, "desc": "GPT-5.4 облегчённый. Быстро и качественно"},
            "5":  {"id": "gpt-4o",                          "label": "GPT-4o",               "free": False, "temp_range": (0.0, 2.0), "max_tokens": 16384, "desc": "Мультимодальный флагман. Текст, код, зрение"},
            "6":  {"id": "claude-sonnet-4-5",               "label": "Claude Sonnet 4.5",    "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Anthropic. Длинные тексты, нюансированный стиль"},
            "7":  {"id": "gemini-2.5-flash-preview-04-17",  "label": "Gemini 2.5 Flash",     "free": False, "temp_range": (0.0, 2.0), "max_tokens": 8192,  "desc": "Google. Быстрый, мультимодальный, длинный контекст"},
            "8":  {"id": "gemini-2-5-flash-lite",           "label": "Gemini 2.5 Flash Lite","free": False, "temp_range": (0.0, 2.0), "max_tokens": 8192,  "desc": "Google. Самый дешёвый Gemini 2.5, высокая скорость"},
            "9":  {"id": "deepseek-chat",                   "label": "DeepSeek Chat",        "free": False, "temp_range": (0.0, 2.0), "max_tokens": 8192,  "desc": "Китайская модель. Код и чат по низкой цене"},
            "10": {"id": "deepseek-r1",                     "label": "DeepSeek R1",          "free": False, "temp_range": (0.0, 2.0), "max_tokens": 16000, "desc": "Reasoning-модель. Математика, логика, сложный анализ"},
            "11": {"id": "glm-5",                           "label": "GLM-5",                "free": False, "temp_range": (0.0, 1.0), "max_tokens": 8192,  "desc": "Z.AI топ-модель. Код, архитектура, агентные задачи"},
            "12": {"id": "qwen-3.5",                        "label": "Qwen 3.5",             "free": False, "temp_range": (0.0, 2.0), "max_tokens": 8192,  "desc": "Alibaba. Длинный контекст, многоязычность"},
            "13": {"id": "gemini-3-flash",                  "label": "Gemini 3 Flash",       "free": False, "temp_range": (0.0, 2.0), "max_tokens": 8192,  "desc": "Google. Frontier-класс по цене Flash, рассуждения"},
        },
        # ── Генерация изображений ─────────────────────────────────────────
        "image_models": {
            "1":  {"id": "glm-image",          "label": "GLM-Image",          "desc": "Авторегрессия + диффузия. Постеры, иллюстрации",    "price": "~$0.06/изобр."},
            "2":  {"id": "flux-2-klein",       "label": "Flux 2 Klein",       "desc": "Black Forest Labs. Быстрая генерация и редактура",   "price": "~$0.02/изобр."},
            "3":  {"id": "recraft-v4-pro",     "label": "Recraft v4 Pro",     "desc": "Иллюстрации, иконки, логотипы, векторная графика",   "price": "~$0.04/изобр."},
            "4":  {"id": "qwen-image-2",       "label": "Qwen Image 2",       "desc": "Alibaba. Генерация и редактирование изображений",    "price": "~$0.03/изобр."},
            "5":  {"id": "qwen-image-max",     "label": "Qwen Image Max",     "desc": "Alibaba. Продвинутая генерация и редактирование",    "price": "~$0.05/изобр."},
            "6":  {"id": "seedream-v5-lite",   "label": "Seedream v5 Lite",   "desc": "ByteDance. Коммерческие фото, товарные снимки",      "price": "~$0.03/изобр."},
            "7":  {"id": "nano-banana-2",      "label": "Nano Banana 2",      "desc": "Быстрая генерация и редактирование по тексту",       "price": "~$0.03/изобр."},
            "8":  {"id": "kling-image-v3",     "label": "Kling Image V3",     "desc": "Text/image-to-image. Реализм и стилизация",          "price": "~$0.04/изобр."},
            "9":  {"id": "hunyuan-image-v3",   "label": "Hunyuan Image V3",   "desc": "Tencent. Генерация по промпту и референсам",         "price": "~$0.05/изобр."},
            "10": {"id": "grok-imagine-image", "label": "Grok Imagine Image", "desc": "xAI. Генерация и редактирование изображений",        "price": "~$0.02/изобр."},
            "11": {"id": "firered-image-edit", "label": "FireRed Image Edit", "desc": "Редактирование по тексту, сохраняет композицию",     "price": "~$0.04/изобр."},
        },
        # ── Генерация видео ───────────────────────────────────────────────
        "video_models": {
            "1": {"id": "kling-video-o3",          "label": "Kling Video O3",          "desc": "Text/image/video-to-video, редактирование",     "price": "~$0.14/сек"},
            "2": {"id": "kling-video-v3",          "label": "Kling Video V3",          "desc": "До 15 сек, standard/pro режимы",                "price": "~$0.10/сек"},
            "3": {"id": "kling-video-v2.6-motion", "label": "Kling v2.6 Motion",       "desc": "Контроль движения камеры и объектов",            "price": "~$0.10/сек"},
            "4": {"id": "ltx-2.3",                 "label": "LTX 2.3",                 "desc": "Text/image-to-video, fast и pro режимы",         "price": "~$0.05/сек"},
            "5": {"id": "ltx-2",                   "label": "LTX 2",                   "desc": "Реалистичное видео, быстрая генерация",          "price": "~$0.04/сек"},
            "6": {"id": "pixverse-5.5",            "label": "PixVerse 5.5",            "desc": "Text/image-to-video, плавная анимация",          "price": "~$0.08/сек"},
            "7": {"id": "vidu-q3-video",           "label": "ViduQ3Video",             "desc": "Text/image-to-video, standard и turbo",          "price": "~$0.07/сек"},
            "8": {"id": "grok-imagine-video",      "label": "Grok Imagine Video",      "desc": "xAI. Генерация видео по тексту",                 "price": "~$0.06/сек"},
        },
    },
    # ── Cerebras ──────────────────────────────────────────────────────────────
    # OpenAI-совместимый API. Ключ: https://cloud.cerebras.ai → API Keys
    # Особенность: самый быстрый инференс в мире (~2200 tok/s), есть free tier
    "5": {
        "name": "Cerebras",
        "api_key_env": "CEREBRAS_API_KEY",
        "api_key": os.environ.get("CEREBRAS_API_KEY", ""),
        "base_url": "https://api.cerebras.ai/v1",
        "models": {
            "1": {"id": "llama3.1-8b",                        "label": "Llama 3.1 8B",          "free": True,  "temp_range": (0.0, 1.5), "max_tokens": 8192,  "desc": "~2200 tok/s. Быстрый и бесплатный. Чат, простые задачи"},
            "2": {"id": "qwen-3-235b-a22b-instruct-2507",     "label": "Qwen 3 235B",           "free": False, "temp_range": (0.0, 1.5), "max_tokens": 131072,"desc": "~1400 tok/s. Мощная модель Alibaba. Код, анализ (Preview)"},
            "3": {"id": "gpt-oss-120b",                       "label": "GPT OSS 120B",          "free": False, "temp_range": (0.0, 1.5), "max_tokens": 16384, "desc": "~3000 tok/s. OpenAI open-source 120B. Самый быстрый"},
            "4": {"id": "llama-3.3-70b",                      "label": "Llama 3.3 70B",         "free": False, "temp_range": (0.0, 1.5), "max_tokens": 8192,  "desc": "~2100 tok/s. Мощный Llama для сложных задач"},
        },
        "image_models": {},
        "video_models": {},
    },
    # ── Hugging Face Inference Providers ──────────────────────────────────────
    # Роутер поверх 18+ провайдеров (Groq, Together, Novita, SambaNova и др.)
    # Ключ: https://huggingface.co/settings/tokens → fine-grained token
    # Модели: owner/model-name, суффикс :fastest/:cheapest для выбора провайдера
    "6": {
        "name": "HuggingFace",
        "api_key_env": "HF_TOKEN",
        "api_key": os.environ.get("HF_TOKEN", ""),
        "base_url": "https://router.huggingface.co/v1",
        "models": {
            "1":  {"id": "meta-llama/Llama-3.1-8B-Instruct:cheapest",       "label": "Llama 3.1 8B (cheapest)",      "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Быстрый и дешёвый Llama. Чат, простые задачи"},
            "2":  {"id": "meta-llama/Llama-3.3-70B-Instruct:fastest",       "label": "Llama 3.3 70B (fastest)",      "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Мощный Llama 3.3. Код, анализ, длинный контекст"},
            "3":  {"id": "openai/gpt-oss-120b:fastest",                     "label": "GPT OSS 120B (fastest)",       "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "OpenAI open-source 120B. Высокая скорость"},
            "4":  {"id": "openai/gpt-oss-20b:cheapest",                     "label": "GPT OSS 20B (cheapest)",       "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "OpenAI open-source 20B. Самый дешёвый"},
            "5":  {"id": "deepseek-ai/DeepSeek-V3.2:cheapest",              "label": "DeepSeek V3.2 (cheapest)",     "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "DeepSeek V3.2. Код, рассуждения, низкая цена"},
            "6":  {"id": "deepseek-ai/DeepSeek-R1:fastest",                 "label": "DeepSeek R1 (fastest)",        "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Reasoning-модель. Математика, логика, анализ"},
            "7":  {"id": "Qwen/Qwen3-235B-A22B-Instruct-2507:cheapest",     "label": "Qwen 3 235B (cheapest)",       "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Мощная Qwen 3 MoE. Код, многоязычность"},
            "8":  {"id": "Qwen/Qwen3-32B:fastest",                          "label": "Qwen 3 32B (fastest)",         "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Qwen 3 32B. Баланс скорости и качества"},
            "9":  {"id": "moonshotai/Kimi-K2.5:cheapest",                   "label": "Kimi K2.5 (cheapest)",         "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Moonshot Kimi K2.5. Длинный контекст 262k"},
            "10": {"id": "zai-org/GLM-5:cheapest",                          "label": "GLM-5 (cheapest)",             "free": False, "temp_range": (0.0, 1.0), "max_tokens": 4096, "desc": "Z.AI GLM-5. Код, агентные задачи"},
            "11": {"id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8:cheapest", "label": "Llama 4 Maverick (cheapest)", "free": False, "temp_range": (0.0, 2.0), "max_tokens": 4096, "desc": "Llama 4 Maverick. 1M контекст, мультимодальный"},
        },
        "image_models": {
            "1": {"id": "black-forest-labs/FLUX.1-dev",           "label": "FLUX.1-dev",       "desc": "Black Forest Labs. Фотореализм, детали",  "price": "~$0.03/изобр."},
            "2": {"id": "black-forest-labs/FLUX.1-schnell",       "label": "FLUX.1-schnell",   "desc": "FLUX быстрый. Наброски, итерации",        "price": "~$0.01/изобр."},
            "3": {"id": "stabilityai/stable-diffusion-3.5-large", "label": "SD 3.5 Large",     "desc": "Stable Diffusion 3.5. Высокое качество",  "price": "~$0.04/изобр."},
        },
        "video_models": {},
    },
}

# ─── Настройки памяти ─────────────────────────────────────────────────────────
MAX_HISTORY_MESSAGES = 10   # последних N пар (user+assistant) в контексте
MEMORY_FILE = "memory.json"
SETTINGS_FILE = "user_settings.json"
PROMPTS_FILE = "prompts.json"

# ─── ЦБ РФ API для курса валют ────────────────────────────────────────────────
CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

# ─── Стоимость токенов (USD за 1M токенов) ───────────────────────────────────
# Приблизительные цены; обновляй по необходимости
TOKEN_PRICES_USD_PER_1M: dict = {
    # ── Z.AI ──────────────────────────────────────────────────────────────
    "glm-4.7-flash": {"input": 0.0,   "output": 0.0},
    "glm-4.5-flash": {"input": 0.0,   "output": 0.0},
    "glm-4.7":       {"input": 0.14,  "output": 0.14},
    "glm-4.5":       {"input": 0.14,  "output": 0.14},
    "glm-4.6":       {"input": 0.14,  "output": 0.14},
    "glm-4.5v":      {"input": 0.14,  "output": 0.14},
    "glm-4.6v":      {"input": 0.14,  "output": 0.14},
    "glm-5":         {"input": 1.0,   "output": 3.0},
    "glm-5-turbo":   {"input": 0.5,   "output": 1.5},
    # ── ProxyAPI / OpenAI ─────────────────────────────────────────────────
    "gpt-4.1-nano":  {"input": 0.1,   "output": 0.4},
    "gpt-4.1-mini":  {"input": 0.4,   "output": 1.6},
    "gpt-4.1":       {"input": 2.0,   "output": 8.0},
    "gpt-4o-mini":   {"input": 0.15,  "output": 0.6},
    "gpt-4o":        {"input": 2.5,   "output": 10.0},
    # ── GenAPI ────────────────────────────────────────────────────────────
    "gpt-4-1-mini":          {"input": 0.4,   "output": 1.6},
    "gpt-4-1":               {"input": 2.0,   "output": 8.0},
    "gpt-5.4":               {"input": 5.0,   "output": 20.0},
    "gpt-5.4-mini":          {"input": 1.0,   "output": 4.0},
    "claude-sonnet-4-5":     {"input": 3.0,   "output": 15.0},
    "gemini-2-5-flash":      {"input": 0.15,  "output": 0.6},
    "gemini-3-1-flash-lite": {"input": 0.1,   "output": 0.4},
    "deepseek-chat":         {"input": 0.27,  "output": 1.1},
    "deepseek-r1":           {"input": 0.55,  "output": 2.19},
    "qwen-3.5":              {"input": 0.3,   "output": 1.2},
    # ── Google AI (Gemini) ────────────────────────────────────────────────
    "gemini-2.5-flash-lite":         {"input": 0.10,  "output": 0.40},
    "gemini-2.5-flash":              {"input": 0.30,  "output": 2.50},
    "gemini-2.5-pro":                {"input": 1.25,  "output": 10.0},
    "gemini-3-flash-preview":        {"input": 0.50,  "output": 3.00},
    "gemini-3.1-flash-lite-preview": {"input": 0.25,  "output": 1.50},
    "gemini-3.1-pro-preview":        {"input": 2.00,  "output": 12.0},
    # ── Cerebras ──────────────────────────────────────────────────────────────    "llama3.1-8b":   {"input": 0.10, "output": 0.10},
    "qwen-3-235b-a22b-instruct-2507": {"input": 0.60, "output": 1.20},
    "gpt-oss-120b":  {"input": 0.35, "output": 0.75},
    "llama-3.3-70b": {"input": 0.59, "output": 0.79},
    # ── HuggingFace (cheapest провайдер, приблизительно) ──────────────────────
    "meta-llama/Llama-3.1-8B-Instruct:cheapest":    {"input": 0.02, "output": 0.05},
    "meta-llama/Llama-3.3-70B-Instruct:fastest":    {"input": 0.59, "output": 0.79},
    "openai/gpt-oss-120b:fastest":                  {"input": 0.15, "output": 0.60},
    "openai/gpt-oss-20b:cheapest":                  {"input": 0.04, "output": 0.15},
    "deepseek-ai/DeepSeek-V3.2:cheapest":           {"input": 0.27, "output": 0.40},
    "deepseek-ai/DeepSeek-R1:fastest":              {"input": 0.70, "output": 2.50},
    "Qwen/Qwen3-235B-A22B-Instruct-2507:cheapest":  {"input": 0.09, "output": 0.58},
    "Qwen/Qwen3-32B:fastest":                       {"input": 0.29, "output": 0.59},
    "moonshotai/Kimi-K2.5:cheapest":                {"input": 0.50, "output": 2.80},
    "zai-org/GLM-5:cheapest":                       {"input": 1.00, "output": 3.20},
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8:cheapest": {"input": 0.27, "output": 0.85},
}
