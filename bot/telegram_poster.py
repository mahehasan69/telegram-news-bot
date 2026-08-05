import requests
import config


def post_to_channel(text, image_path=None):

    if image_path:

        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"

        with open(image_path, "rb") as photo:

            r = requests.post(
                url,
                data={
                    "chat_id": config.TELEGRAM_CHANNEL_ID,
                    "caption": text,
                    "parse_mode": "HTML",
                },
                files={
                    "photo": photo
                },
                timeout=60,
            )

    else:

        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

        r = requests.post(
            url,
            data={
                "chat_id": config.TELEGRAM_CHANNEL_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=60,
        )

    if r.status_code != 200:
        raise RuntimeError(r.text)
