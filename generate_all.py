#!/usr/bin/env python3
"""Generator: 84 bots with beautiful dynamic interface, info, links, source code."""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/cpner/temp-email-api-checker"

SERVICES = [
    {"id":"guerrilla","name":"Guerrilla Mail","url":"https://api.guerrillamail.com/ajax.php","env":"BOT_TOKEN_GUERRILLA","desc_en":"Full REST API for disposable emails","desc_ru":"Полный REST API для одноразовой почты","features_en":"Create, inbox, set user, 9 languages, spam4.me","features_ru":"Создание, входящие, смена имени, 9 языков, spam4.me","site":"https://www.guerrillamail.com"},
    {"id":"tempmail_plus","name":"TempMail.plus","url":"https://tempmail.plus/api/mails","env":"BOT_TOKEN_TEMPMAIL_PLUS","desc_en":"Monitor inbox for any email provider","desc_ru":"Мониторинг почты любых провайдеров","features_en":"Gmail, Yahoo, Outlook, ProtonMail, 13 domains","features_ru":"Gmail, Yahoo, Outlook, ProtonMail, 13 доменов","site":"https://tempmail.plus"},
    {"id":"tempmail_lol","name":"TempMail.lol","url":"https://api.tempmail.lol","env":"BOT_TOKEN_TEMPMAIL_LOL","desc_en":"Generate email + auth token workflow","desc_ru":"Генерация почты + рабочий процесс с токеном","features_en":"Generate, auth token, check inbox","features_ru":"Генерация, токен авторизации, проверка входящих","site":"https://tempmail.lol"},
    {"id":"mail_tm","name":"Mail.tm","url":"https://api.mail.tm","env":"BOT_TOKEN_MAIL_TM","desc_en":"REST API with account creation","desc_ru":"REST API с созданием аккаунтов","features_en":"Domains, accounts, inbox, read messages","features_ru":"Домены, аккаунты, входящие, чтение сообщений","site":"https://mail.tm"},
    {"id":"10minutemail","name":"10MinuteMail","url":"https://10minutemail.net/address.api.php","env":"BOT_TOKEN_10MINUTEMAIL","desc_en":"Email that expires in 10 minutes","desc_ru":"Почта, истекающая через 10 минут","features_en":"Auto-expiring, timer display","features_ru":"Автоудаление, отображение таймера","site":"https://10minutemail.net"},
    {"id":"emailfake","name":"EmailFake","url":"https://emailfake.com/api/v1","env":"BOT_TOKEN_EMAILFAKE","desc_en":"Simple inbox monitoring","desc_ru":"Простой мониторинг входящих","features_en":"Set email, check inbox","features_ru":"Установка почты, проверка входящих","site":"https://emailfake.com"},
    {"id":"anonymbox","name":"AnonymBox","url":"https://api.anonymbox.com/v1","env":"BOT_TOKEN_ANONYMBOX","desc_en":"Anonymous email monitoring","desc_ru":"Мониторинг анонимной почты","features_en":"Set email, check inbox","features_ru":"Установка почты, проверка входящих","site":"https://anonymbox.com"},
    {"id":"mailsac","name":"MailSac","url":"https://mailsac.com/api","env":"BOT_TOKEN_MAILSAC","desc_en":"Professional API with key support","desc_ru":"Профессиональный API с поддержкой ключей","features_en":"Domains, messages (API key required)","features_ru":"Домены, сообщения (нужен API ключ)","site":"https://mailsac.com"},
    {"id":"mailslurp","name":"MailSlurp","url":"https://api.mailslurp.com","env":"BOT_TOKEN_MAILSLURP","desc_en":"Professional testing API","desc_ru":"Профессиональный API для тестирования","features_en":"Inboxes, domains, create (API key required)","features_ru":"Ящики, домены, создание (нужен API ключ)","site":"https://mailslurp.com"},
    {"id":"yopmail","name":"YOPmail","url":"https://yopmail.com","env":"BOT_TOKEN_YOPMAIL","desc_en":"Multi-domain disposable email","desc_ru":"Многодоменная одноразовая почта","features_en":"Check inbox, list domains","features_ru":"Проверка входящих, список доменов","site":"https://yopmail.com"},
    {"id":"burner_kiwi","name":"Burner.kiwi","url":"https://burner.kiwi","env":"BOT_TOKEN_BURNER","desc_en":"Fast 24-hour disposable email","desc_ru":"Быстрая одноразовая почта на 24 часа","features_en":"Quick create, 24h expiry","features_ru":"Быстрое создание, истечение 24ч","site":"https://burner.kiwi"},
    {"id":"mailnesia","name":"Mailnesia","url":"https://mailnesia.com","env":"BOT_TOKEN_MAILNESIA","desc_en":"Anonymous email service","desc_ru":"Сервис анонимной почты","features_en":"Check inbox, direct links","features_ru":"Проверка входящих, прямые ссылки","site":"https://mailnesia.com"},
    {"id":"emailnator","name":"EmailNator","url":"https://www.emailnator.com","env":"BOT_TOKEN_EMAILNATOR","desc_en":"Disposable email generator","desc_ru":"Генератор одноразовой почты","features_en":"Generate, check","features_ru":"Генерация, проверка","site":"https://www.emailnator.com"},
    {"id":"emailondeck","name":"EmailOnDeck","url":"https://api.emailondeck.com/v1","env":"BOT_TOKEN_EMAILONDECK","desc_en":"Fast disposable email","desc_ru":"Быстрая одноразовая почта","features_en":"Quick create","features_ru":"Быстрое создание","site":"https://emailondeck.com"},
]


