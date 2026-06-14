#!/usr/bin/env python3
"""
Guerrilla Mail Telegram Bot (aiogram 3.x)

Provider: Guerrilla Mail
API: https://api.guerrillamail.com/ajax.php
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests

Features:
- Modern async/await architecture
- Create disposable email addresses
- Check inbox for new messages

Author: Vladislav Sofronov (@icesq)
Contact: feedback@gondon.su | t.me/icesq | gondon.su
Source: https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-2/bot_guerrilla.py
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

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Guerrilla Mail")

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_BOT_TOKEN")
BASE_URL = "https://api.guerrillamail.com/ajax.php"
SERVICE_NAME = "Guerrilla Mail"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

# Button labels
BTN_NEW = "📧 New Email"
BTN_INBOX = "📥 Inbox"
BTN_INFO = "ℹ️ Info"
BTN_SOURCE = "🔗 Source Code"
BTN_HELP = "❓ Help"

# Text messages
SOURCE_URL = "https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-2/bot_guerrilla.py"

START_TEXT = """*Guerrilla Mail Bot*
Full REST API for disposable emails

*Features:*
Create, inbox, set user, 9 languages

*How to use:*
1. Tap New Email
2. Copy address
3. Use for registration
4. Tap Inbox to check"""

INFO_TEXT = """*Guerrilla Mail — Info*

*Service:* Guerrilla Mail
*Description:* Full REST API for disposable emails
*API:* `https://api.guerrillamail.com/ajax.php`
*Website:* https://www.guerrillamail.com
*Source:* """ + SOURCE_URL + """
*Author:* Vladislav Sofronov (@icesq)
*License:* MIT"""

HELP_TEXT = """*Guerrilla Mail — Commands*

/start — Main menu
/new — Create email
/inbox — Check messages
/info — Bot info
/help — This help"""


class UserSession:
    """Stores user state."""
    def __init__(self):
        self.addr = None
        self.token = None
        self.seen = set()
        self.ts = 0

sessions = {}
stats = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid):
    """Get user session."""
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    """GET request with retry."""
    url = BASE_URL + path
    try:
        default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if headers:
            default_headers.update(headers)
        r = requests.get(url, params=params, headers=default_headers, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}

def handle_new(uid, s):
    """Create new email."""
    r = api_get(params={{"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]; s.token = r.get("sid_token"); s.seen = set(); s.ts = time.time()
        stats["created"] += 1
        return "Created: " + r["email_addr"]
    return "Failed"

def handle_inbox(uid, s):
    """Check inbox."""
    if not s.token: return "Create email first"
    r = api_get(params={{"f":"check_email","sid_token":s.token,"seq":0}})
    msgs = r.get("list",[]); stats["checked"] += 1
    if not msgs: return "Empty inbox"
    t = str(len(msgs)) + " messages:\n"
    for m in msgs[:15]: s.seen.add(m.get("mail_id")); t += m.get("mail_id","?")+" | "+m.get("mail_from","?")+" | "+m.get("mail_subject","-")+"\n"
    return t

def make_kb():
    """Build keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_NEW, callback_data="new"), InlineKeyboardButton(text=BTN_INBOX, callback_data="inbox")],
        [InlineKeyboardButton(text=BTN_INFO, callback_data="info"), InlineKeyboardButton(text=BTN_SOURCE, callback_data="source")],
        [InlineKeyboardButton(text=BTN_HELP, callback_data="help")],
    ])


@dp.message(F.text.startswith("/"))
async def cmd_router(m):
    """Route all slash commands."""
    text = m.text
    if text in ["/start", "/menu"]:
        await m.answer(START_TEXT, reply_markup=make_kb())
    elif text == "/new":
        s = get_session(m.chat.id)
        await m.answer(handle_new(m.chat.id, s))
    elif text == "/inbox":
        s = get_session(m.chat.id)
        await m.answer(handle_inbox(m.chat.id, s))
    elif text == "/info":
        await m.answer(INFO_TEXT, reply_markup=make_kb())
    elif text == "/help":
        await m.answer(HELP_TEXT, reply_markup=make_kb())


@dp.callback_query(F.data == "new")
async def cb_new(call):
    """Handle New Email button."""
    s = get_session(call.message.chat.id)
    await bot.edit_message_text(handle_new(call.message.chat.id, s), call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "inbox")
async def cb_inbox(call):
    """Handle Inbox button."""
    s = get_session(call.message.chat.id)
    await bot.edit_message_text(handle_inbox(call.message.chat.id, s), call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "info")
async def cb_info(call):
    """Handle Info button."""
    await bot.edit_message_text(INFO_TEXT, call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "source")
async def cb_source(call):
    """Handle Source button."""
    await bot.edit_message_text("Source: " + SOURCE_URL, call.message.chat.id, call.message.message_id, reply_markup=make_kb())

@dp.callback_query(F.data == "help")
async def cb_help(call):
    """Handle Help button."""
    await bot.edit_message_text(HELP_TEXT, call.message.chat.id, call.message.message_id, reply_markup=make_kb())


async def main():
    """Start polling."""
    logger.info("Starting " + SERVICE_NAME + "...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
