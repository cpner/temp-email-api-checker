#!/usr/bin/env python3
"""Generate simple bot files"""
import os

DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    ("bot_mail_gw.py", "Mail.gw", "Альтернатива Mail.tm", "mail.gw", "BOT_TOKEN_MAIL_GW", "mg", "https://api.mail.gw"),
    ("bot_10minutemail.py", "10MinuteMail", "Почта на 10 минут", "10minutemail.net", "BOT_TOKEN_10MIN", "tm10", "https://10minutemail.net/address.api.php"),
    ("bot_emailfake.py", "EmailFake", "Проверка ящиков", "emailfake.com", "BOT_TOKEN_EMAILFAKE", "ef", "https://emailfake.com/api/v1"),
    ("bot_anonymbox.py", "AnonymBox", "Анонимная почта", "anonymbox.com", "BOT_TOKEN_ANONBOX", "ab", "https://api.anonymbox.com/v1"),
    ("bot_dropmail.py", "DropMail", "GraphQL API", "dropmail.me", "BOT_TOKEN_DROPMAIL", "dm", "https://dropmail.me/api/graphql"),
    ("bot_yopmail.py", "YOPmail", "Многодоменный", "yopmail.com", "BOT_TOKEN_YOPMAIL", "yp", "https://yopmail.com"),
    ("bot_mailsac.py", "MailSac", "Про API", "mailsac.com", "BOT_TOKEN_MAILSAC", "ms", "https://mailsac.com/api"),
    ("bot_mailslurp.py", "MailSlurp", "Тестовый API", "mailslurp.com", "BOT_TOKEN_MAILSLURP", "ml", "https://api.mailslurp.com"),
    ("bot_mailtrap.py", "Mailtrap", "Тестовый SMTP", "mailtrap.io", "BOT_TOKEN_MAILTRAP", "mtr", "https://api.mailtrap.io"),
    ("bot_dispostable.py", "Dispostable", "Одноразовая", "dispostable.com", "BOT_TOKEN_DISPOST", "dp", "https://www.dispostable.com/api/v1"),
    ("bot_fakemailgenerator.py", "FakeMailGenerator", "Генератор", "fakemailgenerator.com", "BOT_TOKEN_FAKEMAIL", "fmg", "https://www.fakemailgenerator.com"),
    ("bot_mailnesia.py", "Mailnesia", "Анонимная", "mailnesia.com", "BOT_TOKEN_MAILNESIA", "mn", "https://mailnesia.com"),
    ("bot_burner_kiwi.py", "Burner.kiwi", "Быстрая", "burner.kiwi", "BOT_TOKEN_BURNER", "bk", "https://burner.kiwi"),
    ("bot_getnada.py", "GetNada", "Многодоменная", "getnada.com", "BOT_TOKEN_GETNADA", "gn", "https://getnada.com/api/v1"),
    ("bot_trashmail.py", "TrashMail", "С пересылкой", "trashmail.net", "BOT_TOKEN_TRASHMAIL", "trm", "https://api.trashmail.net"),
    ("bot_spamgourmet.py", "SpamGourmet", "С завершением", "spamgourmet.com", "BOT_TOKEN_SPAMG", "sg", "https://www.spamgourmet.com/xmlapi.pl"),
    ("bot_tempmail_io.py", "TempMail.io", "API v1", "temp-mail.io", "BOT_TOKEN_TMIO", "tio", "https://temp-mail.io/api/v1"),
    ("bot_emailondeck.py", "EmailOnDeck", "Быстрая", "emailondeck.com", "BOT_TOKEN_EOD", "eod", "https://api.emailondeck.com/v1"),
    ("bot_maildrop.py", "MailDrop", "API v2", "maildrop.cc", "BOT_TOKEN_MDRP", "md", "https://api.maildrop.cc/v2"),
    ("bot_tempmail_org.py", "Temp-mail.org", "Домены", "temp-mail.org", "BOT_TOKEN_TMON", "tmo", "https://api.temp-mail.org"),
    ("bot_guerrilla_spam4.py", "Guerrilla Spam4.me", "Альтернативный домен", "guerrillamail", "BOT_TOKEN_GS4", "gs4", "https://api.guerrillamail.com/ajax.php"),
]

