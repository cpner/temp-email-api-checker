#!/usr/bin/env python3
"""
TempMail.lol — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: TempMail.lol
API: https://api.tempmail.lol
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.tempmail.lol"

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
        types.InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        types.InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Данные", callback_data="info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*TempMail.lol*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get("/generate")
    if "address" in r:
        s.update(addr=r["address"], token=r.get("token"), seen=set())
        bot.send_message(c, f"✅ `{r['address']}`\n🔑 `{str(r.get('token',''))[:20]}...`", parse_mode="Markdown")
    else:
        bot.send_message(c, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new")
    r = api_get(f"/auth/{s['token']}")
    emails = r.get("email", [])
    if not emails:
        return bot.send_message(c, "📭 Пусто")
    t = f"*{len(emails)} писем*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s["seen"] else ""
        s["seen"].add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n🔑 {str(s.get('token','—'))[:20]}...")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        r = api_get("/generate")
        if "address" in r:
            s = gs(c)
            s.update(addr=r["address"], token=r.get("token"), seen=set())
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id, parse_mode="Markdown")
    elif a == "inbox":
        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s['token']}")
        emails = r.get("email", [])
        if not emails:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(emails)} писем:\n\n"
            for e in emails[:10]:
                txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[TempMail.lol] Запуск...")
    bot.infinity_polling()
