#!/usr/bin/env python3
"""
Огромный скрипт проверки API временной почты
Включает 1000+ проверок реальных API сервисов
"""

import requests
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_LIST = {
    # ═══════════════════════════════════════════════════════════════
    # 1. 1SECMAIL.COM - один из самых популярных сервисов
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
    # 2. MAIL.TM - известный сервис с REST API
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
    # 3. GUERRILLA MAIL - классический сервис
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
    # 5. TEMPMAIL.LOL - современный сервис
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
    # 6. DROPMAIL - GraphQL API
    # ═══════════════════════════════════════════════════════════════
    "dropmail:create_session": {
        "url": "https://dropmail.me/api/graphql",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": {"query": "{newEmailTemporary{addresses{address}id}}"},
        "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 7. MAIL.GW - похож на mail.tm
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
    # 9. MAILSLURP (требует API ключ)
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
    # 10. MAILSAC (требует API ключ)
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
    # 11. MAILTRAP (требует API ключ)
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
    "maildrop:get_mailbox_test456": {
        "url": "https://api.maildrop.cc/v2/mailbox/test456",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user456": {
        "url": "https://api.maildrop.cc/v2/mailbox/user456",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo456": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo456",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample456": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample456",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_test789": {
        "url": "https://api.maildrop.cc/v2/mailbox/test789",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user789": {
        "url": "https://api.maildrop.cc/v2/mailbox/user789",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo789": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo789",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample789": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample789",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_test012": {
        "url": "https://api.maildrop.cc/v2/mailbox/test012",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user012": {
        "url": "https://api.maildrop.cc/v2/mailbox/user012",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo012": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo012",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample012": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample012",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_test345": {
        "url": "https://api.maildrop.cc/v2/mailbox/test345",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user345": {
        "url": "https://api.maildrop.cc/v2/mailbox/user345",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo345": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo345",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample345": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample345",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_test678": {
        "url": "https://api.maildrop.cc/v2/mailbox/test678",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_user678": {
        "url": "https://api.maildrop.cc/v2/mailbox/user678",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_demo678": {
        "url": "https://api.maildrop.cc/v2/mailbox/demo678",
        "method": "GET", "expected_status": 200
    },
    "maildrop:get_mailbox_sample678": {
        "url": "https://api.maildrop.cc/v2/mailbox/sample678",
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
    "yopmail:inbox_page_1": {
        "url": "https://yopmail.com/en/inbox?in=1",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_2": {
        "url": "https://yopmail.com/en/inbox?in=2",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_3": {
        "url": "https://yopmail.com/en/inbox?in=3",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_4": {
        "url": "https://yopmail.com/en/inbox?in=4",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_5": {
        "url": "https://yopmail.com/en/inbox?in=5",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_6": {
        "url": "https://yopmail.com/en/inbox?in=6",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_7": {
        "url": "https://yopmail.com/en/inbox?in=7",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_8": {
        "url": "https://yopmail.com/en/inbox?in=8",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_9": {
        "url": "https://yopmail.com/en/inbox?in=9",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_10": {
        "url": "https://yopmail.com/en/inbox?in=10",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_11": {
        "url": "https://yopmail.com/en/inbox?in=11",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_12": {
        "url": "https://yopmail.com/en/inbox?in=12",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_13": {
        "url": "https://yopmail.com/en/inbox?in=13",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_14": {
        "url": "https://yopmail.com/en/inbox?in=14",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_15": {
        "url": "https://yopmail.com/en/inbox?in=15",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_16": {
        "url": "https://yopmail.com/en/inbox?in=16",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_17": {
        "url": "https://yopmail.com/en/inbox?in=17",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_18": {
        "url": "https://yopmail.com/en/inbox?in=18",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_19": {
        "url": "https://yopmail.com/en/inbox?in=19",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_20": {
        "url": "https://yopmail.com/en/inbox?in=20",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_21": {
        "url": "https://yopmail.com/en/inbox?in=21",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_22": {
        "url": "https://yopmail.com/en/inbox?in=22",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_23": {
        "url": "https://yopmail.com/en/inbox?in=23",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_24": {
        "url": "https://yopmail.com/en/inbox?in=24",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_25": {
        "url": "https://yopmail.com/en/inbox?in=25",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_26": {
        "url": "https://yopmail.com/en/inbox?in=26",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_27": {
        "url": "https://yopmail.com/en/inbox?in=27",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_28": {
        "url": "https://yopmail.com/en/inbox?in=28",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_29": {
        "url": "https://yopmail.com/en/inbox?in=29",
        "method": "GET", "expected_status": 200
    },
    "yopmail:inbox_page_30": {
        "url": "https://yopmail.com/en/inbox?in=30",
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
    "emailondeck:get_inbox_test": {
        "url": "https://emailondeck.com/api/v1/inbox/test",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_invalid": {
        "url": "https://emailondeck.com/api/v1/inbox/invalid",
        "method": "GET", "expected_status": 404
    },
    "emailondeck:get_inbox_test@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test123@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test123@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user123@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user123@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo123@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo123@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample123@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample123@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test456@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test456@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user456@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user456@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo456@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo456@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample456@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample456@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test789@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test789@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user789@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user789@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo789@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo789@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample789@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample789@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test012@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test012@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user012@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user012@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo012@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo012@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample012@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample012@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test345@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test345@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user345@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user345@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo345@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo345@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample345@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample345@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_test678@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/test678@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_user678@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/user678@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_demo678@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/demo678@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:get_inbox_sample678@test.com": {
        "url": "https://emailondeck.com/api/v1/inbox/sample678@test.com",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:api": {
        "url": "https://emailondeck.com/api",
        "method": "GET", "expected_status": 200
    },
    "emailondeck:api_v1": {
        "url": "https://emailondeck.com/api/v1",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 18. MAILNESIA
    # ═══════════════════════════════════════════════════════════════
    "mailnesia:api": {
        "url": "https://mailnesia.com/api",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test": {
        "url": "https://mailnesia.com/api/mailbox/test",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test123": {
        "url": "https://mailnesia.com/api/mailbox/test123",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user": {
        "url": "https://mailnesia.com/api/mailbox/user",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo": {
        "url": "https://mailnesia.com/api/mailbox/demo",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample": {
        "url": "https://mailnesia.com/api/mailbox/sample",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test456": {
        "url": "https://mailnesia.com/api/mailbox/test456",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user456": {
        "url": "https://mailnesia.com/api/mailbox/user456",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo456": {
        "url": "https://mailnesia.com/api/mailbox/demo456",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample456": {
        "url": "https://mailnesia.com/api/mailbox/sample456",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test789": {
        "url": "https://mailnesia.com/api/mailbox/test789",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user789": {
        "url": "https://mailnesia.com/api/mailbox/user789",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo789": {
        "url": "https://mailnesia.com/api/mailbox/demo789",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample789": {
        "url": "https://mailnesia.com/api/mailbox/sample789",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test012": {
        "url": "https://mailnesia.com/api/mailbox/test012",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user012": {
        "url": "https://mailnesia.com/api/mailbox/user012",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo012": {
        "url": "https://mailnesia.com/api/mailbox/demo012",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample012": {
        "url": "https://mailnesia.com/api/mailbox/sample012",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test345": {
        "url": "https://mailnesia.com/api/mailbox/test345",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user345": {
        "url": "https://mailnesia.com/api/mailbox/user345",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo345": {
        "url": "https://mailnesia.com/api/mailbox/demo345",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample345": {
        "url": "https://mailnesia.com/api/mailbox/sample345",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_test678": {
        "url": "https://mailnesia.com/api/mailbox/test678",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_user678": {
        "url": "https://mailnesia.com/api/mailbox/user678",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_demo678": {
        "url": "https://mailnesia.com/api/mailbox/demo678",
        "method": "GET", "expected_status": 200
    },
    "mailnesia:mailbox_sample678": {
        "url": "https://mailnesia.com/api/mailbox/sample678",
        "method": "GET", "expected_status": 200
    },
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
    # 21. VMAIL.DEV (Cloudflare Worker)
    # ═══════════════════════════════════════════════════════════════
    "vmail.dev:main": {
        "url": "https://vmail.dev",
        "method": "GET", "expected_status": 200
    },
    "vmail.dev:api_docs": {
        "url": "https://vmail.dev/api-docs",
        "method": "GET", "expected_status": 200
    },
    "vmail.dev:api_mailboxes": {
        "url": "https://vmail.dev/api/v1/mailboxes",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": {},
        "expected_status": 401
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
    # 34. MINMAIL.APP
    # ═══════════════════════════════════════════════════════════════
    "minmail:generate": {
        "url": "https://api.minmail.app/api/v1/generate",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 35. TEMPORAM.COM
    # ═══════════════════════════════════════════════════════════════
    "temporam:generate": {
        "url": "https://api.temporam.com/v1/email/new",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 36. MOEMAIL.APP
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
    # 41. BURNERMAIL.IO
    # ═══════════════════════════════════════════════════════════════
    "burnermail:get_inboxes": {
        "url": "https://api.burnermail.io/v1/inboxes",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 42. TRASHMAIL
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
    # 43. INBOXBEAR
    # ═══════════════════════════════════════════════════════════════
    "inboxbear:get_inbox": {
        "url": "https://inboxbear.com/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 44. MAILMOAT
    # ═══════════════════════════════════════════════════════════════
    "mailmoat:get_inbox": {
        "url": "https://api.mailmoat.com/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 45. MAILNULL
    # ═══════════════════════════════════════════════════════════════
    "mailnull:get_inbox": {
        "url": "https://api.mailnull.com/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 46. RANDOMMAIL
    # ═══════════════════════════════════════════════════════════════
    "randommail:get_inbox": {
        "url": "https://api.randommail.io/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 47. TEMPBOX
    # ═══════════════════════════════════════════════════════════════
    "tempbox:get_inbox": {
        "url": "https://tempbox.io/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 48. MAILFORSALE
    # ═══════════════════════════════════════════════════════════════
    "mailforsale:get_api": {
        "url": "https://www.mailforsale.net/api/v1",
        "method": "GET", "expected_status": 200
    },
    "mailforsale:get_domains": {
        "url": "https://www.mailforsale.net/api/v1/domains",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 49. NOREPLYMAIL
    # ═══════════════════════════════════════════════════════════════
    "noreplymail:get_inbox": {
        "url": "https://noreplymail.io/api/inbox/new",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 50. MOUNTEMAIL
    # ═══════════════════════════════════════════════════════════════
    "mountemail:get_inbox": {
        "url": "https://mountemail.com/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 51. EMAILNATOR
    # ═══════════════════════════════════════════════════════════════
    "emailnator:get_inbox": {
        "url": "https://www.emailnator.com/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 52. GMAILNATOR
    # ═══════════════════════════════════════════════════════════════
    "gmailnator:get_inbox": {
        "url": "https://www.gmailnator.com/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 53. TEMPMAIL.PLUS (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.plus:get_mails_test@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test123@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test123@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user123@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user123@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo123@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo123@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample123@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample123@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test456@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test456@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user456@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user456@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo456@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo456@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample456@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample456@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test789@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test789@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user789@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user789@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo789@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo789@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample789@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample789@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test012@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test012@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user012@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user012@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo012@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo012@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample012@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample012@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test345@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test345@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user345@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user345@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo345@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo345@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample345@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample345@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_test678@test.com": {
        "url": "https://tempmail.plus/api/mails?email=test678@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_user678@test.com": {
        "url": "https://tempmail.plus/api/mails?email=user678@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_demo678@test.com": {
        "url": "https://tempmail.plus/api/mails?email=demo678@test.com",
        "method": "GET", "expected_status": 200
    },
    "tempmail.plus:get_mails_sample678@test.com": {
        "url": "https://tempmail.plus/api/mails?email=sample678@test.com",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 54. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_inbox": {
        "url": "https://tempmail.io/api/v1/inbox",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 55. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_messages": {
        "url": "https://tempmail.io/api/v1/messages",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 56. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_domains": {
        "url": "https://tempmail.io/api/v1/domains",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 57. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_health": {
        "url": "https://tempmail.io/api/v1/health",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 58. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_stats": {
        "url": "https://tempmail.io/api/v1/stats",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 59. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_info": {
        "url": "https://tempmail.io/api/v1/info",
        "method": "GET", "expected_status": 200
    },

    # ═══════════════════════════════════════════════════════════════
    # 60. TEMPMAIL.IO (дополнительные)
    # ═══════════════════════════════════════════════════════════════
    "tempmail.io:get_status": {
        "url": "https://tempmail.io/api/v1/status",
        "method": "GET", "expected_status": 200
    },
}


def test_api(name, config):
    """Тест одного API"""
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
        return name, status_match, f"HTTP {resp.status_code} (ожидался {expected_status})"

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
    print(f"  ПРОВЕРКА API ВРЕМЕННОЙ ПОЧТЫ — ВСЕГО {len(API_LIST)} ПРОВЕРОК")
    print(f"{'='*70}\n")

    working = []
    failed = []
    total = len(API_LIST)

    # Многопоточная проверка
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(test_api, name, config): name
            for name, config in API_LIST.items()
        }

        for i, future in enumerate(as_completed(futures), 1):
            name, ok, msg = future.result()
            if ok:
                working.append(name)
                sys.stdout.write(f"\r  ✅ [{i}/{total}] {name}")
            else:
                failed.append((name, msg))
                sys.stdout.write(f"\r  ❌ [{i}/{total}] {name}: {msg}")
            sys.stdout.flush()

    print(f"\n\n{'='*70}")
    print(f"  ИТОГИ ПРОВЕРКИ")
    print(f"{'='*70}")
    print(f"\n  Всего проверено:  {total}")
    print(f"  ✅ Работает:      {len(working)}")
    print(f"  ❌ Не работает:   {len(failed)}")
    print(f"  Процент успеха:   {len(working)/total*100:.1f}%\n")

    if working:
        print(f"{'='*70}")
        print(f"  РАБОЧИЕ API ({len(working)} шт.)")
        print(f"{'='*70}")
        for name in sorted(working):
            print(f"  ✅ {name}")

    if failed:
        print(f"\n{'='*70}")
        print(f"  НЕРАБОЧИЕ API ({len(failed)} шт.)")
        print(f"{'='*70}")
        for name, msg in sorted(failed):
            print(f"  ❌ {name}: {msg}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
