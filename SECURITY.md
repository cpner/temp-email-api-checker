# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly.

**Do NOT open a public issue.**

Instead, contact via:
- **Email:** feedback@gondon.su
- **Telegram:** [t.me/reejb](https://t.me/reejb)
- **Telegram Bot:** [t.me/marco_feedback_bot](https://t.me/marco_feedback_bot)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix released:** Within 2 weeks (for critical issues)

## Scope

This policy covers:
- The bot code in this repository
- API key handling
- User data privacy

## Best Practices for Users

1. **Never commit API tokens** to the repository
2. **Use environment variables** for sensitive data
3. **Rotate tokens** regularly
4. **Use minimal permissions** for bot tokens
5. **Enable 2FA** on your GitHub account

## API Security Notes

- **Guerrilla Mail:** No authentication required
- **MailSac/MailSlurp:** Require API keys — never hardcode them
- **Mail.tm:** Creates accounts with passwords — store securely
- **Bot tokens:** Keep your Telegram bot tokens secret

## Dependencies

This project uses:
- `pyTelegramBotAPI` — reviewed, maintained
- `aiogram` — reviewed, maintained
- `requests` — reviewed, maintained

Run `pip audit` regularly to check for vulnerabilities.

## Author

**Владислав Софронов (cpner)**
- Website: [gondon.su](https://gondon.su)
- Telegram: [t.me/reejb](https://t.me/reejb)
