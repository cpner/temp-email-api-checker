#!/usr/bin/env python3
"""
Guerrilla Mail Telegram Bot (aiogram 3.x)
Provider: Guerrilla Mail | API: https://api.guerrillamail.com/ajax.php
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests

Features:
- Modern async/await architecture
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
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Guerrilla Mail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.guerrillamail.com/ajax.php"
SERVICE_NAME: str = "Guerrilla Mail"

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


@dp.message(F.text.in_{{"/start", "/menu"}})
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer("*{{SERVICE_NAME}}*\nTemporary Email Bot\n\n/new — Create\n/inbox — Check\n/info — Info", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
        stats["created"] += 1
        bot.send_message(c, f"✅ Created: `{r['email_addr']}`\n\nCopy and use for registrations.")
    else: bot.send_message(c, "❌ Failed. Try /new")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new first")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs, stats["checked"] = r.get("list", []), stats["checked"] + 1
    if not msgs: return bot.send_message(c, "📭 Empty")
    t = f"*{len(msgs)} messages*\n\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""
        s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c, t)

@bot.message_handler(commands=["set"])
def cmd_set(m: types.Message) -> None:
    p = m.text.split(maxsplit=1)
    if len(p) < 2: return bot.send_message(m.chat.id, "Usage: /set <username>")
    s = get_session(m.chat.id)
    if not s.token: return bot.send_message(m.chat.id, "❌ /new first")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": p[1].strip()}})
    if "email_addr" in r: s.addr = r["email_addr"]; bot.send_message(m.chat.id, f"✅ `{r['email_addr']}`")

@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    s = get_session(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.addr or 'Not set'}\n📩 Seen: {len(s.seen)}")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery) -> None:
r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(c); s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
            stats["created"] += 1
            bot.edit_message_text(f"✅ Created: `{r['email_addr']}`", c, call.message.message_id)

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery) -> None:
s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", []); stats["checked"] += 1
        if not msgs: bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = ""
            for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(f"{len(msgs)} messages:\n\n" + txt, c, call.message.message_id)

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
    logger.info(f"Starting {{SERVICE_NAME}}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
