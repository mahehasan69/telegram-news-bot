"""
Entry point. Run this script with cron 4-5 times a day.
Each run:
  1. Looks at top headlines across major RSS feeds
  2. Picks the single biggest story (covered by the most outlets, not
     already posted today)
  3. Deep-dives that story via Google News search across many outlets
  4. Gathers what tracked politicians are saying about it
  5. Asks the local AI model to write the 5-part structured post
  6. Posts it to your Telegram channel
  7. Remembers the topic so it won't repeat it today
"""

import json
import os
from datetime import date

import config
import sources
import summarizer
import telegram_poster


def load_state():
    if not os.path.exists(config.STATE_FILE):
        return {"date": str(date.today()), "posted_titles": []}
    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    # reset daily
    if state.get("date") != str(date.today()):
        state = {"date": str(date.today()), "posted_titles": []}
    return state


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    print("[info] fetching top candidate headlines...")
    candidates = sources.fetch_top_candidates()
    if not candidates:
        print("[error] no candidates fetched, check your internet connection / feed URLs")
        return

    state = load_state()
    top_group = sources.pick_top_story(candidates, state["posted_titles"])
    if not top_group:
        print("[info] nothing new to post right now (everything already posted today).")
        return

    topic_title = top_group["title"]
    print(f"[info] chosen topic: {topic_title} (covered by {len(top_group['items'])} feed entries)")

    print("[info] deep-diving coverage across outlets...")
    media_texts = sources.gather_deep_dive_texts(topic_title)

    print("[info] checking politician reactions...")
    politician_reactions = sources.gather_politician_reactions(topic_title)

    print("[info] generating report with local AI model (first run downloads the model)...")
    report = summarizer.build_report(topic_title, media_texts, politician_reactions)

    header = f"📰 *{topic_title}*\n\n"
    full_post = header + report

    print("[info] posting to Telegram channel...")
    telegram_poster.post_to_channel(full_post)

    state["posted_titles"].append(topic_title)
    save_state(state)
    print("[done] posted successfully.")


if __name__ == "__main__":
    main()
