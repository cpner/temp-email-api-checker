#!/usr/bin/env python3
"""
Guerrilla Mail — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: Guerrilla Mail
API: https://api.guerrillamail.com/ajax.php
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_GUERRILLA", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
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


@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        types.InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Данные", callback_data="info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*Guerrilla Mail*\n\n/new — Создать почту\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.update(addr=r["email_addr"], token=r.get("sid_token"), seen=set())
        bot.send_message(c, f"✅ `{r['email_addr']}`", parse_mode="Markdown")
    else:
        bot.send_message(c, "❌ Ошибка создания")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ Сначала /new")
    r = api_get(params={{"f": "check_email", "sid_token": s["token"], "seq": 0}})
    msgs = r.get("list", [])
    if not msgs:
        return bot.send_message(c, "📭 Пусто")
    t = f"*{len(msgs)} писем*\n\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set <имя_пользователя>")
    s = gs(m.chat.id)
    if not s.get("token"):
        return bot.send_message(m.chat.id, "❌ Сначала /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s["token"], "email_user": p[1].strip()}})
    if "email_addr" in r:
        s["addr"] = r["email_addr"]
        bot.send_message(m.chat.id, f"✅ `{r['email_addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    langs = ["en", "ru", "de", "fr", "es", "it", "pt", "ja", "zh"]
    t = "*Доступные языки:*\n" + "\n".join(f"• `{l}`" for l in langs)
    bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["setlang"])
def cmd_setlang(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/setlang <код>")
    r = api_get(params={{"f": "change_lang", "lang": p[1].strip()}})
    l = r.get("lang", p[1].strip())
    bot.send_message(m.chat.id, f"✅ Язык: `{l}`", parse_mode="Markdown")


@bot.message_handler(commands=["ip"])
def cmd_ip(m):
    r = api_get(params={{"f": "get_ip"}})
    ip = r.get("ip_addr", "?")
    bot.send_message(m.chat.id, f"🌐 IP: `{ip}`", parse_mode="Markdown")


@bot.message_handler(commands=["lang"])
def cmd_lang(m):
    r = api_get(params={{"f": "get_lang"}})
    l = r.get("lang", "?")
    bot.send_message(m.chat.id, f"🌐 Язык: `{l}`", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id,
        "/new — Создать\n/inbox — Проверить\n/set — Имя\n/domains — Языки\n/setlang — Сменить язык\n/ip — IP\n/lang — Язык\n/info — Данные")


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = gs(c)
            s.update(addr=r["email_addr"], token=r.get("sid_token"), seen=set())
            bot.edit_message_text(f"✅ `{r['email_addr']}`", c, call.message.message_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка")
    elif a == "inbox":
        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(params={{"f": "check_email", "sid_token": s["token"], "seq": 0}})
        msgs = r.get("list", [])
        if not msgs:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем:\n\n"
            for x in msgs[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(txt, c, call.message.message_id)
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr', 'Не установлена')}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")


if __name__ == "__main__":
    print("[Guerrilla Mail] Запуск...")
    bot.infinity_polling()
