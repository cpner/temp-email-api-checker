#!/usr/bin/env python3
"""Генератор всех ботов-файлов"""
import os

BOTS = {
    "bot_guerrilla_mail": {
        "name": "Guerrilla Mail",
        "desc": "Полный API: создание, чтение, смена имени, языков",
        "api_base": "https://api.guerrillamail.com/ajax.php",
        "features": ["new_email", "inbox", "read", "set_user", "change_lang", "get_ip"],
    },
    "bot_tempmail_plus": {
        "name": "TempMail.plus",
        "desc": "Мониторинг почты любых доменов (gmail, yahoo, outlook...)",
        "api_base": "https://tempmail.plus/api/mails",
        "features": ["set_email", "inbox", "auto_refresh"],
    },
    "bot_tempmail_lol": {
        "name": "TempMail.lol",
        "desc": "Генерация почты + чтение по токену",
        "api_base": "https://api.tempmail.lol",
        "features": ["generate", "inbox", "auth"],
    },
    "bot_mail_tm": {
        "name": "Mail.tm",
        "desc": "REST API: создание аккаунтов, домены, чтение",
        "api_base": "https://api.mail.tm",
        "features": ["new_account", "domains", "inbox", "read", "login"],
    },
    "bot_mail_gw": {
        "name": "Mail.gw",
        "desc": "Альтернатива Mail.tm с похожим API",
        "api_base": "https://api.mail.gw",
        "features": ["new_account", "domains", "inbox", "read"],
    },
    "bot_10minutemail": {
        "name": "10 Minute Mail",
        "desc": "Почта на 10 минут с таймером",
        "api_base": "https://10minutemail.net/address.api.php",
        "features": ["generate", "inbox", "timer"],
    },
    "bot_1secmail": {
        "name": "1secmail",
        "desc": "Почта с доменами 1secmail.com/net/org",
        "api_base": "https://www.1secmail.com/api/v1/",
        "features": ["generate", "domains", "inbox", "read", "delete"],
    },
    "bot_emailfake": {
        "name": "EmailFake",
        "desc": "Простая проверка почтовых ящиков",
        "api_base": "https://emailfake.com/api/v1",
        "features": ["set_email", "inbox"],
    },
    "bot_anonymbox": {
        "name": "AnonymBox",
        "desc": "Анонимная почта без регистрации",
        "api_base": "https://api.anonymbox.com/v1",
        "features": ["set_email", "inbox"],
    },
    "bot_dropmail": {
        "name": "DropMail",
        "desc": "GraphQL API для создания сессий",
        "api_base": "https://dropmail.me/api/graphql",
        "features": ["new_session", "inbox"],
    },
    "bot_yopmail": {
        "name": "YOPmail",
        "desc": "Популярный сервис с многими доменами",
        "api_base": "https://yopmail.com",
        "features": ["inbox", "domains"],
        "note": "HTML-based, скрапинг",
    },
    "bot_mailsac": {
        "name": "MailSac",
        "desc": "API с ключом, профессиональный сервис",
        "api_base": "https://mailsac.com/api",
        "features": ["set_key", "inbox", "domains"],
        "note": "Требует API ключ",
    },
    "bot_mailslurp": {
        "name": "MailSlurp",
        "desc": "Профессиональный API для тестирования",
        "api_base": "https://api.mailslurp.com",
        "features": ["set_key", "create_inbox", "inbox", "domains"],
        "note": "Требует API ключ",
    },
    "bot_mailtrap": {
        "name": "Mailtrap",
        "desc": "Тестовый SMTP-сервис с API",
        "api_base": "https://api.mailtrap.io",
        "features": ["set_key", "inbox", "messages"],
        "note": "Требует API ключ",
    },
    "bot_dispostable": {
        "name": "Dispostable",
        "desc": "Простая одноразовая почта",
        "api_base": "https://www.dispostable.com/api/v1",
        "features": ["set_email", "inbox"],
    },
    "bot_fakemailgenerator": {
        "name": "FakeMailGenerator",
        "desc": "Генератор с доменами cuvox, armyspy и др.",
        "api_base": "https://www.fakemailgenerator.com",
        "features": ["set_email", "inbox"],
        "note": "HTML-based, скрапинг",
    },
    "bot_mailnesia": {
        "name": "Mailnesia",
        "desc": "Анонимная почта mailnesia.com",
        "api_base": "https://mailnesia.com",
        "features": ["set_email", "inbox"],
        "note": "HTML-based, скрапинг",
    },
    "bot_burner_kiwi": {
        "name": "Burner.kiwi",
        "desc": "Быстрая одноразовая почта .kiwi",
        "api_base": "https://burner.kiwi",
        "features": ["generate", "inbox"],
        "note": "HTML-based",
    },
    "bot_getnada": {
        "name": "GetNada",
        "desc": "Почта с несколькими доменами",
        "api_base": "https://getnada.com/api/v1",
        "features": ["set_email", "inbox"],
    },
    "bot_trashmail": {
        "name": "TrashMail",
        "desc": "Одноразовая почта с пересылкой",
        "api_base": "https://api.trashmail.net",
        "features": ["set_email", "inbox"],
    },
    "bot_spamgourmet": {
        "name": "SpamGourmet",
        "desc": "Почта с автоматическим завершением",
        "api_base": "https://www.spamgourmet.com/xmlapi.pl",
        "features": ["generate", "domains"],
    },
    "bot_tempmail_io": {
        "name": "TempMail.io",
        "desc": "API v1 для создания ящиков",
        "api_base": "https://temp-mail.io/api/v1",
        "features": ["new_inbox", "inbox"],
    },
    "bot_emailondeck": {
        "name": "EmailOnDeck",
        "desc": "Быстрая одноразовая почта",
        "api_base": "https://api.emailondeck.com/v1",
        "features": ["set_email", "inbox"],
    },
    "bot_maildrop": {
        "name": "MailDrop",
        "desc": "Простой API для ящиков",
        "api_base": "https://api.maildrop.cc/v2",
        "features": ["set_email", "inbox"],
    },
    "bot_tempmail_org": {
        "name": "Temp-mail.org",
        "desc": "Получение доменов для создания почты",
        "api_base": "https://api.temp-mail.org",
        "features": ["domains", "generate"],
    },
    "bot_guerrilla_spam4": {
        "name": "Guerrilla Spam4.me",
        "desc": "Альтернативный домен Guerrilla",
        "api_base": "https://api.guerrillamail.com/ajax.php",
        "features": ["new_email", "inbox", "read"],
        "site": "spam4.me",
    },
}

print(f"Генерация {len(BOTS)} ботов...")
for key, info in BOTS.items():
    print(f"  - {key}: {info['name']}")
print(f"\nВсего: {len(BOTS)} ботов")
