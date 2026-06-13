#!/usr/bin/env python3
"""
YOPmail Telegram Bot (aiogram 2.x)
Provider: YOPmail | API: https://yopmail.com
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests
Author: Vladislav Sofronov (cpner)
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("YOPmail")

BOT_TOKEN = os.environ.get("BOT_TOKEN_YOPMAIL", "YOUR_BOT_TOKEN")
BASE_URL = "https://yopmail.com"
SERVICE_NAME = "YOPmail"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.key = None
        self.seen = set()
        self.ts = 0
        self.messages = 0

sessions = {}
stats = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.get(url, params=params, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}


def make_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
    )
    kb.add(
        InlineKeyboardButton("ℹ️ Info", callback_data="info"),
        InlineKeyboardButton("🔗 Source Code", callback_data="source"),
    )
    kb.add(
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    return kb


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m):
    await m.answer("*YOPmail Bot*\\nMulti-domain disposable email\\n\\n*Features:*\\nCheck inbox, list domains\\n\\n*How to use:*\\n1. Tap 'New Email' to create\\n2. Copy the email address\\n3. Use it for registration\\n4. Tap 'Inbox' to check messages\\n5. New messages marked with emoji", reply_markup=make_kb())

@dp.message_handler(commands=["new"])
async def cmd_new(m):
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        await m.answer("Created: `" + r["email_addr"] + "`")
    else:
        await m.answer("Failed. Try /new")

@dp.message_handler(commands=["inbox"])
async def cmd_inbox(m):
    c = m.chat.id
    s = get_session(c)
    if not s.token:
        return await m.answer("Create email first: /new")
    r = api_get(params={"f": "check_email", "sid_token": s.token, "seq": 0})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return await m.answer("Empty inbox")
    t = str(len(msgs)) + " messages:\n\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\n"
    await m.answer(t)

@dp.message_handler(commands=["info"])
async def cmd_info(m):
    await m.answer('*YOPmail Bot — Info*\\n\\n*Service:* YOPmail\\n*Description:* Multi-domain disposable email\\n*Features:* Check inbox, list domains\\n*API:* `https://yopmail.com`\\n*Website:* https://yopmail.com\\n*Source:* https://github.com/cpner/temp-email-api-checker/blob/main/en/aiogram-2/bot_yopmail.py\\n*Author:* Vladislav Sofronov (cpner)\\n*License:* MIT', reply_markup=make_kb())

@dp.message_handler(commands=["help"])
async def cmd_help(m):
    await m.answer('*YOPmail Bot — Commands*\\n\\n/start — Main menu\\n/new — Create email\\n/inbox — Check messages\\n/set — Set email manually\\n/info — Bot information\\n/help — This help\\n\\n*Buttons:*\\n📧 New Email — Create address\\n📥 Inbox — Check messages\\nℹ️ Info — Bot details\\n🔗 Source — GitHub link\\n❓ Help — Usage guide', reply_markup=make_kb())


@dp.callback_query_handler(lambda c: True)
async def cb(call):
    c = call.message.chat.id
    a = call.data
    try:
        s = get_session(c)
        if a == "new":
            r = api_get(params={"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"})
            if "email_addr" in r:
                s.addr = r["email_addr"]
                s.token = r.get("sid_token")
                s.seen = set()
                s.ts = time.time()
                stats["created"] += 1
                await bot.edit_message_text("Created: `" + r["email_addr"] + "`", c, call.message.message_id)
            else:
                await call.answer("Failed")
        elif a == "inbox":
            if not s.token:
                return await call.answer("Create email first")
            r = api_get(params={"f": "check_email", "sid_token": s.token, "seq": 0})
            msgs = r.get("list", [])
            stats["checked"] += 1
            if not msgs:
                await bot.edit_message_text("Empty inbox", c, call.message.message_id)
            else:
                txt = ""
                for x in msgs[:10]:
                    s.seen.add(x.get("mail_id"))
                    txt += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\n"
                await bot.edit_message_text(str(len(msgs)) + " messages:\n\n" + txt, c, call.message.message_id)
        elif a == "info":
            await call.answer("Name: " + name + "\nAPI: " + url, show_alert=True)
        elif a == "source":
            await bot.send_message(c, "Source code: " + source_url)
        elif a == "help":
            await bot.send_message(c, '*YOPmail Bot — Commands*\\n\\n/start — Main menu\\n/new — Create email\\n/inbox — Check messages\\n/set — Set email manually\\n/info — Bot information\\n/help — This help\\n\\n*Buttons:*\\n📧 New Email — Create address\\n📥 Inbox — Check messages\\nℹ️ Info — Bot details\\n🔗 Source — GitHub link\\n❓ Help — Usage guide', reply_markup=make_kb())
    except Exception as e:
        logger.error("Error: " + str(e))
        await call.answer(err)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    executor.start_polling(dp, skip_updates=True)
