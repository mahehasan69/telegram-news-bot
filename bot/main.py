import json
import os
from datetime import date
import category
import config
import sources
import summarizer
import telegram_poster
import image_fetcher
import hashtags
import breaking
import database
import news_card




def top_group = None

for group in sources.group_candidates(candidates):

    article = group["items"][0]

    if database.already_posted(
        article["title"],
        article["link"],
    ):
        continue

    top_group = group
    break

if not top_group:
    print("Nothing new.")
    return

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
card = None

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

status = breaking.detect(
    topic_title,
    report,
)
if image_path:

    card = news_card.create_news_card(
        image_path=image_path,
        title=topic_title,
        category=news_category,
        breaking=status,
    )
else:
    card = None
news_category = category.detect(
    topic_title,
    report,
)

tags = hashtags.generate(
    topic_title,
    news_category,
)

source = top_group["items"][0]["source"]
full_post = f"""
{status}

{news_category}

<b>{topic_title}</b>

━━━━━━━━━━━━━━━━━━

{report}

━━━━━━━━━━━━━━━━━━

🌐 <b>Source:</b> {source}

📰 <b>SYSTEMIC NEWS</b>

━━━━━━━━━━━━━━━━━━

{tags}
"""
    print("[INFO] Posting to Telegram...")

  telegram_poster.post_to_channel(
    full_post,
    card,
)

   database.save_post(
    topic_title,
    article_url,
    source,
)
    print("[DONE] Successfully posted.")


if __name__ == "__main__":
    main()