def gen_bot(lang, svc, framework):
    sid = svc["id"]
    name = svc["name"]
    url = svc["url"]
    env = svc["env"]
    site = svc["site"]
    is_en = lang == "en"
    is_telebot = framework == "telebot"
    is_a2 = framework == "aiogram-2"
    is_a3 = framework == "aiogram-3"

    # Language-specific text
    if is_en:
        author = "Vladislav Sofronov (cpner)"
        desc = svc["desc_en"]
        features = svc["features_en"]
        source_label = "Source Code"
        howto = (
            "1. Tap 'New Email' to create\\n"
            "2. Copy the email address\\n"
            "3. Use it for registration\\n"
            "4. Tap 'Inbox' to check messages\\n"
            "5. New messages marked with emoji"
        )
        start_msg = (
            f"*{name} Bot*\\n"
            f"{desc}\\n\\n"
            f"*Features:*\\n{features}\\n\\n"
            f"*How to use:*\\n{howto}"
        )
        info_msg = (
            f"*{name} Bot — Info*\\n\\n"
            f"*Service:* {name}\\n"
            f"*Description:* {desc}\\n"
            f"*Features:* {features}\\n"
            f"*API:* `{url}`\\n"
            f"*Website:* {site}\\n"
            f"*Source:* {REPO_URL}/blob/main/{lang}/{framework}/bot_{sid}.py\\n"
            f"*Author:* {author}\\n"
            f"*License:* MIT"
        )
        help_msg = (
            f"*{name} Bot — Commands*\\n\\n"
            f"/start — Main menu\\n"
            f"/new — Create email\\n"
            f"/inbox — Check messages\\n"
            f"/set — Set email manually\\n"
            f"/info — Bot information\\n"
            f"/help — This help\\n\\n"
            f"*Buttons:*\\n"
            f"📧 New Email — Create address\\n"
            f"📥 Inbox — Check messages\\n"
            f"ℹ️ Info — Bot details\\n"
            f"🔗 Source — GitHub link\\n"
            f"❓ Help — Usage guide"
        )
        new_btn = "📧 New Email"
        inbox_btn = "📥 Inbox"
        info_btn = "ℹ️ Info"
        source_btn = "🔗 Source Code"
        help_btn = "❓ Help"
        err = "Error"
    else:
        author = "Владислав Софронов (cpner)"
        desc = svc["desc_ru"]
        features = svc["features_ru"]
        source_label = "Исходный код"
        howto = (
            "1. Нажмите 'Новая почта'\\n"
            "2. Скопируйте адрес\\n"
            "3. Используйте для регистрации\\n"
            "4. Нажмите 'Входящие'\\n"
            "5. Новые помечены эмодзи"
        )
        start_msg = (
            f"*{name} Бот*\\n"
            f"{desc}\\n\\n"
            f"*Возможности:*\\n{features}\\n\\n"
            f"*Как пользоваться:*\\n{howto}"
        )
        info_msg = (
            f"*{name} — Информация*\\n\\n"
            f"*Сервис:* {name}\\n"
            f"*Описание:* {desc}\\n"
            f"*Возможности:* {features}\\n"
            f"*API:* `{url}`\\n"
            f"*Сайт:* {site}\\n"
            f"*Код:* {REPO_URL}/blob/main/{lang}/{framework}/bot_{sid}.py\\n"
            f"*Автор:* {author}\\n"
            f"*Лицензия:* MIT"
        )
        help_msg = (
            f"*{name} — Команды*\\n\\n"
            f"/start — Главное меню\\n"
            f"/new — Создать почту\\n"
            f"/inbox — Проверить письма\\n"
            f"/set — Установить почту\\n"
            f"/info — Информация\\n"
            f"/help — Эта справка\\n\\n"
            f"*Кнопки:*\\n"
            f"📧 Новая почта — Создать адрес\\n"
            f"📥 Входящие — Проверить письма\\n"
            f"ℹ️ Инфо — О боте\\n"
            f"🔗 Код — Ссылка на GitHub\\n"
            f"❓ Помощь — Инструкция"
        )
        new_btn = "📧 Новая почта"
        inbox_btn = "📥 Входящие"
        info_btn = "ℹ️ Инфо"
        source_btn = "🔗 Исходный код"
        help_btn = "❓ Помощь"
        err = "Ошибка"

    source_url = f"{REPO_URL}/blob/main/{lang}/{framework}/bot_{sid}.py"

    # Framework-specific code
    if is_telebot:
        return f'''#!/usr/bin/env python3
"""
{name} Telegram Bot
Provider: {name} | API: {url}
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests
Author: {author}
License: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN = os.environ.get("{env}", "YOUR_BOT_TOKEN")
BASE_URL = "{url}"
SERVICE_NAME = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.key = None
        self.seen = set()
        self.ts = 0
        self.messages = 0

sessions = {{}}
stats = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning("API error: " + str(e))
            if attempt < 2: time.sleep(1)
    stats["errors"] += 1
    return {{"error": "Max retries"}}

def api_post(path="", data=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}


def make_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("{new_btn}", callback_data="new"),
        types.InlineKeyboardButton("{inbox_btn}", callback_data="inbox"),
    )
    kb.add(
        types.InlineKeyboardButton("{info_btn}", callback_data="info"),
        types.InlineKeyboardButton("{source_btn}", callback_data="source"),
    )
    kb.add(
        types.InlineKeyboardButton("{help_btn}", callback_data="help"),
    )
    return kb


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    bot.send_message(m.chat.id, {repr(start_msg).replace("''", "'")}, reply_markup=make_kb())

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        bot.send_message(c, "Created: `" + r["email_addr"] + "`")
    else:
        bot.send_message(c, "Failed. Try /new")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = get_session(c)
    if not s.token:
        return bot.send_message(c, "Create email first: /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return bot.send_message(c, "Empty inbox")
    t = str(len(msgs)) + " messages:\\n\\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
    bot.send_message(c, t)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "Usage: /set <username>")
    s = get_session(m.chat.id)
    if not s.token:
        return bot.send_message(m.chat.id, "Create email first: /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": p[1].strip()}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        bot.send_message(m.chat.id, "Email: `" + r["email_addr"] + "`")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, {repr(info_msg).replace("''", "'")}, reply_markup=make_kb())

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, {repr(help_msg).replace("''", "'")}, reply_markup=make_kb())


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    try:
        s = get_session(c)
        if a == "new":
            r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
            if "email_addr" in r:
                s.addr = r["email_addr"]
                s.token = r.get("sid_token")
                s.seen = set()
                s.ts = time.time()
                stats["created"] += 1
                bot.edit_message_text("Created: `" + r["email_addr"] + "`", c, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Failed")
        elif a == "inbox":
            if not s.token:
                return bot.answer_callback_query(call.id, "Create email first")
            r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
            msgs = r.get("list", [])
            stats["checked"] += 1
            if not msgs:
                bot.edit_message_text("Empty inbox", c, call.message.message_id)
            else:
                txt = ""
                for x in msgs[:10]:
                    s.seen.add(x.get("mail_id"))
                    txt += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
                bot.edit_message_text(str(len(msgs)) + " messages:\\n\\n" + txt, c, call.message.message_id)
        elif a == "info":
            bot.answer_callback_query(call.id, "Name: " + name + "\\nAPI: " + url, show_alert=True)
        elif a == "source":
            bot.send_message(c, "Source code: " + source_url)
        elif a == "help":
            bot.send_message(c, {repr(help_msg).replace("''", "'")}, reply_markup=make_kb())
    except Exception as e:
        logger.error("Error: " + str(e))
        bot.answer_callback_query(call.id, err)


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''

    elif is_a2:
        return f'''#!/usr/bin/env python3
