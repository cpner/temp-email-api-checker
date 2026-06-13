#!/usr/bin/env python3
"""
EmailNator — Telegram Bot for Temporary Email (aiogram 3.x)
Provider: EmailNator
API: https://www.emailnator.com
Install: pip install "aiogram>=3.28.2" requests
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILNATOR", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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


@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer(
        "*EmailNator*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m):
    await bot.send_message(m.chat.id, "*EmailNator*\n\n🌐 emailnator.com\nGenerator temporary почты")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
        bot.send_message(c, "🌐 emailnator.com")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
        bot.send_message(c, "🌐 emailnator.com")

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


async def main():
    print("[EmailNator] Starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
