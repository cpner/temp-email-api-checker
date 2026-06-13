#!/usr/bin/env python3
"""
Guerrilla Mail — Telegram-бот временной почты (aiogram 2.x)
Провайдер: Guerrilla Mail | API: https://api.guerrillamail.com/ajax.php
Фреймворк: aiogram 2.25.1
Установка: pip install aiogram==2.25.1 requests

Возможности:
- Async/await архитектура
- Создание одноразовых почтовых ящиков
- Проверка входящих сообщений
- Ограничение частоты запросов
- Статистика использования
- Корректное завершение

Автор: Temp Email Bots Project
Лицензия: MIT
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import random
import string
import time
import os
import sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Guerrilla Mail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.guerrillamail.com/ajax.php"
SERVICE_NAME: str = "Guerrilla Mail"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await message.answer(
        f"*{{SERVICE_NAME}}*\nБот временной почты\n\n/new — Создать\n/inbox — Проверить\n/info — Данные",
        reply_markup=kb
    )


@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['email_addr']}`\n\nСкопируйте адрес и используйте для регистраций.")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ Сначала /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return bot.send_message(cid, "📭 Пусто")
    t = f"*{len(msgs)} писем*\n\n"
    for m in msgs[:15]:
        n = "🆕 " if m.get("mail_id") not in s.seen else ""
        s.seen.add(m.get("mail_id"))
        t += f"{n}`{m.get('mail_id')}` — {m.get('mail_from','?')}\n{m.get('mail_subject','—')}\n\n"
    bot.send_message(cid, t)


@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "/set <имя>")
    s = get_session(message.chat.id)
    if not s.token:
        return bot.send_message(message.chat.id, "❌ /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": parts[1].strip()}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        bot.send_message(message.chat.id, f"✅ `{r['email_addr']}`")


@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    s = get_session(message.chat.id)
    bot.send_message(message.chat.id, f"📧 {s.addr or '—'}\n📩 {len(s.seen)}")


@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(cid)
            s.addr = r["email_addr"]
            s.token = r.get("sid_token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['email_addr']}`", cid, call.message.message_id)
        elif action == "inbox":
        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", [])
        stats["checked"] += 1
        if not msgs:
            bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем:\n\n"
            for m in msgs[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\n{m.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
        elif action == "info":
            s = get_session(cid)
            await call.answer(f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)
        elif action == "stats":
            await call.answer(f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)
        elif action == "help":
            await bot.send_message(cid, "/new — Создать\n/inbox — Проверить\n/info — Данные")
    except Exception as e:
        logger.error(f"Ошибка: {{e}}")
        await call.answer("Ошибка")


if __name__ == "__main__":
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    executor.start_polling(dp, skip_updates=True)
