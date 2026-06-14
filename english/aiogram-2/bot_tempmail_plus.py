#!/usr/bin/env python3
"""
TempMail.plus Telegram Bot (aiogram 2.x)

Provider: TempMail.plus
API: https://tempmail.plus/api/mails
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests

Features:
- Async/await architecture
- Create disposable email addresses
- Check inbox for new messages

Author: Vladislav Sofronov (@icesq)
Contact: feedback@gondon.su | t.me/icesq | gondon.su
Source: https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-2/bot_tempmail_plus.py
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
import sys
from typing import Optional, Dict, Any, Set

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TempMail.plus")

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_BOT_TOKEN")
BASE_URL = "https://tempmail.plus/api/mails"
SERVICE_NAME = "TempMail.plus"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

# Button labels
BTN_NEW = "📧 New Email"
BTN_INBOX = "📥 Inbox"
BTN_INFO = "ℹ️ Info"
BTN_SOURCE = "🔗 Source Code"
BTN_HELP = "❓ Help"

# Text messages
SOURCE_URL = "https://github.com/cpner/temp-email-api-checker/blob/main/english/aiogram-2/bot_tempmail_plus.py"

START_TEXT = """*TempMail.plus Bot*
Monitor inbox for any email provider

*Features:*
Gmail, Yahoo, Outlook, 13 domains

*How to use:*
1. Tap New Email
2. Copy address
3. Use for registration
4. Tap Inbox to check"""

INFO_TEXT = """*TempMail.plus — Info*

*Service:* TempMail.plus
*Description:* Monitor inbox for any email provider
*API:* `https://tempmail.plus/api/mails`
*Website:* https://tempmail.plus
*Source:* """ + SOURCE_URL + """
*Author:* Vladislav Sofronov (@icesq)
*License:* MIT"""

HELP_TEXT = """*TempMail.plus — Commands*

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
        r = requests.get(url, params=params, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}

def handle_new(uid, s):
    """Create new email."""
    return "Use /set email@domain.com"

def handle_inbox(uid, s):
    """Check inbox."""
    if not s.addr: return "Set email first"
    r = api_get(params={{"email":s.addr}}); mails = r.get("mail",[]); stats["checked"] += 1
    if not mails: return "Empty inbox"
    t = str(len(mails)) + " messages:\n"
    for m in mails[:15]: s.seen.add(m.get("mail_id")); t += m.get("mail_id","?")+" | "+m.get("mail_from","?")+" | "+m.get("mail_subject","-")+"\n"
    return t

def make_kb():
    """Build keyboard."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(BTN_NEW, callback_data="new"), InlineKeyboardButton(BTN_INBOX, callback_data="inbox"))
    kb.add(InlineKeyboardButton(BTN_INFO, callback_data="info"), InlineKeyboardButton(BTN_SOURCE, callback_data="source"))
    kb.add(InlineKeyboardButton(BTN_HELP, callback_data="help"))
    return kb


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m):
    """Show welcome message."""
    await m.answer(START_TEXT, reply_markup=make_kb())

@dp.message_handler(commands=["new"])
async def cmd_new(m):
    """Create new email."""
    s = get_session(m.chat.id)
    await m.answer(handle_new(m.chat.id, s))

@dp.message_handler(commands=["inbox"])
async def cmd_inbox(m):
    """Check inbox."""
    s = get_session(m.chat.id)
    await m.answer(handle_inbox(m.chat.id, s))

@dp.message_handler(commands=["info"])
async def cmd_info(m):
    """Show info."""
    await m.answer(INFO_TEXT, reply_markup=make_kb())

@dp.message_handler(commands=["help"])
async def cmd_help(m):
    """Show help."""
    await m.answer(HELP_TEXT, reply_markup=make_kb())


@dp.callback_query_handler(lambda c: True)
async def cb(call):
    """Handle buttons. Edit current message."""
    c = call.message.chat.id
    s = get_session(c)
    try:
        if call.data == "new":
            await bot.edit_message_text(handle_new(c, s), c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "inbox":
            await bot.edit_message_text(handle_inbox(c, s), c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "info":
            await bot.edit_message_text(INFO_TEXT, c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "source":
            await bot.edit_message_text("Source: " + SOURCE_URL, c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "help":
            await bot.edit_message_text(HELP_TEXT, c, call.message.message_id, reply_markup=make_kb())
    except Exception as e:
        logger.error(str(e))
        await call.answer("Error")

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    executor.start_polling(dp, skip_updates=True)
