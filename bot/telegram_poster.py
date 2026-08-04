"""
Posts news with image + caption to Telegram.
"""

import requests
import config


def post_to_channel(text, image_path=None):

    # -------- Image Post --------
    if image_path:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"

        with open(image_path, "rb") as photo:
            resp = requests.post(
                url,
                data={
                    "chat_id": config.TELEGRAM_CHANNEL_ID,
                    "caption": text[:1024],  # Telegram caption limit
                    "parse_mode": "HTML",
                },
                files={
                    "photo": photo,
                },
                timeout=60,
            )

        if resp.status_code != 200:
            raise RuntimeError(resp.text)

        return True

    # -------- Text Only --------
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or [text]

    for chunk in chunks:
        resp = requests.post(
            url,
            data={
                "chat_id": config.TELEGRAM_CHANNEL_ID,
                "text": chunk,
                "disable_web_page_preview": False,
                "parse_mode": "HTML",
            },
            timeout=60,
        )

        if resp.status_code != 200:
            raise RuntimeError(resp.text)

    return True
