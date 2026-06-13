#!/usr/bin/env python3
"""
Guerrilla Mail — Telegram Bot for Temporary Email (aiogram 2.x)
Provider: Guerrilla Mail
API: https://api.guerrillamail.com/ajax.php
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

BOT_TOKEN = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "https://api.guerrillamail.com/ajax.php"
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
        "*Guerrilla Mail*\n\n/new — Create email\n/inbox — Check\n/set — Set email\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.update(addr=r["email_addr"], token=r.get("sid_token"), seen=set())
        await bot.send_message(c, f"✅ `{r['email_addr']}`", parse_mode="Markdown")
    else:
        await bot.send_message(c, "❌ Creation error")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return await bot.send_message(c, "❌ First run /new")
    r = api_get(params={{"f": "check_email", "sid_token": s["token"], "seq": 0}})
    msgs = r.get("list", [])
    if not msgs:
        return await bot.send_message(c, "📭 Empty")
    t = f"*{len(msgs)} emails*\n\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    await bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/set <имя_пользователя>")
    s = gs(m.chat.id)
    if not s.get("token"):
        return await bot.send_message(m.chat.id, "❌ First run /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s["token"], "email_user": p[1].strip()}})
    if "email_addr" in r:
        s["addr"] = r["email_addr"]
        await bot.send_message(m.chat.id, f"✅ `{r['email_addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    langs = ["en", "ru", "de", "fr", "es", "it", "pt", "ja", "zh"]
    t = "*Available languages:*\n" + "\n".join(f"• `{l}`" for l in langs)
    await bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["setlang"])
def cmd_setlang(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return await bot.send_message(m.chat.id, "/setlang <код>")
    r = api_get(params={{"f": "change_lang", "lang": p[1].strip()}})
    l = r.get("lang", p[1].strip())
    await bot.send_message(m.chat.id, f"✅ Language: `{l}`", parse_mode="Markdown")


@bot.message_handler(commands=["ip"])
def cmd_ip(m):
    r = api_get(params={{"f": "get_ip"}})
    ip = r.get("ip_addr", "?")
    await bot.send_message(m.chat.id, f"🌐 IP: `{ip}`", parse_mode="Markdown")


@bot.message_handler(commands=["lang"])
def cmd_lang(m):
    r = api_get(params={{"f": "get_lang"}})
    l = r.get("lang", "?")
    await bot.send_message(m.chat.id, f"🌐 Language: `{l}`", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    await bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    await bot.send_message(m.chat.id,
        "/new — Create\n/inbox — Check\n/set — name\n/domains — Languageи\n/setlang — Сменить язык\n/ip — IP\n/lang — Language\n/info — Info")


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = gs(c)
            s.update(addr=r["email_addr"], token=r.get("sid_token"), seen=set())
            await bot.edit_message_text(f"✅ `{r['email_addr']}`", c, call.message.message_id, parse_mode="Markdown")
        else:
            await bot.answer_callback_query(call.id, "❌ Error")
    elif a == "inbox":
        s = gs(c)
        if not s.get("token"):
            return await bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(params={{"f": "check_email", "sid_token": s["token"], "seq": 0}})
        msgs = r.get("list", [])
        if not msgs:
            await bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} emails:\n\n"
            for x in msgs[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            await bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        await call.answer(f"Email: {s.get('addr', 'Not set')}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Create\n/inbox — Check\n/set — Set\n/info — Info")


if __name__ == "__main__":
    print("[Guerrilla Mail] Starting...")
    executor.start_polling(dp, skip_updates=True)
