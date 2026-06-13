#!/usr/bin/env python3
"""
TempMail.lol — Generate

Provider: TempMail.lol | Endpoint: api/generate
Docs: tempmail.lol
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_TML_GEN", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.tempmail.lol"
SVC = "TempMail.lol Gen"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="tlg_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="tlg_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="tlg_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="tlg_help"))
    bot.send_message(m.chat.id, "*TempMail.lol — Generate*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=gs(c); r=g("/generate")
    if "address" in r: s.update(addr=r["address"],token=r.get("token"),seen=set()); bot.send_message(c,f"`{r['address']}`\nToken: `{str(r.get('token',''))[:20]}...`",parse_mode="Markdown")
    else: bot.send_message(c,"Failed.")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/new — Generate")

def cb_new(c,call):
    s=gs(c); r=g("/generate")
    if "address" in r: s.update(addr=r["address"],token=r.get("token"),seen=set()); bot.edit_message_text(f"`{r['address']}`",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call): bot.answer_callback_query(call.id,f"Email: {gs(c).get('addr','—')}",show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tlg_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("tlg_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
