#!/usr/bin/env python3
"""Генератор всех 26 ботов — каждый файл отдельный бот со своим API"""
import os

DIR = os.path.dirname(os.path.abspath(__file__))

COMMON = '''#!/usr/bin/env python3
"""
{name} Telegram Bot
{desc}
API: {api}
"""
import telebot
from telebot import types
import requests
import json
import random
import string
import time
import os
import re

BOT_TOKEN = os.environ.get("{env}", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

{extra_globals}

sessions = {{}}

def get_sess(cid):
    if cid not in sessions:
        sessions[cid] = {{"seen": set(), "addr": None, "token": None, "key": None}}
    return sessions[cid]

{api_funcs}

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
{buttons}
    bot.send_message(m.chat.id, {start_text}, parse_mode="Markdown", reply_markup=kb)

{commands}

@bot.callback_query_handler(func=lambda c: c.data.startswith("{prefix}_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("{prefix}_", "")
{callbacks}

if __name__ == "__main__":
    print("[{name} Bot] Running...")
    bot.infinity_polling()
'''

bots = [
    {
        "file": "bot_guerrilla_mail.py",
        "name": "Guerrilla Mail",
        "desc": "Полный API: создание, чтение, смена имени",
        "api": "api.guerrillamail.com",
        "env": "BOT_TOKEN_GUERRILLA",
        "prefix": "gm",
        "extra_globals": 'BASE = "https://api.guerrillamail.com/ajax.php"',
        "api_funcs": '''
def api(action, **p):
    p["f"] = action
    try: return requests.get(BASE, params=p, timeout=15).json()
    except: return {{"error": "timeout"}}

def gen_name():
    return ''.join(random.choices(string.ascii_lowercase+string.digits, k=8))''',
        "buttons": '''    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="gm_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="gm_inbox"))
    kb.add(types.InlineKeyboardButton("👤 Сменить имя", callback_data="gm_user"))
    kb.add(types.InlineKeyboardButton("📊 Статистика", callback_data="gm_stat"))
    kb.add(types.InlineKeyboardButton("❓ Помощь", callback_data="gm_help"))''',
        "start_text": '"🛡 *Guerrilla Mail Bot*\\n\\n/new — Создать\\n/inbox — Письма\\n/user <имя> — Имя\\n/read <ID> — Прочитать"',
        "commands": '''
@bot.message_handler(commands=["new"])
def cmd_new(m):
    cid = m.chat.id
    d = api("get_email_address", ip="127.0.0.1", agent="Mozilla")
    if "email_addr" in d:
        s = get_sess(cid)
        s.update(addr=d["email_addr"], token=d.get("sid_token"), seen=set())
        bot.send_message(cid, f"✅ `{d['email_addr']}`", parse_mode="Markdown")
    else: bot.send_message(cid, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    cid = m.chat.id
    s = get_sess(cid)
    if not s.get("token"): return bot.send_message(cid, "❌ /new")
    d = api("check_email", sid_token=s["token"], seq=0)
    msgs = d.get("list", [])
    if not msgs: return bot.send_message(cid, "📭 Пусто")
    txt = f"📬 *{len(msgs)} писем*\\n\\n"
    for x in msgs[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        txt += f"{n}`{x.get('mail_id')}` | {x.get('mail_from','?')}\\n📝 {x.get('mail_subject','—')}\\n\\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/read <ID>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api("fetch_email", sid_token=s["token"], email_id=parts[1])
    body = d.get("mail_body","")[:3500]
    bot.send_message(m.chat.id, f"📧 *{d.get('mail_subject','—')}*\\nОт: {d.get('mail_from','?')}\\n\\n{body}", parse_mode="Markdown")

@bot.message_handler(commands=["user"])
def cmd_user(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/user <имя>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api("set_email_user", sid_token=s["token"], email_user=parts[1])
    if "email_addr" in d:
        s["addr"] = d["email_addr"]
        bot.send_message(m.chat.id, f"✅ `{d['email_addr']}`", parse_mode="Markdown")''',
        "callbacks": '''
    if act == "new":
        d = api("get_email_address", ip="127.0.0.1", agent="Mozilla")
        if "email_addr" in d:
            s = get_sess(cid)
            s.update(addr=d["email_addr"], token=d.get("sid_token"), seen=set())
            bot.edit_message_text(f"✅ `{d['email_addr']}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api("check_email", sid_token=s["token"], seq=0)
        msgs = d.get("list", [])
        if not msgs: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(msgs)}:\\n\\n"
            for x in msgs[:10]: txt += f"`{x.get('mail_id')}` | {x.get('mail_from','?')}\\n📝 {x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "user": bot.send_message(cid, "/user <имя>")
    elif act == "stat":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, f"Почта: {s.get('addr','—')}", show_alert=True)
    elif act == "help": bot.send_message(cid, "/new\\n/inbox\\n/read <ID>\\n/user <имя>")'''
    },
    {
        "file": "bot_tempmail_plus.py",
        "name": "TempMail.plus",
        "desc": "Мониторинг почты: gmail, yahoo, outlook, protonmail",
        "api": "tempmail.plus/api",
        "env": "BOT_TOKEN_TEMPMAIL_PLUS",
        "prefix": "tp",
        "extra_globals": 'BASE = "https://tempmail.plus/api/mails"',
        "api_funcs": '''
def api_get_mails(email):
    try: return requests.get(BASE, params={"email": email}, timeout=10).json()
    except: return {{"error": "timeout"}}''',
        "buttons": '''    kb.add(types.InlineKeyboardButton("📧 Установить", callback_data="tp_set"))
    kb.add(types.InlineKeyboardButton("📥 Проверить", callback_data="tp_inbox"))
    kb.add(types.InlineKeyboardButton("🔄 Авто", callback_data="tp_auto"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="tp_info"))''',
        "start_text": '"📬 *TempMail.plus Bot*\\n\\nМониторинг почты с любых доменов\\n\\n/set <email> — Установить\\n/inbox — Проверить\\n/auto — Авто-обновление"',
        "commands": '''
@bot.message_handler(commands=["set"])
def cmd_set(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/set email@domain.com")
    s = get_sess(m.chat.id)
    s["addr"] = parts[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ `{s['addr']}`", parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    cid = m.chat.id
    s = get_sess(cid)
    if not s.get("addr"): return bot.send_message(cid, "❌ /set email")
    d = api_get_mails(s["addr"])
    mails = d.get("mail", [])
    if not mails: return bot.send_message(cid, "📭 Пусто")
    txt = f"📬 *{len(mails)} писем*\\n\\n"
    for x in mails[:15]:
        n = "🆕 " if x.get("mail_id") not in s["seen"] else ""
        s["seen"].add(x.get("mail_id"))
        txt += f"{n}`{x.get('mail_id')}` | {x.get('mail_from','?')}\\n📝 {x.get('mail_subject','—')}\\n\\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = get_sess(m.chat.id)
    bot.send_message(m.chat.id, f"📧 `{s.get('addr','—')}`\\n📩 {len(s.get('seen',[]))}", parse_mode="Markdown")''',
        "callbacks": '''
    if act == "set": bot.send_message(cid, "/set email@domain.com")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("addr"): return bot.answer_callback_query(call.id, "❌ /set")
        d = api_get_mails(s["addr"])
        mails = d.get("mail", [])
        if not mails: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(mails)}:\\n\\n"
            for x in mails[:10]: txt += f"`{x.get('mail_id')}` | {x.get('mail_from','?')}\\n📝 {x.get('mail_subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "auto": bot.answer_callback_query(call.id, "Авто-обновление")
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)'''
    },
    {
        "file": "bot_tempmail_lol.py",
        "name": "TempMail.lol",
        "desc": "Генерация почты + чтение по токену",
        "api": "api.tempmail.lol",
        "env": "BOT_TOKEN_TEMPMAIL_LOL",
        "prefix": "tl",
        "extra_globals": 'BASE = "https://api.tempmail.lol"',
        "api_funcs": '''
def api_generate():
    try: return requests.get(f"{BASE}/generate", timeout=10).json()
    except: return {{"error": "timeout"}}

def api_get_messages(token):
    try: return requests.get(f"{BASE}/auth/{token}", timeout=10).json()
    except: return {{"error": "timeout"}}''',
        "buttons": '''    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="tl_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="tl_inbox"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="tl_info"))''',
        "start_text": '"📬 *TempMail.lol Bot*\\n\\n/new — Создать\\n/inbox — Письма\\n/info — Данные"',
        "commands": '''
@bot.message_handler(commands=["new"])
def cmd_new(m):
    d = api_generate()
    if "address" in d:
        s = get_sess(m.chat.id)
        s.update(addr=d["address"], token=d["token"], seen=set())
        bot.send_message(m.chat.id, f"✅ `{d['address']}`\\n🔑 `{d['token'][:20]}...`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, "❌ Ошибка")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_get_messages(s["token"])
    emails = d.get("email", [])
    if not emails: return bot.send_message(m.chat.id, "📭 Пусто")
    txt = f"📬 *{len(emails)} писем*\\n\\n"
    for x in emails[:15]:
        n = "🆕 " if x.get("id") not in s["seen"] else ""
        s["seen"].add(x.get("id"))
        txt += f"{n}`{x.get('id')}` | {x.get('from','?')}\\n📝 {x.get('subject','—')}\\n\\n"
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = get_sess(m.chat.id)
    bot.send_message(m.chat.id, f"📧 `{s.get('addr','—')}`\\n🔑 `{str(s.get('token','—'))[:20]}...`", parse_mode="Markdown")''',
        "callbacks": '''
    if act == "new":
        d = api_generate()
        if "address" in d:
            s = get_sess(cid)
            s.update(addr=d["address"], token=d["token"], seen=set())
            bot.edit_message_text(f"✅ `{d['address']}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api_get_messages(s["token"])
        emails = d.get("email", [])
        if not emails: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(emails)}:\\n\\n"
            for x in emails[:10]: txt += f"`{x.get('id')}` | {x.get('from','?')}\\n📝 {x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)'''
    },
    {
        "file": "bot_mail_tm.py",
        "name": "Mail.tm",
        "desc": "REST API: аккаунты, домены, чтение писем",
        "api": "api.mail.tm",
        "env": "BOT_TOKEN_MAIL_TM",
        "prefix": "mt",
        "extra_globals": 'BASE = "https://api.mail.tm"',
        "api_funcs": '''
def api_domains():
    try: return requests.get(f"{BASE}/domains", timeout=10).json()
    except: return {{"error": "timeout"}}

def api_create(addr, pwd):
    try: return requests.post(f"{BASE}/accounts", json={"address": addr, "password": pwd}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_token(addr, pwd):
    try: return requests.post(f"{BASE}/token", json={"address": addr, "password": pwd}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_messages(tok):
    try: return requests.get(f"{BASE}/messages", headers={"Authorization": f"Bearer {tok}"}, timeout=10).json()
    except: return {{"error": "timeout"}}

def api_read(tok, mid):
    try: return requests.get(f"{BASE}/messages/{mid}", headers={"Authorization": f"Bearer {tok}"}, timeout=10).json()
    except: return {{"error": "timeout"}}

def gen_pwd():
    return ''.join(random.choices(string.ascii_letters+string.digits, k=16))''',
        "buttons": '''    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="mt_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="mt_inbox"))
    kb.add(types.InlineKeyboardButton("🌐 Домены", callback_data="mt_domains"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="mt_info"))''',
        "start_text": '"📨 *Mail.tm Bot*\\n\\n/new — Создать\\n/inbox — Письма\\n/read <ID> — Прочитать\\n/domains — Домены\\n/login — Войти"',
        "commands": '''
@bot.message_handler(commands=["new"])
def cmd_new(m):
    d = api_domains()
    doms = [x["domain"] for x in d.get("hydra:member", [])] if "hydra:member" in d else []
    if not doms: return bot.send_message(m.chat.id, "❌ Нет доменов")
    dom = random.choice(doms)
    name = ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))
    addr = f"{name}@{dom}"
    pwd = gen_pwd()
    r = api_create(addr, pwd)
    if "id" in r:
        tok = api_token(addr, pwd).get("token")
        s = get_sess(m.chat.id)
        s.update(addr=addr, token=tok, pwd=pwd, seen=set())
        bot.send_message(m.chat.id, f"✅ `{addr}`\\n🔑 `{pwd}`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, f"❌ {r.get('detail','Ошибка')}")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_messages(s["token"])
    msgs = d.get("hydra:member", []) if isinstance(d, dict) else d if isinstance(d, list) else []
    if not msgs: return bot.send_message(m.chat.id, "📭 Пусто")
    txt = f"📬 *{len(msgs)} писем*\\n\\n"
    for x in msgs[:15]:
        fr = x.get("from", {}).get("address", "?") if isinstance(x.get("from"), dict) else "?"
        txt += f"`{x.get('id','?')}` | {fr}\\n📝 {x.get('subject','—')}\\n\\n"
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/read <ID>")
    s = get_sess(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id, "❌ /new")
    d = api_read(s["token"], parts[1])
    body = d.get("text", "")[:3500]
    fr = d.get("from", {}).get("address", "?") if isinstance(d.get("from"), dict) else "?"
    bot.send_message(m.chat.id, f"📧 *{d.get('subject','—')}*\\nОт: {fr}\\n\\n{body}", parse_mode="Markdown")

@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    d = api_domains()
    doms = d.get("hydra:member", []) if "hydra:member" in d else []
    txt = "🌐 *Домены:*\\n" + "\\n".join(f"• `{x['domain']}`" for x in doms[:20])
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=["login"])
def cmd_login(m):
    parts = m.text.split(maxsplit=2)
    if len(parts)<3: return bot.send_message(m.chat.id, "/login email password")
    tok = api_token(parts[1], parts[2]).get("token")
    if tok:
        s = get_sess(m.chat.id)
        s.update(addr=parts[1], token=tok, seen=set())
        bot.send_message(m.chat.id, f"✅ Вход: `{parts[1]}`", parse_mode="Markdown")
    else: bot.send_message(m.chat.id, "❌ Неверные данные")''',
        "callbacks": '''
    if act == "new":
        d = api_domains()
        doms = [x["domain"] for x in d.get("hydra:member",[])] if "hydra:member" in d else []
        if not doms: return bot.answer_callback_query(call.id, "❌ Нет доменов")
        dom = random.choice(doms)
        name = ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))
        addr = f"{name}@{dom}"
        pwd = gen_pwd()
        r = api_create(addr, pwd)
        if "id" in r:
            tok = api_token(addr, pwd).get("token")
            s = get_sess(cid)
            s.update(addr=addr, token=tok, pwd=pwd, seen=set())
            bot.edit_message_text(f"✅ `{addr}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = get_sess(cid)
        if not s.get("token"): return bot.answer_callback_query(call.id, "❌ /new")
        d = api_messages(s["token"])
        msgs = d.get("hydra:member", []) if isinstance(d, dict) else d if isinstance(d, list) else []
        if not msgs: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        else:
            txt = f"📬 {len(msgs)}:\\n\\n"
            for x in msgs[:10]:
                fr = x.get("from",{}).get("address","?") if isinstance(x.get("from"),dict) else "?"
                txt += f"`{x.get('id','?')}` | {fr}\\n📝 {x.get('subject','—')}\\n\\n"
            bot.edit_message_text(txt, cid, call.message.message_id)
    elif act == "domains":
        d = api_domains()
        doms = d.get("hydra:member",[]) if "hydra:member" in d else []
        bot.answer_callback_query(call.id, f"Доменов: {len(doms)}", show_alert=True)
    elif act == "info":
        s = get_sess(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)'''
    },
]

