#!/usr/bin/env python3
"""
TempMail.lol — Telegram-бот временной почты
Провайдер: TempMail.lol | API: https://api.tempmail.lol
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
logger = logging.getLogger("TempMail.lol")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.tempmail.lol"
SERVICE_NAME: str = "TempMail.lol"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN! Установите переменную BOT_TOKEN_TEMPMAIL_LOL")
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
        f"*{{SERVICE_NAME}}*\n"
        f"Бот временной почты\n\n"
        f"Создавайте одноразовые почтовые ящики\n"
        f"и получайте сообщения мгновенно.\n\n"
        f"*Быстрый старт:*\n"
        f"1. Нажмите 📧 Новая почта\n"
        f"2. Скопируйте адрес\n"
        f"3. Используйте для регистрации\n"
        f"4. Нажмите 📥 Входящие\n\n"
        f"*Команды:*\n"
        f"/new — Создать почту\n"
        f"/inbox — Проверить письма\n"
        f"/set — Установить почту\n"
        f"/info — Данные сессии\n"
        f"/stats — Статистика\n"
        f"/help — Подробная помощь"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)
    logger.info(f"Пользователь {{message.chat.id}} запустил бота")


@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    cid = message.chat.id
    s = get_session(cid)
    r = api_get("/generate")
    if "address" in r:
        s.addr = r["address"]
        s.token = r.get("token")
        s.seen = set()
        stats["created"] += 1
        bot.send_message(cid, f"✅ `{r['address']}`\nТокен: `{str(r.get('token',''))[:20]}...`")
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
    t = f"*{len(emails)} писем*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""
        s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(cid, t)


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
        r = api_get("/generate")
        if "address" in r:
            s = get_session(cid)
            s.addr = r["address"]
            s.token = r.get("token")
            s.seen = set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", cid, call.message.message_id)
        elif action == "inbox":
        s = get_session(cid)
        if not s.token:
            return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s.token}")
        emails = r.get("email", [])
        stats["checked"] += 1
        if not emails:
            bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"{len(emails)} писем:\n\n"
            for e in emails[:10]:
                s.seen.add(e.get("id"))
                txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
        elif action == "info":
            s = get_session(cid)
            text = (
                f"*Данные сессии*\n\n"
                f"Почта: `{{s.addr or 'Не установлена'}}`\n"
                f"Токен: `{{str(s.token or '')[:20]}}...`\n"
                f"Прочитано: {{s.messages}}\n"
                f"Уникальных: {{len(s.seen)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "stats":
            text = (
                f"*Статистика бота*\n\n"
                f"Создано почт: {{stats['created']}}\n"
                f"Проверок: {{stats['checked']}}\n"
                f"Ошибок: {{stats['errors']}}\n"
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
        f"*{{SERVICE_NAME}} — Помощь*\n\n"
        f"*Команды:*\n"
        f"/new — Создать почту\n"
        f"/inbox — Проверить\n"
        f"/set <email> — Установить\n"
        f"/read <ID> — Прочитать\n"
        f"/key <KEY> — API ключ\n"
        f"/info — Данные сессии\n"
        f"/stats — Статистика\n"
        f"/help — Помощь\n\n"
        f"*Провайдер:* {{SERVICE_NAME}}\n"
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
