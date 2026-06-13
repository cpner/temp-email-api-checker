#!/usr/bin/env python3
"""
TempMail.plus — Telegram Bot for Temporary Email (aiogram 2.x)
Provider: TempMail.plus
API: https://tempmail.plus/api/mails
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "https://tempmail.plus/api/mails"
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
        "*TempMail.plus*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
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
        return await bot.send_message(c, "❌ /set email email@domain.com")
    r = api_get(params={{"email": s["addr"]}})
    mails = r.get("mail", [])
    if not mails:
        return await bot.send_message(c, "📭 Empty")
    t = f"*{len(mails)} emails*\n\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    await bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    doms = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "aol.com", "zoho.com",
            "gmx.com", "mail.com", "yandex.com", "icloud.com", "1secmail.com", "mailinator.com"]
    t = "*Supported domains:*\n\n" + "\n".join(f"• `{d}`" for d in doms)
    await bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    await bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    await bot.send_message(m.chat.id, "/set <email> — Set\n/inbox — Check\n/domains — Domains\n/info — Info")


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
        r = api_get(params={{"email": s["addr"]}})
        mails = r.get("mail", [])
        if not mails:
            await bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = f"{len(mails)} emails:\n\n"
            for x in mails[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[TempMail.plus] Starting...")
    executor.start_polling(dp, skip_updates=True)
