#!/usr/bin/env python3
"""
EmailFake — Telegram-бот временной почты

Провайдер: EmailFake
API: https://emailfake.com/api/v1
Фреймворк: pyTelegramBotAPI 4.18.0
Установка: pip install pyTelegramBotAPI requests

Возможности:
- Создание одноразовых почтовых ящиков
- Проверка входящих сообщений
- Мониторинг в реальном времени

Автор: Владислав Софронов (cpner)
Контакт: feedback@gondon.su | t.me/icesq | gondon.su
Исходный код: https://github.com/cpner/temp-email-api-checker/blob/main/russian/telebot/bot_emailfake.py
Лицензия: MIT
"""

import telebot
from telebot import types
import requests
import random
import string
import time
import os
import signal
import sys
import logging
from typing import Optional, Dict, Any, Set

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EmailFake")

# Конфигурация бота
BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILFAKE", "YOUR_BOT_TOKEN")
BASE_URL = "https://emailfake.com/api/v1"
SERVICE_NAME = "EmailFake"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Метки кнопок
BTN_NEW = "📧 Новая почта"
BTN_INBOX = "📥 Входящие"
BTN_INFO = "ℹ️ Инфо"
BTN_SOURCE = "🔗 Исходный код"
BTN_HELP = "❓ Помощь"

# Текстовые сообщения
SOURCE_URL = "https://github.com/cpner/temp-email-api-checker/blob/main/russian/telebot/bot_emailfake.py"

START_TEXT = """*EmailFake Бот*
Простой мониторинг

*Возможности:*
Установка, проверка

*Как пользоваться:*
1. Нажмите '📧 Новая почта'
2. Скопируйте адрес
3. Используйте для регистрации
4. Нажмите '📥 Входящие'
5. Новые помечены 🆕"""

INFO_TEXT = """*EmailFake — Инфо*

*Сервис:* EmailFake
*Описание:* Простой мониторинг
*Возможности:* Установка, проверка
*API:* `https://emailfake.com/api/v1`
*Сайт:* https://emailfake.com
*Код:* """ + SOURCE_URL + """
*Автор:* Владислав Софронов (cpner)
*Лицензия:* MIT"""

HELP_TEXT = """*EmailFake — Команды*

/start — Главное меню
/new — Создать почту
/inbox — Проверить письма
/set — Установить имя
/info — Инфо
/help — Помощь

*Кнопки:*
📧 Новая почта — Создать адрес
📥 Входящие — Проверить письма
ℹ️ Инфо — Подробнее
🔗 Код — GitHub
❓ Помощь — Инструкция"""


class UserSession:
    """Хранит состояние пользователя."""
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0

sessions: Dict[int, UserSession] = {}
stats: Dict[str, int] = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid: int) -> UserSession:
    """Получить сессию пользователя."""
    if uid not in sessions:
        sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """GET-запрос к API с повторными попытками."""
    url = BASE_URL + path
    for attempt in range(3):
        try:
            default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if headers:
            default_headers.update(headers)
        r = requests.get(url, params=params, headers=default_headers, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning(f"Ошибка API (попытка {attempt+1}/3): {e}")
            if attempt < 2:
                time.sleep(1)
    stats["errors"] += 1
    return {"error": "Превышено количество попыток"}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """POST-запрос к API."""
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}


def handle_new(user_id: int, session: UserSession) -> str:
    """Создать новую почту."""
    return "Посетите сайт"

def handle_inbox(user_id: int, session: UserSession) -> str:
    """Проверить входящие."""
    return "Посетите сайт"

def handle_set_message(text: str, session: UserSession) -> str:
    """Установить почту вручную."""
    return "Посетите сайт"

def make_keyboard() -> types.InlineKeyboardMarkup:
    """Создать клавиатуру."""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(BTN_NEW, callback_data="new"),
        types.InlineKeyboardButton(BTN_INBOX, callback_data="inbox"),
    )
    kb.add(
        types.InlineKeyboardButton(BTN_INFO, callback_data="info"),
        types.InlineKeyboardButton(BTN_SOURCE, callback_data="source"),
    )
    kb.add(types.InlineKeyboardButton(BTN_HELP, callback_data="help"))
    return kb


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    """Показать приветствие."""
    bot.send_message(m.chat.id, START_TEXT, reply_markup=make_keyboard())

@bot.message_handler(commands=["new"])
def cmd_new(m):
    """Создать почту."""
    s = get_session(m.chat.id)
    result = handle_new(m.chat.id, s)
    bot.send_message(m.chat.id, result)

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    """Проверить входящие."""
    s = get_session(m.chat.id)
    result = handle_inbox(m.chat.id, s)
    bot.send_message(m.chat.id, result)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    """Установить почту."""
    s = get_session(m.chat.id)
    result = handle_set_message(m.text, s)
    bot.send_message(m.chat.id, result)

@bot.message_handler(commands=["info"])
def cmd_info(m):
    """Показать инфо."""
    bot.send_message(m.chat.id, INFO_TEXT, reply_markup=make_keyboard())

@bot.message_handler(commands=["help"])
def cmd_help(m):
    """Показать помощь."""
    bot.send_message(m.chat.id, HELP_TEXT, reply_markup=make_keyboard())


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    """Обработка кнопок. Редактирует текущее сообщение."""
    c = call.message.chat.id
    a = call.data
    s = get_session(c)
    try:
        if a == "new":
            result = handle_new(c, s)
            bot.edit_message_text(result, c, call.message.message_id, reply_markup=make_keyboard())
        elif a == "inbox":
            result = handle_inbox(c, s)
            bot.edit_message_text(result, c, call.message.message_id, reply_markup=make_keyboard())
        elif a == "info":
            bot.edit_message_text(INFO_TEXT, c, call.message.message_id, reply_markup=make_keyboard())
        elif a == "source":
            bot.edit_message_text("🔗 Исходный код:\n" + SOURCE_URL, c, call.message.message_id, reply_markup=make_keyboard())
        elif a == "help":
            bot.edit_message_text(HELP_TEXT, c, call.message.message_id, reply_markup=make_keyboard())
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.answer_callback_query(call.id, "Ошибка")


def signal_handler(sig, frame):
    """Корректное завершение."""
    logger.info("Завершение...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Запуск {SERVICE_NAME}...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
