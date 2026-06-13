#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через AnonymBox API
Анонимная почта без регистрации
"""

import telebot
from telebot import types
import requests
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://api.anonymbox.com/v1"

user_sessions = {}


def get_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "email": None,
            "seen_ids": set()
        }
    return user_sessions[chat_id]


def api_get_inbox(email):
    try:
        r = requests.get(f"{BASE_URL}/inbox/{email}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Установить почту", callback_data="ab_set"),
        types.InlineKeyboardButton("📥 Проверить", callback_data="ab_inbox"),
        types.InlineKeyboardButton("📋 Данные", callback_data="ab_info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="ab_help")
    )
    text = (
        "🔒 *AnonymBox Bot*\n\n"
        "Анонимная временная почта\n\n"
        "/set <email> — Установить почту\n"
        "/inbox — Проверить входящие\n"
        "/info — Данные\n"
        "/help — Справка"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["set"])
def cmd_set(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Использование: /set <email>")
        return
    email = parts[1].strip()
    sess = get_session(msg.chat.id)
    sess["email"] = email
    sess["seen_ids"] = set()
    bot.send_message(msg.chat.id, f"✅ Почта: `{email}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("email"):
        bot.send_message(chat_id, "❌ Сначала: /set <email>")
        return
    data = api_get_inbox(sess["email"])
    if isinstance(data, list):
        if not data:
            bot.send_message(chat_id, "📭 Ящик пуст")
            return
        text = f"📬 *{len(data)} писем:*\n\n"
        for m in data[:15]:
            mid = m.get("id", "?")
            sender = m.get("from", "?")
            subject = m.get("subject", "—")
            text += f"🆔 `{mid}` | {sender}\n📝 {subject}\n\n"
        bot.send_message(chat_id, text, parse_mode="Markdown")
    elif isinstance(data, dict) and "error" in data:
        bot.send_message(chat_id, f"❌ {data['error']}")
    else:
        bot.send_message(chat_id, "❌ Нет данных")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    sess = get_session(msg.chat.id)
    if not sess.get("email"):
        bot.send_message(msg.chat.id, "❌ Почта не установлена")
        return
    text = (
        f"📋 *Данные*\n\n"
        f"📧 Адрес: `{sess['email']}`\n"
        f"📩 Прочитано: {len(sess.get('seen_ids', []))}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "🔒 *AnonymBox Bot*\n\n"
        "/set <email> — Установить почту\n"
        "/inbox — Проверить\n"
        "/info — Данные\n\n"
        "API: anonymbox.com (бесплатно)"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("ab_"))
def callback(call):
    chat_id = call.message.chat.id
    action = call.data.replace("ab_", "")

    if action == "set":
        bot.send_message(chat_id, "Введите: /set <email>")

    elif action == "inbox":
        sess = get_session(chat_id)
        if not sess.get("email"):
            bot.answer_callback_query(call.id, "❌ /set <email>")
            return
        data = api_get_inbox(sess["email"])
        if isinstance(data, list) and data:
            text = f"📬 {len(data)} писем:\n\n"
            for m in data[:10]:
                text += f"🆔 {m.get('id')} | {m.get('from', '?')}\n📝 {m.get('subject', '—')}\n\n"
            bot.edit_message_text(text, chat_id, call.message.message_id)
        else:
            bot.edit_message_text("📭 Пусто", chat_id, call.message.message_id)

    elif action == "info":
        sess = get_session(chat_id)
        if sess.get("email"):
            bot.answer_callback_query(call.id, sess["email"], show_alert=True)

    elif action == "help":
        bot.send_message(chat_id, "/set — Установить\n/inbox — Проверить")


if __name__ == "__main__":
    print("[AnonymBox Bot] Запуск...")
    bot.infinity_polling()
