#!/usr/bin/env python3
"""Simple generator: writes bot files with direct string replacement."""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    ("guerrilla", "Guerrilla Mail", "https://api.guerrillamail.com/ajax.php", "BOT_TOKEN_GUERRILLA"),
    ("tempmail_plus", "TempMail.plus", "https://tempmail.plus/api/mails", "BOT_TOKEN_TEMPMAIL_PLUS"),
    ("tempmail_lol", "TempMail.lol", "https://api.tempmail.lol", "BOT_TOKEN_TEMPMAIL_LOL"),
    ("mail_tm", "Mail.tm", "https://api.mail.tm", "BOT_TOKEN_MAIL_TM"),
    ("10minutemail", "10MinuteMail", "https://10minutemail.net/address.api.php", "BOT_TOKEN_10MINUTEMAIL"),
    ("emailfake", "EmailFake", "https://emailfake.com/api/v1", "BOT_TOKEN_EMAILFAKE"),
    ("anonymbox", "AnonymBox", "https://api.anonymbox.com/v1", "BOT_TOKEN_ANONYMBOX"),
    ("mailsac", "MailSac", "https://mailsac.com/api", "BOT_TOKEN_MAILSAC"),
    ("mailslurp", "MailSlurp", "https://api.mailslurp.com", "BOT_TOKEN_MAILSLURP"),
    ("yopmail", "YOPmail", "https://yopmail.com", "BOT_TOKEN_YOPMAIL"),
    ("burner_kiwi", "Burner.kiwi", "https://burner.kiwi", "BOT_TOKEN_BURNER"),
    ("mailnesia", "Mailnesia", "https://mailnesia.com", "BOT_TOKEN_MAILNESIA"),
    ("emailnator", "EmailNator", "https://www.emailnator.com", "BOT_TOKEN_EMAILNATOR"),
    ("emailondeck", "EmailOnDeck", "https://api.emailondeck.com/v1", "BOT_TOKEN_EMAILONDECK"),
]

# Service-specific command handlers (as raw strings, no f-strings)
HANDLERS = {
    "guerrilla": {
        "en": '''def handle_new(c, s, call):
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr,r["email_addr"]; s.token=r.get("sid_token"); s.seen=set(); s.ts=time.time()
        stats["created"]+=1
        bot.edit_message_text("Created: "+r["email_addr"],c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Failed")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"Create email first")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return bot.edit_message_text("Empty",c,call.message.message_id)
    txt=""
    for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
    bot.edit_message_text(str(len(msgs))+" messages:\\n\\n"+txt,c,call.message.message_id)''',
        "ru": '''def handle_new(c, s, call):
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr=r["email_addr"]; s.token=r.get("sid_token"); s.seen=set(); s.ts=time.time()
        stats["created"]+=1
        bot.edit_message_text("Создано: "+r["email_addr"],c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Ошибка")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"Сначала /new")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return bot.edit_message_text("Пусто",c,call.message.message_id)
    txt=""
    for x in msgs[:10]: s.seen.add(x.get("mail_id")); txt+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
    bot.edit_message_text(str(len(msgs))+" писем:\\n\\n"+txt,c,call.message.message_id)''',
    },
    "tempmail_plus": {
        "en": '''def handle_new(c, s, call):
    bot.send_message(c,"Use /set email@domain.com")

def handle_inbox(c, s, call):
    if not s.addr: return bot.answer_callback_query(call.id,"Set email first")
    r=api_get(params={"email":s.addr}); mails=r.get("mail",[]); stats["checked"]+=1
    if not mails: return bot.edit_message_text("Empty",c,call.message.message_id)
    txt=""
    for x in mails[:10]: s.seen.add(x.get("mail_id")); txt+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
    bot.edit_message_text(str(len(mails))+" messages:\\n\\n"+txt,c,call.message.message_id)''',
        "ru": '''def handle_new(c, s, call):
    bot.send_message(c,"/set email@domain.com")

def handle_inbox(c, s, call):
    if not s.addr: return bot.answer_callback_query(call.id,"Установите email")
    r=api_get(params={"email":s.addr}); mails=r.get("mail",[]); stats["checked"]+=1
    if not mails: return bot.edit_message_text("Пусто",c,call.message.message_id)
    txt=""
    for x in mails[:10]: s.seen.add(x.get("mail_id")); txt+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
    bot.edit_message_text(str(len(mails))+" писем:\\n\\n"+txt,c,call.message.message_id)''',
    },
    "tempmail_lol": {
        "en": '''def handle_new(c, s, call):
    r=api_get("/generate")
    if "address" in r:
        s.addr=r["address"]; s.token=r.get("token"); s.seen=set()
        stats["created"]+=1
        bot.edit_message_text("Created: "+r["address"],c,call.message.message_id)
    else: bot.answer_callback_query(call.id,"Failed")

def handle_inbox(c, s, call):
    if not s.token: return bot.answer_callback_query(call.id,"Create email first")
    r=api_get("/auth/"+s.token); emails=r.get("email",[]); stats["checked"]+=1
    if not emails: return bot.edit_message_text("Empty",c,call.message.message_id)
    txt=""
    for e in emails[:10]: s.seen.add(e.get("id")); txt+=e.get("id","?")+" - "+e.get("from","?")+" "+e.get("subject","-")+"\\n"
    bot.edit_message_text(str(len(emails))+" messages:\\n\\n"+txt,c,call.message.message_id)''',
        "ru": '''def handle_new(c, s, call):
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
    for e in emails[:10]: s.seen.add(e.get("id")); txt+=e.get("id","?")+" - "+e.get("from","?")+" "+e.get("subject","-")+"\\n"
    bot.edit_message_text(str(len(emails))+" писем:\\n\\n"+txt,c,call.message.message_id)''',
    },
}

