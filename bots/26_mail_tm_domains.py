#!/usr/bin/env python3
"""
Mail.tm — Domains & Accounts

Provider: Mail.tm | Endpoint: api/domains
Docs: api.mail.tm
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_MAIL_TM", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.mail.tm"
SVC = "Mail.tm"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="mt_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="mt_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="mt_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="mt_help"))
    bot.send_message(m.chat.id, "*Mail.tm — Domains*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["domains"])
def cmd_domains(m):
    r=g("/domains"); doms=[d["domain"] for d in r.get("hydra:member",[])]
    if not doms: return bot.send_message(m.chat.id,"No domains.")
    t=f"*{len(doms)} domains*\n\n" + "\n".join(f"• `{d}`" for d in doms[:30])
    bot.send_message(m.chat.id,t,parse_mode="Markdown")

@bot.message_handler(commands=["new"])
def cmd_new(m):
    c=m.chat.id; s=gs(c)
    r=g("/domains"); doms=[d["domain"] for d in r.get("hydra:member",[])]
    if not doms: return bot.send_message(c,"No domains.")
    dom=random.choice(doms); name="".join(random.choices(string.ascii_lowercase+string.digits,k=10))
    addr=f"{name}@{dom}"; pwd="".join(random.choices(string.ascii_letters+string.digits,k=16))
    r=p("/accounts",{"address":addr,"password":pwd})
    if "id" in r: tok=p("/token",{"address":addr,"password":pwd}).get("token",""); s.update(addr=addr,token=tok,seen=set()); bot.send_message(c,f"`{addr}`\nPassword: `{pwd}`",parse_mode="Markdown")
    else: bot.send_message(c,f"Error: {r.get('detail','?')}")

@bot.message_handler(commands=["inbox"])
def cmd_inbox(m):
    c=m.chat.id; s=gs(c)
    if not s.get("token"): return bot.send_message(c,"/new first")
    r=g("/messages",h={"Authorization":f"Bearer {s['token']}"})
    msgs=r.get("hydra:member",[]) if isinstance(r,dict) else r if isinstance(r,list) else []
    if not msgs: return bot.send_message(c,"Empty.")
    t=f"*{len(msgs)}*\n\n"
    for x in msgs[:15]: fr=x.get("from",{{}}).get("address","?") if isinstance(x.get("from"),dict) else "?"; t+=f"`{x.get('id','?')}` {fr}\n{x.get('subject','—')}\n\n"
    bot.send_message(c,t,parse_mode="Markdown")

@bot.message_handler(commands=["read"])
def cmd_read(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/read <ID>")
    s=gs(m.chat.id)
    if not s.get("token"): return bot.send_message(m.chat.id,"/new first")
    r=g(f"/messages/{p[1]}",h={"Authorization":f"Bearer {s['token']}"})
    body=r.get("text","")[:3500]; fr=r.get("from",{{}}).get("address","?") if isinstance(r.get("from"),dict) else "?"
    bot.send_message(m.chat.id,f"*{r.get('subject','—')}*\nFrom: {fr}\n\n{body}",parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/domains — List\n/new — Create\n/inbox — Check\n/read <ID> — Read")

def cb_new(c,call):
    s=gs(c); r=g("/domains"); doms=[d["domain"] for d in r.get("hydra:member",[])]
    if not doms: return bot.answer_callback_query(call.id,"No domains")
    dom=random.choice(doms); name="".join(random.choices(string.ascii_lowercase+string.digits,k=10))
    addr=f"{name}@{dom}"; pwd="".join(random.choices(string.ascii_letters+string.digits,k=16))
    r=p("/accounts",{"address":addr,"password":pwd})
    if "id" in r: tok=p("/token",{"address":addr,"password":pwd}).get("token",""); s.update(addr=addr,token=tok,seen=set()); bot.edit_message_text(f"`{addr}`",c,call.message.message_id,parse_mode="Markdown")
def cb_inbox(c,call):
    s=gs(c)
    if not s.get("token"): return bot.answer_callback_query(call.id,"/new first")
    r=g("/messages",h={"Authorization":f"Bearer {s['token']}"})
    msgs=r.get("hydra:member",[]) if isinstance(r,dict) else []
    if not msgs: bot.edit_message_text("Empty.",c,call.message.message_id)
    else: txt=""
    for x in msgs[:10]: fr=x.get("from",{{}}).get("address","?") if isinstance(x.get("from"),dict) else "?"; txt+=f"`{x.get('id','?')}` {fr}\n{x.get('subject','—')}\n\n"
    bot.edit_message_text(f"{len(msgs)}:\n\n"+txt,c,call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("mt_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("mt_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
