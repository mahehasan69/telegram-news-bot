import json
import os
from datetime import date

import config
import sources
import summarizer
import telegram_poster
import image_fetcher


def load_state():
    if not os.path.exists(config.STATE_FILE):
        return {"date": str(date.today()), "posted_titles": []}

    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    if state.get("date") != str(date.today()):
        state = {"date": str(date.today()), "posted_titles": []}

    return state


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    print("[INFO] Fetching headlines...")

    candidates = sources.fetch_top_candidates()

    if not candidates:
        print("[ERROR] No news found.")
        return

    state = load_state()

    top_group = sources.pick_top_story(
        candidates,
        state["posted_titles"],
    )

    if not top_group:
        print("[INFO] Nothing new.")
        return

    topic_title = top_group["title"]

    print(f"[INFO] Selected: {topic_title}")

    # -----------------------------
    # ARTICLE URL
    # -----------------------------
    article_url = top_group["items"][0]["link"]

    # -----------------------------
    # IMAGE
    # -----------------------------
    image_url = image_fetcher.get_article_image(article_url)

    image_path = None

    if image_url:
        print("[INFO] Downloading image...")
        image_path = image_fetcher.download_image(image_url)

    # -----------------------------
    # ARTICLE
    # -----------------------------
    media_texts = sources.gather_deep_dive_texts(topic_title)

    politician_reactions = sources.gather_politician_reactions(topic_title)

    report = summarizer.build_report(
        topic_title,
        media_texts,
        politician_reactions,
    )

    post = f"📰 <b>{topic_title}</b>\n\n{report}"

    # -----------------------------
    # TELEGRAM
    # -----------------------------
    telegram_poster.post_to_channel(
        post,
        image_path,
    )

    state["posted_titles"].append(topic_title)

    save_state(state)

    print("[DONE]")


if __name__ == "__main__":
    main()
