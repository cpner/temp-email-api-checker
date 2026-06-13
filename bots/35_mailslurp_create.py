#!/usr/bin/env python3
"""
MailSlurp — Create Inbox

Provider: MailSlurp | Endpoint: inboxes (POST)
Docs: docs.mailslurp.com
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MLSLURP_CR", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.mailslurp.com"
SVC = "MailSlurp Create"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="mlc_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="mlc_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="mlc_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="mlc_help"))
    bot.send_message(m.chat.id, "*MailSlurp — Create Inbox*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["key"])
def cmd_key(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/key <API_KEY>")
    s=gs(m.chat.id); s["key"]=p[1].strip(); bot.send_message(m.chat.id,f"Key: `{s['key'][:10]}...`",parse_mode="Markdown")

@bot.message_handler(commands=["new"])
def cmd_new(m):
    s=gs(m.chat.id)
    if not s.get("key"): return bot.send_message(m.chat.id,"/key first")
    r=p("/inboxes",{},h={"x-api-key":s["key"]}); d=r if isinstance(r,dict) else {}
    if "id" in d: s.update(addr=d.get("emailAddress",""),token=d.get("id")); bot.send_message(m.chat.id,f"`{d.get('emailAddress','?')}`",parse_mode="Markdown")
    else: bot.send_message(m.chat.id,"Failed.")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/key <KEY>\n/new — Create")
@bot.callback_query_handler(func=lambda c: c.data.startswith("mlc_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("mlc_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
def cb_new(c,call):
    s=gs(c)
    if not s.get("key"): return bot.answer_callback_query(call.id,"/key first")
    r=p("/inboxes",{},h={"x-api-key":s["key"]}); d=r if isinstance(r,dict) else {}
    if "id" in d: s.update(addr=d.get("emailAddress",""),token=d.get("id")); bot.edit_message_text(f"`{d.get('emailAddress','?')}`",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call): bot.send_message(c,"/new to create")