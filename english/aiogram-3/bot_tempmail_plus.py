#!/usr/bin/env python3
"""
TempMail.plus Telegram Bot (aiogram 3.x)

Provider: TempMail.plus
API: https://tempmail.plus/api/mails
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests

Author: Владислав Софронов (@icesq)
Contact: feedback@gondon.su | t.me/icesq | gondon.su
Source: https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-3/bot_tempmail_plus.py
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TempMail.plus")

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_BOT_TOKEN")
BASE_URL = "https://tempmail.plus/api/mails"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.seen = set()
        self.ts = 0

sessions = {}
stats = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    default_headers = {"User-Agent": "Mozilla/5.0"}
    if headers: default_headers.update(headers)
    try:
        r = requests.get(url, params=params, headers=default_headers, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}

def handle_new(uid, s):
    return "Используйте /set email@domain.com"

def handle_inbox(uid, s):
    if not s.addr: return "Установите почту"
    result = api_get(params={"email": s.addr})
    mails = result.get("mail", [])
    stats["checked"] += 1
    if not mails: return "Пусто"
    t = str(len(mails)) + " писем:\n"
    for m in mails[:15]:
        mid = m.get("mail_id", "?")
        marker = "🆕 " if mid not in s.seen else ""
        s.seen.add(mid)
        t += marker + mid + " | " + m.get("mail_from", "?") + " | " + m.get("mail_subject", "-") + "\n"
    return t

def handle_set(text, s):
    parts = text.split(maxsplit=1)
    if len(parts) < 2: return "Использование: /set email@domain.com"
    s.addr = parts[1].strip()
    s.seen = set()
    return "Мониторинг: " + s.addr

def make_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Установить", callback_data="new"), InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info"), InlineKeyboardButton(text="🔗 Код", callback_data="source")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])

@dp.message(F.text.startswith("/"))
async def cmd_router(m):
    text = m.text
    if text in ["/start", "/menu"]:
        await m.answer("TempMail.plus Бот
Мониторинг почты любых провайдеров

Возможности:
Gmail, Yahoo, Outlook, 13 доменов

Как пользоваться:
1. Нажмите Установить
2. Введите email
3. Нажмите Входящие", reply_markup=make_kb())
    elif text.startswith("/set"):
        s = get_session(m.chat.id)
        await m.answer(handle_set(text, s))
    elif text == "/inbox":
        s = get_session(m.chat.id)
        await m.answer(handle_inbox(m.chat.id, s))
    elif text == "/info":
        await m.answer("TempMail.plus — Инфо

Сервис: TempMail.plus
Описание: Мониторинг почты любых провайдеров
Возможности: Gmail, Yahoo, Outlook, 13 доменов
API: https://tempmail.plus/api/mails
Сайт: https://tempmail.plus
Код: https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-3/bot_tempmail_plus.py
Автор: Владислав Софронов (@icesq)
Лицензия: MIT", reply_markup=make_kb())
    elif text == "/help":
        await m.answer("TempMail.plus — Команды

/start — Главное меню
/set — Установить
/inbox — Проверить
/info — Инфо
/help — Помощь", reply_markup=make_kb())

@dp.callback_query(F.data == "new")
async def cb_new(call):
    s = get_session(call.message.chat.id)
    await bot.edit_message_text(handle_new(call.message.chat.id, s), call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "inbox")
async def cb_inbox(call):
    s = get_session(call.message.chat.id)
    await bot.edit_message_text(handle_inbox(call.message.chat.id, s), call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "info")
async def cb_info(call):
    await bot.edit_message_text("TempMail.plus — Инфо

Сервис: TempMail.plus
Описание: Мониторинг почты любых провайдеров
Возможности: Gmail, Yahoo, Outlook, 13 доменов
API: https://tempmail.plus/api/mails
Сайт: https://tempmail.plus
Код: https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-3/bot_tempmail_plus.py
Автор: Владислав Софронов (@icesq)
Лицензия: MIT", call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "source")
async def cb_source(call):
    await bot.edit_message_text("Source: " + "https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-3/bot_tempmail_plus.py", call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "help")
async def cb_help(call):
    await bot.edit_message_text("TempMail.plus — Команды

/start — Главное меню
/set — Установить
/inbox — Проверить
/info — Инфо
/help — Помощь", call.message.chat.id, call.message.message_id, reply_markup=make_kb())

async def main():
    logger.info("Starting TempMail.plus...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
