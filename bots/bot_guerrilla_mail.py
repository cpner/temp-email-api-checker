#!/usr/bin/env python3
"""
Guerrilla Mail Telegram Bot
Полный API: создание, чтение, смена имени
API: api.guerrillamail.com
"""
import telebot
from telebot import types
import requests
import json
import random
import string
import time
import os
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BASE = "https://api.guerrillamail.com/ajax.php"

sessions = {}

def get_sess(cid):
    if cid not in sessions:
        sessions[cid] = {"seen": set(), "addr": None, "token": None, "key": None}
    return sessions[cid]


def api(action, **p):
    p["f"] = action
    try: return requests.get(BASE, params=p, timeout=15).json()
    except: return {{"error": "timeout"}}

def gen_name():
    return ''.join(random.choices(string.ascii_lowercase+string.digits, k=8))

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="gm_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="gm_inbox"))
    kb.add(types.InlineKeyboardButton("👤 Сменить имя", callback_data="gm_user"))
    kb.add(types.InlineKeyboardButton("📊 Статистика", callback_data="gm_stat"))
    kb.add(types.InlineKeyboardButton("❓ Помощь", callback_data="gm_help"))
    bot.send_message(m.chat.id, "🛡 *Guerrilla Mail Bot*\n\n/new — Создать\n/inbox — Письма\n/user <имя> — Имя\n/read <ID> — Прочитать", parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    cid = m.chat.id
    d = api("get_email_address", ip="127.0.0.1", agent="Mozilla")
    if "email_addr" in d:
        s = get_sess(cid)
        s.update(addr=d["email_addr"], token=d.get("sid_token"), seen=set())
        bot.send_message(cid, f"✅ `{d['email_addr']}`", parse_mode="Markdown")
    else: bot.send_message(cid, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    cid = m.chat.id
    s = get_sess(cid)
    if not s.get("token"): return bot.send_message(cid, "❌ /new")
    d = api("check_email", sid_token=s["token"], seq=0)
    msgs = d.get("list", [])
    if not msgs: return bot.send_message(cid, "📭 Пусто")
    txt = f"📬 *{len(msgs)} писем*\n\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        txt += f"{n}`{x.get('mail_id')}` | {x.get('mail_from','?')}\n📝 {x.get('mail_subject','—')}\n\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/read <ID>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api("fetch_email", sid_token=s["token"], email_id=parts[1])
    body = d.get("mail_body","")[:3500]
    bot.send_message(m.chat.id, f"📧 *{d.get('mail_subject','—')}*\nОт: {d.get('mail_from','?')}\n\n{body}", parse_mode="Markdown")

@bot.message_handler(commands=["user"])
def cmd_user(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/user <имя>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api("set_email_user", sid_token=s["token"], email_user=parts[1])
    if "email_addr" in d:
        s["addr"] = d["email_addr"]
        bot.send_message(m.chat.id, f"✅ `{d['email_addr']}`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("gm_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("gm_", "")

    if act == "new":
        d = api("get_email_address", ip="127.0.0.1", agent="Mozilla")
        if "email_addr" in d:
            s = get_sess(cid)
            s.update(addr=d["email_addr"], token=d.get("sid_token"), seen=set())
            bot.edit_message_text(f"✅ `{d['email_addr']}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api("check_email", sid_token=s["token"], seq=0)
        msgs = d.get("list", [])
        if not msgs: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(msgs)}:\n\n"
            for x in msgs[:10]: txt += f"`{x.get('mail_id')}` | {x.get('mail_from','?')}\n📝 {x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "user": bot.send_message(cid, "/user <имя>")
    elif act == "stat":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr','—')}", show_alert=True)
    elif act == "help": bot.send_message(cid, "/new\n/inbox\n/read <ID>\n/user <имя>")

if __name__ == "__main__":
    print("[Guerrilla Mail Bot] Running...")
    bot.infinity_polling()
