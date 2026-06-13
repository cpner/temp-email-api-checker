#!/usr/bin/env python3
"""
Burner.kiwi — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: Burner.kiwi
API: https://burner.kiwi
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_BURNER", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://burner.kiwi"

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
        "*Burner.kiwi*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info\n/help — Help",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "*Burner.kiwi*\n\n🌐 burner.kiwi\n⏱ 24 hours", parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "🌐 burner.kiwi")
    elif a == "inbox":
        bot.send_message(c, "🌐 burner.kiwi")
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[Burner.kiwi] Starting...")
    bot.infinity_polling()
