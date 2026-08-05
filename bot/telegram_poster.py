import requests
import config


API = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"


def send_message(text):

    url = f"{API}/sendMessage"

    return requests.post(
        url,
        data={
            "chat_id": config.TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=60,
    )


def send_photo(photo_path, caption):

    url = f"{API}/sendPhoto"

    with open(photo_path, "rb") as photo:

        return requests.post(
            url,
            data={
                "chat_id": config.TELEGRAM_CHANNEL_ID,
                "caption": caption[:1024],
                "parse_mode": "HTML",
            },
            files={
                "photo": photo
            },
            timeout=120,
        )


def post_to_channel(text, image_path=None):

    if image_path:

        r = send_photo(image_path, text)

        if r.status_code == 200:
            return True

        print("[PHOTO ERROR]", r.text)

    for i in range(0, len(text), 4000):

        part = text[i:i + 4000]

        r = send_message(part)

        if r.status_code != 200:
            raise RuntimeError(r.text)

    return True
