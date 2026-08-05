import category
import breaking
import database
import hashtags
import image_fetcher
import news_card
import sources
import summarizer
import telegram_poster


def main():

    print("[INFO] Fetching headlines...")

    candidates = sources.fetch_top_candidates()

    if not candidates:
        print("[ERROR] No headlines found.")
        return

    top_group = None

    for group in sources.group_candidates(candidates):

        article = group["items"][0]

        if database.already_posted(
            article["title"],
            article["link"],
        ):
            continue

        top_group = group
        break

    if top_group is None:
        print("[INFO] Nothing new.")
        return

    topic_title = top_group["title"]

    article_url = top_group["items"][0]["link"]

    source = top_group["items"][0]["source"]

    print(f"[INFO] Selected: {topic_title}")

    image_path = None

    try:

        image_url = image_fetcher.get_article_image(
            article_url
        )

        if image_url:

            print("[INFO] Downloading image...")

            image_path = image_fetcher.download_image(
                image_url
            )

    except Exception as e:

        print("[IMAGE]", e)

    print("[INFO] Reading articles...")

    media_texts = sources.gather_deep_dive_texts(
        topic_title
    )

    politician_reactions = (
        sources.gather_politician_reactions(
            topic_title
        )
    )

    print("[INFO] Building AI report...")

    report = summarizer.build_report(
        topic_title,
        media_texts,
        politician_reactions,
    )

    news_category = category.detect(
        topic_title,
        report,
    )

    status = breaking.detect(
        topic_title,
        report,
    )

    tags = hashtags.generate(
        topic_title,
        news_category,
    )

    card = image_path
    # ----------------------------
    # Create News Card
    # ----------------------------

    if image_path:

        try:

            card = news_card.create_news_card(
                image_path=image_path,
                title=topic_title,
                category=news_category,
                breaking=status,
            )

        except Exception as e:

            print("[CARD]", e)

            card = image_path

    # ----------------------------
    # Build Telegram Post
    # ----------------------------

    full_post = f"""
{status}

{news_category}

<b>{topic_title}</b>

━━━━━━━━━━━━━━━━━━━━━━

{report}

━━━━━━━━━━━━━━━━━━━━━━

🌐 <b>Source:</b> {source}

📰 <b>SYSTEMIC NEWS</b>

━━━━━━━━━━━━━━━━━━━━━━

{tags}
"""

    print("[INFO] Posting to Telegram...")

    telegram_poster.post_to_channel(
        full_post,
        card,
    )

    print("[INFO] Saving to database...")

    database.save_post(
        topic_title,
        article_url,
        source,
    )

    print("[DONE] News posted successfully.")


if __name__ == "__main__":
    main()
