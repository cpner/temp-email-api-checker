#!/usr/bin/env python3
"""
EmailFake Telegram Bot
Provider: EmailFake | API: https://emailfake.com/api/v1
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests
Author: Vladislav Sofronov (cpner)
License: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("EmailFake")

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILFAKE", "YOUR_BOT_TOKEN")
BASE_URL = "https://emailfake.com/api/v1"
SERVICE_NAME = "EmailFake"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

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
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning("API error: " + str(e))
            if attempt < 2: time.sleep(1)
    stats["errors"] += 1
    return {"error": "Max retries"}

def api_post(path="", data=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}


def make_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
    )
    kb.add(
        types.InlineKeyboardButton("ℹ️ Info", callback_data="info"),
        types.InlineKeyboardButton("🔗 Source Code", callback_data="source"),
    )
    kb.add(
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    return kb


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    bot.send_message(m.chat.id, "*EmailFake Bot*\\nSimple inbox monitoring\\n\\n*Features:*\\nSet email, check inbox\\n\\n*How to use:*\\n1. Tap 'New Email' to create\\n2. Copy the email address\\n3. Use it for registration\\n4. Tap 'Inbox' to check messages\\n5. New messages marked with emoji", reply_markup=make_kb())

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        bot.send_message(c, "Created: `" + r["email_addr"] + "`")
    else:
        bot.send_message(c, "Failed. Try /new")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = get_session(c)
    if not s.token:
        return bot.send_message(c, "Create email first: /new")
    r = api_get(params={"f": "check_email", "sid_token": s.token, "seq": 0})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return bot.send_message(c, "Empty inbox")
    t = str(len(msgs)) + " messages:\n\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\n"
    bot.send_message(c, t)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "Usage: /set <username>")
    s = get_session(m.chat.id)
    if not s.token:
        return bot.send_message(m.chat.id, "Create email first: /new")
    r = api_get(params={"f": "set_email_user", "sid_token": s.token, "email_user": p[1].strip()})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        bot.send_message(m.chat.id, "Email: `" + r["email_addr"] + "`")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, '*EmailFake Bot — Info*\\n\\n*Service:* EmailFake\\n*Description:* Simple inbox monitoring\\n*Features:* Set email, check inbox\\n*API:* `https://emailfake.com/api/v1`\\n*Website:* https://emailfake.com\\n*Source:* https://github.com/cpner/temp-email-api-checker/blob/main/en/telebot/bot_emailfake.py\\n*Author:* Vladislav Sofronov (cpner)\\n*License:* MIT', reply_markup=make_kb())

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, '*EmailFake Bot — Commands*\\n\\n/start — Main menu\\n/new — Create email\\n/inbox — Check messages\\n/set — Set email manually\\n/info — Bot information\\n/help — This help\\n\\n*Buttons:*\\n📧 New Email — Create address\\n📥 Inbox — Check messages\\nℹ️ Info — Bot details\\n🔗 Source — GitHub link\\n❓ Help — Usage guide', reply_markup=make_kb())


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
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
                bot.edit_message_text("Created: `" + r["email_addr"] + "`", c, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Failed")
        elif a == "inbox":
            if not s.token:
                return bot.answer_callback_query(call.id, "Create email first")
            r = api_get(params={"f": "check_email", "sid_token": s.token, "seq": 0})
            msgs = r.get("list", [])
            stats["checked"] += 1
            if not msgs:
                bot.edit_message_text("Empty inbox", c, call.message.message_id)
            else:
                txt = ""
                for x in msgs[:10]:
                    s.seen.add(x.get("mail_id"))
                    txt += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\n"
                bot.edit_message_text(str(len(msgs)) + " messages:\n\n" + txt, c, call.message.message_id)
        elif a == "info":
            bot.answer_callback_query(call.id, "Name: " + name + "\nAPI: " + url, show_alert=True)
        elif a == "source":
            bot.send_message(c, "Source code: " + source_url)
        elif a == "help":
            bot.send_message(c, '*EmailFake Bot — Commands*\\n\\n/start — Main menu\\n/new — Create email\\n/inbox — Check messages\\n/set — Set email manually\\n/info — Bot information\\n/help — This help\\n\\n*Buttons:*\\n📧 New Email — Create address\\n📥 Inbox — Check messages\\nℹ️ Info — Bot details\\n🔗 Source — GitHub link\\n❓ Help — Usage guide', reply_markup=make_kb())
    except Exception as e:
        logger.error("Error: " + str(e))
        bot.answer_callback_query(call.id, err)


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
