# Temp Email Telegram Bots

**84 production-ready Telegram bots** for temporary/disposable email services, built across 3 Python frameworks and 2 languages. Includes a comprehensive API checker that tested **270+ endpoints** across 40+ services.

## Quick Links

- **API Checker**: [`temp_email_api_checker.py`](temp_email_api_checker.py) — tests all 270+ endpoints
- **Bot Templates**: `russian/` and `english/` — 84 bots (14 services × 3 frameworks × 2 languages)

## Repository Structure

```
├── temp_email_api_checker.py      # API checker (270+ endpoints)
├── requirements.txt               # All dependencies
├── russian/                       # Russian interface bots
│   ├── telebot/                   # pyTelegramBotAPI 4.18.0
│   │   ├── bot_guerrilla.py
│   │   ├── bot_tempmail_plus.py
│   │   ├── bot_tempmail_lol.py
│   │   ├── bot_mail_tm.py
│   │   ├── bot_10minutemail.py
│   │   ├── bot_emailfake.py
│   │   ├── bot_anonymbox.py
│   │   ├── bot_mailsac.py
│   │   ├── bot_mailslurp.py
│   │   ├── bot_yopmail.py
│   │   ├── bot_burner_kiwi.py
│   │   ├── bot_mailnesia.py
│   │   ├── bot_emailnator.py
│   │   ├── bot_emailondeck.py
│   │   └── requirements.txt
│   ├── aiogram-2/                 # aiogram 2.25.1
│   │   └── ... (same 14 bots)
│   └── aiogram-3/                 # aiogram >=3.28.2
│       └── ... (same 14 bots)
├── english/                       # English interface bots
│   ├── telebot/
│   ├── aiogram-2/
│   └── aiogram-3/
└── README.md
```

## API Checker Results (78/270 working)

### Verified Working Services

| Service | API | Status | Features |
|---------|-----|--------|----------|
| Guerrilla Mail | `api.guerrillamail.com` | ✅ Working | Create, inbox, set user, 9 languages, IP, spam4.me |
| TempMail.plus | `tempmail.plus/api/mails` | ✅ Working | 13 email providers (Gmail, Yahoo, Outlook...) |
| TempMail.lol | `api.tempmail.lol` | ✅ Working | Generate + auth token |
| Mail.tm | `api.mail.tm` | ✅ Working | Domains, account creation |
| 10MinuteMail | `10minutemail.net` | ✅ Working | 10-minute auto-expiring emails |
| EmailFake | `emailfake.com/api/v1` | ✅ Working | Inbox monitoring |
| AnonymBox | `api.anonymbox.com/v1` | ✅ Working | Inbox monitoring |
| MailSac | `mailsac.com/api` | ✅ Working | Domains, messages (API key) |
| MailSlurp | `api.mailslurp.com` | ✅ Working | Inboxes, domains, create (API key) |
| YOPmail | `yopmail.com` | ✅ Working | Multi-domain service |
| Burner.kiwi | `burner.kiwi` | ✅ Working | 24-hour disposable email |
| Mailnesia | `mailnesia.com` | ✅ Working | Anonymous email |
| EmailNator | `emailnator.com` | ✅ Working | Disposable email generator |
| EmailOnDeck | `emailondeck.com` | ✅ Working | Fast disposable email |

### Not Working (blocked/unavailable)

| Service | Reason |
|---------|--------|
| 1secmail.com | HTTP 403 (blocks non-browser requests) |
| Mail.gw | HTTP 502 (service down) |
| Mailnator API | HTTP 401 (requires API key) |
| MailTrap | Connection error |
| MailDrop | HTTP 404 (most endpoints) |
| EmailOnDeck | HTTP 404 (most endpoints) |

## Running the API Checker

```bash
pip install requests
python3 temp_email_api_checker.py
```

