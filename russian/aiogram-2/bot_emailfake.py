#!/usr/bin/env python3
"""
EmailFake — Telegram-бот временной почты (aiogram 2.x)
Провайдер: EmailFake
API: https://emailfake.com/api/v1
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILFAKE", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "https://emailfake.com/api/v1"
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
        "*EmailFake*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    await bot.send_message(m.chat.id, f"✅ Мониторинг: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return await bot.send_message(c, "❌ /set email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} писем*\n\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
        await bot.send_message(c, t, parse_mode="Markdown")
    else:
        await bot.send_message(c, "📭 Пусто")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    await bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/set email@domain.com")
    elif a == "inbox":
        s = gs(c)
        if not s.get("addr"):
            return await bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/inbox/{s['addr']}")
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} писем:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)
        else:
            await bot.edit_message_text("📭 Пусто", c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        await call.answer(f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[EmailFake] Запуск...")
    executor.start_polling(dp, skip_updates=True)
