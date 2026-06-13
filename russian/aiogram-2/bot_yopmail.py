#!/usr/bin/env python3
"""
YOPmail — Telegram-бот временной почты (aiogram 2.x)
Провайдер: YOPmail
API: https://yopmail.com
Установка: pip install aiogram==2.25.1 requests
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_YOPMAIL", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

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


@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await m.answer(
        "*YOPmail*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["check"])
def cmd_check(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/check <имя>")
    await bot.send_message(m.chat.id, f"📬 Ящик: https://yopmail.com/en/mailbox?id={p[1].strip()}")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    await bot.send_message(m.chat.id, "*Домены YOPmail:*\n• yopmail.com\n• yopmail.fr\n• yopmail.gq\n• drdrb.com\n• c2.hu", parse_mode="Markdown")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/check <имя>")
    elif a == "inbox":
        bot.send_message(c, "📬 yopmail.com")
    elif a == "info":
        s = gs(c)
        await call.answer(f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[YOPmail] Запуск...")
    executor.start_polling(dp, skip_updates=True)
