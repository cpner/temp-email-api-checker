#!/usr/bin/env python3
"""
Telegram-бот: Временная почта через Mail.tm API
Полноценный REST API: создание аккаунта, чтение почты
"""

import telebot
from telebot import types
import requests
import json
import random
import string
import hashlib

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = "https://api.mail.tm"

user_sessions = {}


def get_session(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "address": None,
            "token": None,
            "password": None,
            "account_id": None,
            "seen_ids": set()
        }
    return user_sessions[chat_id]


def api_get_domains():
    try:
        r = requests.get(f"{BASE_URL}/domains", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_create_account(address, password):
    try:
        r = requests.post(
            f"{BASE_URL}/accounts",
            json={"address": address, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_get_token(address, password):
    try:
        r = requests.post(
            f"{BASE_URL}/token",
            json={"address": address, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_get_messages(token):
    try:
        r = requests.get(
            f"{BASE_URL}/messages",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_read_message(token, msg_id):
    try:
        r = requests.get(
            f"{BASE_URL}/messages/{msg_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="mtm_new"),
        types.InlineKeyboardButton("📥 Входящие", callback_data="mtm_inbox"),
        types.InlineKeyboardButton("🌐 Домены", callback_data="mtm_domains"),
        types.InlineKeyboardButton("🔑 Войти", callback_data="mtm_login"),
        types.InlineKeyboardButton("📋 Данные", callback_data="mtm_info"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="mtm_help")
    )
    text = (
        "📨 *Mail.tm Bot*\n\n"
        "Полноценная временная почта с REST API\n\n"
        "/new — Создать почту\n"
        "/inbox — Проверить входящие\n"
        "/read <ID> — Прочитать письмо\n"
        "/domains — Список доменов\n"
        "/login — Войти в существующий\n"
        "/info — Данные почты\n"
        "/help — Справка"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["new"])
def cmd_new(msg):
    chat_id = msg.chat.id
    domains_data = api_get_domains()
    domains = []
    if "hydra:member" in domains_data:
        domains = [d["domain"] for d in domains_data["hydra:member"]]
    elif "hydra:iri" in domains_data:
        try:
            r = requests.get(f"{BASE_URL}/domains", timeout=10)
            data = r.json()
            if "hydra:member" in data:
                domains = [d["domain"] for d in data["hydra:member"]]
        except:
            pass
    if not domains:
        bot.send_message(chat_id, "❌ Не удалось получить домены. Попробуйте позже.")
        return
    domain = random.choice(domains)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    address = f"{username}@{domain}"
    password = generate_password()
    result = api_create_account(address, password)
    if "id" in result:
        token_data = api_get_token(address, password)
        sess = get_session(chat_id)
        sess["address"] = address
        sess["password"] = password
        sess["account_id"] = result["id"]
        sess["token"] = token_data.get("token")
        sess["seen_ids"] = set()
        text = (
            f"✅ *Почта создана!*\n\n"
            f"📧 Адрес: `{address}`\n"
            f"🔑 Пароль: `{password}`\n"
            f"🆔 ID: `{result['id'][:16]}...`\n\n"
            f"Сохраните данные для повторного входа!"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")
    else:
        detail = result.get("detail", "Ошибка")
        bot.send_message(chat_id, f"❌ {detail}")


@bot.message_handler(commands=["domains"])
def cmd_domains(msg):
    data = api_get_domains()
    if "hydra:member" in data:
        domains = data["hydra:member"]
        text = f"🌐 *Доступные домены ({len(domains)}):*\n\n"
        for d in domains:
            text += f"• `{d['domain']}`\n"
        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "❌ Не удалось получить домены")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(msg):
    chat_id = msg.chat.id
    sess = get_session(chat_id)
    if not sess.get("token"):
        bot.send_message(chat_id, "❌ Сначала создайте почту: /new")
        return
    data = api_get_messages(sess["token"])
    messages = []
    if isinstance(data, dict) and "hydra:member" in data:
        messages = data["hydra:member"]
    elif isinstance(data, list):
        messages = data
    if not messages:
        bot.send_message(chat_id, "📭 *Ящик пуст*", parse_mode="Markdown")
        return
    text = f"📬 *{len(messages)} писем:*\n\n"
    for m in messages[:20]:
        mid = m.get("id", "?")
        sender = m.get("from", {}).get("address", "Unknown") if isinstance(m.get("from"), dict) else str(m.get("from", "?"))
        subject = m.get("subject", "Без темы")
        is_new = mid not in sess["seen_ids"]
        marker = "🆕 " if is_new else ""
        if is_new:
            sess["seen_ids"].add(mid)
        text += f"{marker}🆔 `{mid}` | 👤 {sender}\n📝 {subject}\n\n"
    bot.send_message(chat_id, text, parse_mode="Markdown")


@bot.message_handler(commands=["read"])
def cmd_read(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Использование: /read <ID>")
        return
    msg_id = parts[1].strip()
    sess = get_session(msg.chat.id)
    if not sess.get("token"):
        bot.send_message(msg.chat.id, "❌ Сначала создайте почту: /new")
        return
    data = api_read_message(sess["token"], msg_id)
    if "text" in data or "html" in data:
        sender = data.get("from", {}).get("address", "?") if isinstance(data.get("from"), dict) else "?"
        subject = data.get("subject", "Без темы")
        body = data.get("text", data.get("html", "Нет содержимого"))
        if len(body) > 3500:
            body = body[:3500] + "\n\n... [обрезано]"
        text = (
            f"📧 *Письмо*\n\n"
            f"👤 От: {sender}\n"
            f"📝 Тема: {subject}\n\n"
            f"---\n{body}"
        )
        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "❌ Письмо не найдено")


@bot.message_handler(commands=["login"])
def cmd_login(msg):
    bot.send_message(
        msg.chat.id,
        "🔑 *Вход в почту*\n\n"
        "Введите адрес и пароль через пробел:\n"
        "`/login email@domain.com пароль`",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/login "))
def do_login(msg):
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(msg.chat.id, "Использование: /login <адрес> <пароль>")
        return
    address = parts[1]
    password = parts[2]
    token_data = api_get_token(address, password)
    if "token" in token_data:
        sess = get_session(msg.chat.id)
        sess["address"] = address
        sess["password"] = password
        sess["token"] = token_data["token"]
        sess["seen_ids"] = set()
        bot.send_message(msg.chat.id, f"✅ Вход выполнен!\n📧 {address}")
    else:
        bot.send_message(msg.chat.id, "❌ Неверный адрес или пароль")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    sess = get_session(msg.chat.id)
    if not sess.get("address"):
        bot.send_message(msg.chat.id, "❌ Почта не создана")
        return
    text = (
        f"📋 *Данные почты*\n\n"
        f"📧 Адрес: `{sess['address']}`\n"
        f"🔑 Пароль: `{sess['password']}`\n"
        f"🆔 ID: `{sess.get('account_id', '?')}`\n"
        f"📩 Прочитано: {len(sess.get('seen_ids', []))}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "📨 *Mail.tm Bot*\n\n"
        "/new — Создать почту\n"
        "/inbox — Входящие\n"
        "/read <ID> — Прочитать письмо\n"
        "/domains — Доступные домены\n"
        "/login <адрес> <пароль> — Войти\n"
        "/info — Данные почты\n"
        "/help — Справка\n\n"
        "API: mail.tm (REST, бесплатно)"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("mtm_"))
def callback(call):
    chat_id = call.message.chat.id
    action = call.data.replace("mtm_", "")

    if action == "new":
        bot.send_message(chat_id, "Создаю почту...")
        msg = types.Message
        msg.chat = types.Chat(chat_id, "private")
        msg.text = "/new"
        cmd_new(msg)

    elif action == "inbox":
        msg = types.Message
        msg.chat = types.Chat(chat_id, "private")
        msg.text = "/inbox"
        cmd_inbox(msg)

    elif action == "domains":
        data = api_get_domains()
        if "hydra:member" in data:
            count = len(data["hydra:member"])
            bot.answer_callback_query(call.id, f"Доступно доменов: {count}", show_alert=True)

    elif action == "login":
        bot.send_message(chat_id, "Введите: /login <адрес> <пароль>")

    elif action == "info":
        sess = get_session(chat_id)
        if sess.get("address"):
            bot.answer_callback_query(call.id, sess["address"], show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Нет почты")

    elif action == "help":
        bot.send_message(chat_id, "/new — Создать\n/inbox — Проверить\n/read <ID> — Прочитать")


if __name__ == "__main__":
    print("[Mail.tm Bot] Запуск...")
    bot.infinity_polling()
