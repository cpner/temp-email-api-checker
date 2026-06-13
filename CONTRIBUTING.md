# Contributing to Temp Email Telegram Bots

Thank you for your interest in contributing! Here's how you can help.

## How to Contribute

### 1. Report Bugs

Open an issue using the [Bug Report](https://github.com/cpner/temp-email-api-checker/issues/new?template=bug_report.md) template.

Include:
- Bot name and framework
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Error message (if any)

### 2. Suggest Features

Open an issue using the [Feature Request](https://github.com/cpner/temp-email-api-checker/issues/new?template=feature_request.md) template.

### 3. Add New API Services

1. Fork the repository
2. Add the service to `temp_email_api_checker.py`
3. Run the checker to verify it works
4. Create bot files in all 6 directories:
   - `russian/telebot/bot_<service>.py`
   - `russian/aiogram-2/bot_<service>.py`
   - `russian/aiogram-3/bot_<service>.py`
   - `english/telebot/bot_<service>.py`
   - `english/aiogram-2/bot_<service>.py`
   - `english/aiogram-3/bot_<service>.py`
5. Update `README.md`
6. Submit a pull request

### 4. Fix Bugs

1. Fork the repository
2. Create a feature branch: `git checkout -b fix-bug-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions short and focused
- Add docstrings for public functions
- Use meaningful variable names

## Testing

Before submitting a PR:
1. Run `python3 temp_email_api_checker.py` to verify APIs
2. Test your bot with `python3 bot_<service>.py`
3. Check for syntax errors: `python3 -m py_compile bot_<service>.py`

## Pull Request Process

1. Update documentation if needed
2. Add yourself to Contributors section
3. Ensure all checks pass
4. Request a review

## Code of Conduct

Be respectful and inclusive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Contact

- **Author:** Владислав Софронов (cpner)
- **Telegram:** [t.me/reejb](https://t.me/reejb)
- **Email:** feedback@gondon.su
- **Website:** [gondon.su](https://gondon.su)

## Questions?

Open an issue with the "question" label or contact via Telegram.
