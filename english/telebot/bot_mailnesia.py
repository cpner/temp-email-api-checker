#!/usr/bin/env python3
"""
Mailnesia Telegram Bot

Provider: Mailnesia
API: https://mailnesia.com
Framework: pyTelegramBotAPI 4.18.0
Install: pip install pyTelegramBotAPI requests

Features:
- Create disposable email addresses
- Check inbox for new messages
- Set custom username
- Change interface language (9 languages)
- Real-time message monitoring

Author: Vladislav Sofronov (@icesq)
Contact: feedback@gondon.su | t.me/icesq | gondon.su
Source: https://github.com/cpner/temp-email-api-checker
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
# Logging Configuration
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Mailnesia")

# ═══════════════════════════════════════════════════════════════
# Bot Configuration
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN_MAILNESIA", "YOUR_BOT_TOKEN")
BASE_URL = "https://mailnesia.com"
SERVICE_NAME = "Mailnesia"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════════
# Constants: Button Labels
# ═══════════════════════════════════════════════════════════════
BTN_NEW = "📧 New Email"
BTN_INBOX = "📥 Inbox"
BTN_INFO = "ℹ️ Info"
BTN_SOURCE = "🔗 Source Code"
BTN_HELP = "❓ Help"

# ═══════════════════════════════════════════════════════════════
# Constants: Text Messages
# ═══════════════════════════════════════════════════════════════
SOURCE_URL = "https://github.com/cpner/temp-email-api-checker/blob/main/english/telebot/bot_mailnesia.py"

START_TEXT = """*Mailnesia Bot*
Anonymous email service

*Features:*
Check inbox, direct links

*How to use:*
1. Tap '📧 New Email' to create
2. Copy the email address
3. Use it for registration
4. Tap '📥 Inbox' to check messages
5. New messages marked with 🆕"""

INFO_TEXT = """*Mailnesia — Info*

*Service:* Mailnesia
*Description:* Anonymous email service
*Features:* Check inbox, direct links
*API:* `https://mailnesia.com`
*Website:* https://mailnesia.com
*Source:* """ + SOURCE_URL + """
*Author:* Vladislav Sofronov (@icesq)
*License:* MIT"""

HELP_TEXT = """*Mailnesia — Commands*

/start — Main menu
/new — Create email
/inbox — Check messages
/set — Set username
/info — Bot info
/help — This help

*Buttons:*
📧 New Email — Create address
📥 Inbox — Check messages
ℹ️ Info — Bot details
🔗 Source — GitHub link
❓ Help — Usage guide"""


# ═══════════════════════════════════════════════════════════════
# User Session Management
# ═══════════════════════════════════════════════════════════════

class UserSession:
    """Stores user state including email, token, and seen messages.
    
    Attributes:
        addr: Current email address
        token: API session token
        seen: Set of already-read message IDs
        ts: Timestamp of session creation
    """
    def __init__(self):
        self.addr: Optional[str] = None
        self.token: Optional[str] = None
        self.seen: Set[str] = set()
        self.ts: float = 0

# Global session storage
sessions: Dict[int, UserSession] = {}
# Usage statistics
stats: Dict[str, int] = {"created": 0, "checked": 0, "errors": 0}


def get_session(user_id: int) -> UserSession:
    """Get or create a user session by Telegram user ID.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        UserSession object for this user
    """
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]


# ═══════════════════════════════════════════════════════════════
# API Communication Layer
# ═══════════════════════════════════════════════════════════════

def api_get(path: str = "", params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Make GET request to Mailnesia API with retry logic.
    
    Args:
        path: URL path to append to base URL
        params: Query parameters
        headers: Custom HTTP headers
        
    Returns:
        JSON response dict or error dict
    """
    url = BASE_URL + path
    default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        default_headers.update(headers)
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=default_headers, timeout=15)
            return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
        except Exception as e:
            logger.warning(f"API error (attempt {attempt+1}/3): {e}")
            if attempt < 2:
                time.sleep(1)
    stats["errors"] += 1
    return {"error": "Max retries exceeded"}


