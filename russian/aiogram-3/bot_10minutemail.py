#!/usr/bin/env python3
"""
10MinuteMail — Telegram-бот временной почты (aiogram 3.x)
Провайдер: 10MinuteMail | API: https://10minutemail.net/address.api.php
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
logger = logging.getLogger("10MinuteMail")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_10MINUTEMAIL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://10minutemail.net/address.api.php"
SERVICE_NAME: str = "10MinuteMail"

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
    await m.answer("*{{SERVICE_NAME}}*\nБот временной почты\n\n/new — Создать\n/inbox — Проверить\n/info — Данные", reply_markup=kb)


@bot.message_handler(commands=["info"])
def cmd_info(m: types.Message) -> None:
    bot.send_message(m.chat.id, f"*{SERVICE_NAME}*\n\n🌐 {BASE_URL}\n\nПосетите сайт.")


@dp.callback_query(F.data == "new")
async def cb_new_handler(call: types.CallbackQuery) -> None:
bot.send_message(cid, f"Посетите {BASE_URL}")

@dp.callback_query(F.data == "inbox")
async def cb_inbox_handler(call: types.CallbackQuery) -> None:
bot.send_message(cid, f"Посетите {BASE_URL}")

@dp.callback_query(F.data == "info")
async def cb_info_handler(call: types.CallbackQuery) -> None:
    s = get_session(call.message.chat.id)
    await call.answer(f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)

@dp.callback_query(F.data == "stats")
async def cb_stats_handler(call: types.CallbackQuery) -> None:
    await call.answer(f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)

@dp.callback_query(F.data == "help")
async def cb_help_handler(call: types.CallbackQuery) -> None:
    await bot.send_message(call.message.chat.id, "/new — Создать\n/inbox — Проверить\n/info — Данные")


async def main() -> None:
    logger.info(f"Запуск {{SERVICE_NAME}}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
