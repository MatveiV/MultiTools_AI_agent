"""
main.py — Telegram-бот с поддержкой нескольких AI-провайдеров, памятью диалога,
режимами (промптами), генерацией видео и подсчётом стоимости запросов.

Команды:
  /start   — приветствие и первичная настройка
  /mode    — выбор режима (системного промпта)
  /reset   — очистить историю диалога
  /settings — изменить провайдера / модель / температуру
  /video   — генерация видео (если провайдер поддерживает)
  /help    — справка
"""
import asyncio
import html
import json
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from openai import AsyncOpenAI, OpenAIError

import memory
from config import (
    BOT_TOKEN,
    CBR_API_URL,
    MAX_HISTORY_MESSAGES,
    PROMPTS_FILE,
    PROVIDERS,
    TOKEN_PRICES_USD_PER_1M,
)

# ─── Логирование ──────────────────────────────────────────────────────────────
import logging.handlers

LOG_FILE = "bot.log"

_log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Ротация: до 5 МБ, хранить 3 файла
_file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
_file_handler.setFormatter(_log_formatter)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[_console_handler, _file_handler])
logger = logging.getLogger(__name__)

# ─── FSM-состояния ────────────────────────────────────────────────────────────

class Setup(StatesGroup):
    choose_provider = State()
    choose_model = State()
    choose_temperature = State()


class VideoGen(StatesGroup):
    waiting_prompt = State()


class ImageGen(StatesGroup):
    waiting_prompt = State()

# ─── Загрузка промптов ────────────────────────────────────────────────────────

def load_prompts() -> dict:
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        return json.load(f)

PROMPTS_DATA = load_prompts()

# ─── Подсказка команд (добавляется после каждого ответа) ─────────────────────
COMMANDS_HINT = (
    "\n\n<i>🔹 /mode — режим  🔹 /image — картинка  🔹 /video — видео"
    "  🔹 /reset — сброс  🔹 /settings — настройки</i>"
)

# ─── Курс ЦБ РФ ───────────────────────────────────────────────────────────────

_usd_rate_cache: float | None = None


async def get_usd_rate() -> float:
    """Получает курс USD/RUB с API ЦБ РФ (кэшируется на сессию)."""
    global _usd_rate_cache
    if _usd_rate_cache:
        return _usd_rate_cache
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CBR_API_URL, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json(content_type=None)
                rate = data["Valute"]["USD"]["Value"]
                _usd_rate_cache = float(rate)
                logger.info("Курс USD/RUB: %.2f", _usd_rate_cache)
                return _usd_rate_cache
    except Exception as e:
        logger.warning("Не удалось получить курс ЦБ РФ: %s. Используем 90.0", e)
        return 90.0

# ─── Подсчёт стоимости ────────────────────────────────────────────────────────

async def calc_cost_rub(model_id: str, prompt_tokens: int, completion_tokens: int) -> str:
    prices = TOKEN_PRICES_USD_PER_1M.get(model_id, {"input": 0.0, "output": 0.0})
    cost_usd = (prompt_tokens * prices["input"] + completion_tokens * prices["output"]) / 1_000_000
    rate = await get_usd_rate()
    cost_rub = cost_usd * rate
    return (
        f"📊 Токены: вход {prompt_tokens} | выход {completion_tokens}\n"
        f"💰 Стоимость: ${cost_usd:.6f} ≈ {cost_rub:.4f} ₽"
    )

# ─── Вспомогательные функции ──────────────────────────────────────────────────

def get_provider(chat_id: int) -> dict | None:
    p_key = memory.get_setting(chat_id, "provider_key")
    return PROVIDERS.get(p_key) if p_key else None


def get_model_info(chat_id: int) -> dict | None:
    p_key = memory.get_setting(chat_id, "provider_key")
    m_key = memory.get_setting(chat_id, "model_key")
    if p_key and m_key:
        return PROVIDERS[p_key]["models"].get(m_key)
    return None


def is_configured(chat_id: int) -> bool:
    return memory.get_settings(chat_id) is not None


