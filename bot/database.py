import json
import os
from datetime import datetime

DB_FILE = "posted_news.json"


def load_database():
    """Load posted news database."""
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_database(data):
    """Save posted news database."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4,
        )


def normalize(text):
    """Normalize titles for comparison."""
    return (
        text.lower()
        .replace('"', "")
        .replace("'", "")
        .replace(",", "")
        .replace(".", "")
        .replace(":", "")
        .replace("-", " ")
        .strip()
    )


def already_posted(title, url):
    """
    Check if this article has already been posted.
    """

    data = load_database()

    title = normalize(title)

    for item in data:

        if normalize(item["title"]) == title:
            return True

        if item["url"] == url:
            return True

    return False


def save_post(title, url, source):

    data = load_database()

    data.append(
        {
            "title": title,
            "url": url,
            "source": source,
            "posted": datetime.utcnow().isoformat(),
        }
    )

    # Keep only latest 1000 posts
    data = data[-1000:]

    save_database(data)


def get_posted_titles():

    return [
        normalize(item["title"])
        for item in load_database()
    ]


def total_posts():

    return len(load_database())


def latest_post():

    data = load_database()

    if not data:
        return None

    return data[-1]


def database_statistics():

    print("\n========== DATABASE ==========")

    print(
        "Total Posts:",
        total_posts(),
    )

    latest = latest_post()

    if latest:

        print(
            "Latest:",
            latest["title"],
        )

    print("==============================\n")