for fname, name, desc, api_name, env, prefix, base in SERVICES:
    code = '''#!/usr/bin/env python3
"""
{name} Telegram Bot
{desc}
API: {base}
"""
import telebot
from telebot import types
import requests
import random
import string
import os

BOT_TOKEN = os.environ.get("{env}", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "{base}"

sessions = {{}}


def gs(cid):
    if cid not in sessions:
        sessions[cid] = {{"seen": set(), "addr": None, "token": None, "key": None}}
    return sessions[cid]


def api_get(path, **kw):
    try:
        return requests.get(f"{{BASE}}/{{path}}", timeout=10, **kw).json()
    except Exception:
        return {{"error": "timeout"}}


def api_post(path, data=None, **kw):
    try:
        return requests.post(f"{{BASE}}/{{path}}", json=data, timeout=10, **kw).json()
    except Exception:
        return {{"error": "timeout"}}


@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📧 Новая", callback_data="{prefix}_new"))
    kb.add(types.InlineKeyboardButton("📥 Письма", callback_data="{prefix}_inbox"))
    kb.add(types.InlineKeyboardButton("🔑 Ключ", callback_data="{prefix}_key"))
    kb.add(types.InlineKeyboardButton("📋 Данные", callback_data="{prefix}_info"))
    kb.add(types.InlineKeyboardButton("❓ Помощь", callback_data="{prefix}_help"))
    text = (
        "📧 *{name} Bot*\\n"
        "{desc}\\n\\n"
        "/new — Создать почту\\n"
        "/set <email> — Установить\\n"
        "/inbox — Проверить\\n"
        "/key <API_KEY> — Установить ключ\\n"
        "/info — Данные"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=kb)


@bot.message_handler(commands=["new"])
def cmd_new(m):
    s = gs(m.chat.id)
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    addr = f"{{rnd}}@{api_name}"
    s.update(addr=addr, seen=set())
    bot.send_message(m.chat.id, f"✅ `{{addr}}`", parse_mode="Markdown")


@bot.message_handler(commands=["set"])
def cmd_set(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/set email@domain.com")
    s = gs(m.chat.id)
    s["addr"] = parts[1].strip()
    s["seen"] = set()
    bot.send_message(m.chat.id, f"✅ `{{s['addr']}}`", parse_mode="Markdown")


@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = gs(m.chat.id)
    if not s.get("addr"):
        return bot.send_message(m.chat.id, "❌ /new или /set email")
    try:
        r = requests.get(f"{{BASE}}/inbox/{{s['addr']}}", timeout=10)
        if r.ok:
            ct = r.headers.get("content-type", "")
            data = r.json() if "json" in ct else []
            if isinstance(data, list) and data:
                txt = f"📬 *{{len(data)}} писем*\\n\\n"
                for x in data[:15]:
                    nid = x.get("id", "?")
                    new = "🆕 " if nid not in s["seen"] else ""
                    s["seen"].add(nid)
                    txt += f"{{new}}`{{nid}}` | {{x.get("from", "?")}}\\n📝 {{x.get("subject", "—")}}\\n\\n"
                bot.send_message(m.chat.id, txt, parse_mode="Markdown")
            else:
                bot.send_message(m.chat.id, "📭 Пусто")
        else:
            bot.send_message(m.chat.id, "📭 Пусто или ошибка")
    except Exception:
        bot.send_message(m.chat.id, "❌ Сервис недоступен")


@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/read <ID>")
    s = gs(m.chat.id)
    if not s.get("addr"):
        return bot.send_message(m.chat.id, "❌ /new")
    try:
        r = requests.get(f"{{BASE}}/inbox/{{s['addr']}}/{{parts[1]}}", timeout=10)
        if r.ok:
            d = r.json() if "json" in r.headers.get("content-type", "") else {{}}
            body = d.get("text", d.get("html", "Нет содержимого"))[:3500]
            bot.send_message(m.chat.id, f"📧 *Письмо*\\n\\n{{body}}", parse_mode="Markdown")
        else:
            bot.send_message(m.chat.id, "❌ Не найдено")
    except Exception:
        bot.send_message(m.chat.id, "❌ Ошибка")


@bot.message_handler(commands=["key"])
def cmd_key(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "/key YOUR_API_KEY")
    s = gs(m.chat.id)
    s["key"] = parts[1].strip()
    bot.send_message(m.chat.id, f"✅ Ключ установлен: `{{s['key'][:10]}}...`", parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = gs(m.chat.id)
    txt = (
        f"📋 *Данные*\\n\\n"
        f"📧 Адрес: `{{s.get('addr', '—')}}`\\n"
        f"🔑 Ключ: `{{str(s.get('key', '—'))[:10]}}...`\\n"
        f"📩 Прочитано: {{len(s.get('seen', []))}}"
    )
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(m):
    text = (
        "📧 *{name} Bot*\\n\\n"
        "/new — Создать\\n"
        "/set <email> — Установить\\n"
        "/inbox — Проверить\\n"
        "/read <ID> — Прочитать\\n"
        "/key <KEY> — API ключ\\n"
        "/info — Данные"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: c.data.startswith("{prefix}_"))
def cb(call):
    cid = call.message.chat.id
    act = call.data.replace("{prefix}_", "")

    if act == "new":
        s = gs(cid)
        rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        addr = f"{{rnd}}@{api_name}"
        s.update(addr=addr, seen=set())
        bot.edit_message_text(f"✅ `{{addr}}`", cid, call.message.message_id, parse_mode="Markdown")

    elif act == "inbox":
        s = gs(cid)
        if not s.get("addr"):
            return bot.answer_callback_query(call.id, "❌ /new")
        try:
            r = requests.get(f"{{BASE}}/inbox/{{s['addr']}}", timeout=10)
            ct = r.headers.get("content-type", "")
            data = r.json() if r.ok and "json" in ct else []
            if isinstance(data, list) and data:
                txt = f"📬 {{len(data)}} писем:\\n\\n"
                for x in data[:10]:
                    txt += f"`{{x.get('id','?')}}` | {{x.get('from','?')}}\\n📝 {{x.get('subject','—')}}\\n\\n"
                bot.edit_message_text(txt, cid, call.message.message_id)
            else:
                bot.edit_message_text("📭 Пусто", cid, call.message.message_id)
        except Exception:
            bot.edit_message_text("❌ Ошибка", cid, call.message.message_id)

    elif act == "key":
        bot.send_message(cid, "/key YOUR_API_KEY")

    elif act == "info":
        s = gs(cid)
        bot.answer_callback_query(call.id, s.get("addr", "—"), show_alert=True)

    elif act == "help":
        bot.send_message(cid, "/new\\n/inbox\\n/info")


if __name__ == "__main__":
    print("[{name} Bot] Running...")
    bot.infinity_polling()
'''.format(
        name=name, desc=desc, api_name=api_name, env=env, prefix=prefix, base=base
    )
    path = os.path.join(DIR, fname)
    with open(path, "w") as f:
        f.write(code)
    print(f"✅ {fname}")

print(f"\n总计生成: {len(SERVICES)} 个简单 ботов")