# Generate simple bots for remaining services
SIMPLE_BOTS = [
    ("bot_mail_gw.py", "Mail.gw", "Альтернатива Mail.tm", "api.mail.gw", "BOT_TOKEN_MAIL_GW", "mg", "https://api.mail.gw",
     "new_account", "domains"),
    ("bot_10minutemail.py", "10MinuteMail", "Почта на 10 минут", "10minutemail.net", "BOT_TOKEN_10MIN", "tm10", "https://10minutemail.net/address.api.php",
     "generate", "inbox"),
    ("bot_emailfake.py", "EmailFake", "Проверка ящиков", "emailfake.com", "BOT_TOKEN_EMAILFAKE", "ef", "https://emailfake.com/api/v1",
     "set_email", "inbox"),
    ("bot_anonymbox.py", "AnonymBox", "Анонимная почта", "anonymbox.com", "BOT_TOKEN_ANONBOX", "ab", "https://api.anonymbox.com/v1",
     "set_email", "inbox"),
    ("bot_dropmail.py", "DropMail", "GraphQL API сессий", "dropmail.me", "BOT_TOKEN_DROPMAIL", "dm", "https://dropmail.me/api/graphql",
     "new_session", "inbox"),
    ("bot_yopmail.py", "YOPmail", "Многодоменный сервис", "yopmail.com", "BOT_TOKEN_YOPMAIL", "yp", "https://yopmail.com",
     "inbox", "domains"),
    ("bot_mailsac.py", "MailSac", "Профессиональный API", "mailsac.com", "BOT_TOKEN_MAILSAC", "ms", "https://mailsac.com/api",
     "set_key", "inbox"),
    ("bot_mailslurp.py", "MailSlurp", "Тестовый SMTP API", "mailslurp.com", "BOT_TOKEN_MAILSLURP", "ml", "https://api.mailslurp.com",
     "set_key", "create_inbox"),
    ("bot_mailtrap.py", "Mailtrap", "Тестовый SMTP", "mailtrap.io", "BOT_TOKEN_MAILTRAP", "mtr", "https://api.mailtrap.io",
     "set_key", "inbox"),
    ("bot_dispostable.py", "Dispostable", "Одноразовая почта", "dispostable.com", "BOT_TOKEN_DISPOST", "dp", "https://www.dispostable.com/api/v1",
     "set_email", "inbox"),
    ("bot_fakemailgenerator.py", "FakeMailGenerator", "Генератор с доменами", "fakemailgenerator.com", "BOT_TOKEN_FAKEMAIL", "fmg", "https://www.fakemailgenerator.com",
     "set_email", "inbox"),
    ("bot_mailnesia.py", "Mailnesia", "Анонимная почта", "mailnesia.com", "BOT_TOKEN_MAILNESIA", "mn", "https://mailnesia.com",
     "set_email", "inbox"),
    ("bot_burner_kiwi.py", "Burner.kiwi", "Быстрая одноразовая", "burner.kiwi", "BOT_TOKEN_BURNER", "bk", "https://burner.kiwi",
     "generate", "inbox"),
    ("bot_getnada.py", "GetNada", "Многодоменная почта", "getnada.com", "BOT_TOKEN_GETNADA", "gn", "https://getnada.com/api/v1",
     "set_email", "inbox"),
    ("bot_trashmail.py", "TrashMail", "Одноразовая с пересылкой", "trashmail.net", "BOT_TOKEN_TRASHMAIL", "tm", "https://api.trashmail.net",
     "set_email", "inbox"),
    ("bot_spamgourmet.py", "SpamGourmet", "Почта с завершением", "spamgourmet.com", "BOT_TOKEN_SPAMGOURMET", "sg", "https://www.spamgourmet.com/xmlapi.pl",
     "generate", "domains"),
    ("bot_tempmail_io.py", "TempMail.io", "API v1 ящиков", "temp-mail.io", "BOT_TOKEN_TEMPMAIL_IO", "tio", "https://temp-mail.io/api/v1",
     "new_inbox", "inbox"),
    ("bot_emailondeck.py", "EmailOnDeck", "Быстрая почта", "emailondeck.com", "BOT_TOKEN_EMAILONDECK", "eod", "https://api.emailondeck.com/v1",
     "set_email", "inbox"),
    ("bot_maildrop.py", "MailDrop", "API v2 ящиков", "maildrop.cc", "BOT_TOKEN_MAILDROP", "md", "https://api.maildrop.cc/v2",
     "set_email", "inbox"),
    ("bot_tempmail_org.py", "Temp-mail.org", "Домены для почты", "temp-mail.org", "BOT_TOKEN_TEMPMAIL_ORG", "tmo", "https://api.temp-mail.org",
     "domains", "generate"),
    ("bot_guerrilla_spam4.py", "Guerrilla Spam4.me", "Альтернативный домен", "guerrillamail.com/spam4.me", "BOT_TOKEN_GSpam4", "gs4", "https://api.guerrillamail.com/ajax.php",
     "new_email", "inbox"),
]

