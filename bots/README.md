# Telegram-боты временной почты

6 отдельных ботов, каждый работает с **реальным рабочим API**.

## Боты

| Файл | API | Особенности |
|------|-----|-------------|
| `bot_guerrilla.py` | Guerrilla Mail | Полный API: создание, чтение, смена имени |
| `bot_tempmail_lol.py` | TempMail.lol | Генерация + токен, авто-обновление |
| `bot_mail_tm.py` | Mail.tm | REST API, создание аккаунтов, чтение |
| `bot_10minutemail.py` | 10 Minute Mail | Автоудаление через 10 минут |
| `bot_tempmail_plus.py` | TempMail.plus | Любые домены: gmail, yahoo, outlook... |
| `bot_emailfake.py` | EmailFake | Простая проверка ящиков |
| `bot_anonymbox.py` | AnonymBox | Анонимная почта |

## Установка

```bash
pip install pyTelegramBotAPI requests
```

## Настройка

1. Получите токен бота у [@BotFather](https://t.me/BotFather)
2. Вставьте токен в `BOT_TOKEN` в каждом файле
3. Запустите нужного бота:

```bash
python bot_guerrilla.py
```

## Команды (общие)

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/new` | Создать новую почту |
| `/inbox` | Проверить входящие |
| `/read <ID>` | Прочитать письмо |
| `/set <email>` | Установить почту вручную |
| `/info` | Данные текущей почты |
| `/help` | Справка |

## Рабочие API (проверено)

- **Guerrilla Mail** — полный доступ, без ключей
- **TempMail.lol** — генерация + чтение по токену
- **Mail.tm** — REST API, создание аккаунтов
- **10 Minute Mail** — почта на 10 минут
- **TempMail.plus** — мониторинг любых доменов
- **EmailFake** — простая проверка
- **AnonymBox** — анонимная почта
