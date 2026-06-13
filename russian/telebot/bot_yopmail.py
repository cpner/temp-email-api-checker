#!/usr/bin/env python3
"""
YOPmail — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: YOPmail
API: https://yopmail.com
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_YOPMAIL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://yopmail.com"

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
        "*YOPmail*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["check"])
def cmd_check(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/check <имя>")
    bot.send_message(m.chat.id, f"📬 Ящик: https://yopmail.com/en/mailbox?id={p[1].strip()}")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    bot.send_message(m.chat.id, "*Домены YOPmail:*\n• yopmail.com\n• yopmail.fr\n• yopmail.gq\n• drdrb.com\n• c2.hu", parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/check <имя>")
    elif a == "inbox":
        bot.send_message(c, "📬 yopmail.com")
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[YOPmail] Запуск...")
    bot.infinity_polling()
