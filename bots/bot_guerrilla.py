#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через Guerrilla Mail API
Полностью рабочий API без ключей и регистрации
"""

import telebot
from telebot import types
import requests
import json
import hashlib
import string
import random
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://api.guerrillamail.com/ajax.php"

user_sessions = {}
user_stats = {}


def guerrilla_request(action, **params):
    params["f"] = action
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_user_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "sid_token": None,
            "email": None,
            "email_addr": None,
            "seq": 0,
            "messages": [],
            "auto_refresh": False
        }
    return user_sessions[chat_id]


def update_stats(chat_id, action):
    if chat_id not in user_stats:
        user_stats[chat_id] = {"emails": 0, "messages": 0, "checks": 0}
    if action in user_stats[chat_id]:
        user_stats[chat_id][action] += 1


@bot.message_handler(commands=["start"])
def cmd_start(session):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="new_email"),
        types.InlineKeyboardButton("📥 Мои письма", callback_data="check_inbox"),
        types.InlineKeyboardButton("👤 Свое имя", callback_data="set_user"),
        types.InlineKeyboardButton("🔄 Авто-обновление", callback_data="auto_refresh"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    text = (
        "🛡 *Guerrilla Mail Bot*\n"
        "Бесплатная временная почта без регистрации\n\n"
        "Нажмите кнопку или используйте команды:\n"
        "/new — Создать почту\n"
        "/inbox — Проверить письма\n"
        "/user <имя> — Установить имя\n"
        "/read <ID> — Прочитать письмо\n"
        "/help — Список команд"
    )
    bot.send_message(session.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["new"])
def cmd_new(session):
    chat_id = session.chat.id
    username = generate_random_string(8)
    data = guerrilla_request("get_email_address", ip="127.0.0.1", agent="Mozilla")
    if "email_addr" in data:
        sess = get_user_session(chat_id)
        sess["sid_token"] = data.get("sid_token")
        sess["email_addr"] = data["email_addr"]
        sess["email"] = data.get("email", username)
        sess["seq"] = 0
        sess["messages"] = []
        update_stats(chat_id, "emails")
        text = (
            f"✅ *Почта создана!*\n\n"
            f"📧 Адрес: `{data['email_addr']}`\n"
            f"🔑 SID: `{data.get('sid_token', 'N/A')[:16]}...`\n\n"
            f"Скопируйте адрес и используйте для регистраций.\n"
            f"Письма появятся автоматически.\n\n"
            f"Команды:\n"
            f"/inbox — Проверить письма\n"
            f"/read <ID> — Прочитать письмо\n"
            f"/user <имя> — Сменить имя"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ Ошибка создания почты. Попробуйте /new")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(session):
    chat_id = session.chat.id
    sess = get_user_session(chat_id)
    if not sess.get("sid_token"):
        bot.send_message(chat_id, "❌ Сначала создайте почту: /new")
        return
    data = guerrilla_request(
        "check_email",
        sid_token=sess["sid_token"],
        seq=sess["seq"]
    )
    if "list" in data:
        messages = data["list"]
        sess["messages"] = messages
        update_stats(chat_id, "checks")
        if not messages:
            bot.send_message(chat_id, "📭 *Почтовый ящик пуст*\nПисьма появятся автоматически.", parse_mode="Markdown")
            return
        text = f"📬 *{len(messages)} писем:*\n\n"
        for msg in messages[:20]:
            mail_id = msg.get("mail_id", "?")
            sender = msg.get("mail_from", "Unknown")
            subject = msg.get("mail_subject", "Без темы")
            text += f"🆔 `{mail_id}` | 👤 {sender}\n📝 {subject}\n\n"
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        error = data.get("error", "Неизвестная ошибка")
        bot.send_message(chat_id, f"❌ Ошибка: {error}")


@bot.message_handler(commands=["read"])
def cmd_read(session):
    parts = session.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(session.chat.id, "Использование: /read <ID письма>")
        return
    mail_id = parts[1].strip()
    sess = get_user_session(session.chat.id)
    if not sess.get("sid_token"):
        bot.send_message(session.chat.id, "❌ Сначала создайте почту: /new")
        return
    data = guerrilla_request(
        "fetch_email",
        sid_token=sess["sid_token"],
        email_id=mail_id
    )
    if "mail_body" in data:
        sender = data.get("mail_from", "Unknown")
        subject = data.get("mail_subject", "Без темы")
        body = data.get("mail_body", "Пустое письмо")
        if len(body) > 3500:
            body = body[:3500] + "\n\n... [обрезано]"
        text = (
            f"📧 *Письмо #{mail_id}*\n\n"
            f"👤 От: {sender}\n"
            f"📝 Тема: {subject}\n\n"
            f"---\n{body}"
        )
        bot.send_message(session.chat.id, text, parse_mode="Markdown")
    else:
        error = data.get("error", "Письмо не найдено")
        bot.send_message(session.chat.id, f"❌ {error}")


@bot.message_handler(commands=["user"])
def cmd_user(session):
    parts = session.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(session.chat.id, "Использование: /user <имя_пользователя>")
        return
    username = parts[1].strip().replace("@", "").replace(" ", "")
    sess = get_user_session(session.chat.id)
    if not sess.get("sid_token"):
        bot.send_message(session.chat.id, "❌ Сначала создайте почту: /new")
        return
    data = guerrilla_request(
        "set_email_user",
        sid_token=sess["sid_token"],
        email_user=username
    )
    if "email_addr" in data:
        sess["email_addr"] = data["email_addr"]
        sess["email"] = username
        bot.send_message(
            session.chat.id,
            f"✅ Имя установлено!\n📧 Новый адрес: `{data['email_addr']}`",
            parse_mode="Markdown"
        )
    else:
        error = data.get("error", "Не удалось сменить имя")
        bot.send_message(session.chat.id, f"❌ {error}")


@bot.message_handler(commands=["auto"])
def cmd_auto(session):
    chat_id = session.chat.id
    sess = get_user_session(chat_id)
    sess["auto_refresh"] = not sess.get("auto_refresh", False)
    status = "включено" if sess["auto_refresh"] else "выключено"
    bot.send_message(chat_id, f"🔄 Авто-обновление: *{status}*", parse_mode="Markdown")


@bot.message_handler(commands=["stats"])
def cmd_stats(session):
    chat_id = session.chat.id
    stats = user_stats.get(chat_id, {"emails": 0, "messages": 0, "checks": 0})
    sess = get_user_session(chat_id)
    email = sess.get("email_addr", "Не создана")
    text = (
        f"📊 *Статистика*\n\n"
        f"📧 Текущая почта: `{email}`\n"
        f"✉️ Создано почт: {stats.get('emails', 0)}\n"
        f"📬 Проверок: {stats.get('checks', 0)}\n"
        f"📩 Сообщений: {stats.get('messages', 0)}"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(session):
    text = (
        "🛡 *Guerrilla Mail Bot — Команды*\n\n"
        "/new — Создать новую почту\n"
        "/inbox — Проверить входящие\n"
        "/read <ID> — Прочитать письмо\n"
        "/user <имя> — Сменить имя почты\n"
        "/auto — Вкл/выкл авто-обновление\n"
        "/stats — Статистика использования\n"
        "/help — Эта справка\n\n"
        "API: guerrillamail.com (бесплатно, без ключей)"
    )
    bot.send_message(session.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "new_email":
        username = generate_random_string(8)
        resp = guerrilla_request("get_email_address", ip="127.0.0.1", agent="Mozilla")
        if "email_addr" in resp:
            sess = get_user_session(chat_id)
            sess["sid_token"] = resp.get("sid_token")
            sess["email_addr"] = resp["email_addr"]
            sess["email"] = resp.get("email", username)
            sess["seq"] = 0
            update_stats(chat_id, "emails")
            text = (
                f"✅ *Почта создана!*\n\n"
                f"📧 `{resp['email_addr']}`\n\n"
                f"Скопируйте адрес и ждите письма."
            )
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка создания")

    elif data == "check_inbox":
        sess = get_user_session(chat_id)
        if not sess.get("sid_token"):
            bot.answer_callback_query(call.id, "❌ Сначала создайте почту: /new")
            return
        resp = guerrilla_request("check_email", sid_token=sess["sid_token"], seq=sess["seq"])
        if "list" in resp:
            messages = resp["list"]
            update_stats(chat_id, "checks")
            if not messages:
                bot.edit_message_text("📭 Ящик пуст", chat_id, call.message.message_id)
            else:
                text = f"📬 *{len(messages)} писем:*\n\n"
                for msg in messages[:15]:
                    text += f"🆔 `{msg.get('mail_id')}` | {msg.get('mail_from', '?')}\n📝 {msg.get('mail_subject', '—')}\n\n"
                bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown")

    elif data == "set_user":
        bot.send_message(chat_id, "Введите имя: /user <имя>")

    elif data == "auto_refresh":
        sess = get_user_session(chat_id)
        sess["auto_refresh"] = not sess.get("auto_refresh", False)
        status = "вкл" if sess["auto_refresh"] else "выкл"
        bot.answer_callback_query(call.id, f"Авто-обновление: {status}")

    elif data == "stats":
        stats = user_stats.get(chat_id, {"emails": 0, "checks": 0})
        text = f"📊 Создано: {stats.get('emails', 0)} | Проверок: {stats.get('checks', 0)}"
        bot.answer_callback_query(call.id, text, show_alert=True)

    elif data == "help":
        text = (
            "/new — Создать почту\n"
            "/inbox — Проверить письма\n"
            "/read <ID> — Прочитать\n"
            "/user <имя> — Сменить имя\n"
            "/auto — Авто-обновление\n"
            "/stats — Статистика"
        )
        bot.send_message(chat_id, text)


if __name__ == "__main__":
    print(f"[Guerrilla Mail Bot] Запуск...")
    bot.infinity_polling()
