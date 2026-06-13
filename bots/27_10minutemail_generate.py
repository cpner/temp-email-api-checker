#!/usr/bin/env python3
"""
10 Minute Mail — Generate

Provider: 10 Minute Mail | Endpoint: address.api.php?new=1
Docs: 10minutemail.net
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_10MIN", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://10minutemail.net/address.api.php"
SVC = "10 Minute Mail"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="tm10_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="tm10_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="tm10_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="tm10_help"))
    bot.send_message(m.chat.id, "*10 Minute Mail*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=gs(c); r=g(p={"new":1})
    if "address" in r: s.update(addr=r["address"],token=r.get("session_id",""),seen=set(),ts=time.time()); bot.send_message(c,f"`{r['address']}`\nExpires: 10 min",parse_mode="Markdown")
    else: bot.send_message(c,"Failed.")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("token"): return bot.send_message(c,"/new first")
    el=time.time()-s.get("ts",time.time())
    if el>600: return bot.send_message(c,"Expired. /new")
    rem=600-int(el); r=g(p={"sid":s["token"]}); msgs=r.get("messages",[])
    if not msgs: return bot.send_message(c,f"Empty ({rem}s left)")
    t=f"*{len(msgs)}* ({rem}s)\n\n"
    for x in msgs[:15]: t+=f"`{x.get('mail_id','?')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.send_message(c,t,parse_mode="Markdown")

@bot.message_handler(commands=["info"])
def cmd_info(m):
    s=gs(m.chat.id); el=time.time()-s.get("ts",time.time()); rem=max(0,600-int(el)); mn,sc=divmod(rem,60)
    bot.send_message(m.chat.id,f"{s.get('addr','—')} | {mn}m {sc}s left")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/new — Create (10min)\n/inbox — Check\n/info — Timer")

def cb_new(c,call):
    s=gs(c); r=g(p={"new":1})
    if "address" in r: s.update(addr=r["address"],token=r.get("session_id",""),seen=set(),ts=time.time()); bot.edit_message_text(f"`{r['address']}` (10min)",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("token"): return bot.answer_callback_query(call.id,"/new first")
    el=time.time()-s.get("ts",time.time())
    if el>600: return bot.answer_callback_query(call.id,"Expired!")
    rem=600-int(el); r=g(p={"sid":s["token"]}); msgs=r.get("messages",[])
    if not msgs: bot.edit_message_text(f"Empty ({rem}s)",c,call.message.message_id)
    else: txt=""
    for x in msgs[:10]: txt+=f"`{x.get('mail_id')}` {x.get('mail_from','?')}\n{x.get('mail_subject','—')}\n\n"
    bot.edit_message_text(f"{len(msgs)} ({rem}s):\n\n"+txt,c,call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tm10_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("tm10_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
