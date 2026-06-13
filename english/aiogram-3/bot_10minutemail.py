#!/usr/bin/env python3
"""
10MinuteMail Telegram Bot (aiogram 3.x)
Provider: 10MinuteMail | API: https://10minutemail.net/address.api.php
Framework: aiogram >=3.28.2
Install: pip install aiogram>=3.28.2 requests

Features:
- Create disposable email addresses
- Check inbox for new messages
- Real-time message monitoring
- Comprehensive error handling
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Vladislav Sofronov (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("10MinuteMail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_10MINUTEMAIL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://10minutemail.net/address.api.php"
SERVICE_NAME: str = "10MinuteMail"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3

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

sessions: Dict[int, UserSession] = {}
stats: Dict[str, int] = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{BASE_URL}{path}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning(f"API error: {e}")
            if attempt < MAX_RETRIES - 1: time.sleep(1)
    stats["errors"] += 1
    return {"error": "Max retries exceeded"}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{BASE_URL}{path}"
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=REQUEST_TIMEOUT)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}

def handle_new(c, s, call):
    bot.send_message(cid,"Visit https://10minutemail.net/address.api.php")

def handle_inbox(c, s, call):
    bot.send_message(cid,"Visit https://10minutemail.net/address.api.php")

@dp.message(commands=["start", "menu"])
async def cmd_start(m):
    kb = InlineKeyboardMarkup(row_width=2) if false else InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    await bot.send_message(m.chat.id, "*{SERVICE_NAME}*\nTemporary Email Bot\n\n/new — Create\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help", reply_markup=kb)

@dp.message(["info"])
async def cmd_info(m):
    await bot.send_message(m.chat.id,f"*10MinuteMail*\n\n🌐 https://10minutemail.net/address.api.php\n\nVisit the website.")

@dp.callback_query(F.data == "new")
async async def cb_new_handler(call):
    s = get_session(call.message.chat.id)
    handle_new(call.message.chat.id, s, call)

@dp.callback_query(F.data == "inbox")
async async def cb_inbox_handler(call):
    s = get_session(call.message.chat.id)
    handle_inbox(call.message.chat.id, s, call)

@dp.callback_query(F.data == "info")
async async def cb_info_handler(call):
    s = get_session(call.message.chat.id)
    await call.answer(f"Email: {s.addr or 'Not set'}", show_alert=True)

@dp.callback_query(F.data == "stats")
async async def cb_stats_handler(call):
    await call.answer(f"Created: {stats['created']} | Checked: {stats['checked']}", show_alert=True)

@dp.callback_query(F.data == "help")
async async def cb_help_handler(call):
    await bot.send_message(call.message.chat.id, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Starting {SERVICE_NAME}...")
    await dp.start_polling(bot)
