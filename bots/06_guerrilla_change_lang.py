#!/usr/bin/env python3
"""
Guerrilla Change Language

Provider: Guerrilla Mail | Endpoint: change_lang
Docs: guerrillamail.com/GuerrillaMailAPI.html
"""
import telebot, requests, random, string, time, os

BOT_TOKEN = os.environ.get("BOT_TOKEN_GCHLANG", "YOUR_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
BASE = "https://api.guerrillamail.com/ajax.php"
SVC = "Guerrilla ChLang"
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
    kb.add(types.InlineKeyboardButton("New Email", callback_data="gcl_new"))
    kb.add(types.InlineKeyboardButton("Inbox", callback_data="gcl_inbox"))
    kb.add(types.InlineKeyboardButton("Info", callback_data="gcl_info"))
    kb.add(types.InlineKeyboardButton("Help", callback_data="gcl_help"))
    bot.send_message(m.chat.id, "*Guerrilla Change Language*\n\n\n/new — Create\n/inbox — Check\n/info — Info\n/help — Help", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb=types.InlineKeyboardMarkup(row_width=3)
    for code,name in [("en","English"),("ru","Русский"),("de","Deutsch"),("fr","Français"),("es","Español"),("it","Italiano"),("pt","Português"),("ja","日本語"),("zh","中文")]:
        kb.add(types.InlineKeyboardButton(name,callback_data=f"gcl_set_{{code}}"))
    bot.send_message(m.chat.id,"*Change Language*",parse_mode="Markdown",reply_markup=kb)

@bot.message_handler(commands=["setlang"])
def cmd_setlang(m):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"/setlang <code>")
    r=g(p={{"f":"change_lang","lang":p[1].strip()}}); l=r.get("lang",p[1].strip()); bot.send_message(m.chat.id,f"Language: `{l}`",parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(m): bot.send_message(m.chat.id,"/setlang <code> — en,ru,de,fr,it,pt,ja,zh")

def cb_new(c,call): bot.send_message(c,"Select language from menu")
def cb_inbox(c,call):
    r=g(p={{"f":"get_lang"}}); bot.answer_callback_query(call.id,f"Current: {r.get('lang','?')}",show_alert=True)
@bot.callback_query_handler(func=lambda c: c.data.startswith("gcl_"))
def cb(call):
    c = call.message.chat.id
    a = call.data.replace("gcl_","")
    if a=="new": cb_new(c, call)
    elif a=="inbox": cb_inbox(c, call)
    elif a=="info":
        s=gs(c)
        bot.answer_callback_query(call.id, f"Email: {s.get('addr','Not set')}", show_alert=True)
    elif a=="help": bot.send_message(c,"/new — Create\n/inbox — Check\n/info — Info")

if __name__=="__main__":
    print(f"[{SVC} Bot] Running...")
    bot.infinity_polling()
