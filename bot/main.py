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
        return {
            "date": str(date.today()),
            "posted_titles": []
        }

    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    if state.get("date") != str(date.today()):
        state = {
            "date": str(date.today()),
            "posted_titles": []
        }

    return state


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():

    print("[INFO] Fetching headlines...")

    candidates = sources.fetch_top_candidates()

    if not candidates:
        print("[ERROR] No headlines found.")
        return

    state = load_state()

    top_group = sources.pick_top_story(
        candidates,
        state["posted_titles"],
    )

    if not top_group:
        print("[INFO] Nothing new today.")
        return

    topic_title = top_group["title"]

    print(f"[INFO] Selected: {topic_title}")

    # -------------------------
    # ARTICLE URL
    # -------------------------
    article_url = top_group["items"][0]["link"]

    # -------------------------
    # DOWNLOAD IMAGE
    # -------------------------
    image_path = None

    try:
        image_url = image_fetcher.get_article_image(article_url)

        if image_url:
            print("[INFO] Downloading image...")
            image_path = image_fetcher.download_image(image_url)

    except Exception as e:
        print(f"[IMAGE] {e}")

    # -------------------------
    # GET ARTICLE CONTENT
    # -------------------------
    print("[INFO] Reading article...")

    media_texts = sources.gather_deep_dive_texts(topic_title)

    print("[INFO] Collecting reactions...")

    politician_reactions = sources.gather_politician_reactions(topic_title)

    print("[INFO] Building AI summary...")

    report = summarizer.build_report(
        topic_title,
        media_texts,
        politician_reactions,
    )

   source = top_group["items"][0]["source"]

full_post = f"""
🚨 <b>BREAKING NEWS</b>

<b>{topic_title}</b>

━━━━━━━━━━━━━━━━━━━━━━

{report}

━━━━━━━━━━━━━━━━━━━━━━

🌐 <b>Source:</b> {source}

📰 <b>SYSTEMIC NEWS</b>

#SystemicNews
"""
    print("[INFO] Posting to Telegram...")

    telegram_poster.post_to_channel(
        full_post,
        image_path
    )

    state["posted_titles"].append(topic_title)

    save_state(state)

    print("[DONE] Successfully posted.")


if __name__ == "__main__":
    main()