"""
{name} Telegram Bot (aiogram 2.x)
Provider: {name} | API: {url}
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests
Author: {author}
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN = os.environ.get("{env}", "YOUR_BOT_TOKEN")
BASE_URL = "{url}"
SERVICE_NAME = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.key = None
        self.seen = set()
        self.ts = 0
        self.messages = 0

sessions = {{}}
stats = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}


def make_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("{new_btn}", callback_data="new"),
        InlineKeyboardButton("{inbox_btn}", callback_data="inbox"),
    )
    kb.add(
        InlineKeyboardButton("{info_btn}", callback_data="info"),
        InlineKeyboardButton("{source_btn}", callback_data="source"),
    )
    kb.add(
        InlineKeyboardButton("{help_btn}", callback_data="help"),
    )
    return kb


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m):
    await m.answer({repr(start_msg).replace("''", "'")}, reply_markup=make_kb())

@dp.message_handler(commands=["new"])
async def cmd_new(m):
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        await m.answer("Created: `" + r["email_addr"] + "`")
    else:
        await m.answer("Failed. Try /new")

@dp.message_handler(commands=["inbox"])
async def cmd_inbox(m):
    c = m.chat.id
    s = get_session(c)
    if not s.token:
        return await m.answer("Create email first: /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return await m.answer("Empty inbox")
    t = str(len(msgs)) + " messages:\\n\\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
    await m.answer(t)

@dp.message_handler(commands=["info"])
async def cmd_info(m):
    await m.answer({repr(info_msg).replace("''", "'")}, reply_markup=make_kb())

@dp.message_handler(commands=["help"])
async def cmd_help(m):
    await m.answer({repr(help_msg).replace("''", "'")}, reply_markup=make_kb())


@dp.callback_query_handler(lambda c: True)
async def cb(call):
    c = call.message.chat.id
    a = call.data
    try:
        s = get_session(c)
        if a == "new":
            r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
            if "email_addr" in r:
                s.addr = r["email_addr"]
                s.token = r.get("sid_token")
                s.seen = set()
                s.ts = time.time()
                stats["created"] += 1
                await bot.edit_message_text("Created: `" + r["email_addr"] + "`", c, call.message.message_id)
            else:
                await call.answer("Failed")
        elif a == "inbox":
            if not s.token:
                return await call.answer("Create email first")
            r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
            msgs = r.get("list", [])
            stats["checked"] += 1
            if not msgs:
                await bot.edit_message_text("Empty inbox", c, call.message.message_id)
            else:
                txt = ""
                for x in msgs[:10]:
                    s.seen.add(x.get("mail_id"))
                    txt += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
                await bot.edit_message_text(str(len(msgs)) + " messages:\\n\\n" + txt, c, call.message.message_id)
        elif a == "info":
            await call.answer("Name: " + name + "\\nAPI: " + url, show_alert=True)
        elif a == "source":
            await bot.send_message(c, "Source code: " + source_url)
        elif a == "help":
            await bot.send_message(c, {repr(help_msg).replace("''", "'")}, reply_markup=make_kb())
    except Exception as e:
        logger.error("Error: " + str(e))
        await call.answer(err)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    executor.start_polling(dp, skip_updates=True)
'''

    else:  # aiogram-3
        return f'''#!/usr/bin/env python3
"""
{name} Telegram Bot (aiogram 3.x)
Provider: {name} | API: {url}
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests
Author: {author}
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN = os.environ.get("{env}", "YOUR_BOT_TOKEN")
BASE_URL = "{url}"
SERVICE_NAME = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

