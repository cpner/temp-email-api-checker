#!/usr/bin/env python3
"""
MailSac — Messages

Provider: MailSac | Endpoint: api/addresses/{email}/messages
Docs: mailsac.com/api
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILSAC_MSG", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://mailsac.com/api"
SVC = "MailSac Messages"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="msm_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="msm_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="msm_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="msm_help"))
    bot.send_message(m.chat.id, "*MailSac — Messages*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["key"])
def cmd_key(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/key <API_KEY>")
    s=gs(m.chat.id); s["key"]=p[1].strip(); bot.send_message(m.chat.id,f"Key: `{s['key'][:10]}...`",parse_mode="Markdown")

@bot.message_handler(commands=["set"])
def cmd_set(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/set <email>")
    s=gs(m.chat.id); s["addr"]=p[1].strip(); s["seen"]=set(); bot.send_message(m.chat.id,f"`{s['addr']}`",parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("key"): return bot.send_message(c,"/key first")
    if not s.get("addr"): return bot.send_message(c,"/set email")
    r=g(f"/addresses/{s['addr']}/messages",h={"MailsacKey":s["key"]}); data=r if isinstance(r,list) else []
    if data:
        t=f"*{len(data)}*\n\n"
        for x in data[:15]: t+=f"`{x.get('_id','?')}` {x.get('subject','—')}\n\n"
        bot.send_message(c,t,parse_mode="Markdown")
    else: bot.send_message(c,"No messages.")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/key <KEY>\n/set <email>\n/inbox")

def cb_new(c,call): bot.send_message(c,"/key + /set first")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("key") or not s.get("addr"): return bot.answer_callback_query(call.id,"Set key and email first")
    r=g(f"/addresses/{s['addr']}/messages",h={"MailsacKey":s["key"]}); data=r if isinstance(r,list) else []
    if data: txt=""
    for x in data[:10]: txt+=f"`{x.get('_id','?')}` {x.get('subject','—')}\n\n"
    bot.edit_message_text(f"{len(data)}:\n\n"+txt,c,call.message.message_id)
    else: bot.edit_message_text("No messages.",c,call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("msm_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("msm_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
