#!/usr/bin/env python3
"""
TempMail.lol — Telegram-бот временной почты (aiogram 3.x)
Провайдер: TempMail.lol
API: https://api.tempmail.lol
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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


@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Новая почта", callback_data="new"),
         InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Данные", callback_data="info"),
         InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])
    await m.answer(
        "*TempMail.lol*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get("/generate")
    if "address" in r:
        s.update(addr=r["address"], token=r.get("token"), seen=set())
        await bot.send_message(c, f"✅ `{r['address']}`\n🔑 `{str(r.get('token',''))[:20]}...`", parse_mode="Markdown")
    else:
        await bot.send_message(c, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return await bot.send_message(c, "❌ /new")
    r = api_get(f"/auth/{s['token']}")
    emails = r.get("email", [])
    if not emails:
        return await bot.send_message(c, "📭 Пусто")
    t = f"*{len(emails)} писем*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s["seen"] else ""
        s["seen"].add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    await bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    await bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n🔑 {str(s.get('token','—'))[:20]}...")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
        r = api_get("/generate")
        if "address" in r:
            s = gs(c)
            s.update(addr=r["address"], token=r.get("token"), seen=set())
            await bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id, parse_mode="Markdown")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
        s = gs(c)
        if not s.get("token"):
            return await bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s['token']}")
        emails = r.get("email", [])
        if not emails:
            await bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(emails)} писем:\n\n"
            for e in emails[:10]:
                txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


async def main():
    print("[TempMail.lol] Запуск...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
