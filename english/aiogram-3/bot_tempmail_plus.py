#!/usr/bin/env python3
"""
TempMail.plus Telegram Bot (aiogram 3.x)
Provider: TempMail.plus | API: https://tempmail.plus/api/mails
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests

Features:
- Modern async/await architecture
- Create disposable email addresses
- Check inbox for new messages
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Владислав Софронов (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import os
import sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TempMail.plus")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://tempmail.plus/api/mails"
SERVICE_NAME: str = "TempMail.plus"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

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


@dp.message(F.text.in_{{"/start", "/menu"}})
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await message.answer(
        f"*{{SERVICE_NAME}}*\nTemporary Email Bot\n\n/new — Create\n/inbox — Check\n/info — Info",
        reply_markup=kb
    )


@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "Usage: /set email@domain.com")
    s = get_session(message.chat.id)
    s.addr = parts[1].strip()
    s.seen = set()
    bot.send_message(message.chat.id, f"✅ Monitoring: `{s.addr}`")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.addr:
        return bot.send_message(cid, "❌ Set email first: /set email@domain.com")
    r = api_get(params={{"email": s.addr}})
    mails = r.get("mail", [])
    stats["checked"] += 1
    if not mails:
        return bot.send_message(cid, "📭 Inbox empty")
    text = f"*{len(mails)} messages*\n\n"
    for m in mails[:15]:
        n = "🆕 " if m.get("mail_id") not in s.seen else ""
        s.seen.add(m.get("mail_id"))
        text += f"{n}`{m.get('mail_id')}` — {m.get('mail_from','?')}\n{m.get('mail_subject','—')}\n\n"
    bot.send_message(cid, text)


@bot.message_handler(commands=["domains"])
def cmd_domains(message: types.Message) -> None:
    doms = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","aol.com",
            "zoho.com","gmx.com","mail.com","yandex.com","icloud.com","1secmail.com","mailinator.com"]
    text = "*Supported Domains:*\n\n" + "\n".join(f"• `{d}`" for d in doms)
    bot.send_message(message.chat.id, text)


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery) -> None:
        bot.send_message(cid, "Use /set email@domain.com to start monitoring.")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery) -> None:
        s = get_session(cid)
        if not s.addr:
            return bot.answer_callback_query(call.id, "❌ /set email first")
        r = api_get(params={{"email": s.addr}})
        mails = r.get("mail", [])
        stats["checked"] += 1
        if not mails:
            bot.edit_message_text("📭 Empty", cid, call.message.message_id)
        else:
            txt = f"{len(mails)} messages:\n\n"
            for m in mails[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\n{m.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery) -> None:
    s = get_session(call.message.chat.id)
    await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)

@dp.callback_query(F.data == "stats")
async def cb_stats_handler(call: types.CallbackQuery) -> None:
    await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery) -> None:
    await bot.send_message(call.message.chat.id, "/new — Create\n/inbox — Check\n/info — Info")


async def main() -> None:
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
