#!/usr/bin/env python3
"""
AnonymBox — Telegram Bot for Temporary Email (aiogram 3.x)
Provider: AnonymBox
API: https://api.anonymbox.com/v1
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_ANONYMBOX", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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


@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer(
        "*AnonymBox*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    await bot.send_message(m.chat.id, f"✅ Monitoring: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return await bot.send_message(c, "❌ /set email email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} emails*\n\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
        await bot.send_message(c, t, parse_mode="Markdown")
    else:
        await bot.send_message(c, "📭 Empty")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    await bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
        bot.send_message(c, "/set email@domain.com")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
        s = gs(c)
        if not s.get("addr"):
            return await bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/inbox/{s['addr']}")
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} emails:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\n{x.get('subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)
        else:
            await bot.edit_message_text("📭 Empty", c, call.message.message_id)

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


async def main():
    print("[AnonymBox] Starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
