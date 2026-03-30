"""
memory.py — управление памятью диалогов и пользовательскими настройками.
Хранение: JSON-файлы на диске (memory.json, user_settings.json).
"""
import json
import logging
import os
from typing import Any

from config import MEMORY_FILE, SETTINGS_FILE, MAX_HISTORY_MESSAGES

logger = logging.getLogger(__name__)

# ─── Внутренние кэши (in-memory) ─────────────────────────────────────────────
_history: dict[int, list[dict]] = {}       # chat_id → список сообщений
_settings: dict[int, dict] = {}            # chat_id → настройки пользователя

# ─── Загрузка / сохранение на диск ───────────────────────────────────────────

def _load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Не удалось загрузить %s: %s", path, e)
    return {}


def _save_json(path: str, data: dict) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Не удалось сохранить %s: %s", path, e)


def load_all() -> None:
    """Загружает историю и настройки с диска в кэш при старте бота."""
    global _history, _settings
    raw_history = _load_json(MEMORY_FILE)
    _history = {int(k): v for k, v in raw_history.items()}

    raw_settings = _load_json(SETTINGS_FILE)
    _settings = {int(k): v for k, v in raw_settings.items()}
    logger.info("Память загружена: %d чатов, %d настроек", len(_history), len(_settings))


def save_all() -> None:
    """Сохраняет кэш на диск."""
    _save_json(MEMORY_FILE, {str(k): v for k, v in _history.items()})
    _save_json(SETTINGS_FILE, {str(k): v for k, v in _settings.items()})

# ─── История диалога ──────────────────────────────────────────────────────────

def get_history(chat_id: int) -> list[dict]:
    """Возвращает историю сообщений для чата."""
    return _history.get(chat_id, [])


def add_message(chat_id: int, role: str, content: str) -> None:
    """Добавляет сообщение в историю и обрезает до MAX_HISTORY_MESSAGES пар."""
    if chat_id not in _history:
        _history[chat_id] = []
    _history[chat_id].append({"role": role, "content": content})

    # Оставляем только последние MAX_HISTORY_MESSAGES*2 сообщений (пар user+assistant)
    limit = MAX_HISTORY_MESSAGES * 2
    if len(_history[chat_id]) > limit:
        _history[chat_id] = _history[chat_id][-limit:]

    _save_json(MEMORY_FILE, {str(k): v for k, v in _history.items()})


def reset_history(chat_id: int) -> None:
    """Очищает историю диалога для чата."""
    _history[chat_id] = []
    _save_json(MEMORY_FILE, {str(k): v for k, v in _history.items()})
    logger.info("История очищена для chat_id=%d", chat_id)

# ─── Настройки пользователя ───────────────────────────────────────────────────

def get_settings(chat_id: int) -> dict | None:
    """Возвращает настройки пользователя или None если не настроен."""
    return _settings.get(chat_id)


def save_settings(chat_id: int, settings: dict) -> None:
    """Сохраняет настройки пользователя."""
    _settings[chat_id] = settings
    _save_json(SETTINGS_FILE, {str(k): v for k, v in _settings.items()})
    logger.info("Настройки сохранены для chat_id=%d: %s", chat_id, settings)


def get_setting(chat_id: int, key: str, default: Any = None) -> Any:
    """Возвращает конкретное поле настроек."""
    s = _settings.get(chat_id, {})
    return s.get(key, default)


def update_setting(chat_id: int, key: str, value: Any) -> None:
    """Обновляет одно поле настроек."""
    if chat_id not in _settings:
        _settings[chat_id] = {}
    _settings[chat_id][key] = value
    _save_json(SETTINGS_FILE, {str(k): v for k, v in _settings.items()})
