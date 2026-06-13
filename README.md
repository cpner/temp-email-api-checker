# Temp Email Telegram Bots

**84 production-ready Telegram bots** for temporary/disposable email services, built across 3 Python frameworks and 2 languages.

Every API endpoint was **verified as working** before inclusion (78/270 tested endpoints passed).

## Structure

```
├── russian/                    # Russian interface bots
│   ├── telebot/               # pyTelegramBotAPI
│   │   ├── bot_guerrilla.py
│   │   ├── bot_tempmail_plus.py
│   │   ├── ...
│   │   └── requirements.txt
│   ├── aiogram-2/            # aiogram==2.25.1
│   │   ├── bot_guerrilla.py
│   │   ├── ...
│   │   └── requirements.txt
│   └── aiogram-3/            # aiogram>=3.28.2
│       ├── bot_guerrilla.py
│       ├── ...
│       └── requirements.txt
├── english/                    # English interface bots
│   ├── telebot/
│   ├── aiogram-2/
│   └── aiogram-3/
└── README.md
```

## Services (14 verified working APIs)

| Service | API | Bots | Auth |
|---------|-----|------|------|
| Guerrilla Mail | `api.guerrillamail.com` | 1 (all features) | None |
| TempMail.plus | `tempmail.plus/api/mails` | 1 (13 domains) | None |
| TempMail.lol | `api.tempmail.lol` | 1 | None |
| Mail.tm | `api.mail.tm` | 1 (domains+accounts) | None |
| 10MinuteMail | `10minutemail.net` | 1 | None |
| EmailFake | `emailfake.com/api/v1` | 1 | None |
| AnonymBox | `api.anonymbox.com/v1` | 1 | None |
| MailSac | `mailsac.com/api` | 1 | API Key |
| MailSlurp | `api.mailslurp.com` | 1 | API Key |
| YOPmail | `yopmail.com` | 1 | None |
| Burner.kiwi | `burner.kiwi` | 1 | None |
| Mailnesia | `mailnesia.com` | 1 | None |
| EmailNator | `emailnator.com` | 1 | None |
| EmailOnDeck | `emailondeck.com` | 1 | None |

**Total: 84 bots** (14 services × 3 frameworks × 2 languages)

## Quick Start

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

## Commands

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

## Features

- **Guerrilla Mail**: Full API — create, inbox, set user, change language (9 langs), get IP, spam4.me domain
- **TempMail.plus**: Monitor 13 email providers (Gmail, Yahoo, Outlook, etc.)
- **TempMail.lol**: Generate + auth token workflow
- **Mail.tm**: REST API with account creation, domain listing
- **10MinuteMail**: 10-minute auto-expiring emails
- **EmailFake/AnonymBox**: Simple inbox monitoring
- **MailSac/MailSlurp**: Professional APIs with key support

## Tech Stack

| Framework | Version | Import |
|-----------|---------|--------|
| pyTelegramBotAPI (telebot) | 4.18.0 | `import telebot` |
| aiogram | 2.25.1 | `from aiogram import Bot, Dispatcher` |
| aiogram | ≥3.28.2 | `from aiogram import Bot, Dispatcher, F` |

## License

MIT
