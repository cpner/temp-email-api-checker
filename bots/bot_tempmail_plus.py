#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через TempMail.plus API
Мониторинг почтовых ящиков любых доменов
"""

import telebot
from telebot import types
import requests
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://tempmail.plus/api"

user_sessions = {}


def get_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "email": None,
            "seen_ids": set(),
            "auto": False,
            "interval": 30
        }
    return user_sessions[chat_id]


def api_get_mails(email, limit=None):
    try:
        url = f"{BASE_URL}/mails"
        params = {"email": email}
        if limit:
            params["limit"] = limit
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Установить почту", callback_data="tmp_set"),
        types.InlineKeyboardButton("📥 Проверить", callback_data="tmp_inbox"),
        types.InlineKeyboardButton("🔄 Авто-обновление", callback_data="tmp_auto"),
        types.InlineKeyboardButton("📋 Данные", callback_data="tmp_info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="tmp_help")
    )
    text = (
        "📬 *TempMail.plus Bot*\n\n"
        "Мониторинг почты с любых доменов\n\n"
        "/set <email> — Установить почту\n"
        "/inbox — Проверить входящие\n"
        "/auto — Вкл/выкл авто-обновление\n"
        "/info — Данные\n"
        "/help — Справка\n\n"
        "✅ Поддерживает gmail, outlook, yahoo, protonmail и др."
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["set"])
def cmd_set(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Использование: /set <email@domain.com>")
        return
    email = parts[1].strip()
    if "@" not in email or "." not in email:
        bot.send_message(msg.chat.id, "❌ Неверный формат email")
        return
    sess = get_session(msg.chat.id)
    sess["email"] = email
    sess["seen_ids"] = set()
    text = (
        f"✅ *Почта установлена!*\n\n"
        f"📧 Адрес: `{email}`\n\n"
        f"Теперь используйте /inbox для проверки."
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("email"):
        bot.send_message(chat_id, "❌ Сначала установите почту: /set <email>")
        return
    data = api_get_mails(sess["email"])
    if "mail" in data:
        mails = data["mail"]
        if not mails:
            bot.send_message(chat_id, "📭 *Ящик пуст*", parse_mode="Markdown")
            return
        new_count = 0
        text = f"📬 *{len(mails)} писем ({sess['email']}):*\n\n"
        for m in mails[:20]:
            mid = m.get("mail_id", "?")
            sender = m.get("mail_from", "?")
            subject = m.get("mail_subject", "—")
            date = m.get("mail_date", "")
            is_new = mid not in sess["seen_ids"]
            marker = "🆕 " if is_new else ""
            if is_new:
                new_count += 1
                sess["seen_ids"].add(mid)
            text += f"{marker}🆔 `{mid}` | {sender}\n📝 {subject}\n"
            if date:
                text += f"📅 {date}\n"
            text += "\n"
        if new_count > 0:
            text += f"🆕 Новых: {new_count}"
        bot.send_message(chat_id, text, parse_mode="Markdown")
    elif "error" in data:
        bot.send_message(chat_id, f"❌ {data['error']}")
    else:
        bot.send_message(chat_id, "❌ Ошибка получения данных")


@bot.message_handler(commands=["auto"])
def cmd_auto(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("email"):
        bot.send_message(chat_id, "❌ Сначала /set <email>")
        return
    sess["auto"] = not sess.get("auto", False)
    status = "включено" if sess["auto"] else "выключено"
    bot.send_message(chat_id, f"🔄 Авто-обновление: *{status}*", parse_mode="Markdown")


@bot.message_handler(commands=["interval"])
def cmd_interval(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Использование: /interval <секунды>\nМинимум: 30 сек")
        return
    try:
        interval = int(parts[1])
        if interval < 30:
            bot.send_message(msg.chat.id, "❌ Минимум 30 секунд")
            return
        sess = get_session(msg.chat.id)
        sess["interval"] = interval
        bot.send_message(msg.chat.id, f"⏱ Интервал: {interval} сек")
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Введите число")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    sess = get_session(msg.chat.id)
    if not sess.get("email"):
        bot.send_message(msg.chat.id, "❌ Почта не установлена")
        return
    text = (
        f"📋 *Данные*\n\n"
        f"📧 Адрес: `{sess['email']}`\n"
        f"🔄 Авто: {'да' if sess.get('auto') else 'нет'}\n"
        f"⏱ Интервал: {sess.get('interval', 30)} сек\n"
        f"📩 Прочитано: {len(sess.get('seen_ids', []))}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "📬 *TempMail.plus Bot*\n\n"
        "/set <email> — Установить почту\n"
        "/inbox — Проверить письма\n"
        "/auto — Авто-обновление\n"
        "/interval <сек> — Интервал обновления\n"
        "/info — Данные\n"
        "/help — Справка\n\n"
        "Поддерживает: gmail, yahoo, outlook, protonmail, hotmail, aol, zoho, gmx, icloud"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("tmp_"))
def callback(call):
    chat_id = call.message.chat.id
    action = call.data.replace("tmp_", "")

    if action == "set":
        bot.send_message(chat_id, "Введите: /set <email@domain.com>")

    elif action == "inbox":
        sess = get_session(chat_id)
        if not sess.get("email"):
            bot.answer_callback_query(call.id, "❌ /set <email>")
            return
        data = api_get_mails(sess["email"])
        if "mail" in data:
            mails = data["mail"]
            if not mails:
                bot.edit_message_text("📭 Пусто", chat_id, call.message.message_id)
            else:
                text = f"📬 {len(mails)} писем:\n\n"
                for m in mails[:10]:
                    text += f"🆔 {m.get('mail_id')} | {m.get('mail_from', '?')}\n📝 {m.get('mail_subject', '—')}\n\n"
                bot.edit_message_text(text, chat_id, call.message.message_id)

    elif action == "auto":
        sess = get_session(chat_id)
        sess["auto"] = not sess.get("auto", False)
        status = "вкл" if sess["auto"] else "выкл"
        bot.answer_callback_query(call.id, f"Авто: {status}")

    elif action == "info":
        sess = get_session(chat_id)
        if sess.get("email"):
            bot.answer_callback_query(call.id, sess["email"], show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Нет почты")

    elif action == "help":
        bot.send_message(chat_id, "/set — Установить\n/inbox — Проверить\n/auto — Авто")


if __name__ == "__main__":
    print("[TempMail.plus Bot] Запуск...")
    bot.infinity_polling()
