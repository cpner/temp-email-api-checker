#!/usr/bin/env python3
"""
AnonymBox — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: AnonymBox
API: https://api.anonymbox.com/v1
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_ANONYMBOX", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.anonymbox.com/v1"

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
        "*AnonymBox*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ Мониторинг: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return bot.send_message(c, "❌ /set email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} писем*\n\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Пусто")


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
            txt = f"{len(data)} писем:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[AnonymBox] Запуск...")
    bot.infinity_polling()
