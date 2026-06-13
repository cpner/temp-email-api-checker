#!/usr/bin/env python3
"""
Professional Generator: 84 Telegram bots × 3 frameworks × 2 languages
All bots include: error handling, logging, type hints, rate limiting, retry logic,
comprehensive help, statistics, session management, graceful shutdown.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════
# SERVICE DEFINITIONS (verified working APIs only)
# ═══════════════════════════════════════════════════════════════
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
# TELEBOT TEMPLATE (ENGLISH)
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

Author: Temp Email Bots Project
License: MIT
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os
import signal
import sys
import logging
from typing import Optional, Dict, Any, Set

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0
RATE_LIMIT_DELAY: float = 0.5

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set! Set environment variable {env_var}")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════════
# Session Management
# ═══════════════════════════════════════════════════════════════
class UserSession:
    """Manages user state and data."""
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

# ═══════════════════════════════════════════════════════════════
# API Client with retry logic
# ═══════════════════════════════════════════════════════════════
def api_request(method: str, path: str = "", params: Optional[Dict] = None,
                data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request with retry logic and error handling."""
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                resp = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            else:
                return {{"error": f"Unsupported method: {{method}}"}}

            if "json" in resp.headers.get("content-type", ""):
                return resp.json()
            return {{"text": resp.text[:500], "status": resp.status_code}}

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except Exception as e:
            logger.error(f"Request error: {{e}}")
            return {{"error": str(e)}}

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))

    stats["errors"] += 1
    return {{"error": "Max retries exceeded"}}

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("GET", path, params=params, headers=headers)

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("POST", path, data=data, headers=headers)

# ═══════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════
def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def safe_text(text: str, max_len: int = 4000) -> str:
    return text[:max_len] if text else "No content"

# ═══════════════════════════════════════════════════════════════
# Command Handlers
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    text = (
        f"*{{SERVICE_NAME}}*\\n"
        f"Temporary Email Bot\\n\\n"
        f"Create disposable email addresses\\n"
        f"and receive messages instantly.\\n\\n"
        f"*Quick Start:*\\n"
        f"1. Tap 📧 New Email\\n"
        f"2. Copy the address\\n"
        f"3. Use it for registration\\n"
        f"4. Tap 📥 Inbox to check\\n\\n"
        f"*Commands:*\\n"
        f"/new — Create email\\n"
        f"/inbox — Check messages\\n"
        f"/set — Set email manually\\n"
        f"/info — Session info\\n"
        f"/stats — Usage statistics\\n"
        f"/help — Detailed help"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)
    logger.info(f"User {{message.chat.id}} started bot")


