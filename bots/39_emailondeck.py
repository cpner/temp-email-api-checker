#!/usr/bin/env python3
"""
EmailOnDeck — Disposable Email

Provider: EmailOnDeck | Endpoint: emailondeck.com
Docs: emailondeck.com
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_EMAILONDECK", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.emailondeck.com/v1"
SVC = "EmailOnDeck"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="eod_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="eod_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="eod_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="eod_help"))
    bot.send_message(m.chat.id, "*EmailOnDeck*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["info"])
def cmd_info(m): bot.send_message(m.chat.id,"*EmailOnDeck*\n\nVisit https://emailondeck.com\nFast disposable email.",parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/info — Service info\n\nVisit emailondeck.com directly.")

def cb_new(c,call): bot.send_message(c,"Visit https://emailondeck.com")
def cb_inbox(c,call): bot.send_message(c,"Visit https://emailondeck.com")

@bot.callback_query_handler(func=lambda c: c.data.startswith("eod_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("eod_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