class UserSession:
    def __init__(self):
        self.addr = None
        self.token = None
        self.key = None
        self.seen = set()
        self.ts = 0
        self.messages = 0

sessions = {{}}
stats = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}


def make_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="{new_btn}", callback_data="new"),
         InlineKeyboardButton(text="{inbox_btn}", callback_data="inbox")],
        [InlineKeyboardButton(text="{info_btn}", callback_data="info"),
         InlineKeyboardButton(text="{source_btn}", callback_data="source")],
        [InlineKeyboardButton(text="{help_btn}", callback_data="help")],
    ])


@dp.message(F.text.startswith("/"))
async def cmd_start(m):
    await m.answer({repr(start_msg).replace("''", "'")}, reply_markup=make_kb())

@dp.message(F.text == "/new")
async def cmd_new(m):
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        await m.answer("Created: `" + r["email_addr"] + "`")
    else:
        await m.answer("Failed. Try /new")

@dp.message(F.text == "/inbox")
async def cmd_inbox(m):
    c = m.chat.id
    s = get_session(c)
    if not s.token:
        return await m.answer("Create email first: /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return await m.answer("Empty inbox")
    t = str(len(msgs)) + " messages:\\n\\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
    await m.answer(t)

@dp.message(F.text == "/info")
async def cmd_info(m):
    await m.answer({repr(info_msg).replace("''", "'")}, reply_markup=make_kb())

@dp.message(F.text == "/help")
async def cmd_help(m):
    await m.answer({repr(help_msg).replace("''", "'")}, reply_markup=make_kb())


@dp.callback_query(F.data == "new")
async def cb_new(call):
    c = call.message.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        await bot.edit_message_text("Created: `" + r["email_addr"] + "`", c, call.message.message_id)
    else:
        await call.answer("Failed")

@dp.callback_query(F.data == "inbox")
async def cb_inbox(call):
    c = call.message.chat.id
    s = get_session(c)
    if not s.token:
        return await call.answer("Create email first")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        await bot.edit_message_text("Empty inbox", c, call.message.message_id)
    else:
        txt = ""
        for x in msgs[:10]:
            s.seen.add(x.get("mail_id"))
            txt += x.get("mail_id", "?") + " - " + x.get("mail_from", "?") + " " + x.get("mail_subject", "-") + "\\n"
        await bot.edit_message_text(str(len(msgs)) + " messages:\\n\\n" + txt, c, call.message.message_id)

@dp.callback_query(F.data == "info")
async def cb_info(call):
    await call.answer("Name: " + name + "\\nAPI: " + url, show_alert=True)

@dp.callback_query(F.data == "source")
async def cb_source(call):
    await bot.send_message(call.message.chat.id, "Source code: " + source_url)

@dp.callback_query(F.data == "help")
async def cb_help(call):
    await bot.send_message(call.message.chat.id, {repr(help_msg).replace("''", "'")}, reply_markup=make_kb())


async def main():
    logger.info("Starting " + SERVICE_NAME + "...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''


count = 0
for svc in SERVICES:
    for folder, lang, framework in [
        ("english/telebot", "en", "telebot"),
        ("russian/telebot", "ru", "telebot"),
        ("english/aiogram-2", "en", "aiogram-2"),
        ("russian/aiogram-2", "ru", "aiogram-2"),
        ("english/aiogram-3", "en", "aiogram-3"),
        ("russian/aiogram-3", "ru", "aiogram-3"),
    ]:
        path = os.path.join(ROOT, folder, "bot_" + svc["id"] + ".py")
        content = gen_bot(lang, svc, framework)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        count += 1
        print(f"  [{count:02d}] {path.replace(ROOT+'/', '')}")

print(f"\n  Generated: {count} files")
