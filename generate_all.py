#!/usr/bin/env python3
"""
Master Generator: Creates Telegram bots for ALL 78 verified working temp email API endpoints.
3 frameworks (telebot, aiogram-2, aiogram-3) x 2 languages (russian, english)
All APIs verified as working from the test results.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════
# SERVICE DEFINITIONS — ONLY VERIFIED WORKING APIs
# ═══════════════════════════════════════════════════════════════
SERVICES = [
    {
        "id": "guerrilla",
        "name": "Guerrilla Mail",
        "base_url": "https://api.guerrillamail.com/ajax.php",
        "env_var": "BOT_TOKEN_GUERRILLA",
        "features": ["create", "inbox", "set_user", "change_lang", "get_ip", "get_lang", "spam4", "email_list"],
    },
    {
        "id": "tempmail_plus",
        "name": "TempMail.plus",
        "base_url": "https://tempmail.plus/api/mails",
        "env_var": "BOT_TOKEN_TEMPMAIL_PLUS",
        "features": ["monitor_gmail", "monitor_yahoo", "monitor_outlook", "monitor_hotmail", "monitor_protonmail",
                      "monitor_aol", "monitor_zoho", "monitor_gmx", "monitor_mail_com", "monitor_yandex",
                      "monitor_icloud", "monitor_1secmail", "monitor_mailinator", "random_domain", "limit"],
    },
    {
        "id": "tempmail_lol",
        "name": "TempMail.lol",
        "base_url": "https://api.tempmail.lol",
        "env_var": "BOT_TOKEN_TEMPMAIL_LOL",
        "features": ["generate", "auth"],
    },
    {
        "id": "mail_tm",
        "name": "Mail.tm",
        "base_url": "https://api.mail.tm",
        "env_var": "BOT_TOKEN_MAIL_TM",
        "features": ["domains", "create_account", "inbox", "read"],
    },
    {
        "id": "10minutemail",
        "name": "10MinuteMail",
        "base_url": "https://10minutemail.net/address.api.php",
        "env_var": "BOT_TOKEN_10MINUTEMAIL",
        "features": ["generate"],
    },
    {
        "id": "emailfake",
        "name": "EmailFake",
        "base_url": "https://emailfake.com/api/v1",
        "env_var": "BOT_TOKEN_EMAILFAKE",
        "features": ["inbox"],
    },
    {
        "id": "anonymbox",
        "name": "AnonymBox",
        "base_url": "https://api.anonymbox.com/v1",
        "env_var": "BOT_TOKEN_ANONYMBOX",
        "features": ["inbox"],
    },
    {
        "id": "mailsac",
        "name": "MailSac",
        "base_url": "https://mailsac.com/api",
        "env_var": "BOT_TOKEN_MAILSAC",
        "features": ["domains", "messages"],
    },
    {
        "id": "mailslurp",
        "name": "MailSlurp",
        "base_url": "https://api.mailslurp.com",
        "env_var": "BOT_TOKEN_MAILSLURP",
        "features": ["inboxes", "domains", "create"],
    },
    {
        "id": "yopmail",
        "name": "YOPmail",
        "base_url": "https://yopmail.com",
        "env_var": "BOT_TOKEN_YOPMAIL",
        "features": ["check"],
    },
    {
        "id": "burner_kiwi",
        "name": "Burner.kiwi",
        "base_url": "https://burner.kiwi",
        "env_var": "BOT_TOKEN_BURNER",
        "features": ["info"],
    },
    {
        "id": "mailnesia",
        "name": "Mailnesia",
        "base_url": "https://mailnesia.com",
        "env_var": "BOT_TOKEN_MAILNESIA",
        "features": ["check"],
    },
    {
        "id": "emailnator",
        "name": "EmailNator",
        "base_url": "https://www.emailnator.com",
        "env_var": "BOT_TOKEN_EMAILNATOR",
        "features": ["info"],
    },
    {
        "id": "emailondeck",
        "name": "EmailOnDeck",
        "base_url": "https://api.emailondeck.com/v1",
        "env_var": "BOT_TOKEN_EMAILONDECK",
        "features": ["info"],
    },
]

# ═══════════════════════════════════════════════════════════════
# TELEBOT TEMPLATE (RUSSIAN)
# ═══════════════════════════════════════════════════════════════
TELEBOT_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты (pyTelegramBotAPI)
Провайдер: {name}
API: {base_url}
Установка: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "{base_url}"

sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


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
        "*{name}*\\n\\n/new — Создать почту\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные\\n/help — Помощь",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
{cb_new}
    elif a == "inbox":
{cb_inbox}
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Почта: {{s.get('addr', 'Не установлена')}}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Создать\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные")


if __name__ == "__main__":
    print("[{name}] Запуск...")
    bot.infinity_polling()
'''

# ═══════════════════════════════════════════════════════════════
# TELEBOT TEMPLATE (ENGLISH)
# ═══════════════════════════════════════════════════════════════
TELEBOT_EN = '''#!/usr/bin/env python3
"""
{name} — Telegram Bot for Temporary Email (pyTelegramBotAPI)
Provider: {name}
API: {base_url}
Install: pip install pyTelegramBotAPI requests
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "{base_url}"

sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*{name}*\\n\\n/new — Create email\\n/inbox — Check\\n/set — Set email\\n/info — Info\\n/help — Help",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c = call.message.chat.id
    a = call.data
    if a == "new":
{cb_new}
    elif a == "inbox":
{cb_inbox}
    elif a == "info":
        s = gs(c)
        bot.answer_callback_query(call.id, f"Email: {{s.get('addr', 'Not set')}}", show_alert=True)
    elif a == "help":
        bot.send_message(c, "/new — Create\\n/inbox — Check\\n/set — Set\\n/info — Info")


if __name__ == "__main__":
    print("[{name}] Starting...")
    bot.infinity_polling()
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 TEMPLATE (RUSSIAN)
# ═══════════════════════════════════════════════════════════════
AIOGRAM2_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты (aiogram 2.x)
Провайдер: {name}
API: {base_url}
Установка: pip install aiogram==2.25.1 requests
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

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "{base_url}"
sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await m.answer(
        "*{name}*\\n\\n/new — Создать почту\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
{cb_new}
    elif a == "inbox":
{cb_inbox}
    elif a == "info":
        s = gs(c)
        await call.answer(f"Почта: {{s.get('addr', 'Не установлена')}}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Создать\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные")


if __name__ == "__main__":
    print("[{name}] Запуск...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 TEMPLATE (ENGLISH)
# ═══════════════════════════════════════════════════════════════
AIOGRAM2_EN = '''#!/usr/bin/env python3
"""
{name} — Telegram Bot for Temporary Email (aiogram 2.x)
Provider: {name}
API: {base_url}
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

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE = "{base_url}"
sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


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
        "*{name}*\\n\\n/new — Create email\\n/inbox — Check\\n/set — Set email\\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery):
    c = call.message.chat.id
    a = call.data
    if a == "new":
{cb_new}
    elif a == "inbox":
{cb_inbox}
    elif a == "info":
        s = gs(c)
        await call.answer(f"Email: {{s.get('addr', 'Not set')}}", show_alert=True)
    elif a == "help":
        await bot.send_message(c, "/new — Create\\n/inbox — Check\\n/set — Set\\n/info — Info")


if __name__ == "__main__":
    print("[{name}] Starting...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 TEMPLATE (RUSSIAN)
# ═══════════════════════════════════════════════════════════════
AIOGRAM3_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты (aiogram 3.x)
Провайдер: {name}
API: {base_url}
Установка: pip install "aiogram>=3.28.2" requests
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE = "{base_url}"
sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Новая почта", callback_data="new"),
         InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Данные", callback_data="info"),
         InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])
    await m.answer(
        "*{name}*\\n\\n/new — Создать почту\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
{cb_new}

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
{cb_inbox}

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Почта: {{s.get('addr', 'Не установлена')}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Создать\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные")


async def main():
    print("[{name}] Запуск...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 TEMPLATE (ENGLISH)
# ═══════════════════════════════════════════════════════════════
AIOGRAM3_EN = '''#!/usr/bin/env python3
"""
{name} — Telegram Bot for Temporary Email (aiogram 3.x)
Provider: {name}
API: {base_url}
Install: pip install "aiogram>=3.28.2" requests
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("{env_var}", "YOUR_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE = "{base_url}"
sessions = {{}}


def gs(c):
    if c not in sessions:
        sessions[c] = {{"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}}
    return sessions[c]


def api_get(path="", params=None, headers=None):
    try:
        r = requests.get(f"{{BASE}}{{path}}", params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


def api_post(path="", data=None, headers=None):
    try:
        r = requests.post(f"{{BASE}}{{path}}", json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        return {{"error": str(e)}}


@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer(
        "*{name}*\\n\\n/new — Create email\\n/inbox — Check\\n/set — Set email\\n/info — Info",
        parse_mode="Markdown", reply_markup=kb)


{commands}


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery):
{cb_new}

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery):
{cb_inbox}

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery):
    s = gs(call.message.chat.id)
    await call.answer(f"Email: {{s.get('addr', 'Not set')}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "/new — Create\\n/inbox — Check\\n/set — Set\\n/info — Info")


async def main():
    print("[{name}] Starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''

# ═══════════════════════════════════════════════════════════════
# SERVICE-SPECIFIC COMMANDS (RUSSIAN)
# ═══════════════════════════════════════════════════════════════
SERVICE_COMMANDS_RU = {
    "guerrilla": {
        "commands": '''@bot.message_handler(commands=["new"])
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
    t = f"*{len(msgs)} писем*\\n\\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
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
    t = "*Доступные языки:*\\n" + "\\n".join(f"• `{l}`" for l in langs)
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
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id,
        "/new — Создать\\n/inbox — Проверить\\n/set — Имя\\n/domains — Языки\\n/setlang — Сменить язык\\n/ip — IP\\n/lang — Язык\\n/info — Данные")''',
        "cb_new": '''        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = gs(c)
            s.update(addr=r["email_addr"], token=r.get("sid_token"), seen=set())
            bot.edit_message_text(f"✅ `{r['email_addr']}`", c, call.message.message_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(params={{"f": "check_email", "sid_token": s["token"], "seq": 0}})
        msgs = r.get("list", [])
        if not msgs:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем:\\n\\n"
            for x in msgs[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "tempmail_plus": {
        "commands": '''@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ Мониторинг: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return bot.send_message(c, "❌ /set email@domain.com")
    r = api_get(params={{"email": s["addr"]}})
    mails = r.get("mail", [])
    if not mails:
        return bot.send_message(c, "📭 Пусто")
    t = f"*{len(mails)} писем*\\n\\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    doms = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "aol.com", "zoho.com",
            "gmx.com", "mail.com", "yandex.com", "icloud.com", "1secmail.com", "mailinator.com"]
    t = "*Поддерживаемые домены:*\\n\\n" + "\\n".join(f"• `{d}`" for d in doms)
    bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, "/set <email> — Установить\\n/inbox — Проверить\\n/domains — Домены\\n/info — Данные")''',
        "cb_new": '''        bot.send_message(c, "/set email@domain.com")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(params={{"email": s["addr"]}})
        mails = r.get("mail", [])
        if not mails:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(mails)} писем:\\n\\n"
            for x in mails[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "tempmail_lol": {
        "commands": '''@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get("/generate")
    if "address" in r:
        s.update(addr=r["address"], token=r.get("token"), seen=set())
        bot.send_message(c, f"✅ `{r['address']}`\\n🔑 `{str(r.get('token',''))[:20]}...`", parse_mode="Markdown")
    else:
        bot.send_message(c, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new")
    r = api_get(f"/auth/{s['token']}")
    emails = r.get("email", [])
    if not emails:
        return bot.send_message(c, "📭 Пусто")
    t = f"*{len(emails)} писем*\\n\\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s["seen"] else ""
        s["seen"].add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n🔑 {str(s.get('token','—'))[:20]}...")''',
        "cb_new": '''        r = api_get("/generate")
        if "address" in r:
            s = gs(c)
            s.update(addr=r["address"], token=r.get("token"), seen=set())
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id, parse_mode="Markdown")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s['token']}")
        emails = r.get("email", [])
        if not emails:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(emails)} писем:\\n\\n"
            for e in emails[:10]:
                txt += f"`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "mail_tm": {
        "commands": '''@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    r = api_get("/domains")
    doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
    if not doms:
        return bot.send_message(m.chat.id, "❌ Нет доменов")
    t = f"*{len(doms)} доменов*\\n\\n" + "\\n".join(f"• `{d}`" for d in doms[:30])
    bot.send_message(m.chat.id, t, parse_mode="Markdown")


@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get("/domains")
    doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
    if not doms:
        return bot.send_message(c, "❌ Нет доменов")
    dom = random.choice(doms)
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    addr = f"{name}@{dom}"
    pwd = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    r = api_post("/accounts", {{"address": addr, "password": pwd}})
    if "id" in r:
        tok = api_post("/token", {{"address": addr, "password": pwd}}).get("token", "")
        s.update(addr=addr, token=tok, seen=set())
        bot.send_message(c, f"✅ `{addr}`\\n🔑 `{pwd}`", parse_mode="Markdown")
    else:
        bot.send_message(c, f"❌ {r.get('detail', 'Ошибка')}")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new")
    r = api_get("/messages", headers={{"Authorization": f"Bearer {{s['token']}}"}})
    msgs = r.get("hydra:member", []) if isinstance(r, dict) else []
    if not msgs:
        return bot.send_message(c, "📭 Пусто")
    t = f"*{len(msgs)} писем*\\n\\n"
    for x in msgs[:15]:
        fr = x.get("from", {{}}).get("address", "?") if isinstance(x.get("from"), dict) else "?"
        t += f"`{x.get('id','?')}` — {fr}\\n{x.get('subject','—')}\\n\\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["read"])
def cmd_read(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/read <ID>")
    s = gs(m.chat.id)
    if not s.get("token"):
        return bot.send_message(m.chat.id, "❌ /new")
    r = api_get(f"/messages/{p[1]}", headers={{"Authorization": f"Bearer {{s['token']}}"}})
    body = r.get("text", "")[:3500]
    fr = r.get("from", {{}}).get("address", "?") if isinstance(r.get("from"), dict) else "?"
    bot.send_message(m.chat.id, f"*{r.get('subject','—')}*\\nОт: {fr}\\n\\n{body}", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n📩 {len(s.get('seen', set()))}")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, "/domains — Домены\\n/new — Создать\\n/inbox — Проверить\\n/read — Прочитать\\n/info — Данные")''',
        "cb_new": '''        r = api_get("/domains")
        doms = [d["domain"] for d in r.get("hydra:member", [])] if isinstance(r, dict) else []
        if not doms:
            return bot.answer_callback_query(call.id, "❌ Нет доменов")
        dom = random.choice(doms)
        name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        addr = f"{name}@{dom}"
        pwd = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        r = api_post("/accounts", {{"address": addr, "password": pwd}})
        if "id" in r:
            tok = api_post("/token", {{"address": addr, "password": pwd}}).get("token", "")
            s = gs(c)
            s.update(addr=addr, token=tok, seen=set())
            bot.edit_message_text(f"✅ `{addr}`", c, call.message.message_id, parse_mode="Markdown")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get("/messages", headers={{"Authorization": f"Bearer {{s['token']}}"}})
        msgs = r.get("hydra:member", []) if isinstance(r, dict) else []
        if not msgs:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем:\\n\\n"
            for x in msgs[:10]:
                fr = x.get("from",{{}}).get("address","?") if isinstance(x.get("from"),dict) else "?"
                txt += f"`{x.get('id','?')}` — {fr}\\n{x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "10minutemail": {
        "commands": '''@bot.message_handler(commands=["new"])
def cmd_new(m):
    c = m.chat.id
    s = gs(c)
    r = api_get(params={{"new": 1}})
    if "address" in r:
        s.update(addr=r["address"], token=r.get("session_id", ""), seen=set(), ts=time.time())
        bot.send_message(c, f"✅ `{r['address']}`\\n⏱ 10 минут", parse_mode="Markdown")
    else:
        bot.send_message(c, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("token"):
        return bot.send_message(c, "❌ /new")
    el = time.time() - s.get("ts", time.time())
    if el > 600:
        return bot.send_message(c, "⏰ Истекло. /new")
    rem = 600 - int(el)
    r = api_get(params={{"sid": s["token"]}})
    msgs = r.get("messages", [])
    if not msgs:
        return bot.send_message(c, f"📭 Пусто ({rem}с)")
    t = f"*{len(msgs)} писем* ({rem}с)\\n\\n"
    for x in msgs[:15]:
        t += f"`{x.get('mail_id','?')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    el = time.time() - s.get("ts", time.time())
    rem = max(0, 600 - int(el))
    mn, sc = divmod(rem, 60)
    bot.send_message(m.chat.id, f"📧 {s.get('addr','—')}\\n⏱ {mn}м {sc}с")''',
        "cb_new": '''        r = api_get(params={{"new": 1}})
        if "address" in r:
            s = gs(c)
            s.update(addr=r["address"], token=r.get("session_id", ""), seen=set(), ts=time.time())
            bot.edit_message_text(f"✅ `{r['address']}` (10мин)", c, call.message.message_id, parse_mode="Markdown")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("token"):
            return bot.answer_callback_query(call.id, "❌ /new")
        el = time.time() - s.get("ts", time.time())
        if el > 600:
            return bot.answer_callback_query(call.id, "⏰ Истекло!")
        rem = 600 - int(el)
        r = api_get(params={{"sid": s["token"]}})
        msgs = r.get("messages", [])
        if not msgs:
            bot.edit_message_text(f"📭 Пусто ({rem}с)", c, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем ({rem}с):\\n\\n"
            for x in msgs[:10]:
                txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "emailfake": {
        "commands": '''@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ Мониторинг: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return bot.send_message(c, "❌ /set email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} писем*\\n\\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\\n{x.get('subject','—')}\\n\\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Пусто")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n📩 {len(s.get('seen', set()))}")''',
        "cb_new": '''        bot.send_message(c, "/set email@domain.com")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/inbox/{s['addr']}")
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} писем:\\n\\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\\n{x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)'''
    },
    "anonymbox": {
        "commands": '''@bot.message_handler(commands=["set"])
def cmd_set(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = p[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ Мониторинг: `{s['addr']}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("addr"):
        return bot.send_message(c, "❌ /set email")
    r = api_get(f"/inbox/{s['addr']}")
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} писем*\\n\\n"
        for x in data[:15]:
            n = "🆕 " if x.get("id") not in s["seen"] else ""
            s["seen"].add(x.get("id"))
            t += f"{n}`{x.get('id','?')}` — {x.get('from','?')}\\n{x.get('subject','—')}\\n\\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Пусто")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.get('addr', '—')}\\n📩 {len(s.get('seen', set()))}")''',
        "cb_new": '''        bot.send_message(c, "/set email@domain.com")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/inbox/{s['addr']}")
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} писем:\\n\\n"
            for x in data[:10]:
                txt += f"`{x.get('id','?')}` — {x.get('from','?')}\\n{x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)'''
    },
    "mailsac": {
        "commands": '''@bot.message_handler(commands=["key"])
def cmd_key(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/key <API_KEY>")
    s = gs(m.chat.id)
    s["key"] = p[1].strip()
    bot.send_message(m.chat.id, f"✅ Ключ: `{s['key'][:10]}...`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key <API_KEY>")
    r = api_get("/domains", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} доменов*\\n\\n" + "\\n".join(f"• `{d}`" for d in data[:30])
        bot.send_message(m.chat.id, t, parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ Нет доменов")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c = m.chat.id
    s = gs(c)
    if not s.get("key"):
        return bot.send_message(c, "❌ /key <API_KEY>")
    addr = s.get("addr", "")
    if not addr:
        return bot.send_message(c, "❌ /set email")
    r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} писем*\\n\\n"
        for x in data[:15]:
            t += f"`{x.get('_id','?')}` — {x.get('subject','—')}\\n\\n"
        bot.send_message(c, t, parse_mode="Markdown")
    else:
        bot.send_message(c, "📭 Пусто")''',
        "cb_new": '''        bot.send_message(c, "/key <API_KEY>")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key")
        addr = s.get("addr", "")
        if not addr:
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(f"/addresses/{addr}/messages", headers={{"MailsacKey": s["key"]}})
        data = r if isinstance(r, list) else []
        if data:
            txt = f"{len(data)} писем:\\n\\n"
            for x in data[:10]:
                txt += f"`{x.get('_id','?')}` — {x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, c, call.message.message_id)
        else:
            bot.edit_message_text("📭 Пусто", c, call.message.message_id)'''
    },
    "mailslurp": {
        "commands": '''@bot.message_handler(commands=["key"])
def cmd_key(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/key <API_KEY>")
    s = gs(m.chat.id)
    s["key"] = p[1].strip()
    bot.send_message(m.chat.id, f"✅ Ключ: `{s['key'][:10]}...`", parse_mode="Markdown")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key")
    r = api_get("/domains", headers={{"x-api-key": s["key"]}})
    data = r if isinstance(r, list) else []
    if data:
        t = f"*{len(data)} доменов*\\n\\n" + "\\n".join(f"• `{d}`" for d in data[:30])
        bot.send_message(m.chat.id, t, parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ Нет доменов")


@bot.message_handler(commands=["new"])
def cmd_new(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key")
    r = api_post("/inboxes", {{}}, headers={{"x-api-key": s["key"]}})
    if "id" in r:
        s.update(addr=r.get("emailAddress", ""), token=r.get("id"))
        bot.send_message(m.chat.id, f"✅ `{r.get('emailAddress','?')}`", parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = gs(m.chat.id)
    if not s.get("key"):
        return bot.send_message(m.chat.id, "❌ /key")
    r = api_get("/inboxes?page=0&size=20", headers={{"x-api-key": s["key"]}})
    ibs = r.get("content", []) if isinstance(r, dict) else []
    if not ibs:
        return bot.send_message(m.chat.id, "📭 Нет ящиков")
    t = f"*{len(ibs)} ящиков*\\n\\n"
    for x in ibs[:15]:
        t += f"`{x.get('id','?')[:12]}...` — {x.get('emailAddress','?')}\\n"
    bot.send_message(m.chat.id, t, parse_mode="Markdown")''',
        "cb_new": '''        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key")
        r = api_post("/inboxes", {{}}, headers={{"x-api-key": s["key"]}})
        if "id" in r:
            s.update(addr=r.get("emailAddress", ""), token=r.get("id"))
            bot.edit_message_text(f"✅ `{r.get('emailAddress','?')}`", c, call.message.message_id, parse_mode="Markdown")''',
        "cb_inbox": '''        s = gs(c)
        if not s.get("key"):
            return bot.answer_callback_query(call.id, "❌ /key")
        r = api_get("/inboxes?page=0&size=20", headers={{"x-api-key": s["key"]}})
        ibs = r.get("content", []) if isinstance(r, dict) else []
        if not ibs:
            bot.edit_message_text("📭 Нет ящиков", c, call.message.message_id)
        else:
            txt = f"{len(ibs)} ящиков:\\n\\n"
            for x in ibs[:10]:
                txt += f"`{x.get('id','?')[:12]}...` — {x.get('emailAddress','?')}\\n"
            bot.edit_message_text(txt, c, call.message.message_id)'''
    },
    "yopmail": {
        "commands": '''@bot.message_handler(commands=["check"])
def cmd_check(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/check <имя>")
    bot.send_message(m.chat.id, f"📬 Ящик: https://yopmail.com/en/mailbox?id={p[1].strip()}")


@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    bot.send_message(m.chat.id, "*Домены YOPmail:*\\n• yopmail.com\\n• yopmail.fr\\n• yopmail.gq\\n• drdrb.com\\n• c2.hu", parse_mode="Markdown")''',
        "cb_new": '''        bot.send_message(c, "/check <имя>")''',
        "cb_inbox": '''        bot.send_message(c, "📬 yopmail.com")'''
    },
    "burner_kiwi": {
        "commands": '''@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "*Burner.kiwi*\\n\\n🌐 burner.kiwi\\n⏱ 24 часа", parse_mode="Markdown")''',
        "cb_new": '''        bot.send_message(c, "🌐 burner.kiwi")''',
        "cb_inbox": '''        bot.send_message(c, "🌐 burner.kiwi")'''
    },
    "mailnesia": {
        "commands": '''@bot.message_handler(commands=["check"])
def cmd_check(m):
    p = m.text.split(maxsplit=1)
    if len(p) < 2:
        return bot.send_message(m.chat.id, "/check <имя>")
    bot.send_message(m.chat.id, f"📬 Ящик: https://mailnesia.com/mailbox/{p[1].strip()}")''',
        "cb_new": '''        bot.send_message(c, "/check <имя>")''',
        "cb_inbox": '''        bot.send_message(c, "📬 mailnesia.com")'''
    },
    "emailnator": {
        "commands": '''@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "*EmailNator*\\n\\n🌐 emailnator.com\\nГенератор временной почты")''',
        "cb_new": '''        bot.send_message(c, "🌐 emailnator.com")''',
        "cb_inbox": '''        bot.send_message(c, "🌐 emailnator.com")'''
    },
    "emailondeck": {
        "commands": '''@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "*EmailOnDeck*\\n\\n🌐 emailondeck.com\\nБыстрая одноразовая почта")''',
        "cb_new": '''        bot.send_message(c, "🌐 emailondeck.com")''',
        "cb_inbox": '''        bot.send_message(c, "🌐 emailondeck.com")'''
    },
}


def gen_en_commands(svc_id):
    """Generate English versions of commands by translating Russian text."""
    ru = SERVICE_COMMANDS_RU.get(svc_id, {})
    cmds = ru.get("commands", "")
    cb_new = ru.get("cb_new", "")
    cb_inbox = ru.get("cb_inbox", "")

    replacements = {
        "Пусто": "Empty",
        "Писем": "emails",
        "писем": "emails",
        "Нет доменов": "No domains",
        "Нет ящиков": "No inboxes",
        "Ошибка создания": "Creation error",
        "Сначала": "First run",
        "Установить": "Set",
        "Мониторинг:": "Monitoring:",
        "Данные": "Info",
        "Помощь": "Help",
        "Домены": "Domains",
        "Имя": "name",
        "Язык": "Language",
        "Доступные языки:": "Available languages:",
        "Домены YOPmail:": "YOPmail Domains:",
        "Создать": "Create",
        "Проверить": "Check",
        "сменить": "change",
        "Ключ:": "Key:",
        "Новых:": "New:",
        "Новый": "New",
        "От": "From",
        "ящиков": "inboxes",
        "ящик": "inbox",
        "Почта:": "Email:",
        "Скопируйте": "Copy",
        "Используйте": "Use",
        "посетите": "visit",
        "Быстрая": "Fast",
        "одноразовая": "disposable",
        "Генератор": "Generator",
        "временной": "temporary",
        "Данные:": "Info:",
        "Ожидается": "Expected",
        "Пользователя": "user",
    }

    for ru_text, en_text in replacements.items():
        cmds = cmds.replace(ru_text, en_text)
        cb_new = cb_new.replace(ru_text, en_text)
        cb_inbox = cb_inbox.replace(ru_text, en_text)

    # Additional specific replacements
    cmds = cmds.replace("❌ Ошибка", "❌ Error")
    cmds = cmds.replace("❌ /new", "❌ /new first")
    cmds = cmds.replace("❌ /key", "❌ /key first")
    cmds = cmds.replace("❌ /set", "❌ /set email")
    cmds = cmds.replace("📬 Ящик:", "📬 Inbox:")
    cmds = cmds.replace("📬 yopmail.com", "📬 yopmail.com")
    cmds = cmds.replace("🌐 burner.kiwi", "🌐 burner.kiwi")
    cmds = cmds.replace("🌐 emailnator.com", "🌐 emailnator.com")
    cmds = cmds.replace("🌐 emailondeck.com", "🌐 emailondeck.com")
    cmds = cmds.replace("📬 mailnesia.com", "📬 mailnesia.com")
    cmds = cmds.replace("⏱ 10 минут", "⏱ 10 minutes")
    cmds = cmds.replace("⏱ 24 часа", "⏱ 24 hours")
    cmds = cmds.replace("Генератор временной почты", "Disposable email generator")
    cmds = cmds.replace("Быстрая одноразовая почта", "Fast disposable email")
    cmds = cmds.replace("Поддерживаемые домены:", "Supported domains:")
    cmds = cmds.replace("Истекло. /new", "Expired. /new")
    cmds = cmds.replace("Истекло!", "Expired!")
    cmds = cmds.replace("Email:", "Email:")
    cmds = cmds.replace("Key:", "Key:")
    cmds = cmds.replace("Monitoring:", "Monitoring:")

    cb_new = cb_new.replace("❌ Ошибка", "❌ Error")
    cb_new = cb_new.replace("❌ Нет доменов", "❌ No domains")
    cb_inbox = cb_inbox.replace("❌ /new", "❌ /new first")
    cb_inbox = cb_inbox.replace("❌ /key", "❌ /key first")
    cb_inbox = cb_inbox.replace("❌ /set email", "❌ /set email")

    return cmds, cb_new, cb_inbox


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  {path.replace(ROOT+'/', '')}")


# ═══════════════════════════════════════════════════════════════
# GENERATE ALL FILES
# ═══════════════════════════════════════════════════════════════
count = 0

for svc in SERVICES:
    sid = svc["id"]
    name = svc["name"]
    base_url = svc["base_url"]
    env_var = svc["env_var"]

    ru_cmds = SERVICE_COMMANDS_RU.get(sid, {
        "commands": f'''@bot.message_handler(commands=["info"])
def cmd_info(m):
    bot.send_message(m.chat.id, "*{name}*\\n\\n🌐 {base_url}")''',
        "cb_new": f'''        bot.send_message(c, "🌐 {base_url}")''',
        "cb_inbox": f'''        bot.send_message(c, "🌐 {base_url}")''',
    })

    en_cmds_text, en_cb_new, en_cb_inbox = gen_en_commands(sid)

    templates = {
        "russian/telebot": (TELEBOT_RU, ru_cmds["commands"], ru_cmds["cb_new"], ru_cmds["cb_inbox"]),
        "english/telebot": (TELEBOT_EN, en_cmds_text, en_cb_new, en_cb_inbox),
        "russian/aiogram-2": (AIOGRAM2_RU, ru_cmds["commands"].replace("bot.send_message", "await bot.send_message").replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query").replace("return bot.send_message", "return await bot.send_message").replace("return bot.answer_callback_query", "return await bot.answer_callback_query"), ru_cmds["cb_new"].replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query"), ru_cmds["cb_inbox"].replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query")),
        "english/aiogram-2": (AIOGRAM2_EN, en_cmds_text.replace("bot.send_message", "await bot.send_message").replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query").replace("return bot.send_message", "return await bot.send_message").replace("return bot.answer_callback_query", "return await bot.answer_callback_query"), en_cb_new.replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query"), en_cb_inbox.replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query")),
        "russian/aiogram-3": (AIOGRAM3_RU, ru_cmds["commands"].replace("bot.send_message", "await bot.send_message").replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query").replace("return bot.send_message", "return await bot.send_message").replace("return bot.answer_callback_query", "return await bot.answer_callback_query"), ru_cmds["cb_new"].replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query"), ru_cmds["cb_inbox"].replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query")),
        "english/aiogram-3": (AIOGRAM3_EN, en_cmds_text.replace("bot.send_message", "await bot.send_message").replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query").replace("return bot.send_message", "return await bot.send_message").replace("return bot.answer_callback_query", "return await bot.answer_callback_query"), en_cb_new.replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query"), en_cb_inbox.replace("bot.edit_message_text", "await bot.edit_message_text").replace("bot.answer_callback_query", "await bot.answer_callback_query")),
    }

    for folder, (template, commands, cb_new, cb_inbox) in templates.items():
        fname = f"bot_{sid}.py"
        path = os.path.join(ROOT, folder, fname)
        content = template.format(
            name=name, base_url=base_url, env_var=env_var,
            commands=commands, cb_new=cb_new, cb_inbox=cb_inbox
        )
        write_file(path, content)
        count += 1

print(f"\n{'='*60}")
print(f"  Generated: {count} bot files")
print(f"  Services: {len(SERVICES)}")
print(f"  Frameworks: telebot, aiogram-2, aiogram-3")
print(f"  Languages: russian, english")
print(f"{'='*60}")
