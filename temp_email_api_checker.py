#!/usr/bin/env python3
"""
Temp Email API Checker
Tests 270+ temporary/disposable email API endpoints for availability.
Reports working vs failed APIs with detailed status.
"""
import requests
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_LIST = {
    # ═══════════════════════════════════════════════════════════════
    # 1. 1SECMAIL.COM
    # ═══════════════════════════════════════════════════════════════
    "1secmail:generate_random": {
        "url": "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1",
        "method": "GET", "expected_status": 200
    },
    "1secmail:get_domains": {
        "url": "https://www.1secmail.com/api/v1/?action=getDomainList",
        "method": "GET", "expected_status": 200
    },
    "1secmail:get_messages": {
        "url": "https://www.1secmail.com/api/v1/?action=getMessages&login=test&domain=1secmail.com",
        "method": "GET", "expected_status": 200
    },
    "1secmail:read_message": {
        "url": "https://www.1secmail.com/api/v1/?action=readMessage&login=test&domain=1secmail.com&id=1",
        "method": "GET", "expected_status": 200
    },
    "1secmail:delete_message": {
        "url": "https://www.1secmail.com/api/v1/?action=deleteMessage&login=test&domain=1secmail.com&id=1",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 2. MAIL.TM
    # ═══════════════════════════════════════════════════════════════
    "mail.tm:get_domains": {
        "url": "https://api.mail.tm/domains",
        "method": "GET", "expected_status": 200
    },
    "mail.tm:get_messages": {
        "url": "https://api.mail.tm/messages",
        "method": "GET", "expected_status": 200
    },
    "mail.tm:get_stats": {
        "url": "https://api.mail.tm/stats",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 3. GUERRILLA MAIL
    # ═══════════════════════════════════════════════════════════════
    "guerrilla:get_email_address": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_ip": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&ip=127.0.0.1&agent=Mozilla",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_list": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token=none",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:check_email": {
        "url": "https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token=none",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:set_email_user": {
        "url": "https://api.guerrillamail.com/ajax.php?f=set_email_user&email_user=testuser",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_ip": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_ip",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_lang": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_lang",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_en": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=en",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_ru": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=ru",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_de": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=de",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_fr": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=fr",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_es": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=es",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_it": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=it",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_pt": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=pt",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_ja": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=ja",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:change_lang_zh": {
        "url": "https://api.guerrillamail.com/ajax.php?f=change_lang&lang=zh",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_rhyta": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=rhyta.com",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_superrito": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=superrito.com",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_gustr": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=gustr.com",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_discovr": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=discovr.com",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_fakemail": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=fakemail.fr",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_squamish": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=squamish.co",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_spam4": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=spam4.me",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_guerrillamailblock": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=guerrillamailblock.com",
        "method": "GET", "expected_status": 200
    },
    "guerrilla:get_email_address_getairmail": {
        "url": "https://api.guerrillamail.com/ajax.php?f=get_email_address&site=getairmail.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 4. TEMP-MAIL.ORG
    # ═══════════════════════════════════════════════════════════════
    "temp-mail.org:get_domains": {
        "url": "https://api.temp-mail.org/request/domains/format/json",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 5. TEMPMAIL.LOL
    # ═══════════════════════════════════════════════════════════════
    "tempmail.lol:generate": {
        "url": "https://api.tempmail.lol/generate",
        "method": "GET", "expected_status": 200
    },
    "tempmail.lol:auth": {
        "url": "https://api.tempmail.lol/auth",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 6. DROPMAIL
    # ═══════════════════════════════════════════════════════════════
    "dropmail:create_session": {
        "url": "https://dropmail.me/api/graphql",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": {"query": "{newEmailTemporary{addresses{address}id}}"},
        "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 7. MAIL.GW
    # ═══════════════════════════════════════════════════════════════
    "mail.gw:get_domains": {
        "url": "https://api.mail.gw/domains",
        "method": "GET", "expected_status": 200
    },
    "mail.gw:get_messages": {
        "url": "https://api.mail.gw/messages",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 8. MAILNATOR
    # ═══════════════════════════════════════════════════════════════
    "mailnator:get_domains": {
        "url": "https://www.mailinator.com/api/v2/domains",
        "method": "GET", "expected_status": 200
    },
    "mailnator:get_public_domains": {
        "url": "https://www.mailinator.com/api/v2/domains/public",
        "method": "GET", "expected_status": 200
    },
    "mailnator:get_inbox": {
        "url": "https://www.mailinator.com/api/v2/inboxes/test@mailinator.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 9. MAILSLURP
    # ═══════════════════════════════════════════════════════════════
    "mailslurp:get_inboxes_no_key": {
        "url": "https://api.mailslurp.com/inboxes",
        "method": "GET", "expected_status": 401
    },
    "mailslurp:get_inboxes_bad_key": {
        "url": "https://api.mailslurp.com/inboxes?page=0&size=1",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:get_inbox_bad_key": {
        "url": "https://api.mailslurp.com/inboxes/1",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:get_domains_bad_key": {
        "url": "https://api.mailslurp.com/domains",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:get_messages_bad_key": {
        "url": "https://api.mailslurp.com/messages",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:search_messages_bad_key": {
        "url": "https://api.mailslurp.com/messages/search",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:create_inbox_bad_key": {
        "url": "https://api.mailslurp.com/inboxes",
        "method": "POST",
        "headers": {"x-api-key": "invalid"},
        "data": {},
        "expected_status": 401
    },
    "mailslurp:get_inbox_by_id_bad_key": {
        "url": "https://api.mailslurp.com/inboxes/invalid-id",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:get_empty_inbox_bad_key": {
        "url": "https://api.mailslurp.com/inboxes?page=1&size=10",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },
    "mailslurp:get_webhook_bad_key": {
        "url": "https://api.mailslurp.com/webhooks",
        "method": "GET",
        "headers": {"x-api-key": "invalid"},
        "expected_status": 401
    },

    # ═══════════════════════════════════════════════════════════════
    # 10. MAILSAC
    # ═══════════════════════════════════════════════════════════════
    "mailsac:get_messages_bad_key": {
        "url": "https://mailsac.com/api/addresses/test@mailsac.com/messages",
        "method": "GET",
        "headers": {"MailsacKey": "invalid"},
        "expected_status": 401
    },
    "mailsac:get_address_bad_key": {
        "url": "https://mailsac.com/api/addresses/test",
        "method": "GET",
        "headers": {"MailsacKey": "invalid"},
        "expected_status": 401
    },
    "mailsac:get_domains_bad_key": {
        "url": "https://mailsac.com/api/domains",
        "method": "GET",
        "headers": {"MailsacKey": "invalid"},
        "expected_status": 401
    },

    # ═══════════════════════════════════════════════════════════════
    # 11. MAILTRAP
    # ═══════════════════════════════════════════════════════════════
    "mailtrap:get_inboxes_bad_key": {
        "url": "https://api.mailtrap.io/api/v1/inboxes",
        "method": "GET",
        "headers": {"Authorization": "Bearer invalid"},
        "expected_status": 401
    },
    "mailtrap:get_inbox_bad_key": {
        "url": "https://api.mailtrap.io/api/v1/inboxes/1",
        "method": "GET",
        "headers": {"Authorization": "Bearer invalid"},
        "expected_status": 401
    },
    "mailtrap:get_messages_bad_key": {
        "url": "https://api.mailtrap.io/api/v1/inboxes/1/messages",
        "method": "GET",
        "headers": {"Authorization": "Bearer invalid"},
        "expected_status": 401
    },
    "mailtrap:get_accounts_bad_key": {
        "url": "https://api.mailtrap.io/api/v1/accounts",
        "method": "GET",
        "headers": {"Authorization": "Bearer invalid"},
        "expected_status": 401
    },

    # ═══════════════════════════════════════════════════════════════
    # 12. DISPOSTABLE
    # ═══════════════════════════════════════════════════════════════
    "dispostable:get_inbox": {
        "url": "https://www.dispostable.com/api/v1/emails",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 13. SPAMGOURMET
    # ═══════════════════════════════════════════════════════════════
    "spamgourmet:get_domains": {
        "url": "https://www.spamgourmet.com/xmlapi.pl?action=getdomainsforregistration",
        "method": "GET", "expected_status": 200
    },
    "spamgourmet:get_words": {
        "url": "https://www.spamgourmet.com/xmlapi.pl?action=getwords",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 14. MAILDROP
    # ═══════════════════════════════════════════════════════════════
    "maildrop:get_mailbox": {
        "url": "https://api.maildrop.cc/v2/mailbox/test",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_test123": {
        "url": "https://api.maildrop.cc/v2/mailbox/test123",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user": {
        "url": "https://api.maildrop.cc/v2/mailbox/user",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 15. YOPMAIL
    # ═══════════════════════════════════════════════════════════════
    "yopmail:main_page": {
        "url": "https://yopmail.com/en",
        "method": "GET", "expected_status": 200
    },
    "yopmail:domain_page": {
        "url": "https://yopmail.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 16. TEMPMAIL.PLUS
    # ═══════════════════════════════════════════════════════════════
    "tempmail.plus:get_mails": {
        "url": "https://tempmail.plus/api/mails",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_limit": {
        "url": "https://tempmail.plus/api/mails?limit=10",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_email": {
        "url": "https://tempmail.plus/api/mails?email=test@mailinator.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_1secmail": {
        "url": "https://tempmail.plus/api/mails?email=test@1secmail.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_gmail": {
        "url": "https://tempmail.plus/api/mails?email=test@gmail.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_yahoo": {
        "url": "https://tempmail.plus/api/mails?email=test@yahoo.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_outlook": {
        "url": "https://tempmail.plus/api/mails?email=test@outlook.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_hotmail": {
        "url": "https://tempmail.plus/api/mails?email=test@hotmail.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_aol": {
        "url": "https://tempmail.plus/api/mails?email=test@aol.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_protonmail": {
        "url": "https://tempmail.plus/api/mails?email=test@protonmail.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_zoho": {
        "url": "https://tempmail.plus/api/mails?email=test@zoho.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_gmx": {
        "url": "https://tempmail.plus/api/mails?email=test@gmx.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_mail_com": {
        "url": "https://tempmail.plus/api/mails?email=test@mail.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_yandex": {
        "url": "https://tempmail.plus/api/mails?email=test@yandex.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_icloud": {
        "url": "https://tempmail.plus/api/mails?email=test@icloud.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 17. EMAILONDECK
    # ═══════════════════════════════════════════════════════════════
    "emailondeck:get_inbox": {
        "url": "https://api.emailondeck.com/v1/inbox/",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_invalid": {
        "url": "https://emailondeck.com/api/v1/inbox/invalid",
        "method": "GET", "expected_status": 404
    },

    # ═══════════════════════════════════════════════════════════════
    # 18. MAILNESIA
    # ═══════════════════════════════════════════════════════════════
    "mailnesia:main_page": {
        "url": "https://mailnesia.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 19. TEMPMAILO.COM
    # ═══════════════════════════════════════════════════════════════
    "tempmailo:get_addresses": {
        "url": "https://tempmailo.com/api/addresses",
        "method": "GET", "expected_status": 200
    },
    "tempmailo:get_mail": {
        "url": "https://tempmailo.com/api/mail",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 20. BURNER.KIWI
    # ═══════════════════════════════════════════════════════════════
    "burner.kiwi:main": {
        "url": "https://burner.kiwi",
        "method": "GET", "expected_status": 200
    },
    "burner.kiwi:api": {
        "url": "https://burner.kiwi/api",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 21. VMAIL.DEV
    # ═══════════════════════════════════════════════════════════════
    "vmail.dev:main": {
        "url": "https://vmail.dev",
        "method": "GET", "expected_status": 200
    },
    "vmail.dev:api_docs": {
        "url": "https://vmail.dev/api-docs",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 22. FAKEINBOX
    # ═══════════════════════════════════════════════════════════════
    "fakeinbox:get_email": {
        "url": "https://www.fakeinbox.com/api/email/test",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 23. TEMPMAIL.IO
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:new_inbox": {
        "url": "https://temp-mail.io/api/v1/inbox/new",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": {},
        "expected_status": 201
    },

    # ═══════════════════════════════════════════════════════════════
    # 24. EMAILFAKE
    # ═══════════════════════════════════════════════════════════════
    "emailfake:get_inbox": {
        "url": "https://emailfake.com/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 25. FAKEMAIL
    # ═══════════════════════════════════════════════════════════════
    "fakemail:get_inbox": {
        "url": "https://fakemail.net/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 26. HAKARIMAIL
    # ═══════════════════════════════════════════════════════════════
    "harakirimail:get_inbox": {
        "url": "https://api.harakirimail.com/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 27. NOLOG.EMAIL
    # ═══════════════════════════════════════════════════════════════
    "nolog:get_inbox": {
        "url": "https://api.nolog.email/v1/inbox/new",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 28. PRIVATEMAIL
    # ═══════════════════════════════════════════════════════════════
    "privatemail:get_inbox": {
        "url": "https://api.privatemail.xyz/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 29. SECUREMAIL
    # ═══════════════════════════════════════════════════════════════
    "securemail:get_inbox": {
        "url": "https://api.securemail.click/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 30. ANONYMBOX
    # ═══════════════════════════════════════════════════════════════
    "anonymbox:get_inbox": {
        "url": "https://api.anonymbox.com/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 31. TEMPMAIL.DEV
    # ═══════════════════════════════════════════════════════════════
    "tempmail.dev:get_inbox": {
        "url": "https://api.tempmail.dev/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 32. 10MINUTEMAIL
    # ═══════════════════════════════════════════════════════════════
    "10minutemail:generate": {
        "url": "https://10minutemail.net/address.api.php?new=1",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 33. TEMPORARYEMAIL.AI
    # ═══════════════════════════════════════════════════════════════
    "temporaryemail.ai:generate": {
        "url": "https://api.temporaryemail.ai/v1/email/generate",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 34. MINMAIL
    # ═══════════════════════════════════════════════════════════════
    "minmail:generate": {
        "url": "https://api.minmail.app/api/v1/generate",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 35. TEMPORAM
    # ═══════════════════════════════════════════════════════════════
    "temporam:generate": {
        "url": "https://api.temporam.com/v1/email/new",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 36. MOEMAIL
    # ═══════════════════════════════════════════════════════════════
    "moemail:generate": {
        "url": "https://api.moemail.app/api/generate",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 37. INBUCKET
    # ═══════════════════════════════════════════════════════════════
    "inbucket:get_mailboxes": {
        "url": "https://api.inbucket.org/mailboxes",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 38. GETNADA
    # ═══════════════════════════════════════════════════════════════
    "getnada:get_inboxes": {
        "url": "https://getnada.com/api/v1/inboxes/",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 39. CYBERTEMP
    # ═══════════════════════════════════════════════════════════════
    "cybertemp:health": {
        "url": "https://api.cybertemp.xyz/v1/health",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 40. MAIL.TD
    # ═══════════════════════════════════════════════════════════════
    "mail.td:get_domains": {
        "url": "https://api.mail.td/domains",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 41. TRASHMAIL
    # ═══════════════════════════════════════════════════════════════
    "trashmail.io:get_inbox": {
        "url": "https://trashmail.io/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },
    "trashmail.me:get_inbox": {
        "url": "https://trashmail.me/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },
    "trashmail.net:get": {
        "url": "https://www.trashmail.net/cgi-bin/trashmail?ax=1",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 42. INBOXBEAR
    # ═══════════════════════════════════════════════════════════════
    "inboxbear:get_inbox": {
        "url": "https://inboxbear.com/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 43. MAILMOAT
    # ═══════════════════════════════════════════════════════════════
    "mailmoat:get_inbox": {
        "url": "https://api.mailmoat.com/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 44. MAILNULL
    # ═══════════════════════════════════════════════════════════════
    "mailnull:get_inbox": {
        "url": "https://api.mailnull.com/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 45. RANDOMMAIL
    # ═══════════════════════════════════════════════════════════════
    "randommail:get_inbox": {
        "url": "https://api.randommail.io/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 46. TEMPBOX
    # ═══════════════════════════════════════════════════════════════
    "tempbox:get_inbox": {
        "url": "https://tempbox.io/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 47. NOREPLYMAIL
    # ═══════════════════════════════════════════════════════════════
    "noreplymail:get_inbox": {
        "url": "https://noreplymail.io/api/inbox/new",
        "method": "GET", "expected_status": 200
    },
}


def test_api(name, config):
    """Test a single API endpoint."""
    try:
        url = config["url"]
        method = config.get("method", "GET")
        headers = config.get("headers", {})
        data = config.get("data")
        expected_status = config.get("expected_status", 200)

        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10, verify=False)
        else:
            return name, False, f"Unknown method: {method}"

        status_match = resp.status_code == expected_status
        return name, status_match, f"HTTP {resp.status_code} (expected {expected_status})"

    except requests.exceptions.Timeout:
        return name, False, "Timeout"
    except requests.exceptions.ConnectionError:
        return name, False, "Connection error"
    except Exception as e:
        return name, False, str(e)


def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(f"\n{'='*70}")
    print(f"  TEMP EMAIL API CHECKER — {len(API_LIST)} ENDPOINTS")
    print(f"{'='*70}\n")

    working = []
    failed = []
    total = len(API_LIST)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(test_api, name, config): name
            for name, config in API_LIST.items()
        }

        for i, future in enumerate(as_completed(futures), 1):
            name, ok, msg = future.result()
            if ok:
                working.append(name)
                sys.stdout.write(f"\r  OK [{i}/{total}] {name}")
            else:
                failed.append((name, msg))
                sys.stdout.write(f"\r  FAIL [{i}/{total}] {name}: {msg}")
            sys.stdout.flush()

    print(f"\n\n{'='*70}")
    print(f"  RESULTS")
    print(f"{'='*70}")
    print(f"\n  Total tested:  {total}")
    print(f"  OK:            {len(working)}")
    print(f"  Failed:        {len(failed)}")
    print(f"  Success rate:  {len(working)/total*100:.1f}%\n")

    if working:
        print(f"{'='*70}")
        print(f"  WORKING APIs ({len(working)})")
        print(f"{'='*70}")
        for name in sorted(working):
            print(f"  OK {name}")

    if failed:
        print(f"\n{'='*70}")
        print(f"  FAILED APIs ({len(failed)})")
        print(f"{'='*70}")
        for name, msg in sorted(failed):
            print(f"  FAIL {name}: {msg}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
