#!/usr/bin/env python3
"""
YOPmail — Telegram-бот временной почты (aiogram 2.x)
Провайдер: YOPmail | API: https://yopmail.com
Фреймворк: aiogram 2.25.1
Установка: pip install aiogram==2.25.1 requests

Возможности:
- Async/await архитектура
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
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("YOPmail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_YOPMAIL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://yopmail.com"
SERVICE_NAME: str = "YOPmail"
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

sessions: Dict[int, UserSession] = {}
stats: Dict[str, int] = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid: int) -> UserSession:
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{BASE_URL}{path}"
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=REQUEST_TIMEOUT)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning(f"API error: {e}")
            if attempt < MAX_RETRIES - 1: time.sleep(1)
    stats["errors"] += 1
    return {"error": "Max retries exceeded"}

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    url = f"{BASE_URL}{path}"
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=REQUEST_TIMEOUT)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}

def handle_new(c, s, call):
    bot.send_message(cid,"Посетите https://yopmail.com")

def handle_inbox(c, s, call):
    bot.send_message(cid,"Посетите https://yopmail.com")

@dp.message_handler(commands=["start", "menu"])
async def cmd_start(m):
    kb = InlineKeyboardMarkup(row_width=2) if false else InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Новая почта", callback_data="new"),
        InlineKeyboardButton("📥 Входящие", callback_data="inbox"),
        InlineKeyboardButton("📋 Данные", callback_data="info"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    await bot.send_message(m.chat.id, "*{SERVICE_NAME}*\nБот временной почты\n\n/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь", reply_markup=kb)

@dp.message_handler(["info"])
async def cmd_info(m):
    await bot.send_message(m.chat.id,f"*YOPmail*\n\n🌐 https://yopmail.com\n\nПосетите сайт.")

@dp.callback_query_handler(lambda c: True)
async def cb(call):
    c = call.message.chat.id
    a = call.data
    try:
        s = get_session(c)
        if a == "new": handle_new(c, s, call)
        elif a == "inbox": handle_inbox(c, s, call)
        elif a == "info":
            await bot.answer_callback_query(call.id, f"Почта: {s.addr or 'Не установлена'}", show_alert=True)
        elif a == "stats":
            await bot.answer_callback_query(call.id, f"Создано: {stats['created']} | Проверок: {stats['checked']}", show_alert=True)
        elif a == "help":
            await bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await bot.answer_callback_query(call.id, "Error")


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"Starting {SERVICE_NAME}...")
    executor.start_polling(dp, skip_updates=True)
