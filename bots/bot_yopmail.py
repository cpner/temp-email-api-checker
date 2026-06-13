#!/usr/bin/env python3
"""
YOPmail Telegram Bot
Многодоменный
API: https://yopmail.com
"""
import telebot
from telebot import types
import requests
import random
import string
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN_YOPMAIL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://yopmail.com"

sessions = {}


def gs(cid):
    if cid not in sessions:
        sessions[cid] = {"seen": set(), "addr": None, "token": None, "key": None}
    return sessions[cid]


def api_get(path, **kw):
    try:
        return requests.get(f"{BASE}/{path}", timeout=10, **kw).json()
    except Exception:
        return {"error": "timeout"}


def api_post(path, data=None, **kw):
    try:
        return requests.post(f"{BASE}/{path}", json=data, timeout=10, **kw).json()
    except Exception:
        return {"error": "timeout"}


@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="yp_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="yp_inbox"))
    kb.add(types.InlineKeyboardButton("🔑 Ключ", callback_data="yp_key"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="yp_info"))
    kb.add(types.InlineKeyboardButton("❓ Помощь", callback_data="yp_help"))
    text = (
        "📧 *YOPmail Bot*\n"
        "Многодоменный\n\n"
        "/new — Создать почту\n"
        "/set <email> — Установить\n"
        "/inbox — Проверить\n"
        "/key <API_KEY> — Установить ключ\n"
        "/info — Данные"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    s = gs(m.chat.id)
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    addr = f"{rnd}@yopmail.com"
    s.update(addr=addr, seen=set())
    bot.send_message(m.chat.id, f"✅ `{addr}`", parse_mode="Markdown")


@bot.message_handler(commands=["set"])
def cmd_set(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = parts[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = gs(m.chat.id)
    if not s.get("addr"):
        return bot.send_message(m.chat.id, "❌ /new или /set email")
    try:
        r = requests.get(f"{BASE}/inbox/{s['addr']}", timeout=10)
        if r.ok:
            ct = r.headers.get("content-type", "")
            data = r.json() if "json" in ct else []
            if isinstance(data, list) and data:
                txt = f"📬 *{len(data)} писем*\n\n"
                for x in data[:15]:
                    nid = x.get("id", "?")
                    new = "🆕 " if nid not in s["seen"] else ""
                    s["seen"].add(nid)
                    txt += f"{new}`{nid}` | {x.get("from", "?")}\n📝 {x.get("subject", "—")}\n\n"
                bot.send_message(m.chat.id, txt, parse_mode="Markdown")
            else:
                bot.send_message(m.chat.id, "📭 Пусто")
        else:
            bot.send_message(m.chat.id, "📭 Пусто или ошибка")
    except Exception:
        bot.send_message(m.chat.id, "❌ Сервис недоступен")


@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/read <ID>")
    s = gs(m.chat.id)
    if not s.get("addr"):
        return bot.send_message(m.chat.id, "❌ /new")
    try:
        r = requests.get(f"{BASE}/inbox/{s['addr']}/{parts[1]}", timeout=10)
        if r.ok:
            d = r.json() if "json" in r.headers.get("content-type", "") else {}
            body = d.get("text", d.get("html", "Нет содержимого"))[:3500]
            bot.send_message(m.chat.id, f"📧 *Письмо*\n\n{body}", parse_mode="Markdown")
        else:
            bot.send_message(m.chat.id, "❌ Не найдено")
    except Exception:
        bot.send_message(m.chat.id, "❌ Ошибка")


@bot.message_handler(commands=["key"])
def cmd_key(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/key YOUR_API_KEY")
    s = gs(m.chat.id)
    s["key"] = parts[1].strip()
    bot.send_message(m.chat.id, f"✅ Ключ установлен: `{s['key'][:10]}...`", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    txt = (
        f"📋 *Данные*\n\n"
        f"📧 Адрес: `{s.get('addr', '—')}`\n"
        f"🔑 Ключ: `{str(s.get('key', '—'))[:10]}...`\n"
        f"📩 Прочитано: {len(s.get('seen', []))}"
    )
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    text = (
        "📧 *YOPmail Bot*\n\n"
        "/new — Создать\n"
        "/set <email> — Установить\n"
        "/inbox — Проверить\n"
        "/read <ID> — Прочитать\n"
        "/key <KEY> — API ключ\n"
        "/info — Данные"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: c.data.startswith("yp_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("yp_", "")

    if act == "new":
        s = gs(cid)
        rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        addr = f"{rnd}@yopmail.com"
        s.update(addr=addr, seen=set())
        bot.edit_message_text(f"✅ `{addr}`", cid, call.message.message_id, parse_mode="Markdown")

    elif act == "inbox":
        s = gs(cid)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /new")
        try:
            r = requests.get(f"{BASE}/inbox/{s['addr']}", timeout=10)
            ct = r.headers.get("content-type", "")
            data = r.json() if r.ok and "json" in ct else []
            if isinstance(data, list) and data:
                txt = f"📬 {len(data)} писем:\n\n"
                for x in data[:10]:
                    txt += f"`{x.get('id','?')}` | {x.get('from','?')}\n📝 {x.get('subject','—')}\n\n"
                bot.edit_message_text(txt, cid, call.message.message_id)
            else:
                bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        except Exception:
            bot.edit_message_text("❌ Ошибка", cid, call.message.message_id)

    elif act == "key":
        bot.send_message(cid, "/key YOUR_API_KEY")

    elif act == "info":
        s = gs(cid)
        bot.answer_callback_query(call.id, s.get("addr", "—"), show_alert=True)

    elif act == "help":
        bot.send_message(cid, "/new\n/inbox\n/info")


if __name__ == "__main__":
    print("[YOPmail Bot] Running...")
    bot.infinity_polling()
