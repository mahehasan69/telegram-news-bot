import category
import breaking
import fact_extractor
import hashtags
import image_fetcher
import news_card
import sources
import summarizer
import telegram_poster
import website_manager

from db_manager import DatabaseManager


def main():

    print("=" * 60)
    print("SYSTEMIC NEWS v3")
    print("=" * 60)

    # =========================================
    # DATABASE
    # =========================================

    print("[0/8] Connecting database...")

    db = DatabaseManager()

    # =========================================
    # FETCH HEADLINES
    # =========================================

    print("[1/8] Fetching headlines...")

    candidates = sources.fetch_top_candidates()

    print(
        f"[INFO] Candidates found: {len(candidates)}"
    )

    if not candidates:

        print("[ERROR] No headlines found.")

        db.close()
        return

    # =========================================
    # SELECT STORY
    # =========================================

    print("[INFO] Selecting best new story...")

    top_group = sources.pick_top_story(
        candidates,
        db,
    )

    if not top_group:

        print("[INFO] No new stories available.")

        db.close()
        return

    # =========================================
    # SELECT BEST ARTICLE
    # =========================================

    article = max(
        top_group["items"],
        key=lambda item: item.get(
            "score",
            0,
        ),
    )

    topic_title = article.get(
        "title",
        "",
    ).strip()

    article_url = article.get(
        "url",
        "",
    ).strip()

    source = article.get(
        "source",
        "",
    ).strip()

    print()
    print("[SELECTED]")
    print(f"Title : {topic_title}")
    print(f"Source: {source}")
    print(f"URL   : {article_url}")
    print()

    # =========================================
    # IMAGE
    # =========================================

    print("[2/8] Downloading image...")

    image_path = None

    try:

        image_url = image_fetcher.get_article_image(
            article_url
        )

        if image_url:

            image_path = image_fetcher.download_image(
                image_url
            )

            print(
                f"[IMAGE] Downloaded: {image_path}"
            )

        else:

            print("[IMAGE] No image found.")

    except Exception as e:

        print(
            f"[IMAGE ERROR] {e}"
        )

    # =========================================
    # RESEARCH
    # =========================================

    print("[3/8] Researching story...")

    try:

        articles = sources.gather_deep_dive_texts(
            topic_title
        )

    except Exception as e:

        print(
            f"[RESEARCH ERROR] {e}"
        )

        articles = []

    print(
        f"[INFO] {len(articles)} articles collected."
    )

    if not articles:

        print(
            "[ERROR] No research articles collected."
        )

        db.close()
        return

    # =========================================
    # FACTS
    # =========================================

    print("[4/8] Extracting verified facts...")

    try:

        facts = fact_extractor.build_fact_sheet(
            articles
        )

    except Exception as e:

        print(
            f"[FACT ERROR] {e}"
        )

        db.close()
        return

    # =========================================
    # AI ARTICLE
    # =========================================

    print("[5/8] Writing article...")

    try:

        report = summarizer.build_report(
            facts
        )

    except Exception as e:

        print(
            f"[SUMMARY ERROR] {e}"
        )

        db.close()
        return

    if not report:

        print(
            "[ERROR] AI returned empty article."
        )

        db.close()
        return

    # =========================================
    # SUMMARY
    # =========================================

    summary = ""

    for paragraph in report.split("\n"):

        paragraph = paragraph.strip()

        if len(paragraph) > 40:

            summary = paragraph
            break

    if not summary:

        summary = report[:300]

    # =========================================
    # CATEGORY
    # =========================================

    print("[6/8] Detecting category...")

    try:

        news_category = category.detect(
            topic_title,
            report,
        )

    except Exception as e:

        print(
            f"[CATEGORY ERROR] {e}"
        )

        news_category = "World"

    # =========================================
    # BREAKING
    # =========================================

    try:

        status = breaking.detect(
            topic_title,
            report,
        )

    except Exception as e:

        print(
            f"[BREAKING ERROR] {e}"
        )

        status = "📰 NEWS UPDATE"

    # =========================================
    # HASHTAGS
    # =========================================

    try:

        tags = hashtags.generate(
            topic_title,
            news_category,
        )

    except Exception as e:

        print(
            f"[HASHTAG ERROR] {e}"
        )

        tags = "#SystemicNews"

    # =========================================
    # NEWS CARD
    # =========================================

    card = image_path

    if image_path:

        try:

            card = news_card.create_news_card(
                image_path=image_path,
                title=topic_title,
                category=news_category,
                breaking=status,
            )

            print(
                f"[CARD] Created: {card}"
            )

        except Exception as e:

            print(
                f"[CARD ERROR] {e}"
            )

            card = image_path

    # =========================================
    # TELEGRAM
    # =========================================

    full_post = f"""
{status}

🌍 {news_category}

<b>{topic_title}</b>

━━━━━━━━━━━━━━━━━━━━━━

{report}

━━━━━━━━━━━━━━━━━━━━━━

🌐 <b>Source:</b> {source}

📰 <b>SYSTEMIC NEWS</b>

━━━━━━━━━━━━━━━━━━━━━━

{tags}
"""

    print("[7/8] Posting to Telegram...")

    try:

        result = telegram_poster.post_to_channel(
            full_post,
            card,
        )

        print(
            f"[TELEGRAM] Result: {result}"
        )

    except Exception as e:

        print(
            f"[TELEGRAM ERROR] {e}"
        )

        db.close()
        return

    # =========================================
    # WEBSITE
    # =========================================

    print("[WEBSITE] Publishing article...")

    try:

        website_result = website_manager.publish_article(

            title=topic_title,

            summary=summary,

            article=report,

            category=news_category,

            image=card,

            facts=facts.get(
                "verified_facts",
                [],
            ),

            timeline=facts.get(
                "timeline",
                [],
            ),

            sources=list(
                facts.get(
                    "sources",
                    {},
                ).keys()
            ),

            confidence=facts.get(
                "confidence",
                100,
            ),
        )

        print(
            f"[WEBSITE] Result: {website_result}"
        )

    except Exception as e:
        print(
             f"[WEBSITE ERROR] {e}"
             )

    print(
        "[WEBSITE] Failed, but continuing to database..."
         )
    # =========================================
    # DATABASE
    # =========================================

    print("[8/8] Saving database...")

    try:

        db.save_article(

            title=topic_title,

            url=article_url,

            source=source,

            category=news_category,

            confidence=facts.get(
                "confidence",
                100,
            ),
        )

        print(
            "[DB] Article saved."
        )

        db.sync(
            f"News: {topic_title}"
        )

        print(
            "[DB] Database pushed to GitHub."
        )

    except Exception as e:

        print(
            f"[DB ERROR] {e}"
        )

        return

    print()
    print("=" * 60)
    print("✅ NEWS POSTED SUCCESSFULLY")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
