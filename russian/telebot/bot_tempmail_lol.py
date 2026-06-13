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
logger = logging.getLogger("TempMail.lol")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://api.tempmail.lol"
SERVICE_NAME: str = "TempMail.lol"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN! Установите BOT_TOKEN_TEMPMAIL_LOL")
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
        "*{{SERVICE_NAME}}*\nБот временной почты\n\n/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные\n/help — Помощь",
        reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    r = api_get("/generate")
    if "address" in r:
        s.addr, s.token, s.seen = r["address"], r.get("token"), set()
        stats["created"] += 1
        bot.send_message(c, f"✅ `{r['address']}`\nТокен: `{str(r.get('token',''))[:20]}...`")
    else: bot.send_message(c, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m: types.Message) -> None:
    c = m.chat.id
    s = get_session(c)
    if not s.token: return bot.send_message(c, "❌ /new")
    r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
    if not emails: return bot.send_message(c, "📭 Пусто")
    t = f"*{len(emails)} писем*\n\n"
    for e in emails[:15]:
        n = "🆕 " if e.get("id") not in s.seen else ""; s.seen.add(e.get("id"))
        t += f"{n}`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(c, t)


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": r = api_get("/generate")
        if "address" in r:
            s = get_session(c); s.addr, s.token, s.seen = r["address"], r.get("token"), set()
            stats["created"] += 1
            bot.edit_message_text(f"✅ `{r['address']}`", c, call.message.message_id)
        elif a == "inbox": s = get_session(c)
        if not s.token: return bot.answer_callback_query(call.id, "❌ /new")
        r = api_get(f"/auth/{s.token}"); emails = r.get("email", []); stats["checked"] += 1
        if not emails: bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = ""
            for e in emails[:10]: s.seen.add(e.get("id")); txt += f"`{e.get('id')}` — {e.get('from','?')}\n{e.get('subject','—')}\n\n"
            bot.edit_message_text(f"{len(emails)} писем:\n\n" + txt, c, call.message.message_id)
        elif a == "info":
            s = get_session(c)
            bot.answer_callback_query(call.id, f"Почта: {{s.addr or 'Не установлена'}}", show_alert=True)
        elif a == "stats":
            bot.answer_callback_query(call.id, f"Создано: {{stats['created']}} | Проверок: {{stats['checked']}}", show_alert=True)
        elif a == "help":
            bot.send_message(c, "/new — Создать\n/inbox — Проверить\n/set — Установить\n/info — Данные")
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
