#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через 10 Minute Mail API
Быстрая почта с автоматическим удалением через 10 минут
"""

import telebot
from telebot import types
import requests
import re
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://10minutemail.net"

user_sessions = {}


def get_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "address": None,
            "session_id": None,
            "seen_ids": set(),
            "created_at": None
        }
    return user_sessions[chat_id]


def api_generate():
    try:
        r = requests.get(f"{BASE_URL}/address.api.php?new=1", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_get_messages(session_id):
    try:
        r = requests.get(
            f"{BASE_URL}/address.api.php?sid={session_id}",
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="tm10_new"),
        types.InlineKeyboardButton("📥 Проверить", callback_data="tm10_inbox"),
        types.InlineKeyboardButton("⏱ Осталось", callback_data="tm10_time"),
        types.InlineKeyboardButton("📋 Данные", callback_data="tm10_info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="tm10_help")
    )
    text = (
        "⏰ *10 Minute Mail Bot*\n\n"
        "Временная почта на 10 минут\n\n"
        "/new — Создать почту\n"
        "/inbox — Проверить входящие\n"
        "/info — Данные и время\n"
        "/help — Справка\n\n"
        "⚠️ Почта автоматически удаляется через 10 минут!"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["new"])
def cmd_new(msg):
    chat_id = msg.chat.id
    data = api_generate()
    if "address" in data:
        sess = get_session(chat_id)
        sess["address"] = data["address"]
        sess["session_id"] = data.get("session_id", "")
        sess["seen_ids"] = set()
        sess["created_at"] = time.time()
        timer = data.get("timer", 600)
        minutes = int(timer) // 60
        text = (
            f"✅ *Почта создана!*\n\n"
            f"📧 Адрес: `{data['address']}`\n"
            f"⏱ Время жизни: *{minutes} мин*\n\n"
            f"Используйте адрес, пока он активен!"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ Ошибка создания почты")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("session_id"):
        bot.send_message(chat_id, "❌ Сначала создайте почту: /new")
        return
    elapsed = time.time() - sess.get("created_at", time.time())
    if elapsed > 600:
        bot.send_message(chat_id, "⏰ *Время почты истекло!*\nСоздайте новую: /new", parse_mode="Markdown")
        return
    remaining = 600 - int(elapsed)
    data = api_get_messages(sess["session_id"])
    if "messages" in data:
        messages = data["messages"]
        if not messages:
            bot.send_message(chat_id, f"📭 Ящик пуст (⏱ {remaining} сек)")
            return
        text = f"📬 *{len(messages)} писем* (⏱ {remaining} сек)\n\n"
        for m in messages[:15]:
            mid = m.get("mail_id", "?")
            sender = m.get("mail_from", "?")
            subject = m.get("mail_subject", "—")
            text += f"🆔 `{mid}` | {sender}\n📝 {subject}\n\n"
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ Ошибка получения писем")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    sess = get_session(msg.chat.id)
    if not sess.get("address"):
        bot.send_message(msg.chat.id, "❌ Почта не создана")
        return
    elapsed = time.time() - sess.get("created_at", time.time())
    remaining = max(0, 600 - int(elapsed))
    minutes = remaining // 60
    seconds = remaining % 60
    text = (
        f"📋 *Данные*\n\n"
        f"📧 Адрес: `{sess['address']}`\n"
        f"⏱ Осталось: *{minutes}м {seconds}с*\n"
        f"📩 Прочитано: {len(sess.get('seen_ids', []))}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "⏰ *10 Minute Mail Bot*\n\n"
        "/new — Создать почту (10 мин)\n"
        "/inbox — Проверить письма\n"
        "/info — Данные и время\n"
        "/help — Справка\n\n"
        "API: 10minutemail.net (бесплатно)"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("tm10_"))
def callback(call):
    chat_id = call.message.chat.id
    action = call.data.replace("tm10_", "")

    if action == "new":
        data = api_generate()
        if "address" in data:
            sess = get_session(chat_id)
            sess["address"] = data["address"]
            sess["session_id"] = data.get("session_id", "")
            sess["seen_ids"] = set()
            sess["created_at"] = time.time()
            bot.edit_message_text(
                f"✅ `{data['address']}`\n⏱ {data.get('timer', 600) // 60} мин",
                chat_id, call.message.message_id, parse_mode="Markdown"
            )

    elif action == "inbox":
        sess = get_session(chat_id)
        if not sess.get("session_id"):
            bot.answer_callback_query(call.id, "❌ /new")
            return
        elapsed = time.time() - sess.get("created_at", time.time())
        if elapsed > 600:
            bot.answer_callback_query(call.id, "⏰ Время истекло!")
            return
        data = api_get_messages(sess["session_id"])
        if "messages" in data:
            msgs = data["messages"]
            if not msgs:
                bot.edit_message_text("📭 Пусто", chat_id, call.message.message_id)
            else:
                text = f"📬 {len(msgs)} писем:\n\n"
                for m in msgs[:10]:
                    text += f"🆔 {m.get('mail_id')} | {m.get('mail_from', '?')}\n📝 {m.get('mail_subject', '—')}\n\n"
                bot.edit_message_text(text, chat_id, call.message.message_id)

    elif action == "time":
        sess = get_session(chat_id)
        if sess.get("created_at"):
            elapsed = time.time() - sess["created_at"]
            remaining = max(0, 600 - int(elapsed))
            m, s = divmod(remaining, 60)
            bot.answer_callback_query(call.id, f"Осталось: {m}м {s}с", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Нет активной почты")

    elif action == "info":
        sess = get_session(chat_id)
        if sess.get("address"):
            bot.answer_callback_query(call.id, sess["address"], show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Нет почты")

    elif action == "help":
        bot.send_message(chat_id, "/new — Создать\n/inbox — Проверить\n/info — Данные")


if __name__ == "__main__":
    print("[10MinuteMail Bot] Запуск...")
    bot.infinity_polling()
