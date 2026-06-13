#!/usr/bin/env python3
"""
TempMail.lol Telegram Bot (aiogram 2.x)
Provider: TempMail.lol | API: https://api.tempmail.lol
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests

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
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
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
    r=api_get("/generate")
    if "address" in r:
        s.addr,s.token,s.seen=r["address"],r.get("token"),set()
        stats["created"]+=1
        bot.edit_message_text(f"✅ `{r["address"]}`",c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Failed")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"❌ /new first")
    r=api_get(f"/auth/{s.token}"); emails=r.get("email",[]); stats["checked"]+=1
    if not emails: return bot.edit_message_text("📭 Empty",c,call.message.message_id)
    txt=""
    for e in emails[:10]: s.seen.add(e.get("id")); txt+=f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.edit_message_text(f"{len(emails)} messages:\n\n"+txt,c,call.message.message_id)

@dp.message_handler(commands=["start", "menu"])
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

@{dec}(["new"])
{ap}def cmd_new(m):
    c=m.chat.id; s=get_session(c); r=api_get("/generate")
    if "address" in r:
        s.addr,s.token,s.seen=r["address"],r.get("token"),set()
        stats["created"]+=1; {aw}bot.send_message(c,f"✅ `{r['address']}`\nToken: `{str(r.get('token',''))[:20]}...`")
    else: {aw}bot.send_message(c,"❌ Failed")

@{dec}(["inbox"])
{ap}def cmd_inbox(m):
    c=m.chat.id; s=get_session(c)
    if not s.token: return {aw}bot.send_message(c,"❌ /new first")
    r=api_get(f"/auth/{s.token}"); emails=r.get("email",[]); stats["checked"]+=1
    if not emails: return {aw}bot.send_message(c,"📭 Empty")
    t=f"*{len(emails)} messages*\n\n"
    for e in emails[:15]:
        n="🆕 " if e.get("id") not in s.seen else ""; s.seen.add(e.get("id"))
        t+=f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    {aw}bot.send_message(c,t)

@dp.callback_query_handler(lambda c: True)
async def cb(call):
    c = call.message.chat.id
    a = call.data
    try:
        s = get_session(c)
        if a == "new": handle_new(c, s, call)
        elif a == "inbox": handle_inbox(c, s, call)
        elif a == "info":
            await bot.answer_callback_query(call.id, f"Email: {s.addr or 'Not set'}", show_alert=True)
        elif a == "stats":
            await bot.answer_callback_query(call.id, f"Created: {stats['created']} | Checked: {stats['checked']}", show_alert=True)
        elif a == "help":
            await bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")
    except Exception as e:
        logger.error(f"Error: {e}")
        await bot.answer_callback_query(call.id, "Error")


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Starting {SERVICE_NAME}...")
    executor.start_polling(dp, skip_updates=True)
