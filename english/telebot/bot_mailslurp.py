#!/usr/bin/env python3
"""
MailSlurp — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: MailSlurp
API: https://api.mailslurp.com
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILSLURP", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.mailslurp.com"

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
        "*MailSlurp*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
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
        return bot.send_message(m.chat.id, "❌ /key first")
    r = api_get("/domains", headers={{"x-api-key": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} доменов*\n\n" + "\n".join(f"• `{d}`" for d in data[:30])
        bot.send_message(m.chat.id, t, parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ No domains")


@bot.message_handler(commands=["new"])
def cmd_new(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key first")
    r = api_post("/inboxes", {{}}, headers={{"x-api-key": s["key"]}})
    if "id" in r:
        s.update(addr=r.get("emailAddress", ""), token=r.get("id"))
        bot.send_message(m.chat.id, f"✅ `{r.get('emailAddress','?')}`", parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ Error")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key first")
    r = api_get("/inboxes?page=0&size=20", headers={{"x-api-key": s["key"]}})
    ibs = r.get("content", []) if isinstance(r, dict) else []
    if not ibs:
        return bot.send_message(m.chat.id, "📭 No inboxes")
    t = f"*{len(ibs)} inboxes*\n\n"
    for x in ibs[:15]:
        t += f"`{x.get('id','?')[:12]}...` — {x.get('emailAddress','?')}\n"
    bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key")
        r = api_post("/inboxes", {{}}, headers={{"x-api-key": s["key"]}})
        if "id" in r:
            s.update(addr=r.get("emailAddress", ""), token=r.get("id"))
            bot.edit_message_text(f"✅ `{r.get('emailAddress','?')}`", c, call.message.message_id, parse_mode="Markdown")
    elif a == "inbox":
        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key first")
        r = api_get("/inboxes?page=0&size=20", headers={{"x-api-key": s["key"]}})
        ibs = r.get("content", []) if isinstance(r, dict) else []
        if not ibs:
            bot.edit_message_text("📭 No inboxes", c, call.message.message_id)
        else:
            txt = f"{len(ibs)} inboxes:\n\n"
            for x in ibs[:10]:
                txt += f"`{x.get('id','?')[:12]}...` — {x.get('emailAddress','?')}\n"
            bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[MailSlurp] Starting...")
    bot.infinity_polling()
