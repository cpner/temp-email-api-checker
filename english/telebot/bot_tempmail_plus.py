#!/usr/bin/env python3
"""
TempMail.plus Telegram Bot

Provider: TempMail.plus
API: https://tempmail.plus/api/mails
Framework: pyTelegramBotAPI 4.18.0

Author: Vladislav Sofronov (@icesq)
Contact: feedback@gondon.su | t.me/icesq | gondon.su
License: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TempMail.plus")

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_BOT_TOKEN")
BASE_URL = "https://tempmail.plus/api/mails"
SERVICE_NAME = "TempMail.plus"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.seen = set()
        self.ts = 0

sessions = {{}}
stats = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    default_headers = {{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}}
    if headers: default_headers.update(headers)
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=default_headers, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"API error: {{e}}")
            if attempt < 2: time.sleep(1)
    stats["errors"] += 1
    return {{"error": "Max retries"}}

def handle_new(uid, s):
    """TempMail.plus monitors existing emails. User must /set email first."""
    return "Use /set email@domain.com to start monitoring"

def handle_inbox(uid, s):
    """Check inbox for messages on TempMail.plus."""
    if not s.addr:
        return "Set email first with /set"
    result = api_get(params={{"email": s.addr}})
    mails = result.get("mail", [])
    stats["checked"] += 1
    if not mails:
        return "Inbox empty"
    t = str(len(mails)) + " messages:\n"
    for m in mails[:15]:
        mid = m.get("mail_id", "?")
        marker = "NEW " if mid not in s.seen else ""
        s.seen.add(mid)
        t += marker + mid + " | " + m.get("mail_from", "?") + " | " + m.get("mail_subject", "-") + "\n"
    return t

def handle_set(text, s):
    """Set email address to monitor."""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: /set email@domain.com"
    s.addr = parts[1].strip()
    s.seen = set()
    return "Monitoring: " + s.addr

def make_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("Set Email", callback_data="new"), types.InlineKeyboardButton("Inbox", callback_data="inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="info"), types.InlineKeyboardButton("Source", callback_data="source"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="help"))
    return kb

@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    bot.send_message(m.chat.id, "TempMail.plus Bot\nMonitor inbox for any email\n\nHow to use:\n1. /set email@domain.com\n2. /inbox to check", reply_markup=make_kb())

@bot.message_handler(commands=["set"])
def cmd_set(m):
    s = get_session(m.chat.id)
    bot.send_message(m.chat.id, handle_set(m.text, s))

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = get_session(m.chat.id)
    bot.send_message(m.chat.id, handle_inbox(m.chat.id, s))

@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "TempMail.plus\nAPI: tempmail.plus/api/mails\nWebsite: tempmail.plus\nAuthor: Vladislav Sofronov (@icesq)", reply_markup=make_kb())

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, "/set email@domain.com\n/inbox - check\n/info - info", reply_markup=make_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    s = get_session(c)
    try:
        if call.data == "new":
            bot.edit_message_text(handle_new(c, s), c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "inbox":
            bot.edit_message_text(handle_inbox(c, s), c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "info":
            bot.edit_message_text("TempMail.plus\nAPI: tempmail.plus/api/mails\nAuthor: @icesq", c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "source":
            bot.edit_message_text("Source: https://github.com/cpner/temp-email-api-checker/blob/main/english/telebot/bot_tempmail_plus.py/blob/main/english/telebot/bot_tempmail_plus.py", c, call.message.message_id, reply_markup=make_kb())
        elif call.data == "help":
            bot.edit_message_text("/set email@domain.com\n/inbox - check\n/info - info", c, call.message.message_id, reply_markup=make_kb())
    except Exception as e:
        if "message is not modified" in str(e):
            bot.answer_callback_query(call.id)
        else:
            logger.error(str(e))
            bot.answer_callback_query(call.id, "Error")

def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting TempMail.plus...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
