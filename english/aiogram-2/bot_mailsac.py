#!/usr/bin/env python3
"""
MailSac — Telegram Bot for Temporary Email (aiogram 2.x)
Provider: MailSac
API: https://mailsac.com/api
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILSAC", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "https://mailsac.com/api"
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
        "*MailSac*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["key"])
def cmd_key(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/key <API_KEY>")
    s = gs(m.chat.id)
    s["key"] = p[1].strip()
    await bot.send_message(m.chat.id, f"✅ Key: `{s['key'][:10]}...`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return await bot.send_message(m.chat.id, "❌ /key first <API_KEY>")
    r = api_get("/domains", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} доменов*\n\n" + "\n".join(f"• `{d}`" for d in data[:30])
        await bot.send_message(m.chat.id, t, parse_mode="Markdown")
    else:
        await bot.send_message(m.chat.id, "❌ No domains")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("key"):
        return await bot.send_message(c, "❌ /key first <API_KEY>")
    addr = s.get("addr", "")
    if not addr:
        return await bot.send_message(c, "❌ /set email email")
    r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} emails*\n\n"
        for x in data[:15]:
            t += f"`{x.get('_id','?')}` — {x.get('subject','—')}\n\n"
        await bot.send_message(c, t, parse_mode="Markdown")
    else:
        await bot.send_message(c, "📭 Empty")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        bot.send_message(c, "/key <API_KEY>")
    elif a == "inbox":
        s = gs(c)
        if not s.get("key"):
            return await bot.answer_callback_query(call.id, "❌ /key first")
        addr = s.get("addr", "")
        if not addr:
            return await bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} emails:\n\n"
            for x in data[:10]:
                txt += f"`{x.get('_id','?')}` — {x.get('subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)
        else:
            await bot.edit_message_text("📭 Empty", c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[MailSac] Starting...")
    executor.start_polling(dp, skip_updates=True)
