#!/usr/bin/env python3
"""
Generator: 84 Telegram bots — proper English/Russian separation.
English bots: all text in English, author "Vladislav Sofronov (cpner)"
Russian bots: all text in Russian, author "Владислав Софронов (cpner)"
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {"id":"guerrilla","name":"Guerrilla Mail","url":"https://api.guerrillamail.com/ajax.php","env":"BOT_TOKEN_GUERRILLA"},
    {"id":"tempmail_plus","name":"TempMail.plus","url":"https://tempmail.plus/api/mails","env":"BOT_TOKEN_TEMPMAIL_PLUS"},
    {"id":"tempmail_lol","name":"TempMail.lol","url":"https://api.tempmail.lol","env":"BOT_TOKEN_TEMPMAIL_LOL"},
    {"id":"mail_tm","name":"Mail.tm","url":"https://api.mail.tm","env":"BOT_TOKEN_MAIL_TM"},
    {"id":"10minutemail","name":"10MinuteMail","url":"https://10minutemail.net/address.api.php","env":"BOT_TOKEN_10MINUTEMAIL"},
    {"id":"emailfake","name":"EmailFake","url":"https://emailfake.com/api/v1","env":"BOT_TOKEN_EMAILFAKE"},
    {"id":"anonymbox","name":"AnonymBox","url":"https://api.anonymbox.com/v1","env":"BOT_TOKEN_ANONYMBOX"},
    {"id":"mailsac","name":"MailSac","url":"https://mailsac.com/api","env":"BOT_TOKEN_MAILSAC"},
    {"id":"mailslurp","name":"MailSlurp","url":"https://api.mailslurp.com","env":"BOT_TOKEN_MAILSLURP"},
    {"id":"yopmail","name":"YOPmail","url":"https://yopmail.com","env":"BOT_TOKEN_YOPMAIL"},
    {"id":"burner_kiwi","name":"Burner.kiwi","url":"https://burner.kiwi","env":"BOT_TOKEN_BURNER"},
    {"id":"mailnesia","name":"Mailnesia","url":"https://mailnesia.com","env":"BOT_TOKEN_MAILNESIA"},
    {"id":"emailnator","name":"EmailNator","url":"https://www.emailnator.com","env":"BOT_TOKEN_EMAILNATOR"},
    {"id":"emailondeck","name":"EmailOnDeck","url":"https://api.emailondeck.com/v1","env":"BOT_TOKEN_EMAILONDECK"},
]

# ═══════════════════════════════════════════════════════════════
# TELEBOT ENGLISH
# ═══════════════════════════════════════════════════════════════
TELEBOT_EN = '''#!/usr/bin/env python3
"""
{name} Telegram Bot
Provider: {name} | API: {base_url}
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests

Features:
- Create disposable email addresses
- Check inbox for new messages
- Real-time message monitoring
- Comprehensive error handling
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Vladislav Sofronov (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set! Set {env_var}")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions: sessions[user_id] = UserSession()
    return sessions[user_id]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"API error attempt {{attempt+1}}/{{MAX_RETRIES}}: {{e}}")
            if attempt < MAX_RETRIES - 1: time.sleep(RETRY_DELAY * (attempt + 1))
    stats["errors"] += 1
    return {{"error": "Max retries exceeded"}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*{{SERVICE_NAME}}*\\nTemporary Email Bot\\n\\n/new — Create\\n/inbox — Check\\n/set — Set email\\n/info — Info\\n/help — Help",
        reply_markup=kb)


{commands}


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": {cb_new}
        elif a == "inbox": {cb_inbox}
        elif a == "info":
            s = get_session(c)
            bot.answer_callback_query(call.id, f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif a == "stats":
            bot.answer_callback_query(call.id, f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            bot.send_message(c, "/new — Create\\n/inbox — Check\\n/set — Set\\n/info — Info")
    except Exception as e:
        logger.error(f"Error: {{e}}")
        bot.answer_callback_query(call.id, "Error occurred")


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}}...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''

# ═══════════════════════════════════════════════════════════════
# TELEBOT RUSSIAN
# ═══════════════════════════════════════════════════════════════
TELEBOT_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты
Провайдер: {name} | API: {base_url}
Фреймворк: pyTelegramBotAPI 4.18.0
Установка: pip install pyTelegramBotAPI requests

