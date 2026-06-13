#!/usr/bin/env python3
"""
TempMail.plus — Yahoo

Provider: TempMail.plus | Endpoint: api/mails?email=...@yahoo.com
Docs: tempmail.plus
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_TP_YAHOO_COM", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://tempmail.plus/api/mails"
SVC = "TempMail.plus Yahoo"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="tp10_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="tp10_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="tp10_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="tp10_help"))
    bot.send_message(m.chat.id, "*TempMail.plus — Yahoo*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/set email@yahoo.com")
    s=gs(m.chat.id); s["addr"]=p[1].strip(); s["seen"]=set(); bot.send_message(m.chat.id,f"Monitoring: `{s['addr']}`",parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("addr"): return bot.send_message(c,"/set email@yahoo.com")
    r=g(p={"email":s["addr"]}); mails=r.get("mail",[])
    if not mails: return bot.send_message(c,"Empty.")
    t=f"*{len(mails)}*\n\n"
    for x in mails[:15]: n="NEW " if x.get("mail_id") not in s["seen"] else ""; s["seen"].add(x.get("mail_id")); t+=f"{n}`{x.get('mail_id')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c,t,parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m): s=gs(m.chat.id); bot.send_message(m.chat.id,f"{s.get('addr','—')} | Provider: yahoo.com")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/set <email> — Set\n/inbox — Check")

def cb_new(c,call): bot.send_message(c,"/set email@yahoo.com")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("addr"): return bot.answer_callback_query(call.id,"/set first")
    r=g(p={"email":s["addr"]}); mails=r.get("mail",[])
    if not mails: bot.edit_message_text("Empty.",c,call.message.message_id)
    else: txt=""
    for x in mails[:10]: txt+=f"`{x.get('mail_id')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.edit_message_text(f"{len(mails)}:\n\n"+txt,c,call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tp10_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("tp10_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
