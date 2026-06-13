#!/usr/bin/env python3
"""
MailSlurp — Domains

Provider: MailSlurp | Endpoint: domains
Docs: docs.mailslurp.com
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MLSLURP_DOM", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.mailslurp.com"
SVC = "MailSlurp Domains"
sess = {}

def gs(c):
    if c not in sess: sess[c] = {"seen": set(), "addr": None, "token": None, "key": None, "ts": 0}
    return sess[c]

def g(path="", h=None, p=None):
    try: return requests.get(f"{BASE}{path}", headers=h or {}, params=p, timeout=15).json()
    except: return {"error": "timeout"}

def p(path="", d=None, h=None):
    try: return requests.post(f"{BASE}{path}", json=d, headers=h or {}, timeout=15).json()
    except: return {"error": "timeout"}

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("New Email", callback_data="mld_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="mld_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="mld_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="mld_help"))
    bot.send_message(m.chat.id, "*MailSlurp — Domains*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["key"])
def cmd_key(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/key <API_KEY>")
    s=gs(m.chat.id); s["key"]=p[1].strip(); bot.send_message(m.chat.id,f"Key: `{s['key'][:10]}...`",parse_mode="Markdown")

@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    s=gs(m.chat.id)
    if not s.get("key"): return bot.send_message(m.chat.id,"/key first")
    r=g("/domains",h={"x-api-key":s["key"]}); data=r if isinstance(r,list) else []
    if data:
        t=f"*{len(data)}*\n\n" + "\n".join(f"• `{d}`" for d in data[:30])
        bot.send_message(m.chat.id,t,parse_mode="Markdown")
    else: bot.send_message(m.chat.id,"No domains.")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/key <KEY>\n/domains")
@bot.callback_query_handler(func=lambda c: c.data.startswith("mld_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("mld_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
def cb_new(c,call): bot.send_message(c,"/key <API_KEY>")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("key"): return bot.answer_callback_query(call.id,"/key first")
    r=g("/domains",h={"x-api-key":s["key"]}); data=r if isinstance(r,list) else []
    bot.answer_callback_query(call.id,f"{len(data)} domains",show_alert=True)