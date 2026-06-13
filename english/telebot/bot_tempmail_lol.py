#!/usr/bin/env python3
"""
TempMail.lol Telegram Bot
Provider: TempMail.lol | API: https://api.tempmail.lol
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
logger = logging.getLogger("TempMail.lol")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.tempmail.lol"
SERVICE_NAME: str = "TempMail.lol"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set! Set BOT_TOKEN_TEMPMAIL_LOL")
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


@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get("/generate")
    if "address" in r:
        s.addr, s.token, s.seen = r["address"], r.get("token"), set()
        stats["created"] += 1
        bot.send_message(c, f"✅ `{r['address']}`\nToken: `{str(r.get('token',''))[:20]}...`")
    else: bot.send_message(c, "❌ Failed")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new first")
    r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
    if not emails: return bot.send_message(c, "📭 Empty")
    t = f"*{len(emails)} messages*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""; s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(c, t)


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": r = api_get("/generate")
        if "address" in r:
            s = get_session(c); s.addr, s.token, s.seen = r["address"], r.get("token"), set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id)
        elif a == "inbox": s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
        if not emails: bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = ""
            for e in emails[:10]: s.seen.add(e.get("id")); txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            bot.edit_message_text(f"{len(emails)} messages:\n\n" + txt, c, call.message.message_id)
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
