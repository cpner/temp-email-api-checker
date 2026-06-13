# Temp Email Telegram Bots

**39 standalone Telegram bots** — each file wraps a unique, verified-working temporary email API endpoint.

## Bot Inventory

### Guerrilla Mail (8 bots)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 01 | `01_guerrilla_create_email.py` | `get_email_address` | Generate random disposable email |
| 02 | `02_guerrilla_check_inbox.py` | `check_email` | Poll inbox for new messages |
| 03 | `03_guerrilla_set_user.py` | `set_email_user` | Set custom username |
| 04 | `04_guerrilla_get_ip.py` | `get_ip` | Retrieve session IP address |
| 05 | `05_guerrilla_get_lang.py` | `get_lang` | Get current language setting |
| 06 | `06_guerrilla_change_lang.py` | `change_lang` | Switch language (en/ru/de/fr/es/it/pt/ja/zh) |
| 07 | `07_guerrilla_spam4.py` | `get_email_address&site=spam4.me` | Create on spam4.me domain |
| 08 | `08_guerrilla_get_list.py` | `get_email_list` | Retrieve full email list |

### TempMail.plus — Domain Monitors (15 bots)
| # | File | Target Domain |
|---|------|---------------|
| 09 | `09_tempmail_plus_gmail_com.py` | gmail.com |
| 10 | `10_tempmail_plus_yahoo_com.py` | yahoo.com |
| 11 | `11_tempmail_plus_outlook_com.py` | outlook.com |
| 12 | `12_tempmail_plus_hotmail_com.py` | hotmail.com |
| 13 | `13_tempmail_plus_protonmail_com.py` | protonmail.com |
| 14 | `14_tempmail_plus_aol_com.py` | aol.com |
| 15 | `15_tempmail_plus_zoho_com.py` | zoho.com |
| 16 | `16_tempmail_plus_gmx_com.py` | gmx.com |
| 17 | `17_tempmail_plus_mail_com.py` | mail.com |
| 18 | `18_tempmail_plus_yandex_com.py` | yandex.com |
| 19 | `19_tempmail_plus_icloud_com.py` | icloud.com |
| 20 | `20_tempmail_plus_1secmail_com.py` | 1secmail.com |
| 21 | `21_tempmail_plus_mailinator_com.py` | mailinator.com |
| 22 | `22_tempmail_plus_random.py` | Random/temp domains |
| 23 | `23_tempmail_plus_limit.py` | Custom limit parameter |

### TempMail.lol (2 bots)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 24 | `24_tempmail_lol_generate.py` | `api/generate` | Generate email + auth token |
| 25 | `25_tempmail_lol_auth.py` | `api/auth/{token}` | Check inbox via auth token |

### Mail.tm (1 bot)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 26 | `26_mail_tm_domains.py` | `api/domains` | List domains, create accounts, read mail |

### 10MinuteMail (1 bot)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 27 | `27_10minutemail_generate.py` | `address.api.php` | Generate 10-minute email |

### EmailFake (1 bot)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 28 | `28_emailfake_inbox.py` | `api/v1/inbox/{email}` | Monitor any email inbox |

### AnonymBox (1 bot)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 29 | `29_anonymbox_inbox.py` | `api/v1/inbox/{email}` | Monitor anonymous email |

### YOPmail (1 bot)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 30 | `30_yopmail_main.py` | `yopmail.com` | Multi-domain disposable email |

### MailSac (2 bots)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 31 | `31_mailsac_domains.py` | `api/domains` | List available domains |
| 32 | `32_mailsac_messages.py` | `api/addresses/{email}/messages` | Retrieve messages |

### MailSlurp (4 bots)
| # | File | API Endpoint | Function |
|---|------|-------------|----------|
| 33 | `33_mailslurp_inboxes.py` | `inboxes` | List all inboxes |
| 34 | `34_mailslurp_domains.py` | `domains` | List verified domains |
| 35 | `35_mailslurp_create.py` | `inboxes (POST)` | Create new inbox |
| 36 | `36_mailslurp_empty.py` | `inboxes?page=1` | Get empty inboxes |

### Other Services (4 bots)
| # | File | Service | Function |
|---|------|---------|----------|
| 37 | `37_burner_kiwi.py` | Burner.kiwi | Disposable email (24h expiry) |
| 38 | `38_mailnesia.py` | Mailnesia | Anonymous email |
| 39 | `39_emailondeck.py` | EmailOnDeck | Fast disposable email |

---

## Quick Start

```bash
# Install dependencies
pip install pyTelegramBotAPI requests

# Set your bot token from @BotFather
export BOT_TOKEN_GCREATE="your_token_here"

# Run any bot
python3 01_guerrilla_create_email.py
```

## Environment Variables

| Bot | Env Variable |
|-----|-------------|
| 01-08 Guerrilla | `BOT_TOKEN_GCREATE`, `BOT_TOKEN_GINBOX`, `BOT_TOKEN_GUSER`, `BOT_TOKEN_GIP`, `BOT_TOKEN_GLANG`, `BOT_TOKEN_GCHLANG`, `BOT_TOKEN_GSPAM4`, `BOT_TOKEN_GLIST` |
| 09-21 TempMail.plus | `BOT_TOKEN_TP_GMAIL_COM`, `BOT_TOKEN_TP_YAHOO_COM`, etc. |
| 22-23 TempMail.plus | `BOT_TOKEN_TP_RANDOM`, `BOT_TOKEN_TP_LIMIT` |
| 24-25 TempMail.lol | `BOT_TOKEN_TML_GEN`, `BOT_TOKEN_TML_AUTH` |
| 26 Mail.tm | `BOT_TOKEN_MAIL_TM` |
| 27 10MinuteMail | `BOT_TOKEN_10MIN` |
| 28 EmailFake | `BOT_TOKEN_EMAILFAKE` |
| 29 AnonymBox | `BOT_TOKEN_ANONBOX` |
| 30 YOPmail | `BOT_TOKEN_YOPMAIL` |
| 31-32 MailSac | `BOT_TOKEN_MAILSAC`, `BOT_TOKEN_MAILSAC_MSG` |
| 33-36 MailSlurp | `BOT_TOKEN_MLSLURP`, `BOT_TOKEN_MLSLURP_DOM`, `BOT_TOKEN_MLSLURP_CR`, `BOT_TOKEN_MLSLURP_EMP` |
| 37-39 Other | `BOT_TOKEN_BURNER`, `BOT_TOKEN_MAILNESIA`, `BOT_TOKEN_EMAILONDECK` |

## Commands (Universal)

| Command | Description |
|---------|-------------|
| `/start` | Show main menu with inline buttons |
| `/new` | Create a new email address |
| `/set <email>` | Set email to monitor manually |
| `/inbox` | Check for new messages |
| `/read <ID>` | Read a specific message |
| `/key <API_KEY>` | Set API key (MailSac/MailSlurp) |
| `/info` | Show current session info |
| `/help` | Display help text |

## API Providers

| Provider | Auth | Free Tier | Rate Limit |
|----------|------|-----------|------------|
| Guerrilla Mail | None | Unlimited | Generous |
| TempMail.plus | None | Unlimited | Generous |
| TempMail.lol | None | Unlimited | Moderate |
| Mail.tm | None (create account) | Unlimited | Moderate |
| 10MinuteMail | None | 1 email/10min | Strict |
| MailSac | API Key | 50 req/day | Strict |
| MailSlurp | API Key | 50 inboxes | Moderate |

## License

MIT
