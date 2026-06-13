#!/usr/bin/env python3
"""
Mailnesia — Anonymous Email

Provider: Mailnesia | Endpoint: mailnesia.com
Docs: mailnesia.com
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILNESIA", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://mailnesia.com"
SVC = "Mailnesia"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="mn_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="mn_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="mn_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="mn_help"))
    bot.send_message(m.chat.id, "*Mailnesia*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["check"])
def cmd_check(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/check <name>")
    bot.send_message(m.chat.id,f"Inbox: https://mailnesia.com/mailbox/{p[1].strip()}")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/check <name>\n\nThen visit mailnesia.com/mailbox/<name>")

def cb_new(c,call): bot.send_message(c,"/check <name>")
def cb_inbox(c,call): bot.send_message(c,"Visit mailnesia.com")

@bot.callback_query_handler(func=lambda c: c.data.startswith("mn_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("mn_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
