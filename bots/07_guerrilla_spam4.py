#!/usr/bin/env python3
"""
Guerrilla Spam4.me

Provider: Guerrilla Mail | Endpoint: get_email_address&site=spam4.me
Docs: guerrillamail.com/GuerrillaMailAPI.html
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_GSPAM4", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.guerrillamail.com/ajax.php"
SVC = "Guerrilla Spam4"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="gsp4_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="gsp4_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="gsp4_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="gsp4_help"))
    bot.send_message(m.chat.id, "*Guerrilla Spam4.me*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=gs(c); r=g(p={{"f":"get_email_address","site":"spam4.me"}})
    if "email_addr" in r: s.update(addr=r["email_addr"],token=r.get("sid_token"),seen=set()); bot.send_message(c,f"`{r['email_addr']}`",parse_mode="Markdown")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("token"): return bot.send_message(c,"/new first")
    r=g(p={{"f":"check_email","sid_token":s["token"],"seq":0}}); msgs=r.get("list",[])
    if not msgs: return bot.send_message(c,"Empty.")
    t=f"*{len(msgs)}*\n\n"
    for x in msgs[:15]: n="NEW " if x.get("mail_id") not in s["seen"] else ""; s["seen"].add(x.get("mail_id")); t+=f"{n}`{x.get('mail_id')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c,t,parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/new — Create spam4.me\n/inbox — Check")

def cb_new(c,call):
    s=gs(c); r=g(p={{"f":"get_email_address","site":"spam4.me"}})
    if "email_addr" in r: s.update(addr=r["email_addr"],token=r.get("sid_token"),seen=set()); bot.edit_message_text(f"`{r['email_addr']}`",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("token"): return bot.answer_callback_query(call.id,"/new")
    r=g(p={{"f":"check_email","sid_token":s["token"],"seq":0}}); msgs=r.get("list",[])
    if not msgs: bot.edit_message_text("Empty.",c,call.message.message_id)
    else: txt=""
    for x in msgs[:10]: txt+=f"`{x.get('mail_id')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.edit_message_text(f"{len(msgs)}:\n\n"+txt,c,call.message.message_id)
@bot.callback_query_handler(func=lambda c: c.data.startswith("gsp4_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("gsp4_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
