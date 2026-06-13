#!/usr/bin/env python3
"""1secmail.com — API генерации и чтения почты"""
import telebot, requests, random, string, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_1SECMAIL", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
API = "https://www.1secmail.com/api/v1/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
sessions = {}

def gen_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(telebot.types.InlineKeyboardButton("📧 Новая", callback_data="1s_new"))
    kb.add(telebot.types.InlineKeyboardButton("📥 Входящие", callback_data="1s_inbox"))
    kb.add(telebot.types.InlineKeyboardButton("📋 Данные", callback_data="1s_info"))
    kb.add(telebot.types.InlineKeyboardButton("🌐 Домены", callback_data="1s_domains"))
    bot.send_message(m.chat.id, "📧 *1secmail Bot*\n\n/new — Почта\n/inbox — Письма\n/domains — Домены\n/info — Данные", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new"])
def cmd_new(m):
    name = gen_name()
    s = sessions.setdefault(m.chat.id, {})
    try:
        r = requests.get(f"{API}?action=genRandomMailbox&count=1", headers=UA, timeout=10)
        addr = r.json()[0] if r.ok else f"{name}@1secmail.com"
    except:
        addr = f"{name}@1secmail.com"
    login, domain = addr.split("@")
    s.update(addr=addr, login=login, domain=domain, seen=set())
    bot.send_message(m.chat.id, f"✅ `{addr}`", parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    s = sessions.get(m.chat.id)
    if not s: return bot.send_message(m.chat.id, "❌ /new")
    try:
        r = requests.get(f"{API}?action=getMessages&login={s['login']}&domain={s['domain']}", headers=UA, timeout=10)
        msgs = r.json()
        if not msgs: return bot.send_message(m.chat.id, "📭 Пусто")
        txt = f"📬 *{len(msgs)} писем*\n\n"
        for x in msgs[:15]:
            new = "🆕 " if x["id"] not in s.get("seen", set()) else ""
            s.setdefault("seen", set()).add(x["id"])
            txt += f"{new}🆔 `{x['id']}` | {x.get('from','?')}\n📝 {x.get('subject','—')}\n\n"
        bot.send_message(m.chat.id, txt, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ {e}")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2: return bot.send_message(m.chat.id, "/read <ID>")
    s = sessions.get(m.chat.id)
    if not s: return bot.send_message(m.chat.id, "❌ /new")
    try:
        r = requests.get(f"{API}?action=readMessage&login={s['login']}&domain={s['domain']}&id={parts[1]}", headers=UA, timeout=10)
        d = r.json()
        body = d.get("textBody","") or d.get("htmlBody","Нет")[:3500]
        bot.send_message(m.chat.id, f"📧 *{d.get('subject','—')}*\nОт: {d.get('from','?')}\n\n{body}", parse_mode="Markdown")
    except: bot.send_message(m.chat.id, "❌ Ошибка")

@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    try:
        r = requests.get(f"{API}?action=getDomainList", headers=UA, timeout=10)
        domains = r.json()
        txt = "🌐 *Домены:*\n" + "\n".join(f"• `{d}`" for d in domains[:20])
        bot.send_message(m.chat.id, txt, parse_mode="Markdown")
    except: bot.send_message(m.chat.id, "❌ Ошибка")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s = sessions.get(m.chat.id, {})
    bot.send_message(m.chat.id, f"📧 `{s.get('addr','—')}`\n📩 Прочитано: {len(s.get('seen',[]))}", parse_mode="Markdown")

if __name__=="__main__":
    print("[1secmail Bot] OK")
    bot.infinity_polling()
