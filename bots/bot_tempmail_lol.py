#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через TempMail.lol API
Генерация почты + чтение входящих по токену
"""

import telebot
from telebot import types
import requests
import json
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://api.tempmail.lol"

user_sessions = {}


def get_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "token": None,
            "address": None,
            "seen_ids": set(),
            "auto": False
        }
    return user_sessions[chat_id]


def api_generate():
    try:
        r = requests.get(f"{BASE_URL}/generate", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_get_messages(token):
    try:
        headers = {"Authorization": token}
        r = requests.get(f"{BASE_URL}/auth/{token}", headers=headers, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="tml_generate"),
        types.InlineKeyboardButton("📥 Проверить", callback_data="tml_inbox"),
        types.InlineKeyboardButton("🔄 Авто-обновление", callback_data="tml_auto"),
        types.InlineKeyboardButton("📋 Мои данные", callback_data="tml_info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="tml_help")
    )
    text = (
        "📬 *TempMail.lol Bot*\n\n"
        "Быстрая временная почта без регистрации\n\n"
        "/new — Создать почту\n"
        "/inbox — Проверить входящие\n"
        "/info — Данные почты\n"
        "/help — Справка"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["new"])
def cmd_new(msg):
    chat_id = msg.chat.id
    data = api_generate()
    if "address" in data:
        sess = get_session(chat_id)
        sess["token"] = data["token"]
        sess["address"] = data["address"]
        sess["seen_ids"] = set()
        text = (
            f"✅ *Почта создана!*\n\n"
            f"📧 Адрес: `{data['address']}`\n"
            f"🔑 Токен: `{data['token'][:20]}...`\n\n"
            f"Используйте адрес для регистраций.\n"
            f"Проверяйте письма: /inbox"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, f"❌ Ошибка: {data.get('error', 'Unknown')}")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("token"):
        bot.send_message(chat_id, "❌ Сначала создайте почту: /new")
        return
    data = api_get_messages(sess["token"])
    if "email" in data:
        emails = data["email"]
        if not emails:
            bot.send_message(chat_id, "📭 *Ящик пуст*", parse_mode="Markdown")
            return
        new_count = 0
        text = f"📬 *{len(emails)} писем:*\n\n"
        for e in emails:
            eid = e.get("id", "?")
            sender = e.get("from", "Unknown")
            subject = e.get("subject", "Без темы")
            is_new = eid not in sess["seen_ids"]
            marker = "🆕 " if is_new else ""
            if is_new:
                new_count += 1
                sess["seen_ids"].add(eid)
            text += f"{marker}🆔 `{eid}` | 👤 {sender}\n📝 {subject}\n\n"
        if new_count > 0:
            text += f"\n🆕 Новых: {new_count}"
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ Ошибка получения писем")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    sess = get_session(msg.chat.id)
    if not sess.get("token"):
        bot.send_message(msg.chat.id, "❌ Почта не создана")
        return
    text = (
        f"📋 *Данные почты*\n\n"
        f"📧 Адрес: `{sess['address']}`\n"
        f"🔑 Токен: `{sess['token']}`\n"
        f"🔄 Авто: {'да' if sess.get('auto') else 'нет'}\n"
        f"📩 Всего писем: {len(sess.get('seen_ids', []))}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "📬 *TempMail.lol Bot*\n\n"
        "/new — Создать почту\n"
        "/inbox — Проверить письма\n"
        "/info — Данные почты\n"
        "/help — Справка\n\n"
        "API: tempmail.lol (бесплатно)"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("tml_"))
def callback(call):
    chat_id = call.message.chat.id
    action = call.data.replace("tml_", "")

    if action == "generate":
        data = api_generate()
        if "address" in data:
            sess = get_session(chat_id)
            sess["token"] = data["token"]
            sess["address"] = data["address"]
            sess["seen_ids"] = set()
            text = f"✅ `{data['address']}`\n🔑 `{data['token'][:20]}...`"
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка")

    elif action == "inbox":
        sess = get_session(chat_id)
        if not sess.get("token"):
            bot.answer_callback_query(call.id, "❌ Сначала /new")
            return
        data = api_get_messages(sess["token"])
        if "email" in data:
            emails = data["email"]
            if not emails:
                bot.edit_message_text("📭 Пусто", chat_id, call.message.message_id)
            else:
                text = f"📬 *{len(emails)} писем:*\n\n"
                for e in emails[:15]:
                    text += f"🆔 `{e.get('id')}` | {e.get('from', '?')}\n📝 {e.get('subject', '—')}\n\n"
                bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown")

    elif action == "auto":
        sess = get_session(chat_id)
        sess["auto"] = not sess.get("auto", False)
        status = "вкл" if sess["auto"] else "выкл"
        bot.answer_callback_query(call.id, f"Авто: {status}")

    elif action == "info":
        sess = get_session(chat_id)
        if sess.get("address"):
            bot.answer_callback_query(call.id, sess["address"], show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Нет почты")

    elif action == "help":
        bot.send_message(chat_id, "/new — Создать\n/inbox — Проверить\n/info — Данные")


if __name__ == "__main__":
    print("[TempMail.lol Bot] Запуск...")
    bot.infinity_polling()
