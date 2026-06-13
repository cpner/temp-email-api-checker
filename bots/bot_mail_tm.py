#!/usr/bin/env python3
"""
Mail.tm Telegram Bot
REST API: аккаунты, домены, чтение писем
API: api.mail.tm
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAIL_TM", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BASE = "https://api.mail.tm"

sessions = {}

def get_sess(cid):
    if cid not in sessions:
        sessions[cid] = {"seen": set(), "addr": None, "token": None, "key": None}
    return sessions[cid]


def api_domains():
    try: return requests.get(f"{BASE}/domains", timeout=10).json()
    except: return {{"error": "timeout"}}

def api_create(addr, pwd):
    try: return requests.post(f"{BASE}/accounts", json={"address": addr, "password": pwd}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_token(addr, pwd):
    try: return requests.post(f"{BASE}/token", json={"address": addr, "password": pwd}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_messages(tok):
    try: return requests.get(f"{BASE}/messages", headers={"Authorization": f"Bearer {tok}"}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_read(tok, mid):
    try: return requests.get(f"{BASE}/messages/{mid}", headers={"Authorization": f"Bearer {tok}"}, timeout=10).json()
    except: return {{"error": "timeout"}}

def gen_pwd():
    return ''.join(random.choices(string.ascii_letters+string.digits, k=16))

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="mt_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="mt_inbox"))
    kb.add(types.InlineKeyboardButton("🌐 Домены", callback_data="mt_domains"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="mt_info"))
    bot.send_message(m.chat.id, "📨 *Mail.tm Bot*\n\n/new — Создать\n/inbox — Письма\n/read <ID> — Прочитать\n/domains — Домены\n/login — Войти", parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    d = api_domains()
    doms = [x["domain"] for x in d.get("hydra:member", [])] if "hydra:member" in d else []
    if not doms: return bot.send_message(m.chat.id, "❌ Нет доменов")
    dom = random.choice(doms)
    name = ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))
    addr = f"{name}@{dom}"
    pwd = gen_pwd()
    r = api_create(addr, pwd)
    if "id" in r:
        tok = api_token(addr, pwd).get("token")
        s = get_sess(m.chat.id)
        s.update(addr=addr, token=tok, pwd=pwd, seen=set())
        bot.send_message(m.chat.id, f"✅ `{addr}`\n🔑 `{pwd}`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, f"❌ {r.get('detail','Ошибка')}")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_messages(s["token"])
    msgs = d.get("hydra:member", []) if isinstance(d, dict) else d if isinstance(d, list) else []
    if not msgs: return bot.send_message(m.chat.id, "📭 Пусто")
    txt = f"📬 *{len(msgs)} писем*\n\n"
    for x in msgs[:15]:
        fr = x.get("from", {}).get("address", "?") if isinstance(x.get("from"), dict) else "?"
        txt += f"`{x.get('id','?')}` | {fr}\n📝 {x.get('subject','—')}\n\n"
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/read <ID>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_read(s["token"], parts[1])
    body = d.get("text", "")[:3500]
    fr = d.get("from", {}).get("address", "?") if isinstance(d.get("from"), dict) else "?"
    bot.send_message(m.chat.id, f"📧 *{d.get('subject','—')}*\nОт: {fr}\n\n{body}", parse_mode="Markdown")

@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    d = api_domains()
    doms = d.get("hydra:member", []) if "hydra:member" in d else []
    txt = "🌐 *Домены:*\n" + "\n".join(f"• `{x['domain']}`" for x in doms[:20])
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["login"])
def cmd_login(m):
    parts = m.text.split(maxsplit=2)
    if len(parts)<3: return bot.send_message(m.chat.id, "/login email password")
    tok = api_token(parts[1], parts[2]).get("token")
    if tok:
        s = get_sess(m.chat.id)
        s.update(addr=parts[1], token=tok, seen=set())
        bot.send_message(m.chat.id, f"✅ Вход: `{parts[1]}`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, "❌ Неверные данные")

@bot.callback_query_handler(func=lambda c: c.data.startswith("mt_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("mt_", "")

    if act == "new":
        d = api_domains()
        doms = [x["domain"] for x in d.get("hydra:member",[])] if "hydra:member" in d else []
        if not doms: return bot.answer_callback_query(call.id, "❌ Нет доменов")
        dom = random.choice(doms)
        name = ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))
        addr = f"{name}@{dom}"
        pwd = gen_pwd()
        r = api_create(addr, pwd)
        if "id" in r:
            tok = api_token(addr, pwd).get("token")
            s = get_sess(cid)
            s.update(addr=addr, token=tok, pwd=pwd, seen=set())
            bot.edit_message_text(f"✅ `{addr}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api_messages(s["token"])
        msgs = d.get("hydra:member", []) if isinstance(d, dict) else d if isinstance(d, list) else []
        if not msgs: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(msgs)}:\n\n"
            for x in msgs[:10]:
                fr = x.get("from",{}).get("address","?") if isinstance(x.get("from"),dict) else "?"
                txt += f"`{x.get('id','?')}` | {fr}\n📝 {x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "domains":
        d = api_domains()
        doms = d.get("hydra:member",[]) if "hydra:member" in d else []
        bot.answer_callback_query(call.id, f"Доменов: {len(doms)}", show_alert=True)
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)

if __name__ == "__main__":
    print("[Mail.tm Bot] Running...")
    bot.infinity_polling()
