#!/usr/bin/env python3
"""
10MinuteMail — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: 10MinuteMail
API: https://10minutemail.net/address.api.php
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_10MINUTEMAIL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://10minutemail.net/address.api.php"

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
        "*10MinuteMail*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get(params={{"new": 1}})
    if "address" in r:
        s.update(addr=r["address"], token=r.get("session_id", ""), seen=set(), ts=time.time())
        bot.send_message(c, f"✅ `{r['address']}`\n⏱ 10 минут", parse_mode="Markdown")
    else:
        bot.send_message(c, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new")
    el = time.time() - s.get("ts", time.time())
    if el > 600:
        return bot.send_message(c, "⏰ Истекло. /new")
    rem = 600 - int(el)
    r = api_get(params={{"sid": s["token"]}})
    msgs = r.get("messages", [])
    if not msgs:
        return bot.send_message(c, f"📭 Пусто ({rem}с)")
    t = f"*{len(msgs)} писем* ({rem}с)\n\n"
    for x in msgs[:15]:
        t += f"`{x.get('mail_id','?')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    el = time.time() - s.get("ts", time.time())
    rem = max(0, 600 - int(el))
    mn, sc = divmod(rem, 60)
    bot.send_message(m.chat.id, f"📧 {s.get('addr','—')}\n⏱ {mn}м {sc}с")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        r = api_get(params={{"new": 1}})
        if "address" in r:
            s = gs(c)
            s.update(addr=r["address"], token=r.get("session_id", ""), seen=set(), ts=time.time())
            bot.edit_message_text(f"✅ `{r['address']}` (10мин)", c, call.message.message_id, parse_mode="Markdown")
    elif a == "inbox":
        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        el = time.time() - s.get("ts", time.time())
        if el > 600:
            return bot.answer_callback_query(call.id, "⏰ Истекло!")
        rem = 600 - int(el)
        r = api_get(params={{"sid": s["token"]}})
        msgs = r.get("messages", [])
        if not msgs:
            bot.edit_message_text(f"📭 Пусто ({rem}с)", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем ({rem}с):\n\n"
            for x in msgs[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[10MinuteMail] Запуск...")
    bot.infinity_polling()
