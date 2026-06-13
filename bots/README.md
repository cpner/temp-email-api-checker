# Telegram-боты временной почты

**26 ботов**, каждый работает с отдельным API. Все API проверены как рабочие.

## Все боты

| # | Файл | API | Тип |
|---|------|-----|-----|
| 1 | `bot_guerrilla_mail.py` | Guerrilla Mail | REST API |
| 2 | `bot_tempmail_plus.py` | TempMail.plus | REST API |
| 3 | `bot_tempmail_lol.py` | TempMail.lol | REST API |
| 4 | `bot_mail_tm.py` | Mail.tm | REST API |
| 5 | `bot_mail_gw.py` | Mail.gw | REST API |
| 6 | `bot_10minutemail.py` | 10MinuteMail | REST API |
| 7 | `bot_1secmail.py` | 1secmail.com | REST API |
| 8 | `bot_emailfake.py` | EmailFake | REST API |
| 9 | `bot_anonymbox.py` | AnonymBox | REST API |
| 10 | `bot_dropmail.py` | DropMail | GraphQL API |
| 11 | `bot_yopmail.py` | YOPmail | HTML/scraping |
| 12 | `bot_mailsac.py` | MailSac | REST API (key) |
| 13 | `bot_mailslurp.py` | MailSlurp | REST API (key) |
| 14 | `bot_mailtrap.py` | Mailtrap | REST API (key) |
| 15 | `bot_dispostable.py` | Dispostable | REST API |
| 16 | `bot_fakemailgenerator.py` | FakeMailGenerator | HTML |
| 17 | `bot_mailnesia.py` | Mailnesia | HTML |
| 18 | `bot_burner_kiwi.py` | Burner.kiwi | HTML |
| 19 | `bot_getnada.py` | GetNada | REST API |
| 20 | `bot_trashmail.py` | TrashMail | REST API |
| 21 | `bot_spamgourmet.py` | SpamGourmet | XML API |
| 22 | `bot_tempmail_io.py` | TempMail.io | REST API |
| 23 | `bot_emailondeck.py` | EmailOnDeck | REST API |
| 24 | `bot_maildrop.py` | MailDrop | REST API v2 |
| 25 | `bot_tempmail_org.py` | Temp-mail.org | REST API |
| 26 | `bot_guerrilla_spam4.py` | Guerrilla Spam4.me | REST API |

## Установка

```bash
pip install pyTelegramBotAPI requests
```

## Запуск

```bash
# Получите токен у @BotFather

# Запустить конкретного бота:
BOT_TOKEN_1SECMAIL="ваш_токен" python3 bots/bot_1secmail.py
BOT_TOKEN_GUERRILLA="ваш_токен" python3 bots/bot_guerrilla_mail.py
BOT_TOKEN_TEMPMAIL_PLUS="ваш_токен" python3 bots/bot_tempmail_plus.py

# Или вставить токен прямо в файл (найти YOUR_TOKEN)
```

## Команды (общие для всех)

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/new` | Создать почту |
| `/set <email>` | Установить почту |
| `/inbox` | Проверить входящие |
| `/read <ID>` | Прочитать письмо |
| `/key <KEY>` | Установить API ключ |
| `/info` | Данные почты |
| `/help` | Справка |

## Категории API

### Бесплатные без ключей (основные)
- Guerrilla Mail, TempMail.plus, TempMail.lol, Mail.tm, 10MinuteMail, 1secmail, EmailFake, AnonymBox, DropMail, MailDrop, GetNada, TrashMail, SpamGourmet, TempMail.io, EmailOnDeck, Mail.gw, Guerrilla Spam4.me

### Требуют API ключ
- MailSac, MailSlurp, Mailtrap

### HTML-based (скрапинг)
- YOPmail, Mailnesia, FakeMailGenerator, Burner.kiwi

## Проверка API

```bash
python3 temp_email_api_checker.py
```
