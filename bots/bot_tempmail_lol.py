#!/usr/bin/env python3
"""
TempMail.lol Telegram Bot
Генерация почты + чтение по токену
API: api.tempmail.lol
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BASE = "https://api.tempmail.lol"

sessions = {}

def get_sess(cid):
    if cid not in sessions:
        sessions[cid] = {"seen": set(), "addr": None, "token": None, "key": None}
    return sessions[cid]


def api_generate():
    try: return requests.get(f"{BASE}/generate", timeout=10).json()
    except: return {{"error": "timeout"}}

def api_get_messages(token):
    try: return requests.get(f"{BASE}/auth/{token}", timeout=10).json()
    except: return {{"error": "timeout"}}

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="tl_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="tl_inbox"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="tl_info"))
    bot.send_message(m.chat.id, "📬 *TempMail.lol Bot*\n\n/new — Создать\n/inbox — Письма\n/info — Данные", parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    d = api_generate()
    if "address" in d:
        s = get_sess(m.chat.id)
        s.update(addr=d["address"], token=d["token"], seen=set())
        bot.send_message(m.chat.id, f"✅ `{d['address']}`\n🔑 `{d['token'][:20]}...`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_get_messages(s["token"])
    emails = d.get("email", [])
    if not emails: return bot.send_message(m.chat.id, "📭 Пусто")
    txt = f"📬 *{len(emails)} писем*\n\n"
    for x in emails[:15]:
        n = "🆕 " if x.get("id") not in s["seen"] else ""
        s["seen"].add(x.get("id"))
        txt += f"{n}`{x.get('id')}` | {x.get('from','?')}\n📝 {x.get('subject','—')}\n\n"
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = get_sess(m.chat.id)
    bot.send_message(m.chat.id, f"📧 `{s.get('addr','—')}`\n🔑 `{str(s.get('token','—'))[:20]}...`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("tl_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("tl_", "")

    if act == "new":
        d = api_generate()
        if "address" in d:
            s = get_sess(cid)
            s.update(addr=d["address"], token=d["token"], seen=set())
            bot.edit_message_text(f"✅ `{d['address']}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api_get_messages(s["token"])
        emails = d.get("email", [])
        if not emails: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(emails)}:\n\n"
            for x in emails[:10]: txt += f"`{x.get('id')}` | {x.get('from','?')}\n📝 {x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)

if __name__ == "__main__":
    print("[TempMail.lol Bot] Running...")
    bot.infinity_polling()
