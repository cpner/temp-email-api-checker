#!/usr/bin/env python3
"""
EmailNator — Telegram Bot for Temporary Email (aiogram 2.x)
Provider: EmailNator
API: https://www.emailnator.com
Install: pip install aiogram==2.25.1 requests
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import random
import string
import time
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILNATOR", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "https://www.emailnator.com"
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


@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    await m.answer(
        "*EmailNator*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m):
    await bot.send_message(m.chat.id, "*EmailNator*\n\n🌐 emailnator.com\nGenerator temporary почты")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "🌐 emailnator.com")
    elif a == "inbox":
        bot.send_message(c, "🌐 emailnator.com")
    elif a == "info":
        s = gs(c)
        await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[EmailNator] Starting...")
    executor.start_polling(dp, skip_updates=True)
