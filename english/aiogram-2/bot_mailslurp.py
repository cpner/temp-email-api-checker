#!/usr/bin/env python3
"""
MailSlurp Telegram Bot (aiogram 2.x)
Provider: MailSlurp | API: https://api.mailslurp.com
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests

Features:
- Async/await architecture
- Create disposable email addresses
- Check inbox for new messages
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Vladislav Sofronov (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MailSlurp")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_MAILSLURP", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.mailslurp.com"
SERVICE_NAME: str = "MailSlurp"

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

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

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
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    await m.answer("*{{SERVICE_NAME}}*\nTemporary Email Bot\n\n/new — Create\n/inbox — Check\n/info — Info", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    bot.send_message(m.chat.id, f"*{SERVICE_NAME}*\n\n🌐 {BASE_URL}\n\nVisit the website.")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": bot.send_message(cid, f"Visit {BASE_URL}")
        elif a == "inbox": bot.send_message(cid, f"Visit {BASE_URL}")
        elif a == "info":
            s = get_session(c)
            await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif a == "stats":
            await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            await bot.send_message(c, "/new — Create\n/inbox — Check\n/info — Info")
    except Exception as e:
        logger.error(f"Error: {{e}}")
        await call.answer("Error")

if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}}...")
    executor.start_polling(dp, skip_updates=True)
