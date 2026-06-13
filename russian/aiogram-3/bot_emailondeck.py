#!/usr/bin/env python3
"""
EmailOnDeck — Telegram-бот временной почты (aiogram 3.x)
Провайдер: EmailOnDeck
API: https://api.emailondeck.com/v1
Установка: pip install "aiogram>=3.28.2" requests
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILONDECK", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE = "https://api.emailondeck.com/v1"
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
        [InlineKeyboardButton(text="📧 Новая почта", callback_data="new"),
         InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Данные", callback_data="info"),
         InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])
    await m.answer(
        "*EmailOnDeck*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m):
    await bot.send_message(m.chat.id, "*EmailOnDeck*\n\n🌐 emailondeck.com\nБыстрая одноразовая почта")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
        bot.send_message(c, "🌐 emailondeck.com")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
        bot.send_message(c, "🌐 emailondeck.com")

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


async def main():
    print("[EmailOnDeck] Запуск...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