DEFAULT_HANDLER = {
    "en": '''def handle_new(c, s, call):
    bot.send_message(c,"Visit the website")

def handle_inbox(c, s, call):
    bot.send_message(c,"Visit the website")''',
    "ru": '''def handle_new(c, s, call):
    bot.send_message(c,"Посетите сайт")

def handle_inbox(c, s, call):
    bot.send_message(c,"Посетите сайт")''',
}


def gen_telebot(sid, name, url, env, lang):
    is_en = lang == "en"
    h = HANDLERS.get(sid, DEFAULT_HANDLER)
    handler = h.get(lang, h["en"])

    author = "Vladislav Sofronov (cpner)" if is_en else "Владислав Софронов (cpner)"
    contact = "feedback@gondon.su | t.me/reejb | gondon.su"

    if is_en:
        new_btn = "New Email"
        inbox_btn = "Inbox"
        info_btn = "Info"
        stats_btn = "Stats"
        help_btn = "Help"
        start = name+" Telegram Bot\\n\\n/new - Create\\n/inbox - Check\\n/set - Set email\\n/info - Info\\n/help - Help"
        info_txt = "Email: Not set"
        stats_txt = "Created: 0"
        help_txt = "/new - Create\\n/inbox - Check\\n/set - Set\\n/info - Info"
        cmd_new = '''@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=get_session(c)
    r=api_get(params={"f":"get_email_address","ip":"127.0.0.1","agent":"Mozilla"})
    if "email_addr" in r:
        s.addr=r["email_addr"]; s.token=r.get("sid_token"); s.seen=set(); s.ts=time.time()
        stats["created"]+=1
        bot.send_message(c,"Created: "+r["email_addr"])
    else: bot.send_message(c,"Failed")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=get_session(c)
    if not s.token: return bot.send_message(c,"Create email first")
    r=api_get(params={"f":"check_email","sid_token":s.token,"seq":0})
    msgs=r.get("list",[]); stats["checked"]+=1
    if not msgs: return bot.send_message(c,"Empty")
    t=str(len(msgs))+" messages:\\n\\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
    bot.send_message(c,t)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"Usage: /set <username>")
    s=get_session(m.chat.id)
    if not s.token: return bot.send_message(m.chat.id,"Create email first")
    r=api_get(params={"f":"set_email_user","sid_token":s.token,"email_user":p[1].strip()})
    if "email_addr" in r: s.addr=r["email_addr"]; bot.send_message(m.chat.id,"Email: "+r["email_addr"])

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s=get_session(m.chat.id)
    bot.send_message(m.chat.id,"Email: "+str(s.addr or "Not set")+" Seen: "+str(len(s.seen)))'''
        cb_handler = '''@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c=call.message.chat.id; a=call.data
    try:
        s=get_session(c)
        if a=="new": handle_new(c,s,call)
        elif a=="inbox": handle_inbox(c,s,call)
        elif a=="info": bot.answer_callback_query(call.id,"Email: "+str(s.addr or "Not set"),show_alert=True)
        elif a=="stats": bot.answer_callback_query(call.id,"Created: "+str(stats["created"])+" Checked: "+str(stats["checked"]),show_alert=True)
        elif a=="help": bot.send_message(c,"/new - Create\\n/inbox - Check\\n/info - Info")
    except Exception as e:
        logger.error("Error: "+str(e))
        bot.answer_callback_query(call.id,"Error")'''
    else:
        new_btn = "Новая почта"
        inbox_btn = "Входящие"
        info_btn = "Данные"
        stats_btn = "Статистика"
        help_btn = "Помощь"
        start = name+" Telegram-бот\\n\\n/new - Создать\\n/inbox - Проверить\\n/set - Установить\\n/info - Данные\\n/help - Помощь"
        info_txt = "Почта: Не установлена"
        stats_txt = "Создано: 0"
        help_txt = "/new - Создать\\n/inbox - Проверить\\n/set - Установить\\n/info - Данные"
        cmd_new = '''@bot.message_handler(commands=["new"])
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
    t=str(len(msgs))+" писем:\\n\\n"
    for x in msgs[:15]:
        s.seen.add(x.get("mail_id"))
        t+=x.get("mail_id","?")+" - "+x.get("mail_from","?")+" "+x.get("mail_subject","-")+"\\n"
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
    bot.send_message(m.chat.id,"Почта: "+str(s.addr or "—")+" Прочитано: "+str(len(s.seen)))'''
        cb_handler = '''@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    c=call.message.chat.id; a=call.data
    try:
        s=get_session(c)
        if a=="new": handle_new(c,s,call)
        elif a=="inbox": handle_inbox(c,s,call)
        elif a=="info": bot.answer_callback_query(call.id,"Почта: "+str(s.addr or "—"),show_alert=True)
        elif a=="stats": bot.answer_callback_query(call.id,"Создано: "+str(stats["created"])+" Проверок: "+str(stats["checked"]),show_alert=True)
        elif a=="help": bot.send_message(c,"/new - Создать\\n/inbox - Проверить\\n/info - Данные")
    except Exception as e:
        logger.error("Ошибка: "+str(e))
        bot.answer_callback_query(call.id,"Ошибка")'''

    return '''#!/usr/bin/env python3
"""
{name} Telegram Bot
Provider: {name} | API: {url}
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests
Author: {author}
Contact: {contact}
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
    return {{"error": "Max retries exceeded"}}

def api_post(path="", data=None, headers=None):
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {{}}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {{"text": r.text[:500]}}
    except Exception as e:
        stats["errors"] += 1
        return {{"error": str(e)}}
{handler}

@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("{new_btn}", callback_data="new"),
        types.InlineKeyboardButton("{inbox_btn}", callback_data="inbox"),
        types.InlineKeyboardButton("{info_btn}", callback_data="info"),
        types.InlineKeyboardButton("{stats_btn}", callback_data="stats"),
        types.InlineKeyboardButton("{help_btn}", callback_data="help"),
    )
    bot.send_message(m.chat.id, "{start}", reply_markup=kb)
{cmd_new}

{cb_handler}

def signal_handler(sig, frame):
    logger.info("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting " + SERVICE_NAME + "...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
'''.format(name=name, url=url, env=env, author=author, contact=contact,
           new_btn=new_btn, inbox_btn=inbox_btn, info_btn=info_btn, stats_btn=stats_btn, help_btn=help_btn,
           start=start, handler=handler, cmd_new=cmd_new, cb_handler=cb_handler)


count = 0
for sid, name, url, env in SERVICES:
    for folder, lang in [("english/telebot","en"),("russian/telebot","ru")]:
        path = os.path.join(ROOT, folder, "bot_"+sid+".py")
        content = gen_telebot(sid, name, url, env, lang)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: f.write(content)
        count += 1
        print(f"  [{count:02d}] {path.replace(ROOT+'/', '')}")

print(f"\n  Generated: {count} files")
