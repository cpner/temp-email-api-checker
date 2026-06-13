#!/usr/bin/env python3
"""
TempMail.plus Telegram Bot
Мониторинг почты: gmail, yahoo, outlook, protonmail
API: tempmail.plus/api
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BASE = "https://tempmail.plus/api/mails"

sessions = {}

def get_sess(cid):
    if cid not in sessions:
        sessions[cid] = {"seen": set(), "addr": None, "token": None, "key": None}
    return sessions[cid]


def api_get_mails(email):
    try: return requests.get(BASE, params={"email": email}, timeout=10).json()
    except: return {{"error": "timeout"}}

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Установить", callback_data="tp_set"))
    kb.add(types.InlineKeyboardButton("📥 Проверить", callback_data="tp_inbox"))
    kb.add(types.InlineKeyboardButton("🔄 Авто", callback_data="tp_auto"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="tp_info"))
    bot.send_message(m.chat.id, "📬 *TempMail.plus Bot*\n\nМониторинг почты с любых доменов\n\n/set <email> — Установить\n/inbox — Проверить\n/auto — Авто-обновление", parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["set"])
def cmd_set(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/set email@domain.com")
    s = get_sess(m.chat.id)
    s["addr"] = parts[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ `{s['addr']}`", parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    cid = m.chat.id
    s = get_sess(cid)
    if not s.get("addr"): return bot.send_message(cid, "❌ /set email")
    d = api_get_mails(s["addr"])
    mails = d.get("mail", [])
    if not mails: return bot.send_message(cid, "📭 Пусто")
    txt = f"📬 *{len(mails)} писем*\n\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        txt += f"{n}`{x.get('mail_id')}` | {x.get('mail_from','?')}\n📝 {x.get('mail_subject','—')}\n\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = get_sess(m.chat.id)
    bot.send_message(m.chat.id, f"📧 `{s.get('addr','—')}`\n📩 {len(s.get('seen',[]))}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("tp_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("tp_", "")

    if act == "set": bot.send_message(cid, "/set email@domain.com")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("addr"): return bot.answer_callback_query(call.id, "❌ /set")
        d = api_get_mails(s["addr"])
        mails = d.get("mail", [])
        if not mails: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(mails)}:\n\n"
            for x in mails[:10]: txt += f"`{x.get('mail_id')}` | {x.get('mail_from','?')}\n📝 {x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "auto": bot.answer_callback_query(call.id, "Авто-обновление")
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)

if __name__ == "__main__":
    print("[TempMail.plus Bot] Running...")
    bot.infinity_polling()
