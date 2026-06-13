#!/usr/bin/env python3
"""
TempMail.lol — Auth Inbox

Provider: TempMail.lol | Endpoint: api/auth/{token}
Docs: tempmail.lol
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_TML_AUTH", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.tempmail.lol"
SVC = "TempMail.lol Auth"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="tla_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="tla_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="tla_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="tla_help"))
    bot.send_message(m.chat.id, "*TempMail.lol — Auth*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=gs(c); r=g("/generate")
    if "address" in r: s.update(addr=r["address"],token=r.get("token"),seen=set()); bot.send_message(c,f"`{r['address']}`",parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("token"): return bot.send_message(c,"/new first")
    r=g(f"/auth/{s['token']}"); emails=r.get("email",[])
    if not emails: return bot.send_message(c,"Empty.")
    t=f"*{len(emails)}*\n\n"
    for e in emails[:15]: n="NEW " if e.get("id") not in s["seen"] else ""; s["seen"].add(e.get("id")); t+=f"{n}`{e.get('id')}` {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.send_message(c,t,parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/new — Create\n/inbox — Check")

def cb_new(c,call):
    s=gs(c); r=g("/generate")
    if "address" in r: s.update(addr=r["address"],token=r.get("token"),seen=set()); bot.edit_message_text(f"`{r['address']}`",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("token"): return bot.answer_callback_query(call.id,"/new first")
    r=g(f"/auth/{s['token']}"); emails=r.get("email",[])
    if not emails: bot.edit_message_text("Empty.",c,call.message.message_id)
    else: txt=""
    for e in emails[:10]: txt+=f"`{e.get('id')}` {e.get('from','?')}\n{e.get('subject','—')}\n\n"
    bot.edit_message_text(f"{len(emails)}:\n\n"+txt,c,call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tla_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("tla_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
