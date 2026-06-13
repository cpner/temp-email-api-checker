#!/usr/bin/env python3
"""
TempMail.lol Telegram Bot
Provider: TempMail.lol | API: https://api.tempmail.lol
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests
Author: Владислав Софронов (cpner)
Contact: feedback@gondon.su | t.me/reejb | gondon.su
License: MIT
"""
import telebot
from telebot import types
import requests
import random, string, time, os, signal, sys, logging
from typing import Optional, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TempMail.lol")

BOT_TOKEN = os.environ.get("BOT_TOKEN_TEMPMAIL_LOL", "YOUR_BOT_TOKEN")
BASE_URL = "https://api.tempmail.lol"
SERVICE_NAME = "TempMail.lol"

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

sessions = {}
stats = {"created": 0, "checked": 0, "errors": 0}

def get_session(uid):
    if uid not in sessions: sessions[uid] = UserSession()
    return sessions[uid]

def api_get(path="", params=None, headers=None):
    url = BASE_URL + path
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning("API error: " + str(e))
            if attempt < 2: time.sleep(1)
    stats["errors"] += 1
    return {"error": "Max retries exceeded"}

def api_post(path="", data=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}
def handle_new(c, s, call):
    r=api_get("/generate")
    if "address" in r:
        s.addr=r["address"]; s.token=r.get("token"); s.seen=set()
        stats["created"]+=1
        bot.edit_message_text("Создано: "+r["address"],c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Ошибка")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"Сначала /new")
    r=api_get("/auth/"+s.token); emails=r.get("email",[]); stats["checked"]+=1
    if not emails: return bot.edit_message_text("Пусто",c,call.message.message_id)
    txt=""
    for e in emails[:10]: s.seen.add(e.get("id")); txt+=e.get("id","?")+" - "+e.get("from","?")+" "+e.get("subject","-")+"\n"
    bot.edit_message_text(str(len(emails))+" писем:\n\n"+txt,c,call.message.message_id)

@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Новая почта", callback_data="new"),
        types.InlineKeyboardButton("Входящие", callback_data="inbox"),
        types.InlineKeyboardButton("Данные", callback_data="info"),
        types.InlineKeyboardButton("Статистика", callback_data="stats"),
        types.InlineKeyboardButton("Помощь", callback_data="help"),
    )
    bot.send_message(m.chat.id, "TempMail.lol Telegram-бот\n\n/new - Создать\n/inbox - Проверить\n/set - Установить\n/info - Данные\n/help - Помощь", reply_markup=kb)
@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=get_session(c)
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr=r["email_addr"]; s.token=r.get("sid_token"); s.seen=set(); s.ts=time.time()
        stats["created"]+=1
        bot.send_message(c,"Создано: "+r["email_addr"])
    else: bot.send_message(c,"Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=get_session(c)
    if not s.token: return bot.send_message(c,"Сначала /new")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return bot.send_message(c,"Пусто")
    t=str(len(msgs))+" писем:\n\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\n"
    bot.send_message(c,t)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/set <имя>")
    s=get_session(m.chat.id)
    if not s.token: return bot.send_message(m.chat.id,"Сначала /new")
    r=api_get(params={"f":"set_email_user","sid_token":s.token,"email_user":p[1].strip()})
    if "email_addr" in r: s.addr=r["email_addr"]; bot.send_message(m.chat.id,"Почта: "+r["email_addr"])

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s=get_session(m.chat.id)
    bot.send_message(m.chat.id,"Почта: "+str(s.addr or "—")+" Прочитано: "+str(len(s.seen)))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c=call.message.chat.id; a=call.data
    try:
        s=get_session(c)
        if a=="new": handle_new(c,s,call)
        elif a=="inbox": handle_inbox(c,s,call)
        elif a=="info": bot.answer_callback_query(call.id,"Почта: "+str(s.addr or "—"),show_alert=True)
        elif a=="stats": bot.answer_callback_query(call.id,"Создано: "+str(stats["created"])+" Проверок: "+str(stats["checked"]),show_alert=True)
        elif a=="help": bot.send_message(c,"/new - Создать\n/inbox - Проверить\n/info - Данные")
    except Exception as e:
        logger.error("Ошибка: "+str(e))
        bot.answer_callback_query(call.id,"Ошибка")

def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
