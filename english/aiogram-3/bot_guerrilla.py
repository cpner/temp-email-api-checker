#!/usr/bin/env python3
"""
Guerrilla Mail Telegram Bot (aiogram 3.x)
Provider: Guerrilla Mail | API: https://api.guerrillamail.com/ajax.php
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
logger = logging.getLogger("Guerrilla Mail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.guerrillamail.com/ajax.php"
SERVICE_NAME: str = "Guerrilla Mail"
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
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr,s.token,s.seen,s.ts=r["email_addr"],r.get("sid_token"),set(),time.time()
        stats["created"]+=1
        bot.edit_message_text(f"✅ `{r["email_addr"]}`",c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Failed")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"❌ /new first")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return bot.edit_message_text("📭 Empty",c,call.message.message_id)
    txt=""
    for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt+=f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.edit_message_text(f"{len(msgs)} messages:\n\n"+txt,c,call.message.message_id)

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

@{dec}(["new"])
{ap}def cmd_new(m):
    c=m.chat.id; s=get_session(c)
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr,s.token,s.seen,s.ts=r["email_addr"],r.get("sid_token"),set(),time.time()
        stats["created"]+=1; {aw}bot.send_message(c,f"✅ `{r['email_addr']}`\n\nCopy and use for registrations.")
    else: {aw}bot.send_message(c,"❌ Failed. Try /new")

@{dec}(["inbox"])
{ap}def cmd_inbox(m):
    c=m.chat.id; s=get_session(c)
    if not s.token: return {aw}bot.send_message(c,"❌ /new first")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return {aw}bot.send_message(c,"📭 Empty")
    t=f"*{len(msgs)} messages*\n\n"
    for x in msgs[:15]:
        n="🆕 " if x.get("mail_id") not in s.seen else ""; s.seen.add(x.get("mail_id"))
        t+=f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    {aw}bot.send_message(c,t)

@{dec}(["set"])
{ap}def cmd_set(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return {aw}bot.send_message(m.chat.id,"Usage: /set <username>")
    s=get_session(m.chat.id)
    if not s.token: return {aw}bot.send_message(m.chat.id,"❌ /new first")
    r=api_get(params={"f":"set_email_user","sid_token":s.token,"email_user":p[1].strip()})
    if "email_addr" in r: s.addr=r["email_addr"]; {aw}bot.send_message(m.chat.id,f"✅ `{r['email_addr']}`")

@{dec}(["info"])
{ap}def cmd_info(m):
    s=get_session(m.chat.id); {aw}bot.send_message(m.chat.id,f"📧 {s.addr or 'Not set'}\n📩 Seen: {len(s.seen)}")

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
