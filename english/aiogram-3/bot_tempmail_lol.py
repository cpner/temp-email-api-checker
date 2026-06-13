#!/usr/bin/env python3
"""
TempMail.lol — Telegram Bot for Temporary Email (aiogram 3.x)
Provider: TempMail.lol
API: https://api.tempmail.lol
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
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer(
        "*TempMail.lol*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
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
        await bot.send_message(c, "❌ Error")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return await bot.send_message(c, "❌ /new first")
    r = api_get(f"/auth/{s['token']}")
    emails = r.get("email", [])
    if not emails:
        return await bot.send_message(c, "📭 Empty")
    t = f"*{len(emails)} emails*\n\n"
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
            return await bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(f"/auth/{s['token']}")
        emails = r.get("email", [])
        if not emails:
            await bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = f"{len(emails)} emails:\n\n"
            for e in emails[:10]:
                txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


async def main():
    print("[TempMail.lol] Starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
