"""
Sends the generated report to a Telegram channel via the Bot API.
"""

import requests

import config


def post_to_channel(text):
    if not config.TELEGRAM_BOT_TOKEN or "PUT_YOUR" in config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Edit config.py or set the env var.")

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram messages are capped at 4096 characters; split if needed.
    chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)] or [text]

    for chunk in chunks:
        resp = requests.post(
            url,
            data={
                "chat_id": config.TELEGRAM_CHANNEL_ID,
                "text": chunk,
                "disable_web_page_preview": False,
            },
            timeout=20,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Telegram API error {resp.status_code}: {resp.text}")
    return True