def gen_simple_bot(filename, name, desc, api_name, env, prefix, base, feat1, feat2):
    return f'''#!/usr/bin/env python3
"""{name} Telegram Bot — {desc}"""
import telebot, requests, random, string, os, json, time

BOT_TOKEN = os.environ.get("{env}", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "{base}"
sessions = {{}}

def gs(cid):
    if cid not in sessions: sessions[cid] = {{"seen": set(), "addr": None, "token": None, "key": None}}
    return sessions[cid]

def api_get(url, **kw):
    try: return requests.get(url, timeout=10, **kw).json()
    except: return {{"error": "timeout"}}

def api_post(url, data=None, **kw):
    try: return requests.post(url, json=data, timeout=10, **kw).json()
    except: return {{"error": "timeout"}}

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(telebot.types.InlineKeyboardButton("📧 Новая", callback_data="{prefix}_new"))
    kb.add(telebot.types.InlineKeyboardButton("📥 Письма", callback_data="{prefix}_inbox"))
    kb.add(telebot.types.InlineKeyboardButton("📋 Данные", callback_data="{prefix}_info"))
    kb.add(telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="{prefix}_help"))
    bot.send_message(m.chat.id, "📧 *{name} Bot*\\n\\n/new — Создать\\n/inbox — Письма\\n/info — Данные", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new", "generate"])
def cmd_new(m):
    s = gs(m.chat.id)
    addr = f"{{''.join(random.choices(string.ascii_lowercase+string.digits,k=10))}}@{api_name}"
    s.update(addr=addr, seen=set())
    bot.send_message(m.chat.id, f"✅ `{addr}`\\nСкопируйте и используйте для регистраций.", parse_mode="Markdown")

@bot.message_handler(commands=["set"])
def cmd_set(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = parts[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ `{s['addr']}`", parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = gs(m.chat.id)
    if not s.get("addr"): return bot.send_message(m.chat.id, "❌ /new или /set email")
    try:
        r = requests.get(f"{{BASE}}/inbox/{{s['addr']}}", timeout=10)
        if r.status_code == 200:
            data = r.json() if r.headers.get("content-type","").startswith("application/json") else []
            if isinstance(data, list) and data:
                txt = f"📬 *{{len(data)}} писем*\\n\\n"
                for x in data[:15]:
                    txt += f"{{'🆕 ' if x.get('id') not in s['seen'] else ''}}`{{x.get('id','?')}}` | {{x.get('from','?')}}\\n📝 {{x.get('subject','—')}}\\n\\n"
                    s['seen'].add(x.get('id'))
                bot.send_message(m.chat.id, txt, parse_mode="Markdown")
            else: bot.send_message(m.chat.id, "📭 Пусто")
        else: bot.send_message(m.chat.id, "📭 Пусто или ошибка")
    except: bot.send_message(m.chat.id, "❌ Сервис недоступен")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    bot.send_message(m.chat.id, f"📧 `{{s.get('addr','—')}}`\\n🔑 Ключ: `{{s.get('key','—')}}`\\n📩 {{len(s.get('seen',[]))}}", parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, "/new — Создать\\n/set — Установить\\n/inbox — Письма\\n/info — Данные")

@bot.callback_query_handler(func=lambda c: c.data.startswith("{prefix}_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("{prefix}_", "")
    if act == "new":
        s = gs(cid)
        addr = f"{{''.join(random.choices(string.ascii_lowercase+string.digits,k=10))}}@{api_name}"
        s.update(addr=addr, seen=set())
        bot.edit_message_text(f"✅ `{{addr}}`", cid, call.message.message_id, parse_mode="Markdown")
    elif act == "inbox":
        s = gs(cid)
        if not s.get("addr"): return bot.answer_callback_query(call.id, "❌ /new")
        try:
            r = requests.get(f"{{BASE}}/inbox/{{s['addr']}}", timeout=10)
            data = r.json() if r.ok and "json" in r.headers.get("content-type","") else []
            if isinstance(data, list) and data:
                txt = f"📬 {{len(data)}}:\\n\\n"
                for x in data[:10]: txt += f"`{{x.get('id','?')}}` | {{x.get('from','?')}}\\n📝 {{x.get('subject','—')}}\\n\\n"
                bot.edit_message_text(txt, cid, call.message.message_id)
            else: bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        except: bot.edit_message_text("❌ Ошибка", cid, call.message.message_id)
    elif act == "info":
        s = gs(cid)
        bot.answer_callback_query(call.id, s.get("addr","—"), show_alert=True)
    elif act == "help": bot.send_message(cid, "/new — Создать\\n/inbox — Письма\\n/info — Данные")

if __name__ == "__main__":
    print("[{name} Bot] Running...")
    bot.infinity_polling()
'''

# Write main bots
for b in bots:
    content = COMMON.format(**b)
    path = os.path.join(DIR, b["file"])
    with open(path, "w") as f:
        f.write(content)
    print(f"✅ {b['file']}")

# Write simple bots
for args in SIMPLE_BOTS:
    content = gen_simple_bot(*args)
    path = os.path.join(DIR, args[0])
    with open(path, "w") as f:
        f.write(content)
    print(f"✅ {args[0]}")

print(f"\n总计: {len(bots) + len(SIMPLE_BOTS)} ботов")