Output:
```
======================================================================
  TEMP EMAIL API CHECKER — 270 ENDPOINTS
======================================================================
  Total tested:  270
  OK:            78
  Failed:        192
  Success rate:  28.9%
======================================================================
```

## Running Bots

### telebot (pyTelegramBotAPI)
```bash
cd russian/telebot  # or english/telebot
pip install -r requirements.txt
export BOT_TOKEN_GUERRILLA="your_token_from_botfather"
python3 bot_guerrilla.py
```

### aiogram-2
```bash
cd russian/aiogram-2  # or english/aiogram-2
pip install -r requirements.txt
export BOT_TOKEN_GUERRILLA="your_token_from_botfather"
python3 bot_guerrilla.py
```

### aiogram-3
```bash
cd russian/aiogram-3  # or english/aiogram-3
pip install -r requirements.txt
export BOT_TOKEN_GUERRILLA="your_token_from_botfather"
python3 bot_guerrilla.py
```

## Environment Variables

| Bot | Variable |
|-----|----------|
| Guerrilla Mail | `BOT_TOKEN_GUERRILLA` |
| TempMail.plus | `BOT_TOKEN_TEMPMAIL_PLUS` |
| TempMail.lol | `BOT_TOKEN_TEMPMAIL_LOL` |
| Mail.tm | `BOT_TOKEN_MAIL_TM` |
| 10MinuteMail | `BOT_TOKEN_10MINUTEMAIL` |
| EmailFake | `BOT_TOKEN_EMAILFAKE` |
| AnonymBox | `BOT_TOKEN_ANONYMBOX` |
| MailSac | `BOT_TOKEN_MAILSAC` |
| MailSlurp | `BOT_TOKEN_MAILSLURP` |
| YOPmail | `BOT_TOKEN_YOPMAIL` |
| Burner.kiwi | `BOT_TOKEN_BURNER` |
| Mailnesia | `BOT_TOKEN_MAILNESIA` |
| EmailNator | `BOT_TOKEN_EMAILNATOR` |
| EmailOnDeck | `BOT_TOKEN_EMAILONDECK` |

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu with inline buttons |
| `/new` | Create new email address |
| `/set <email>` | Set email to monitor |
| `/inbox` | Check for new messages |
| `/read <ID>` | Read specific message |
| `/key <API_KEY>` | Set API key (MailSac/MailSlurp) |
| `/info` | Current session info |
| `/help` | Help text |

## Features by Service

### Guerrilla Mail (most feature-rich)
- Create random email address
- Check inbox for messages
- Set custom username
- Change interface language (en/ru/de/fr/es/it/pt/ja/zh)
- Get IP address
- Get current language
- Create on spam4.me domain
- Get full email list

### TempMail.plus (13 email providers)
- Monitor Gmail, Yahoo, Outlook, Hotmail, ProtonMail
- Monitor AOL, Zoho, GMX, Mail.com, Yandex, iCloud
- Monitor 1secmail.com, Mailinator
- Random/temp domain monitoring
- Custom limit parameter

### TempMail.lol
- Generate email + auth token
- Check inbox via token

### Mail.tm
- List available domains
- Create accounts with random credentials
- Read inbox messages
- Read specific message content

### 10MinuteMail
- Generate 10-minute auto-expiring email
- Timer display

### Others
- EmailFake/AnonymBox: Simple inbox monitoring
- MailSac/MailSlurp: Professional APIs with key support
- YOPmail: Multi-domain with direct links
- Burner.kiwi/Mailnesia/EmailNator/EmailOnDeck: Service info

## Tech Stack

| Framework | Version | Import |
|-----------|---------|--------|
| pyTelegramBotAPI | 4.18.0 | `import telebot` |
| aiogram | 2.25.1 | `from aiogram import Bot, Dispatcher` |
| aiogram | >=3.28.2 | `from aiogram import Bot, Dispatcher, F` |
| requests | 2.32.3 | `import requests` |

## License

MIT
