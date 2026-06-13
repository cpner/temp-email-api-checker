#!/usr/bin/env python3
"""
MailSac — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: MailSac
API: https://mailsac.com/api
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILSAC", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://mailsac.com/api"

sessions = {}


def gs(c):
    if c not in sessions:
        sessions[c] = {"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{BASE}{path}", params=params, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{BASE}{path}", json=data, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*MailSac*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["key"])
def cmd_key(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/key <API_KEY>")
    s = gs(m.chat.id)
    s["key"] = p[1].strip()
    bot.send_message(m.chat.id, f"✅ Key: `{s['key'][:10]}...`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key first <API_KEY>")
    r = api_get("/domains", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} доменов*\n\n" + "\n".join(f"• `{d}`" for d in data[:30])
        bot.send_message(m.chat.id, t, parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ No domains")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("key"):
        return bot.send_message(c, "❌ /key first <API_KEY>")
    addr = s.get("addr", "")
    if not addr:
        return bot.send_message(c, "❌ /set email email")
    r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} emails*\n\n"
        for x in data[:15]:
            t += f"`{x.get('_id','?')}` — {x.get('subject','—')}\n\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Empty")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/key <API_KEY>")
    elif a == "inbox":
        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key first")
        addr = s.get("addr", "")
        if not addr:
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} emails:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('_id','?')}` — {x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Empty", c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[MailSac] Starting...")
    bot.infinity_polling()