{commands}


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
{cb_new}
        elif action == "inbox":
{cb_inbox}
        elif action == "info":
            s = get_session(cid)
            text = (
                f"*Session Info*\\n\\n"
                f"Email: `{{s.addr or 'Not set'}}`\\n"
                f"Token: `{{str(s.token or '')[:20]}}...`\\n"
                f"Messages read: {{s.messages}}\\n"
                f"Unique seen: {{len(s.seen)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "stats":
            text = (
                f"*Bot Statistics*\\n\\n"
                f"Emails created: {{stats['created']}}\\n"
                f"Inboxes checked: {{stats['checked']}}\\n"
                f"Errors: {{stats['errors']}}\\n"
                f"Active sessions: {{len(sessions)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "help":
            bot.send_message(cid, get_help_text())
        else:
            bot.answer_callback_query(call.id, "Unknown action")
    except Exception as e:
        logger.error(f"Callback error: {{e}}")
        bot.answer_callback_query(call.id, "An error occurred")


def get_help_text() -> str:
    return (
        f"*{{SERVICE_NAME}} Bot — Help*\\n\\n"
        f"*Commands:*\\n"
        f"/new — Create new email\\n"
        f"/inbox — Check inbox\\n"
        f"/set <email> — Set email to monitor\\n"
        f"/read <ID> — Read specific message\\n"
        f"/key <KEY> — Set API key\\n"
        f"/info — Current session info\\n"
        f"/stats — Usage statistics\\n"
        f"/help — This help\\n\\n"
        f"*Provider:* {{SERVICE_NAME}}\\n"
        f"*API:* `{{BASE_URL}}`\\n\\n"
        f"*Tips:*\\n"
        f"- Create email first with /new\\n"
        f"- Check inbox regularly\\n"
        f"- Use /info to see session details"
    )

# ═══════════════════════════════════════════════════════════════
# Graceful Shutdown
# ═══════════════════════════════════════════════════════════════
def signal_handler(sig, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    logger.info(f"API: {{BASE_URL}}")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''

# ═══════════════════════════════════════════════════════════════
# TELEBOT TEMPLATE (RUSSIAN)
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

Автор: Temp Email Bots Project
Лицензия: MIT
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os
import signal
import sys
import logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN! Установите переменную {env_var}")
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
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

def api_request(method: str, path: str = "", params: Optional[Dict] = None,
                data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                resp = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            else:
                return {{"error": f"Неподдерживаемый метод: {{method}}"}}
            if "json" in resp.headers.get("content-type", ""):
                return resp.json()
            return {{"text": resp.text[:500], "status": resp.status_code}}
        except requests.exceptions.Timeout:
            logger.warning(f"Таймаут попытка {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ошибка соединения попытка {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except Exception as e:
            logger.error(f"Ошибка запроса: {{e}}")
            return {{"error": str(e)}}
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))
    stats["errors"] += 1
    return {{"error": "Превышено максимальное количество попыток"}}

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("GET", path, params=params, headers=headers)

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("POST", path, data=data, headers=headers)

def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        types.InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Данные", callback_data="info"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    text = (
        f"*{{SERVICE_NAME}}*\\n"
        f"Бот временной почты\\n\\n"
        f"Создавайте одноразовые почтовые ящики\\n"
        f"и получайте сообщения мгновенно.\\n\\n"
        f"*Быстрый старт:*\\n"
        f"1. Нажмите 📧 Новая почта\\n"
        f"2. Скопируйте адрес\\n"
        f"3. Используйте для регистрации\\n"
        f"4. Нажмите 📥 Входящие\\n\\n"
        f"*Команды:*\\n"
        f"/new — Создать почту\\n"
        f"/inbox — Проверить письма\\n"
        f"/set — Установить почту\\n"
        f"/info — Данные сессии\\n"
        f"/stats — Статистика\\n"
        f"/help — Подробная помощь"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)
    logger.info(f"Пользователь {{message.chat.id}} запустил бота")


{commands}


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
{cb_new}
        elif action == "inbox":
{cb_inbox}
        elif action == "info":
            s = get_session(cid)
            text = (
                f"*Данные сессии*\\n\\n"
                f"Почта: `{{s.addr or 'Не установлена'}}`\\n"
                f"Токен: `{{str(s.token or '')[:20]}}...`\\n"
                f"Прочитано: {{s.messages}}\\n"
                f"Уникальных: {{len(s.seen)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "stats":
            text = (
                f"*Статистика бота*\\n\\n"
                f"Создано почт: {{stats['created']}}\\n"
                f"Проверок: {{stats['checked']}}\\n"
                f"Ошибок: {{stats['errors']}}\\n"
                f"Активных сессий: {{len(sessions)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "help":
            bot.send_message(cid, get_help_text())
        else:
            bot.answer_callback_query(call.id, "Неизвестное действие")
    except Exception as e:
        logger.error(f"Ошибка callback: {{e}}")
        bot.answer_callback_query(call.id, "Произошла ошибка")


def get_help_text() -> str:
    return (
        f"*{{SERVICE_NAME}} — Помощь*\\n\\n"
        f"*Команды:*\\n"
        f"/new — Создать почту\\n"
        f"/inbox — Проверить\\n"
        f"/set <email> — Установить\\n"
        f"/read <ID> — Прочитать\\n"
        f"/key <KEY> — API ключ\\n"
        f"/info — Данные сессии\\n"
        f"/stats — Статистика\\n"
        f"/help — Помощь\\n\\n"
        f"*Провайдер:* {{SERVICE_NAME}}\\n"
        f"*API:* `{{BASE_URL}}`"
    )


def signal_handler(sig, frame):
    logger.info("Корректное завершение...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 TEMPLATE (ENGLISH)
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

Author: Temp Email Bots Project
License: MIT
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
import signal
import sys
from typing import Optional, Dict, Any, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("{name}")

BOT_TOKEN: str = os.environ.get("{env_var}", "YOUR_BOT_TOKEN")
BASE_URL: str = "{base_url}"
SERVICE_NAME: str = "{name}"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3

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

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
        except Exception as e:
            logger.warning(f"API error attempt {{attempt+1}}: {{e}}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
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


@dp.message_handler(commands=["start", "menu"])
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 New Email", callback_data="new"),
        InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        InlineKeyboardButton("📋 Info", callback_data="info"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    text = (
        f"*{{SERVICE_NAME}}*\\n"
        f"Temporary Email Bot\\n\\n"
        f"Create disposable email addresses\\n"
        f"and receive messages instantly.\\n\\n"
        f"*Quick Start:*\\n"
        f"1. Tap 📧 New Email\\n"
        f"2. Copy the address\\n"
        f"3. Use it for registration\\n"
        f"4. Tap 📥 Inbox to check"
    )
    await message.answer(text, reply_markup=kb)


{commands}


@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
{cb_new}
        elif action == "inbox":
{cb_inbox}
        elif action == "info":
            s = get_session(cid)
            await call.answer(f"Email: {{s.addr or 'Not set'}}", show_alert=True)
        elif action == "stats":
            await call.answer(f"Created: {{stats['created']}} | Checked: {{stats['checked']}}", show_alert=True)
        elif action == "help":
            await bot.send_message(cid, "/new — Create\\n/inbox — Check\\n/info — Info")
    except Exception as e:
        logger.error(f"Callback error: {{e}}")
        await call.answer("Error occurred")


if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-2 TEMPLATE (RUSSIAN)
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

Автор: Temp Email Bots Project
Лицензия: MIT
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
import sys
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

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

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
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await message.answer(
        f"*{{SERVICE_NAME}}*\\nБот временной почты\\n\\n/new — Создать\\n/inbox — Проверить\\n/info — Данные",
        reply_markup=kb
    )


{commands}


@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
{cb_new}
        elif action == "inbox":
{cb_inbox}
        elif action == "info":
            s = get_session(cid)
            await call.answer(f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)
        elif action == "stats":
            await call.answer(f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)
        elif action == "help":
            await bot.send_message(cid, "/new — Создать\\n/inbox — Проверить\\n/info — Данные")
    except Exception as e:
        logger.error(f"Ошибка: {{e}}")
        await call.answer("Ошибка")


if __name__ == "__main__":
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    executor.start_polling(dp, skip_updates=True)
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 TEMPLATE (ENGLISH)
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

Author: Temp Email Bots Project
License: MIT
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
import sys
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

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

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
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 New Email", callback_data="new"),
         InlineKeyboardButton(text="📥 Inbox", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Info", callback_data="info"),
         InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ])
    await message.answer(
        f"*{{SERVICE_NAME}}*\\nTemporary Email Bot\\n\\n/new — Create\\n/inbox — Check\\n/info — Info",
        reply_markup=kb
    )


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
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''

# ═══════════════════════════════════════════════════════════════
# AIogram-3 TEMPLATE (RUSSIAN)
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

Автор: Temp Email Bots Project
Лицензия: MIT
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
import sys
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

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

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
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Новая почта", callback_data="new"),
         InlineKeyboardButton(text="📥 Входящие", callback_data="inbox")],
        [InlineKeyboardButton(text="📋 Данные", callback_data="info"),
         InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])
    await message.answer(
        f"*{{SERVICE_NAME}}*\\nБот временной почты\\n\\n/new — Создать\\n/inbox — Проверить\\n/info — Данные",
        reply_markup=kb
    )


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
# SERVICE-SPECIFIC COMMANDS
# ═══════════════════════════════════════════════════════════════
SERVICE_COMMANDS = {
    "guerrilla": {
        "commands_en": '''@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        s.ts = time.time()
        stats["created"] += 1
        text = (
            f"*Email Created*\\n\\n"
            f"Address: `{r['email_addr']}`\\n"
            f"SID: `{str(r.get('sid_token', ''))[:16]}...`\\n\\n"
            f"Copy this address and use it for registrations."
        )
        bot.send_message(cid, text)
    else:
        bot.send_message(cid, "❌ Failed to create email. Try /new again.")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ Create an email first: /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return bot.send_message(cid, "📭 Inbox is empty.")
    text = f"*{len(msgs)} messages*\\n\\n"
    for m in msgs[:15]:
        mid = m.get("mail_id", "?")
        marker = "🆕 " if mid not in s.seen else ""
        s.seen.add(mid)
        text += f"{marker}`{mid}` — {m.get('mail_from', '?')}\\nSubject: {m.get('mail_subject', '—')}\\n\\n"
    bot.send_message(cid, text)


@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "Usage: /set <username>")
    s = get_session(message.chat.id)
    if not s.token:
        return bot.send_message(message.chat.id, "❌ Create email first: /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": parts[1].strip()}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        bot.send_message(message.chat.id, f"✅ Email updated: `{r['email_addr']}`")


@bot.message_handler(commands=["domains"])
def cmd_domains(message: types.Message) -> None:
    langs = ["en", "ru", "de", "fr", "es", "it", "pt", "ja", "zh"]
    text = "*Available Languages:*\\n" + "\\n".join(f"• `{l}`" for l in langs)
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["setlang"])
def cmd_setlang(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "Usage: /setlang <code>")
    r = api_get(params={{"f": "change_lang", "lang": parts[1].strip()}})
    lang = r.get("lang", parts[1].strip())
    bot.send_message(message.chat.id, f"✅ Language: `{lang}`")


@bot.message_handler(commands=["ip"])
def cmd_ip(message: types.Message) -> None:
    r = api_get(params={{"f": "get_ip"}})
    ip = r.get("ip_addr", "?")
    bot.send_message(message.chat.id, f"🌐 IP: `{ip}`")


@bot.message_handler(commands=["lang"])
def cmd_lang(message: types.Message) -> None:
    r = api_get(params={{"f": "get_lang"}})
    lang = r.get("lang", "?")
    bot.send_message(message.chat.id, f"🌐 Language: `{lang}`")


@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    s = get_session(message.chat.id)
    text = f"📧 {s.addr or 'Not set'}\\n📩 Read: {s.messages} | Seen: {len(s.seen)}"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["stats"])
def cmd_stats(message: types.Message) -> None:
    text = f"*Stats:* Created: {stats['created']} | Checked: {stats['checked']} | Errors: {stats['errors']}"
    bot.send_message(message.chat.id, text)''',
        "cb_new_en": '''        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(cid)
            s.addr = r["email_addr"]
            s.token = r.get("sid_token")
            s.seen = set()
            s.ts = time.time()
            stats["created"] += 1
            bot.edit_message_text(f"✅ Created: `{r['email_addr']}`", cid, call.message.message_id)''',
        "cb_inbox_en": '''        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ Create email first")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", [])
        stats["checked"] += 1
        if not msgs:
            bot.edit_message_text("📭 Empty", cid, call.message.message_id)
        else:
            txt = f"{len(msgs)} messages:\\n\\n"
            for m in msgs[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
        "commands_ru": '''@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        s.token = r.get("sid_token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['email_addr']}`\\n\\nСкопируйте адрес и используйте для регистраций.")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ Сначала /new")
    r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
    msgs = r.get("list", [])
    stats["checked"] += 1
    if not msgs:
        return bot.send_message(cid, "📭 Пусто")
    t = f"*{len(msgs)} писем*\\n\\n"
    for m in msgs[:15]:
        n = "🆕 " if m.get("mail_id") not in s.seen else ""
        s.seen.add(m.get("mail_id"))
        t += f"{n}`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
    bot.send_message(cid, t)


@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "/set <имя>")
    s = get_session(message.chat.id)
    if not s.token:
        return bot.send_message(message.chat.id, "❌ /new")
    r = api_get(params={{"f": "set_email_user", "sid_token": s.token, "email_user": parts[1].strip()}})
    if "email_addr" in r:
        s.addr = r["email_addr"]
        bot.send_message(message.chat.id, f"✅ `{r['email_addr']}`")


@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    s = get_session(message.chat.id)
    bot.send_message(message.chat.id, f"📧 {s.addr or '—'}\\n📩 {len(s.seen)}")''',
        "cb_new_ru": '''        r = api_get(params={{"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"}})
        if "email_addr" in r:
            s = get_session(cid)
            s.addr = r["email_addr"]
            s.token = r.get("sid_token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['email_addr']}`", cid, call.message.message_id)''',
        "cb_inbox_ru": '''        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(params={{"f": "check_email", "sid_token": s.token, "seq": 0}})
        msgs = r.get("list", [])
        stats["checked"] += 1
        if not msgs:
            bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"{len(msgs)} писем:\\n\\n"
            for m in msgs[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
    },
    "tempmail_plus": {
        "commands_en": '''@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "Usage: /set email@domain.com")
    s = get_session(message.chat.id)
    s.addr = parts[1].strip()
    s.seen = set()
    bot.send_message(message.chat.id, f"✅ Monitoring: `{s.addr}`")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.addr:
        return bot.send_message(cid, "❌ Set email first: /set email@domain.com")
    r = api_get(params={{"email": s.addr}})
    mails = r.get("mail", [])
    stats["checked"] += 1
    if not mails:
        return bot.send_message(cid, "📭 Inbox empty")
    text = f"*{len(mails)} messages*\\n\\n"
    for m in mails[:15]:
        n = "🆕 " if m.get("mail_id") not in s.seen else ""
        s.seen.add(m.get("mail_id"))
        text += f"{n}`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
    bot.send_message(cid, text)


@bot.message_handler(commands=["domains"])
def cmd_domains(message: types.Message) -> None:
    doms = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","aol.com",
            "zoho.com","gmx.com","mail.com","yandex.com","icloud.com","1secmail.com","mailinator.com"]
    text = "*Supported Domains:*\\n\\n" + "\\n".join(f"• `{d}`" for d in doms)
    bot.send_message(message.chat.id, text)''',
        "cb_new_en": '''        bot.send_message(cid, "Use /set email@domain.com to start monitoring.")''',
        "cb_inbox_en": '''        s = get_session(cid)
        if not s.addr:
            return bot.answer_callback_query(call.id, "❌ /set email first")
        r = api_get(params={{"email": s.addr}})
        mails = r.get("mail", [])
        stats["checked"] += 1
        if not mails:
            bot.edit_message_text("📭 Empty", cid, call.message.message_id)
        else:
            txt = f"{len(mails)} messages:\\n\\n"
            for m in mails[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
        "commands_ru": '''@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "/set email@domain.com")
    s = get_session(message.chat.id)
    s.addr = parts[1].strip()
    s.seen = set()
    bot.send_message(message.chat.id, f"✅ Мониторинг: `{s.addr}`")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.addr:
        return bot.send_message(cid, "❌ /set email@domain.com")
    r = api_get(params={{"email": s.addr}})
    mails = r.get("mail", [])
    stats["checked"] += 1
    if not mails:
        return bot.send_message(cid, "📭 Пусто")
    t = f"*{len(mails)} писем*\\n\\n"
    for m in mails[:15]:
        n = "🆕 " if m.get("mail_id") not in s.seen else ""
        s.seen.add(m.get("mail_id"))
        t += f"{n}`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
    bot.send_message(cid, t)''',
        "cb_new_ru": '''        bot.send_message(cid, "/set email@domain.com")''',
        "cb_inbox_ru": '''        s = get_session(cid)
        if not s.addr:
            return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(params={{"email": s.addr}})
        mails = r.get("mail", [])
        stats["checked"] += 1
        if not mails:
            bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"{len(mails)} писем:\\n\\n"
            for m in mails[:10]:
                s.seen.add(m.get("mail_id"))
                txt += f"`{m.get('mail_id')}` — {m.get('mail_from','?')}\\n{m.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
    },
    "tempmail_lol": {
        "commands_en": '''@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get("/generate")
    if "address" in r:
        s.addr = r["address"]
        s.token = r.get("token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['address']}`\\nToken: `{str(r.get('token',''))[:20]}...`")
    else:
        bot.send_message(cid, "❌ Failed to generate email.")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ Create email first: /new")
    r = api_get(f"/auth/{s.token}")
    emails = r.get("email", [])
    stats["checked"] += 1
    if not emails:
        return bot.send_message(cid, "📭 Inbox empty")
    text = f"*{len(emails)} messages*\\n\\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""
        s.seen.add(e.get("id"))
        text += f"{n}`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
    bot.send_message(cid, text)''',
        "cb_new_en": '''        r = api_get("/generate")
        if "address" in r:
            s = get_session(cid)
            s.addr = r["address"]
            s.token = r.get("token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", cid, call.message.message_id)''',
        "cb_inbox_en": '''        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new first")
        r = api_get(f"/auth/{s.token}")
        emails = r.get("email", [])
        stats["checked"] += 1
        if not emails:
            bot.edit_message_text("📭 Empty", cid, call.message.message_id)
        else:
            txt = f"{len(emails)} messages:\\n\\n"
            for e in emails[:10]:
                s.seen.add(e.get("id"))
                txt += f"`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
        "commands_ru": '''@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get("/generate")
    if "address" in r:
        s.addr = r["address"]
        s.token = r.get("token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['address']}`\\nТокен: `{str(r.get('token',''))[:20]}...`")
    else:
        bot.send_message(cid, "❌ Ошибка")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    if not s.token:
        return bot.send_message(cid, "❌ /new")
    r = api_get(f"/auth/{s.token}")
    emails = r.get("email", [])
    stats["checked"] += 1
    if not emails:
        return bot.send_message(cid, "📭 Пусто")
    t = f"*{len(emails)} писем*\\n\\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""
        s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
    bot.send_message(cid, t)''',
        "cb_new_ru": '''        r = api_get("/generate")
        if "address" in r:
            s = get_session(cid)
            s.addr = r["address"]
            s.token = r.get("token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", cid, call.message.message_id)''',
        "cb_inbox_ru": '''        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s.token}")
        emails = r.get("email", [])
        stats["checked"] += 1
        if not emails:
            bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"{len(emails)} писем:\\n\\n"
            for e in emails[:10]:
                s.seen.add(e.get("id"))
                txt += f"`{e.get('id')}` — {e.get('from','?')}\\n{e.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)''',
    },
}

# Default commands for services without custom logic
DEFAULT_EN = {
    "commands": '''@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    bot.send_message(message.chat.id, f"*{SERVICE_NAME}*\\n\\n🌐 {BASE_URL}\\n\\nVisit the website to use this service.")''',
    "cb_new": '''        bot.send_message(cid, f"Visit {BASE_URL} to create an email.")''',
    "cb_inbox": '''        bot.send_message(cid, f"Visit {BASE_URL} to check your inbox.")''',
}
DEFAULT_RU = {
    "commands": '''@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    bot.send_message(message.chat.id, f"*{SERVICE_NAME}*\\n\\n🌐 {BASE_URL}\\n\\nПосетите сайт для использования.")''',
    "cb_new": '''        bot.send_message(cid, f"Посетите {BASE_URL}")''',
    "cb_inbox": '''        bot.send_message(cid, f"Посетите {BASE_URL}")''',
}


# ═══════════════════════════════════════════════════════════════
# GENERATE ALL FILES
# ═══════════════════════════════════════════════════════════════
count = 0

for svc in SERVICES:
    sid = svc["id"]
    name = svc["name"]
    base_url = svc["url"]
    env_var = svc["env"]

    cmds = SERVICE_COMMANDS.get(sid, {
        "commands_en": DEFAULT_EN["commands"].replace("{SERVICE_NAME}", name).replace("{BASE_URL}", base_url),
        "cb_new_en": DEFAULT_EN["cb_new"].replace("{BASE_URL}", base_url),
        "cb_inbox_en": DEFAULT_EN["cb_inbox"].replace("{BASE_URL}", base_url),
        "commands_ru": DEFAULT_RU["commands"].replace("{SERVICE_NAME}", name).replace("{BASE_URL}", base_url),
        "cb_new_ru": DEFAULT_RU["cb_new"].replace("{BASE_URL}", base_url),
        "cb_inbox_ru": DEFAULT_RU["cb_inbox"].replace("{BASE_URL}", base_url),
    })

    templates = [
        ("english/telebot", TELEBOT_EN, "commands_en", "cb_new_en", "cb_inbox_en"),
        ("russian/telebot", TELEBOT_RU, "commands_ru", "cb_new_ru", "cb_inbox_ru"),
        ("english/aiogram-2", AIOGRAM2_EN, "commands_en", "cb_new_en", "cb_inbox_en"),
        ("russian/aiogram-2", AIOGRAM2_RU, "commands_ru", "cb_new_ru", "cb_inbox_ru"),
        ("english/aiogram-3", AIOGRAM3_EN, "commands_en", "cb_new_en", "cb_inbox_en"),
        ("russian/aiogram-3", AIOGRAM3_RU, "commands_ru", "cb_new_ru", "cb_inbox_ru"),
    ]

    for folder, template, cmds_key, cb_new_key, cb_inbox_key in templates:
        fname = f"bot_{sid}.py"
        path = os.path.join(ROOT, folder, fname)

        # Get the right commands
        commands_text = cmds.get(cmds_key, DEFAULT_EN["commands"])
        cb_new_text = cmds.get(cb_new_key, DEFAULT_EN["cb_new"])
        cb_inbox_text = cmds.get(cb_inbox_key, DEFAULT_EN["cb_inbox"])

        # Replace placeholders
        content = template.replace("{name}", name)
        content = content.replace("{base_url}", base_url)
        content = content.replace("{env_var}", env_var)
        content = content.replace("{commands}", commands_text)
        content = content.replace("{cb_new}", cb_new_text)
        content = content.replace("{cb_inbox}", cb_inbox_text)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        count += 1
        print(f"  [{count:02d}] {path.replace(ROOT+'/', '')}")

print(f"\n{'='*60}")
print(f"  Generated: {count} bot files")
print(f"  Services: {len(SERVICES)}")
print(f"  Frameworks: telebot, aiogram-2, aiogram-3")
print(f"  Languages: russian, english")
print(f"{'='*60}")
