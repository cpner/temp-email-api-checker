#!/usr/bin/env python3
"""
Mail.tm — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: Mail.tm
API: https://api.mail.tm
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAIL_TM", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.mail.tm"

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
        "*Mail.tm*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    r = api_get("/domains")
    doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
    if not doms:
        return bot.send_message(m.chat.id, "❌ No domains")
    t = f"*{len(doms)} доменов*\n\n" + "\n".join(f"• `{d}`" for d in doms[:30])
    bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get("/domains")
    doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
    if not doms:
        return bot.send_message(c, "❌ No domains")
    dom = random.choice(doms)
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    addr = f"{name}@{dom}"
    pwd = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    r = api_post("/accounts", {{"address": addr, "password": pwd}})
    if "id" in r:
        tok = api_post("/token", {{"address": addr, "password": pwd}}).get("token", "")
        s.update(addr=addr, token=tok, seen=set())
        bot.send_message(c, f"✅ `{addr}`\n🔑 `{pwd}`", parse_mode="Markdown")
    else:
        bot.send_message(c, f"❌ {r.get('detail', 'Ошибка')}")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new first")
    r = api_get("/messages", headers={{"Authorization": f"Bearer {{s['token']}}"}})
    msgs = r.get("hydra:member", []) if isinstance(r, dict) else []
    if not msgs:
        return bot.send_message(c, "📭 Empty")
    t = f"*{len(msgs)} emails*\n\n"
    for x in msgs[:15]:
        fr = x.get("from", {{}}).get("address", "?") if isinstance(x.get("from"), dict) else "?"
        t += f"`{x.get('id','?')}` — {fr}\n{x.get('subject','—')}\n\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["read"])
def cmd_read(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/read <ID>")
    s = gs(m.chat.id)
    if not s.get("token"):
        return bot.send_message(m.chat.id, "❌ /new first")
    r = api_get(f"/messages/{p[1]}", headers={{"Authorization": f"Bearer {{s['token']}}"}})
    body = r.get("text", "")[:3500]
    fr = r.get("from", {{}}).get("address", "?") if isinstance(r.get("from"), dict) else "?"
    bot.send_message(m.chat.id, f"*{r.get('subject','—')}*\nFrom: {fr}\n\n{body}", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, "/domains — Domains\n/new — Create\n/inbox — Check\n/read — Прочитать\n/info — Info")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        r = api_get("/domains")
        doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
        if not doms:
            return bot.answer_callback_query(call.id, "❌ No domains")
        dom = random.choice(doms)
        name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        addr = f"{name}@{dom}"
        pwd = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        r = api_post("/accounts", {{"address": addr, "password": pwd}})
        if "id" in r:
            tok = api_post("/token", {{"address": addr, "password": pwd}}).get("token", "")
            s = gs(c)
            s.update(addr=addr, token=tok, seen=set())
            bot.edit_message_text(f"✅ `{addr}`", c, call.message.message_id, parse_mode="Markdown")
    elif a == "inbox":
        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get("/messages", headers={{"Authorization": f"Bearer {{s['token']}}"}})
        msgs = r.get("hydra:member", []) if isinstance(r, dict) else []
        if not msgs:
            bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} emails:\n\n"
            for x in msgs[:10]:
                fr = x.get("from",{{}}).get("address","?") if isinstance(x.get("from"),dict) else "?"
                txt += f"`{x.get('id','?')}` — {fr}\n{x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[Mail.tm] Starting...")
    bot.infinity_polling()
