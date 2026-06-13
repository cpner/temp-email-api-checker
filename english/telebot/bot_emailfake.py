#!/usr/bin/env python3
"""
EmailFake — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: EmailFake
API: https://emailfake.com/api/v1
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILFAKE", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://emailfake.com/api/v1"

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
        "*EmailFake*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ Monitoring: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return bot.send_message(c, "❌ /set email email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} emails*\n\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Empty")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/set email@domain.com")
    elif a == "inbox":
        s = gs(c)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/inbox/{s['addr']}")
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} emails:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Empty", c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[EmailFake] Starting...")
    bot.infinity_polling()