def api_post(path: str = "", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Make POST request to Mailnesia API.
    
    Args:
        path: URL path to append to base URL
        data: JSON body data
        headers: Custom HTTP headers
        
    Returns:
        JSON response dict or error dict
    """
    url = BASE_URL + path
    try:
        r = requests.post(url, json=data, headers=headers or {}, timeout=15)
        return r.json() if "json" in r.headers.get("content-type", "") else {"text": r.text[:500]}
    except Exception as e:
        stats["errors"] += 1
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# Core Logic Functions
# ═══════════════════════════════════════════════════════════════

def handle_new(user_id: int, session: UserSession) -> str:
    """Create a new Mailnesia email address.
    
    Generates a random email address via the API and stores
    the session token for future inbox checks.
    
    Args:
        user_id: Telegram user ID
        session: UserSession object to update
        
    Returns:
        Success message with email address or error message
    """
    result = api_get(params={"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla"})
    if "email_addr" in result:
        session.addr = result["email_addr"]
        session.token = result.get("sid_token")
        session.seen = set()
        session.ts = time.time()
        stats["created"] += 1
        return f"✅ Created: `{result['email_addr']}`"
    return "❌ Failed to create email. Try again."


def handle_inbox(user_id: int, session: UserSession) -> str:
    """Check inbox for new messages.
    
    Fetches messages from the API and marks new ones with 🆕.
    Updates the seen set to track which messages have been read.
    
    Args:
        user_id: Telegram user ID
        session: UserSession object with token
        
    Returns:
        Formatted message list or status message
    """
    if not session.token:
        return "❌ Create email first with /new"
    
    result = api_get(params={"f": "check_email", "sid_token": session.token, "seq": 0})
    msgs = result.get("list", [])
    stats["checked"] += 1
    
    if not msgs:
        return "📭 Inbox is empty"
    
    lines = [f"*{len(msgs)} messages*\n"]
    for msg in msgs[:15]:
        mid = msg.get("mail_id", "?")
        is_new = mid not in session.seen
        marker = "🆕 " if is_new else ""
        session.seen.add(mid)
        lines.append(f"{marker}`{mid}` | {msg.get('mail_from', '?')} | {msg.get('mail_subject', '-')}")
    
    return "\n".join(lines)


def handle_set_message(text: str, session: UserSession) -> str:
    """Set email address manually from user command.
    
    Parses /set <username> command and creates the email.
    
    Args:
        text: Full command text (/set username)
        session: UserSession object to update
        
    Returns:
        Confirmation message or error
    """
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: /set <username>"
    
    username = parts[1].strip().replace("@", "")
    result = api_get(params={
        "f": "set_email_user",
        "sid_token": session.token or "",
        "email_user": username
    })
    
    if "email_addr" in result:
        session.addr = result["email_addr"]
        return f"✅ Email set: `{result['email_addr']}`"
    return "❌ Failed to set username"


# ═══════════════════════════════════════════════════════════════
# Keyboard Builder
# ═══════════════════════════════════════════════════════════════

def make_keyboard() -> types.InlineKeyboardMarkup:
    """Build the main inline keyboard with navigation buttons.
    
    Returns:
        InlineKeyboardMarkup with 5 buttons in 3 rows
    """
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(BTN_NEW, callback_data="new"),
        types.InlineKeyboardButton(BTN_INBOX, callback_data="inbox"),
    )
    kb.add(
        types.InlineKeyboardButton(BTN_INFO, callback_data="info"),
        types.InlineKeyboardButton(BTN_SOURCE, callback_data="source"),
    )
    kb.add(
        types.InlineKeyboardButton(BTN_HELP, callback_data="help"),
    )
    return kb


# ═══════════════════════════════════════════════════════════════
# Command Handlers
# ═══════════════════════════════════════════════════════════════

@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message) -> None:
    """Handle /start command. Shows welcome message with buttons."""
    bot.send_message(message.chat.id, START_TEXT, reply_markup=make_keyboard())


@bot.message_handler(commands=["new"])
def cmd_new(message: types.Message) -> None:
    """Handle /new command. Creates new email address."""
    session = get_session(message.chat.id)
    result = handle_new(message.chat.id, session)
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=["inbox"])
def cmd_inbox(message: types.Message) -> None:
    """Handle /inbox command. Checks for new messages."""
    session = get_session(message.chat.id)
    result = handle_inbox(message.chat.id, session)
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=["set"])
def cmd_set(message: types.Message) -> None:
    """Handle /set command. Sets email manually."""
    session = get_session(message.chat.id)
    result = handle_set_message(message.text, session)
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=["info"])
def cmd_info(message: types.Message) -> None:
    """Handle /info command. Shows bot information."""
    bot.send_message(message.chat.id, INFO_TEXT, reply_markup=make_keyboard())


@bot.message_handler(commands=["help"])
def cmd_help(message: types.Message) -> None:
    """Handle /help command. Shows usage guide."""
    bot.send_message(message.chat.id, HELP_TEXT, reply_markup=make_keyboard())


# ═══════════════════════════════════════════════════════════════
# Callback Query Handler (Inline Buttons)
# ═══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery) -> None:
    """Handle all inline button callbacks.
    
    Edits the current message (instead of sending new ones)
    to keep the chat clean and provide smooth UX.
    
    Args:
        call: CallbackQuery from inline button press
    """
    chat_id = call.message.chat.id
    action = call.data
    session = get_session(chat_id)
    
    try:
        if action == "new":
            # Create new email and update message
            result = handle_new(chat_id, session)
            bot.edit_message_text(result, chat_id, call.message.message_id, reply_markup=make_keyboard())
            
        elif action == "inbox":
            # Check inbox and update message
            result = handle_inbox(chat_id, session)
            bot.edit_message_text(result, chat_id, call.message.message_id, reply_markup=make_keyboard())
            
        elif action == "info":
            # Show info and update message
            bot.edit_message_text(INFO_TEXT, chat_id, call.message.message_id, reply_markup=make_keyboard())
            
        elif action == "source":
            # Show source code link and update message
            bot.edit_message_text("🔗 Source code:\n" + SOURCE_URL, chat_id, call.message.message_id, reply_markup=make_keyboard())
            
        elif action == "help":
            # Show help and update message
            bot.edit_message_text(HELP_TEXT, chat_id, call.message.message_id, reply_markup=make_keyboard())
            
    except Exception as e:
        if "message is not modified" in str(e):
            bot.answer_callback_query(call.id)
        else:
            logger.error(f"Callback error: {e}")
            bot.answer_callback_query(call.id, "Error occurred")


# ═══════════════════════════════════════════════════════════════
# Graceful Shutdown
# ═══════════════════════════════════════════════════════════════

def signal_handler(sig, frame):
    """Handle shutdown signals for clean exit."""
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"Starting {SERVICE_NAME} Bot...")
    logger.info(f"API: {BASE_URL}")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
