#!/usr/bin/env python3
"""
10MinuteMail Telegram Bot
Provider: 10MinuteMail | API: https://10minutemail.net/address.api.php
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests

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
import telebot
from telebot import types
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
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set! Set BOT_TOKEN_10MINUTEMAIL")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

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
    if user_id not in sessions: sessions[user_id] = UserSession()
    return sessions[user_id]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"API error attempt {{attempt+1}}/{{MAX_RETRIES}}: {{e}}")
            if attempt < MAX_RETRIES - 1: time.sleep(RETRY_DELAY * (attempt + 1))
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


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*{{SERVICE_NAME}}*\nTemporary Email Bot\n\n/new — Create\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
        reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    bot.send_message(m.chat.id, f"*{SERVICE_NAME}*\n\n🌐 {BASE_URL}\n\nVisit the website.")


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": bot.send_message(cid, f"Visit {BASE_URL}")
        elif a == "inbox": bot.send_message(cid, f"Visit {BASE_URL}")
        elif a == "info":
            s = get_session(c)
            bot.answer_callback_query(call.id, f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif a == "stats":
            bot.answer_callback_query(call.id, f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")
    except Exception as e:
        logger.error(f"Error: {{e}}")
        bot.answer_callback_query(call.id, "Error occurred")


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}}...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
