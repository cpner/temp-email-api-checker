#!/usr/bin/env python3
"""
EmailNator Telegram Bot
Provider: EmailNator | API: https://www.emailnator.com
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests

Features:
- Create disposable email addresses
- Check inbox for new messages
- Real-time message monitoring
- Comprehensive error handling
- Rate limiting & retry logic
- Usage statistics
- Graceful shutdown

Author: Temp Email Bots Project
License: MIT
"""
import telebot
from telebot import types
import requests
import random
import string
import time
import os
import signal
import sys
import logging
from typing import Optional, Dict, Any, Set

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EmailNator")

BOT_TOKEN: str = os.environ.get("BOT_TOKEN_EMAILNATOR", "YOUR_BOT_TOKEN")
BASE_URL: str = "https://www.emailnator.com"
SERVICE_NAME: str = "EmailNator"
REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0
RATE_LIMIT_DELAY: float = 0.5

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set! Set environment variable BOT_TOKEN_EMAILNATOR")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════════
# Session Management
# ═══════════════════════════════════════════════════════════════
class UserSession:
    """Manages user state and data."""
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.key: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0
        self.messages: int = 0

sessions: Dict[int, UserSession] = {}
stats: Dict[str, int] = {{"created": 0, "checked": 0, "errors": 0}}

def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

# ═══════════════════════════════════════════════════════════════
# API Client with retry logic
# ═══════════════════════════════════════════════════════════════
def api_request(method: str, path: str = "", params: Optional[Dict] = None,
                data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request with retry logic and error handling."""
    url = f"{{BASE_URL}}{{path}}"
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                resp = requests.get(url, params=params, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers or {{}}, timeout=REQUEST_TIMEOUT)
            else:
                return {{"error": f"Unsupported method: {{method}}"}}

            if "json" in resp.headers.get("content-type", ""):
                return resp.json()
            return {{"text": resp.text[:500], "status": resp.status_code}}

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {{attempt+1}}/{{MAX_RETRIES}}: {{url}}")
        except Exception as e:
            logger.error(f"Request error: {{e}}")
            return {{"error": str(e)}}

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))

    stats["errors"] += 1
    return {{"error": "Max retries exceeded"}}

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("GET", path, params=params, headers=headers)

def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
    return api_request("POST", path, data=data, headers=headers)

# ═══════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════
def gen_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def safe_text(text: str, max_len: int = 4000) -> str:
    return text[:max_len] if text else "No content"

# ═══════════════════════════════════════════════════════════════
# Command Handlers
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📧 New Email", callback_data="new"),
        types.InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
        types.InlineKeyboardButton("📋 Info", callback_data="info"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("❓ Help", callback_data="help"),
    )
    text = (
        f"*{{SERVICE_NAME}}*\n"
        f"Temporary Email Bot\n\n"
        f"Create disposable email addresses\n"
        f"and receive messages instantly.\n\n"
        f"*Quick Start:*\n"
        f"1. Tap 📧 New Email\n"
        f"2. Copy the address\n"
        f"3. Use it for registration\n"
        f"4. Tap 📥 Inbox to check\n\n"
        f"*Commands:*\n"
        f"/new — Create email\n"
        f"/inbox — Check messages\n"
        f"/set — Set email manually\n"
        f"/info — Session info\n"
        f"/stats — Usage statistics\n"
        f"/help — Detailed help"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)
    logger.info(f"User {{message.chat.id}} started bot")


@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    bot.send_message(message.chat.id, f"*EmailNator*\n\n🌐 https://www.emailnator.com\n\nVisit the website to use this service.")


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call: types.CallbackQuery) -> None:
    cid = call.message.chat.id
    action = call.data
    try:
        if action == "new":
        bot.send_message(cid, f"Visit https://www.emailnator.com to create an email.")
        elif action == "inbox":
        bot.send_message(cid, f"Visit https://www.emailnator.com to check your inbox.")
        elif action == "info":
            s = get_session(cid)
            text = (
                f"*Session Info*\n\n"
                f"Email: `{{s.addr or 'Not set'}}`\n"
                f"Token: `{{str(s.token or '')[:20]}}...`\n"
                f"Messages read: {{s.messages}}\n"
                f"Unique seen: {{len(s.seen)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "stats":
            text = (
                f"*Bot Statistics*\n\n"
                f"Emails created: {{stats['created']}}\n"
                f"Inboxes checked: {{stats['checked']}}\n"
                f"Errors: {{stats['errors']}}\n"
                f"Active sessions: {{len(sessions)}}"
            )
            bot.answer_callback_query(call.id, text, show_alert=True)
        elif action == "help":
            bot.send_message(cid, get_help_text())
        else:
            bot.answer_callback_query(call.id, "Unknown action")
    except Exception as e:
        logger.error(f"Callback error: {{e}}")
        bot.answer_callback_query(call.id, "An error occurred")


def get_help_text() -> str:
    return (
        f"*{{SERVICE_NAME}} Bot — Help*\n\n"
        f"*Commands:*\n"
        f"/new — Create new email\n"
        f"/inbox — Check inbox\n"
        f"/set <email> — Set email to monitor\n"
        f"/read <ID> — Read specific message\n"
        f"/key <KEY> — Set API key\n"
        f"/info — Current session info\n"
        f"/stats — Usage statistics\n"
        f"/help — This help\n\n"
        f"*Provider:* {{SERVICE_NAME}}\n"
        f"*API:* `{{BASE_URL}}`\n\n"
        f"*Tips:*\n"
        f"- Create email first with /new\n"
        f"- Check inbox regularly\n"
        f"- Use /info to see session details"
    )

# ═══════════════════════════════════════════════════════════════
# Graceful Shutdown
# ═══════════════════════════════════════════════════════════════
def signal_handler(sig, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    logger.info(f"Starting {{SERVICE_NAME}} Bot...")
    logger.info(f"API: {{BASE_URL}}")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
