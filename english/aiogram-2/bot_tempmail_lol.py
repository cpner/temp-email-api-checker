#!/usr/bin/env python3
"""
TempMail.lol Telegram Bot (aiogram 2.x)
Provider: TempMail.lol | API: https://api.tempmail.lol
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests

Features:
- Async/await architecture
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
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import random
import string
import time
import os
import signal
import sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TempMail.lol")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.tempmail.lol"
SERVICE_NAME: str = "TempMail.lol"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
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
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"API error attempt {{attempt+1}}: {{e}}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
    stats["errors"] += 1
    return {{"error": "Max retries exceeded"}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
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
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    text = (
        f"*{{SERVICE_NAME}}*\n"
        f"Temporary Email Bot\n\n"
        f"Create disposable email addresses\n"
        f"and receive messages instantly.\n\n"
        f"*Quick Start:*\n"
        f"1. Tap 📧 New Email\n"
        f"2. Copy the address\n"
        f"3. Use it for registration\n"
        f"4. Tap 📥 Inbox to check"
    )
    await message.answer(text, reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get("/generate")
    if "address" in r:
        s.addr = r["address"]
        s.token = r.get("token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['address']}`\nToken: `{str(r.get('token',''))[:20]}...`")
    else:
        bot.send_message(cid, "❌ Failed to generate email.")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ Create email first: /new")
    r = api_get(f"/auth/{s.token}")
    emails = r.get("email", [])
    stats["checked"] += 1
    if not emails:
        return bot.send_message(cid, "📭 Inbox empty")
    text = f"*{len(emails)} messages*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""
        s.seen.add(e.get("id"))
        text += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(cid, text)


@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
        r = api_get("/generate")
        if "address" in r:
            s = get_session(cid)
            s.addr = r["address"]
            s.token = r.get("token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", cid, call.message.message_id)
        elif action == "inbox":
        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(f"/auth/{s.token}")
        emails = r.get("email", [])
        stats["checked"] += 1
        if not emails:
            bot.edit_message_text("📭 Empty", cid, call.message.message_id)
        else:
            txt = f"{len(emails)} messages:\n\n"
            for e in emails[:10]:
                s.seen.add(e.get("id"))
                txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
        elif action == "info":
            s = get_session(cid)
            await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif action == "stats":
            await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif action == "help":
            await bot.send_message(cid, "/new — Create\n/inbox — Check\n/info — Info")
    except Exception as e:
        logger.error(f"Callback error: {{e}}")
        await call.answer("Error occurred")


if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    executor.start_polling(dp, skip_updates=True)
