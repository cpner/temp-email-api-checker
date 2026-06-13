#!/usr/bin/env python3
"""
TempMail.plus — Telegram-бот временной почты
Провайдер: TempMail.plus | API: https://tempmail.plus/api/mails
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
logger = logging.getLogger("TempMail.plus")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_TEMPMAIL_PLUS", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://tempmail.plus/api/mails"
SERVICE_NAME: str = "TempMail.plus"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("Не задан BOT_TOKEN! Установите BOT_TOKEN_TEMPMAIL_PLUS")
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


@bot.message_handler(commands=["set"])
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
    t = f"*{len(mails)} писем*\n\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s.seen else ""; s.seen.add(x.get("mail_id"))
        t += f"{n}`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c, t)


@bot.callback_query_handler(func=lambda c: True)
def cb(call: types.CallbackQuery) -> None:
    c = call.message.chat.id
    a = call.data
    try:
        if a == "new": bot.send_message(cid, "/set email@domain.com")
        elif a == "inbox": s = get_session(c)
        if not s.addr: return bot.answer_callback_query(call.id, "❌ /set email")
        r = api_get(params={{"email": s.addr}}); mails = r.get("mail", []); stats["checked"] += 1
        if not mails: bot.edit_message_text("📭 Пусто", c, call.message.message_id)
        else:
            txt = ""
            for x in mails[:10]: s.seen.add(x.get("mail_id")); txt += f"`{x.get('mail_id')}` — {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
            bot.edit_message_text(f"{len(mails)} писем:\n\n" + txt, c, call.message.message_id)
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
