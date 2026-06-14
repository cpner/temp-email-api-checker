# Temp Email Telegram Bots

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Last Check](https://img.shields.io/badge/Last%20API%20Check-2026--06--13-orange.svg)](#api-checker-results)
[![APIs Tested](https://img.shields.io/badge/APIs%20Tested-270+-red.svg)](#api-checker-results)
[![Working APIs](https://img.shields.io/badge/Working-78-brightgreen.svg)](#api-checker-results)
[![Bots](https://img.shields.io/badge/Bots-84-blueviolet.svg)](#repository-structure)

**84 production-ready Telegram bots** for temporary/disposable email services, built across 3 Python frameworks and 2 languages. Includes a comprehensive API checker that tested **270+ endpoints** across 40+ services.

## Author

| | |
|---|---|
| **Name** | Vladislav Alekseevich Sofronov |
| **GitHub** | [cpner](https://github.com/cpner) |
| **Telegram** | [t.me/reejb](https://t.me/reejb) |
| **Telegram Bot** | [t.me/marco_feedback_bot](https://t.me/marco_feedback_bot) |
| **Email** | [feedback@gondon.su](mailto:feedback@gondon.su) |
| **Website** | [gondon.su](https://gondon.su) |
| **City** | Cherepovets, Russia |

## Quick Start

```bash
# Clone
git clone https://github.com/cpner/temp-email-api-checker.git
cd temp-email-api-checker

# Run API checker
pip install requests
python3 temp_email_api_checker.py

# Run a bot
cd russian/telebot
pip install -r requirements.txt
export BOT_TOKEN_GUERRILLA="your_token_from_botfather"
python3 bot_guerrilla.py
```

## Repository Structure

```
├── temp_email_api_checker.py      # API checker (270+ endpoints)
├── requirements.txt               # All dependencies
├── LICENSE                        # MIT License — Vladislav Sofronov
├── CONTRIBUTING.md                # Contribution guidelines
├── SECURITY.md                    # Security policy
├── CODE_OF_CONDUCT.md             # Code of conduct
├── .github/                       # GitHub templates & CI
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── check_apis.yml         # Weekly API check
├── russian/                       # Russian interface bots
│   ├── telebot/                   # pyTelegramBotAPI 4.18.0
│   │   ├── bot_guerrilla.py       # Guerrilla Mail
│   │   ├── bot_tempmail_plus.py   # TempMail.plus
│   │   ├── bot_tempmail_lol.py    # TempMail.lol
│   │   ├── bot_mail_tm.py         # Mail.tm
│   │   ├── bot_10minutemail.py    # 10MinuteMail
│   │   ├── bot_emailfake.py       # EmailFake
│   │   ├── bot_anonymbox.py       # AnonymBox
│   │   ├── bot_mailsac.py         # MailSac
│   │   ├── bot_mailslurp.py       # MailSlurp
│   │   ├── bot_yopmail.py         # YOPmail
│   │   ├── bot_burner_kiwi.py     # Burner.kiwi
│   │   ├── bot_mailnesia.py       # Mailnesia
│   │   ├── bot_emailnator.py      # EmailNator
│   │   ├── bot_emailondeck.py     # EmailOnDeck
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

## API Checker Results

### Last Check: 2026-06-13 22:44 UTC

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

### Verified Working (78 endpoints)

| # | Service | API | Endpoints | Status |
|---|---------|-----|-----------|--------|
| 1 | Guerrilla Mail | `api.guerrillamail.com` | 15 | ✅ All working |
| 2 | TempMail.plus | `tempmail.plus/api/mails` | 42 | ✅ All working |
| 3 | TempMail.lol | `api.tempmail.lol` | 2 | ✅ All working |
| 4 | Mail.tm | `api.mail.tm` | 1 | ✅ Working |
| 5 | 10MinuteMail | `10minutemail.net` | 1 | ✅ Working |
| 6 | EmailFake | `emailfake.com/api/v1` | 1 | ✅ Working |
| 7 | AnonymBox | `api.anonymbox.com/v1` | 1 | ✅ Working |
| 8 | MailSac | `mailsac.com/api` | 2 | ✅ Working (key) |
| 9 | MailSlurp | `api.mailslurp.com` | 5 | ✅ Working (key) |
| 10 | YOPmail | `yopmail.com` | 2 | ✅ Working |
| 11 | Burner.kiwi | `burner.kiwi` | 1 | ✅ Working |
| 12 | Mailnesia | `mailnesia.com` | 1 | ✅ Working |
| 13 | EmailNator | `emailnator.com` | 1 | ✅ Working |
| 14 | EmailOnDeck | `emailondeck.com` | 1 | ✅ Working |

### Not Working (192 endpoints)

| Service | Reason | Code |
|---------|--------|------|
| 1secmail.com | Blocks non-browser requests | 403 |
| Mail.gw | Service down | 502 |
| Mailnator | Requires API key | 401 |
| MailTrap | Connection error | — |
| MailDrop | Most endpoints | 404 |
| EmailOnDeck | Most endpoints | 404 |
| DropMail | Wrong method | 405 |
| Mailnesia | API endpoints | 404/503 |
| Trashmail.io | Timeout | — |
| YOPmail inbox | Rate limited | 429 |
| Others | Various | — |

## Services Detail

### Guerrilla Mail (15 endpoints)
Full REST API — no registration required.
- Create random email address
- Check inbox for messages
- Set custom username
- Change interface language (9 languages: en/ru/de/fr/es/it/pt/ja/zh)
- Get IP address
- Get current language
- Create on spam4.me domain
- Get full email list

### TempMail.plus (42 endpoints)
Monitor inbox for any email provider.
- **Supported:** Gmail, Yahoo, Outlook, Hotmail, ProtonMail, AOL, Zoho, GMX, Mail.com, Yandex, iCloud, 1secmail, Mailinator
- Random/temp domain monitoring
- Custom limit parameter

### TempMail.lol (2 endpoints)
Simple generate + auth workflow.
- Generate email + auth token
- Check inbox via token

### Mail.tm (1 endpoint)
REST API with account creation.
- List available domains
- Create accounts with random credentials
- Read inbox messages
- Read specific message content

### 10MinuteMail (1 endpoint)
Auto-expiring emails.
- Generate 10-minute email
- Timer display

### Others
- **EmailFake/AnonymBox:** Simple inbox monitoring
- **MailSac/MailSlurp:** Professional APIs with key support
- **YOPmail:** Multi-domain with direct links
- **Burner.kiwi/Mailnesia/EmailNator/EmailOnDeck:** Service info

## Running Bots

### Frameworks

| Framework | Version | Directory |
|-----------|---------|-----------|
| pyTelegramBotAPI | 4.18.0 | `*/telebot/` |
| aiogram | 2.25.1 | `*/aiogram-2/` |
| aiogram | >=3.28.2 | `*/aiogram-3/` |

### Commands

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

### Environment Variables

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

**Author:** Vladislav Sofronov (cpner)

## Contact

| | |
|---|---|
| **Telegram** | [t.me/reejb](https://t.me/reejb) |
| **Bot** | [t.me/marco_feedback_bot](https://t.me/marco_feedback_bot) |
| **Email** | [feedback@gondon.su](mailto:feedback@gondon.su) |
| **Website** | [gondon.su](https://gondon.su) |