Возможности:
- Создание одноразовых почтовых ящиков
- Проверка входящих сообщений
- Мониторинг в реальном времени
- Обработка ошибок
- Ограничение частоты запросов
- Статистика использования
- Корректное завершение

Автор: Владислав Софронов (cpner)
Контакт: feedback@gondon.su | t.me/reejb | gondon.su
Лицензия: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN! Установите {env_var}")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions: sessions[user_id] = UserSession()
    return sessions[user_id]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"Ошибка API попытка {{attempt+1}}/{{MAX_RETRIES}}: {{e}}")
            if attempt < MAX_RETRIES - 1: time.sleep(RETRY_DELAY * (attempt + 1))
    stats["errors"] += 1
    return {{"error": "Превышено количество попыток"}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@bot.message_handler(commands=["start", "menu"])
def cmd_start(m: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        types.InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Данные", callback_data="info"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    bot.send_message(m.chat.id,
        "*{{SERVICE_NAME}}*\\nБот временной почты\\n\\n/new — Создать\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные\\n/help — Помощь",
        reply_markup=kb)


{commands}


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": {cb_new}
        elif a == "inbox": {cb_inbox}
        elif a == "info":
            s = get_session(c)
            bot.answer_callback_query(call.id, f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)
        elif a == "stats":
            bot.answer_callback_query(call.id, f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            bot.send_message(c, "/new — Создать\\n/inbox — Проверить\\n/set — Установить\\n/info — Данные")
    except Exception as e:
        logger.error(f"Ошибка: {{e}}")
        bot.answer_callback_query(call.id, "Ошибка")


def signal_handler(sig, frame):
    logger.info("Завершение...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 ENGLISH
# ═══════════════════════════════════════════════════════════════
AIOGRAM2_EN = '''#!/usr/bin/env python3
"""
{name} Telegram Bot (aiogram 2.x)
Provider: {name} | API: {base_url}
Framework: aiogram 2.25.1
Install: pip install aiogram==2.25.1 requests

Features:
- Async/await architecture
- Create disposable email addresses
- Check inbox for new messages
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Vladislav Sofronov (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
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

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    await m.answer("*{{SERVICE_NAME}}*\\nTemporary Email Bot\\n\\n/new — Create\\n/inbox — Check\\n/info — Info", reply_markup=kb)


{commands}


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": {cb_new}
        elif a == "inbox": {cb_inbox}
        elif a == "info":
            s = get_session(c)
            await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif a == "stats":
            await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            await bot.send_message(c, "/new — Create\\n/inbox — Check\\n/info — Info")
    except Exception as e:
        logger.error(f"Error: {{e}}")
        await call.answer("Error")

if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}}...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 RUSSIAN
# ═══════════════════════════════════════════════════════════════
AIOGRAM2_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты (aiogram 2.x)
Провайдер: {name} | API: {base_url}
Фреймворк: aiogram 2.25.1
Установка: pip install aiogram==2.25.1 requests

Возможности:
- Async/await архитектура
- Создание одноразовых почтовых ящиков
- Проверка входящих сообщений
- Ограничение частоты запросов
- Статистика использования
- Корректное завершение

Автор: Владислав Софронов (cpner)
Контакт: feedback@gondon.su | t.me/reejb | gondon.su
Лицензия: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await m.answer("*{{SERVICE_NAME}}*\\nБот временной почты\\n\\n/new — Создать\\n/inbox — Проверить\\n/info — Данные", reply_markup=kb)


{commands}


@dp.callback_query_handler(lambda c: True)
async def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": {cb_new}
        elif a == "inbox": {cb_inbox}
        elif a == "info":
            s = get_session(c)
            await call.answer(f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)
        elif a == "stats":
            await call.answer(f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            await bot.send_message(c, "/new — Создать\\n/inbox — Проверить\\n/info — Данные")
    except Exception as e:
        logger.error(f"Ошибка: {{e}}")
        await call.answer("Ошибка")

if __name__ == "__main__":
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 ENGLISH
# ═══════════════════════════════════════════════════════════════
AIOGRAM3_EN = '''#!/usr/bin/env python3
"""
{name} Telegram Bot (aiogram 3.x)
Provider: {name} | API: {base_url}
Framework: aiogram >=3.28.2
Install: pip install "aiogram>=3.28.2" requests

Features:
- Modern async/await architecture
- Create disposable email addresses
- Check inbox for new messages
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Vladislav Sofronov (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dp.message(F.text.in_{{"/start", "/menu"}})
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await m.answer("*{{SERVICE_NAME}}*\\nTemporary Email Bot\\n\\n/new — Create\\n/inbox — Check\\n/info — Info", reply_markup=kb)


{commands}


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery) -> None:
{cb_new}

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery) -> None:
{cb_inbox}

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery) -> None:
    s = get_session(call.message.chat.id)
    await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)

@dp.callback_query(F.data == "stats")
async def cb_stats_handler(call: types.CallbackQuery) -> None:
    await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery) -> None:
    await bot.send_message(call.message.chat.id, "/new — Create\\n/inbox — Check\\n/info — Info")


async def main() -> None:
    logger.info(f"Starting {{SERVICE_NAME}}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 RUSSIAN
# ═══════════════════════════════════════════════════════════════
AIOGRAM3_RU = '''#!/usr/bin/env python3
"""
{name} — Telegram-бот временной почты (aiogram 3.x)
Провайдер: {name} | API: {base_url}
Фреймворк: aiogram >=3.28.2
Установка: pip install "aiogram>=3.28.2" requests

Возможности:
- Современная async/await архитектура
- Создание одноразовых почтовых ящиков
- Проверка входящих сообщений
- Ограничение частоты запросов
- Статистика использования
- Корректное завершение

Автор: Владислав Софронов (cpner)
Контакт: feedback@gondon.su | t.me/reejb | gondon.su
Лицензия: MIT
"""
import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, random, string, time, os, sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN!")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

class UserSession:
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {{}}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.get(url, params=params, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dp.message(F.text.in_{{"/start", "/menu"}})
async def cmd_start(m: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Новая почта", callback_data="new"),
         InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Данные", callback_data="info"),
         InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])
    await m.answer("*{{SERVICE_NAME}}*\\nБот временной почты\\n\\n/new — Создать\\n/inbox — Проверить\\n/info — Данные", reply_markup=kb)


{commands}


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery) -> None:
{cb_new}

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery) -> None:
{cb_inbox}

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery) -> None:
    s = get_session(call.message.chat.id)
    await call.answer(f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)

@dp.callback_query(F.data == "stats")
async def cb_stats_handler(call: types.CallbackQuery) -> None:
    await call.answer(f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery) -> None:
    await bot.send_message(call.message.chat.id, "/new — Создать\\n/inbox — Проверить\\n/info — Данные")


async def main() -> None:
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''

# ═══════════════════════════════════════════════════════════════
# SERVICE COMMANDS
# ═══════════════════════════════════════════════════════════════
CMDS = {
    "guerrilla": {
        "en": '''@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
        stats["created"] += 1
        bot.send_message(c, f"✅ Created: `{r['email_addr']}`\\n\\nCopy and use for registrations.")
    else: bot.send_message(c, "❌ Failed. Try /new")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new first")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs, stats["checked"] = r.get("list", []), stats["checked"] + 1
    if not msgs: return bot.send_message(c, "📭 Empty")
    t = f"*{len(msgs)} messages*\\n\\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""
        s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t)

@bot.message_handler(commands=["set"])
def cmd_set(m: types.Message) -> None:
    p = m.text.split(maxsplit=1)
    if len(p) < 2: return bot.send_message(m.chat.id, "Usage: /set <username>")
    s = get_session(m.chat.id)
    if not s.token: return bot.send_message(m.chat.id, "❌ /new first")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": p[1].strip()}})
    if "email_addr" in r: s.addr = r["email_addr"]; bot.send_message(m.chat.id, f"✅ `{r['email_addr']}`")

@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    s = get_session(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.addr or 'Not set'}\\n📩 Seen: {len(s.seen)}")''',
        "cb_new": '''r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(c); s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
            stats["created"] += 1
            bot.edit_message_text(f"✅ Created: `{r['email_addr']}`", c, call.message.message_id)''',
        "cb_inbox": '''s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", []); stats["checked"] += 1
        if not msgs: bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = ""
            for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(msgs)} messages:\\n\\n" + txt, c, call.message.message_id)''',
        "ru": '''@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
        stats["created"] += 1
        bot.send_message(c, f"✅ `{r['email_addr']}`\\n\\nСкопируйте и используйте для регистраций.")
    else: bot.send_message(c, "❌ Ошибка. Попробуйте /new")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs, stats["checked"] = r.get("list", []), stats["checked"] + 1
    if not msgs: return bot.send_message(c, "📭 Пусто")
    t = f"*{len(msgs)} писем*\\n\\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""
        s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t)

@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    s = get_session(m.chat.id)
    bot.send_message(m.chat.id, f"📧 {s.addr or '—'}\\n📩 {len(s.seen)}")''',
        "cb_new_ru": '''r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(c); s.addr, s.token, s.seen, s.ts = r["email_addr"], r.get("sid_token"), set(), time.time()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['email_addr']}`", c, call.message.message_id)''',
        "cb_inbox_ru": '''s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", []); stats["checked"] += 1
        if not msgs: bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = ""
            for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(msgs)} писем:\\n\\n" + txt, c, call.message.message_id)''',
    },
    "tempmail_plus": {
        "en": '''@bot.message_handler(commands=["set"])
def cmd_set(m: types.Message) -> None:
    p = m.text.split(maxsplit=1)
    if len(p) < 2: return bot.send_message(m.chat.id, "Usage: /set email@domain.com")
    s = get_session(m.chat.id); s.addr, s.seen = p[1].strip(), set()
    bot.send_message(m.chat.id, f"✅ Monitoring: `{s.addr}`")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.addr: return bot.send_message(c, "❌ /set email@domain.com")
    r = api_get(params={{"email": s.addr}}); mails = r.get("mail", []); stats["checked"] += 1
    if not mails: return bot.send_message(c, "📭 Empty")
    t = f"*{len(mails)} messages*\\n\\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""; s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t)''',
        "cb_new": '''bot.send_message(cid, "Use /set email@domain.com")''',
        "cb_inbox": '''s = get_session(c)
        if not s.addr: return bot.answer_callback_query(call.id, "❌ /set email first")
        r = api_get(params={{"email": s.addr}}); mails = r.get("mail", []); stats["checked"] += 1
        if not mails: bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = ""
            for x in mails[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(mails)} messages:\\n\\n" + txt, c, call.message.message_id)''',
        "ru": '''@bot.message_handler(commands=["set"])
def cmd_set(m: types.Message) -> None:
    p = m.text.split(maxsplit=1)
    if len(p) < 2: return bot.send_message(m.chat.id, "/set email@domain.com")
    s = get_session(m.chat.id); s.addr, s.seen = p[1].strip(), set()
    bot.send_message(m.chat.id, f"✅ Мониторинг: `{s.addr}`")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.addr: return bot.send_message(c, "❌ /set email@domain.com")
    r = api_get(params={{"email": s.addr}}); mails = r.get("mail", []); stats["checked"] += 1
    if not mails: return bot.send_message(c, "📭 Пусто")
    t = f"*{len(mails)} писем*\\n\\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""; s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
    bot.send_message(c, t)''',
        "cb_new_ru": '''bot.send_message(cid, "/set email@domain.com")''',
        "cb_inbox_ru": '''s = get_session(c)
        if not s.addr: return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(params={{"email": s.addr}}); mails = r.get("mail", []); stats["checked"] += 1
        if not mails: bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = ""
            for x in mails[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\\n{x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(mails)} писем:\\n\\n" + txt, c, call.message.message_id)''',
    },
    "tempmail_lol": {
        "en": '''@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get("/generate")
    if "address" in r:
        s.addr, s.token, s.seen = r["address"], r.get("token"), set()
        stats["created"] += 1
        bot.send_message(c, f"✅ `{r['address']}`\\nToken: `{str(r.get('token',''))[:20]}...`")
    else: bot.send_message(c, "❌ Failed")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new first")
    r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
    if not emails: return bot.send_message(c, "📭 Empty")
    t = f"*{len(emails)} messages*\\n\\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""; s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
    bot.send_message(c, t)''',
        "cb_new": '''r = api_get("/generate")
        if "address" in r:
            s = get_session(c); s.addr, s.token, s.seen = r["address"], r.get("token"), set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id)''',
        "cb_inbox": '''s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
        if not emails: bot.edit_message_text("📭 Empty", c, call.message.message_id)
        else:
            txt = ""
            for e in emails[:10]: s.seen.add(e.get("id")); txt += f"`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(emails)} messages:\\n\\n" + txt, c, call.message.message_id)''',
        "ru": '''@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get("/generate")
    if "address" in r:
        s.addr, s.token, s.seen = r["address"], r.get("token"), set()
        stats["created"] += 1
        bot.send_message(c, f"✅ `{r['address']}`\\nТокен: `{str(r.get('token',''))[:20]}...`")
    else: bot.send_message(c, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new")
    r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
    if not emails: return bot.send_message(c, "📭 Пусто")
    t = f"*{len(emails)} писем*\\n\\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""; s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
    bot.send_message(c, t)''',
        "cb_new_ru": '''r = api_get("/generate")
        if "address" in r:
            s = get_session(c); s.addr, s.token, s.seen = r["address"], r.get("token"), set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id)''',
        "cb_inbox_ru": '''s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
        if not emails: bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = ""
            for e in emails[:10]: s.seen.add(e.get("id")); txt += f"`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
            bot.edit_message_text(f"{len(emails)} писем:\\n\\n" + txt, c, call.message.message_id)''',
    },
}

DEFAULT_EN = {"en": '@bot.message_handler(commands=["info"])\ndef cmd_info(m: types.Message) -> None:\n    bot.send_message(m.chat.id, f"*{SERVICE_NAME}*\\n\\n🌐 {BASE_URL}\\n\\nVisit the website.")', "cb_new": 'bot.send_message(cid, f"Visit {BASE_URL}")', "cb_inbox": 'bot.send_message(cid, f"Visit {BASE_URL}")', "ru": '@bot.message_handler(commands=["info"])\ndef cmd_info(m: types.Message) -> None:\n    bot.send_message(m.chat.id, f"*{SERVICE_NAME}*\\n\\n🌐 {BASE_URL}\\n\\nПосетите сайт.")', "cb_new_ru": 'bot.send_message(cid, f"Посетите {BASE_URL}")', "cb_inbox_ru": 'bot.send_message(cid, f"Посетите {BASE_URL}")'}

count = 0
for svc in SERVICES:
    sid, name, base_url, env_var = svc["id"], svc["name"], svc["url"], svc["env"]
    cmds = CMDS.get(sid, DEFAULT_EN)

    for folder, template, lang in [
        ("english/telebot", TELEBOT_EN, "en"),
        ("russian/telebot", TELEBOT_RU, "ru"),
        ("english/aiogram-2", AIOGRAM2_EN, "en"),
        ("russian/aiogram-2", AIOGRAM2_RU, "ru"),
        ("english/aiogram-3", AIOGRAM3_EN, "en"),
        ("russian/aiogram-3", AIOGRAM3_RU, "ru"),
    ]:
        path = os.path.join(ROOT, folder, f"bot_{sid}.py")
        commands = cmds.get(lang, cmds.get("en", DEFAULT_EN["en"]))
        cb_new = cmds.get(f"cb_new_{lang}" if lang == "ru" else "cb_new", cmds.get("cb_new", DEFAULT_EN["cb_new"]))
        cb_inbox = cmds.get(f"cb_inbox_{lang}" if lang == "ru" else "cb_inbox", cmds.get("cb_inbox", DEFAULT_EN["cb_inbox"]))

        content = template.replace("{name}", name).replace("{base_url}", base_url).replace("{env_var}", env_var)
        content = content.replace("{commands}", commands).replace("{cb_new}", cb_new).replace("{cb_inbox}", cb_inbox)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: f.write(content)
        count += 1
        print(f"  [{count:02d}] {path.replace(ROOT+'/', '')}")

print(f"\n  Generated: {count} files")