def provider_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{k}. {p['name']}", callback_data=f"prov:{k}")]
        for k, p in PROVIDERS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def model_keyboard(provider_key: str) -> InlineKeyboardMarkup:
    models = PROVIDERS[provider_key]["models"]
    buttons = [
        [InlineKeyboardButton(
            text=f"{'🆓 ' if m['free'] else ''}{m['label']} — {m.get('desc', '')}",
            callback_data=f"model:{provider_key}:{k}"
        )]
        for k, m in models.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def temperature_keyboard(provider_key: str, model_key: str) -> InlineKeyboardMarkup:
    model = PROVIDERS[provider_key]["models"][model_key]
    lo, hi = model["temp_range"]
    temps = [round(lo + i * (hi - lo) / 4, 1) for i in range(5)]
    buttons = [
        [InlineKeyboardButton(text=str(t), callback_data=f"temp:{provider_key}:{model_key}:{t}")]
        for t in temps
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mode_keyboard() -> InlineKeyboardMarkup:
    prompts = PROMPTS_DATA["prompts"]
    buttons = [
        [InlineKeyboardButton(
            text=f"{data['name']} — {data['description']}",
            callback_data=f"mode:{key}"
        )]
        for key, data in prompts.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def video_model_keyboard(provider_key: str) -> InlineKeyboardMarkup | None:
    video_models = PROVIDERS[provider_key].get("video_models", {})
    if not video_models:
        return None
    provider_name = PROVIDERS[provider_key]["name"]
    buttons = [
        [InlineKeyboardButton(
            text=f"🎬 {m['label']} | {m.get('price', '?')} | {provider_name}",
            callback_data=f"vidmodel:{provider_key}:{k}"
        )]
        for k, m in video_models.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def image_model_keyboard(provider_key: str) -> InlineKeyboardMarkup | None:
    image_models = PROVIDERS[provider_key].get("image_models", {})
    if not image_models:
        return None
    provider_name = PROVIDERS[provider_key]["name"]
    buttons = [
        [InlineKeyboardButton(
            text=f"🖼 {m['label']} | {m.get('price', '?')} | {provider_name}",
            callback_data=f"imgmodel:{provider_key}:{k}"
        )]
        for k, m in image_models.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── Handlers: команды ────────────────────────────────────────────────────────

async def cmd_start(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    logger.info("/start от chat_id=%d", chat_id)
    await message.answer(
        "👋 Привет! Я AI-бот с поддержкой нескольких провайдеров.\n\n"
        "Для начала выбери провайдера:",
        reply_markup=provider_keyboard(),
    )
    await state.set_state(Setup.choose_provider)


async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 Команды:\n"
        "/start — начало / сброс настроек\n"
        "/mode — выбрать режим (роль ИИ)\n"
        "/reset — очистить историю диалога\n"
        "/settings — изменить провайдера/модель/температуру\n"
        "/image — генерация изображения\n"
        "/video — генерация видео\n"
        "/help — эта справка"
    )


async def cmd_reset(message: Message) -> None:
    chat_id = message.chat.id
    memory.reset_history(chat_id)
    logger.info("/reset от chat_id=%d", chat_id)
    await message.answer("🗑 История диалога очищена.")


async def cmd_mode(message: Message) -> None:
    if not is_configured(message.chat.id):
        await message.answer("Сначала настрой бота командой /start")
        return
    await message.answer("🎭 Выбери режим:", reply_markup=mode_keyboard())


async def cmd_settings(message: Message, state: FSMContext) -> None:
    await message.answer("⚙️ Выбери провайдера:", reply_markup=provider_keyboard())
    await state.set_state(Setup.choose_provider)


async def cmd_video(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    if not is_configured(chat_id):
        await message.answer("Сначала настрой бота командой /start")
        return
    p_key = memory.get_setting(chat_id, "provider_key")
    kb = video_model_keyboard(p_key)
    if kb is None:
        await message.answer(
            "❌ Текущий провайдер не поддерживает генерацию видео.\n"
            "Переключись на ProxyAPI или GenAPI через /settings."
        )
        return
    await message.answer("🎬 Выбери модель для генерации видео:", reply_markup=kb)


async def cmd_image(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    if not is_configured(chat_id):
        await message.answer("Сначала настрой бота командой /start")
        return
    p_key = memory.get_setting(chat_id, "provider_key")
    kb = image_model_keyboard(p_key)
    if kb is None:
        await message.answer(
            "❌ Текущий провайдер не поддерживает генерацию изображений.\n"
            "Переключись на Z.AI, ProxyAPI или GenAPI через /settings."
        )
        return
    await message.answer("🖼 Выбери модель для генерации изображения:", reply_markup=kb)

# ─── Handlers: FSM — настройка ────────────────────────────────────────────────

async def cb_choose_provider(callback: CallbackQuery, state: FSMContext) -> None:
    p_key = callback.data.split(":")[1]
    await state.update_data(provider_key=p_key)
    await callback.message.edit_text(
        f"✅ Провайдер: {PROVIDERS[p_key]['name']}\n\nВыбери модель:",
        reply_markup=model_keyboard(p_key),
    )
    await state.set_state(Setup.choose_model)
    await callback.answer()


async def cb_choose_model(callback: CallbackQuery, state: FSMContext) -> None:
    _, p_key, m_key = callback.data.split(":")
    model = PROVIDERS[p_key]["models"][m_key]
    await state.update_data(model_key=m_key)
    await callback.message.edit_text(
        f"✅ Модель: {model['label']}\n\nВыбери температуру:",
        reply_markup=temperature_keyboard(p_key, m_key),
    )
    await state.set_state(Setup.choose_temperature)
    await callback.answer()


async def cb_choose_temperature(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    p_key, m_key, temp = parts[1], parts[2], float(parts[3])
    data = await state.get_data()
    chat_id = callback.message.chat.id

    settings = {
        "provider_key": p_key,
        "model_key": m_key,
        "temperature": temp,
        "mode": PROMPTS_DATA["default_prompt"],
    }
    memory.save_settings(chat_id, settings)
    await state.clear()

    provider = PROVIDERS[p_key]
    model = provider["models"][m_key]
    await callback.message.edit_text(
        f"✅ Настройки сохранены!\n\n"
        f"Провайдер: {provider['name']}\n"
        f"Модель: {model['label']}\n"
        f"Температура: {temp}\n\n"
        f"Теперь можешь писать мне сообщения. Используй /mode для смены режима."
    )
    await callback.answer()
    logger.info("Настройки сохранены для chat_id=%d: %s", chat_id, settings)

# ─── Handlers: выбор режима ───────────────────────────────────────────────────

async def cb_choose_mode(callback: CallbackQuery) -> None:
    mode_key = callback.data.split(":")[1]
    chat_id = callback.message.chat.id
    memory.update_setting(chat_id, "mode", mode_key)
    # Сбрасываем историю при смене режима
    memory.reset_history(chat_id)
    mode_data = PROMPTS_DATA["prompts"][mode_key]
    await callback.message.edit_text(
        f"✅ Режим: {mode_data['name']}\n{mode_data['description']}\n\n"
        f"История очищена. Начинаем новый диалог!"
    )
    await callback.answer()
    logger.info("Режим изменён для chat_id=%d: %s", chat_id, mode_key)

# ─── Handlers: генерация видео ────────────────────────────────────────────────

def _make_openai_client(provider: dict) -> AsyncOpenAI:
    """Создаёт AsyncOpenAI клиент для провайдера."""
    return AsyncOpenAI(api_key=provider["api_key"], base_url=provider["base_url"])


async def _genapi_generate(
    api_key: str,
    network_id: str,
    payload: dict,
    poll_timeout: int = 180,
) -> str | None:
    """
    Отправляет запрос в GenAPI (POST /api/v1/networks/{network_id}),
    затем polling GET /api/v1/request/get/{id} до status=success.
    Возвращает URL первого результата или None при таймауте.
    """
    base = "https://api.gen-api.ru/api/v1"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        # 1. Создаём задачу
        async with session.post(
            f"{base}/networks/{network_id}",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data = await resp.json(content_type=None)

        logger.info("GenAPI create task: %s", data)
        request_id = data.get("request_id")
        if not request_id:
            logger.error("GenAPI: нет request_id в ответе: %s", data)
            return None

        # 2. Polling до готовности
        deadline = asyncio.get_event_loop().time() + poll_timeout
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(5)
            async with session.get(
                f"{base}/request/get/{request_id}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                result = await resp.json(content_type=None)

            status = result.get("status")
            logger.info("GenAPI polling id=%s status=%s", request_id, status)

            if status == "success":
                urls = result.get("result", [])
                return urls[0] if urls else None
            if status in ("error", "failed"):
                logger.error("GenAPI task failed: %s", result)
                return None

    logger.warning("GenAPI polling timeout для request_id=%s", request_id)
    return None

async def cb_choose_video_model(callback: CallbackQuery, state: FSMContext) -> None:
    _, p_key, vm_key = callback.data.split(":")
    vm = PROVIDERS[p_key]["video_models"][vm_key]
    await state.update_data(video_provider_key=p_key, video_model_id=vm["id"])
    await callback.message.edit_text(
        f"🎬 Модель: {vm['label']}\n\nОпиши видео, которое хочешь сгенерировать:"
    )
    await state.set_state(VideoGen.waiting_prompt)
    await callback.answer()


async def handle_video_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    p_key = data["video_provider_key"]
    model_id = data["video_model_id"]
    chat_id = message.chat.id
    provider = PROVIDERS[p_key]
    await state.clear()
    await message.answer("⏳ Генерирую видео, это может занять некоторое время...")
    logger.info("Генерация видео: chat_id=%d model=%s prompt=%s", chat_id, model_id, message.text[:80])

    try:
        from aiogram.types import BufferedInputFile

        # ── GenAPI: собственный API с polling ────────────────────────────
        if p_key == "3":
            video_url = await _genapi_generate(
                api_key=provider["api_key"],
                network_id=model_id,
                payload={"prompt": message.text},
                poll_timeout=180,
            )
            if video_url:
                async with aiohttp.ClientSession() as s:
                    async with s.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as r:
                        video_bytes = await r.read()
                await message.answer_video(
                    BufferedInputFile(video_bytes, filename="video.mp4"),
                    caption=f"🎬 Готово! Модель: {model_id}",
                )
                await message.answer(COMMANDS_HINT.strip())
            else:
                await message.answer("⏳ Видео ещё генерируется. Попробуй позже." + COMMANDS_HINT)
            return

        # ── Z.AI: POST /videos/generations → async task ──────────────────
        if p_key == "1":
            headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}
            payload = {"model": model_id, "prompt": message.text, "quality": "quality", "with_audio": True}
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    f"{provider['base_url'].rstrip('/')}/videos/generations",
                    json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    result = await resp.json(content_type=None)
            task_id = result.get("id") or result.get("task_id") if isinstance(result, dict) else None
            logger.info("Z.AI видео task: %s", task_id)
            if task_id:
                await message.answer(
                    f"✅ Задача создана (id: <code>{html.escape(str(task_id))}</code>).\n"
                    f"Видео будет готово через несколько минут." + COMMANDS_HINT,
                    parse_mode=ParseMode.HTML,
                )
            else:
                await message.answer(
                    f"✅ Запрос отправлен:\n<code>{html.escape(str(result))}</code>" + COMMANDS_HINT,
                    parse_mode=ParseMode.HTML,
                )
            return

        # ── ProxyAPI (OpenAI Sora): videos.create() + polling ────────────
        client = _make_openai_client(provider)
        # Создаём задачу генерации видео
        video_job = await client.videos.create(
            model=model_id,
            prompt=message.text,
        )
        logger.info("ProxyAPI Sora job id=%s status=%s", video_job.id, video_job.status)

        # Polling до завершения (max 5 минут)
        deadline = asyncio.get_event_loop().time() + 300
        while video_job.status not in ("completed", "failed", "cancelled") and \
              asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(15)
            video_job = await client.videos.retrieve(video_job.id)
            logger.info("ProxyAPI Sora polling id=%s status=%s", video_job.id, video_job.status)

        if video_job.status == "completed":
            content = await client.videos.download_content(video_job.id, variant="video")
            video_bytes = b""
            async for chunk in content.aiter_bytes():
                video_bytes += chunk
            await message.answer_video(
                BufferedInputFile(video_bytes, filename="video.mp4"),
                caption=f"🎬 Готово! Модель: {model_id}",
            )
            await message.answer(COMMANDS_HINT.strip())
        else:
            await message.answer(
                f"❌ Генерация завершилась со статусом: {video_job.status}" + COMMANDS_HINT
            )

    except Exception as e:
        logger.error("Ошибка генерации видео: %s", e)
        await message.answer(f"❌ Ошибка генерации видео: {html.escape(str(e))}" + COMMANDS_HINT)


# ─── Handlers: генерация изображений ─────────────────────────────────────────

async def cb_choose_image_model(callback: CallbackQuery, state: FSMContext) -> None:
    _, p_key, im_key = callback.data.split(":")
    im = PROVIDERS[p_key]["image_models"][im_key]
    await state.update_data(image_provider_key=p_key, image_model_id=im["id"])
    await callback.message.edit_text(
        f"🖼 Модель: {im['label']}\n\nОпиши изображение, которое хочешь сгенерировать:"
    )
    await state.set_state(ImageGen.waiting_prompt)
    await callback.answer()


async def handle_image_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    p_key = data["image_provider_key"]
    model_id = data["image_model_id"]
    chat_id = message.chat.id
    provider = PROVIDERS[p_key]
    await state.clear()
    await message.answer("⏳ Генерирую изображение...")
    logger.info("Генерация изображения: chat_id=%d model=%s prompt=%s", chat_id, model_id, message.text[:80])

    try:
        import base64
        from aiogram.types import BufferedInputFile

        # ── GenAPI: собственный API с polling ────────────────────────────
        if p_key == "3":
            image_url = await _genapi_generate(
                api_key=provider["api_key"],
                network_id=model_id,
                payload={"prompt": message.text},
                poll_timeout=120,
            )
            if image_url:
                async with aiohttp.ClientSession() as s:
                    async with s.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                        img_bytes = await r.read()
                await message.answer_document(
                    BufferedInputFile(img_bytes, filename="image.png"),
                    caption=f"🖼 Готово! Модель: {model_id}",
                )
                await message.answer(COMMANDS_HINT.strip())
            else:
                await message.answer("⏳ Изображение ещё генерируется. Попробуй позже." + COMMANDS_HINT)
            return

        # ── HuggingFace: text_to_image через huggingface_hub ─────────────
        if p_key == "6":
            hf_token = provider["api_key"]
            if not hf_token:
                await message.answer("❌ HF_TOKEN не задан в .env" + COMMANDS_HINT)
                return
            try:
                from huggingface_hub import AsyncInferenceClient
                hf_client = AsyncInferenceClient(token=hf_token)
                img = await hf_client.text_to_image(prompt=message.text, model=model_id)
                # img — PIL Image
                import io
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                await message.answer_document(
                    BufferedInputFile(buf.read(), filename="image.png"),
                    caption=f"🖼 Готово! Модель: {model_id}",
                )
                await message.answer(COMMANDS_HINT.strip())
            except ImportError:
                await message.answer(
                    "❌ Установи huggingface_hub: pip install huggingface_hub" + COMMANDS_HINT
                )
            return

        # ── Google AI (Imagen / Gemini Image): OpenAI-совместимый API ────
        if p_key == "4":
            client = _make_openai_client(provider)
            response = await client.images.generate(
                model=model_id,
                prompt=message.text,
                n=1,
                response_format="b64_json",
            )
            b64 = response.data[0].b64_json if response.data else None
            if b64:
                img_bytes = base64.b64decode(b64)
                await message.answer_document(
                    BufferedInputFile(img_bytes, filename="image.png"),
                    caption=f"🖼 Готово! Модель: {model_id}",
                )
                await message.answer(COMMANDS_HINT.strip())
            else:
                await message.answer("❌ Пустой ответ от Google API" + COMMANDS_HINT)
            return

        # ── ProxyAPI / Z.AI: OpenAI-совместимый API ──────────────────────
        client = _make_openai_client(provider)

        # gpt-image-1 возвращает только b64_json
        kwargs = dict(model=model_id, prompt=message.text, n=1, size="1024x1024")
        if model_id == "gpt-image-1":
            kwargs["response_format"] = "b64_json"

        response = await client.images.generate(**kwargs)

        # Пробуем b64 сначала (надёжнее)
        b64 = getattr(response.data[0], "b64_json", None) if response.data else None
        if b64:
            img_bytes = base64.b64decode(b64)
            await message.answer_document(
                BufferedInputFile(img_bytes, filename="image.png"),
                caption=f"🖼 Готово! Модель: {model_id}",
            )
            await message.answer(COMMANDS_HINT.strip())
            return

        # Fallback: URL — скачиваем сами
        image_url = response.data[0].url if response.data else None
        if image_url:
            async with aiohttp.ClientSession() as s:
                async with s.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    img_bytes = await r.read()
            await message.answer_document(
                BufferedInputFile(img_bytes, filename="image.png"),
                caption=f"🖼 Готово! Модель: {model_id}",
            )
            await message.answer(COMMANDS_HINT.strip())
        else:
            await message.answer("❌ Не удалось получить изображение от API" + COMMANDS_HINT)

    except Exception as e:
        logger.error("Ошибка генерации изображения: %s", e)
        await message.answer(f"❌ Ошибка генерации изображения: {html.escape(str(e))}" + COMMANDS_HINT)

# ─── Handler: обычное сообщение → запрос к AI ─────────────────────────────────

async def handle_message(message: Message) -> None:
    chat_id = message.chat.id
    user_text = message.text or ""

    if not is_configured(chat_id):
        await message.answer("Сначала настрой бота командой /start")
        return

    p_key = memory.get_setting(chat_id, "provider_key")
    m_key = memory.get_setting(chat_id, "model_key")
    temperature = memory.get_setting(chat_id, "temperature", 0.7)
    mode_key = memory.get_setting(chat_id, "mode", PROMPTS_DATA["default_prompt"])

    provider = PROVIDERS[p_key]
    model = provider["models"][m_key]
    system_prompt = PROMPTS_DATA["prompts"][mode_key]["system_prompt"]

    # Формируем контекст: system + история + новое сообщение
    history = memory.get_history(chat_id)
    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_text}
    ]

    logger.info(
        "Запрос: chat_id=%d provider=%s model=%s mode=%s msgs=%d",
        chat_id, provider["name"], model["id"], mode_key, len(messages)
    )

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        client = _make_openai_client(provider)
        response = await client.chat.completions.create(
            model=model["id"],
            messages=messages,
            temperature=temperature,
            max_tokens=model["max_tokens"],
        )
        reply = response.choices[0].message.content or ""

        # Сохраняем в память
        memory.add_message(chat_id, "user", user_text)
        memory.add_message(chat_id, "assistant", reply)

        # Подсчёт стоимости
        cost_info = ""
        if response.usage:
            u = response.usage
            cost_info = "\n\n" + await calc_cost_rub(model["id"], u.prompt_tokens, u.completion_tokens)
            logger.info(
                "Токены: вход=%d выход=%d total=%d",
                u.prompt_tokens, u.completion_tokens, u.total_tokens
            )

        full_text = reply + cost_info + COMMANDS_HINT
        # Telegram ограничивает сообщение до 4096 символов — разбиваем на части
        chunk_size = 4000
        for i in range(0, len(full_text), chunk_size):
            await message.answer(full_text[i:i + chunk_size])

    except OpenAIError as e:
        logger.error("OpenAI ошибка для chat_id=%d: %s", chat_id, e)
        err_str = str(e)
        if "User location is not supported" in err_str or "FAILED_PRECONDITION" in err_str:
            await message.answer(
                "❌ Google Gemini API недоступен из вашего региона (Россия заблокирована).\n"
                "Используй другого провайдера: /settings" + COMMANDS_HINT
            )
        else:
            await message.answer(f"❌ Ошибка API: {html.escape(err_str)}" + COMMANDS_HINT)
    except Exception as e:
        logger.error("Неожиданная ошибка для chat_id=%d: %s", chat_id, e)
        await message.answer(f"❌ Ошибка: {html.escape(str(e))}" + COMMANDS_HINT)

# ─── Инициализация и запуск ───────────────────────────────────────────────────

async def main() -> None:
    # Загружаем память с диска
    memory.load_all()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация команд
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_reset, Command("reset"))
    dp.message.register(cmd_mode, Command("mode"))
    dp.message.register(cmd_settings, Command("settings"))
    dp.message.register(cmd_video, Command("video"))
    dp.message.register(cmd_image, Command("image"))

    # FSM: настройка
    dp.callback_query.register(cb_choose_provider, F.data.startswith("prov:"), Setup.choose_provider)
    dp.callback_query.register(cb_choose_model, F.data.startswith("model:"), Setup.choose_model)
    dp.callback_query.register(cb_choose_temperature, F.data.startswith("temp:"), Setup.choose_temperature)

    # Выбор режима
    dp.callback_query.register(cb_choose_mode, F.data.startswith("mode:"))

    # Генерация видео
    dp.callback_query.register(cb_choose_video_model, F.data.startswith("vidmodel:"))
    dp.message.register(handle_video_prompt, VideoGen.waiting_prompt)

    # Генерация изображений
    dp.callback_query.register(cb_choose_image_model, F.data.startswith("imgmodel:"))
    dp.message.register(handle_image_prompt, ImageGen.waiting_prompt)

    # Обычные сообщения
    dp.message.register(handle_message, F.text)

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
