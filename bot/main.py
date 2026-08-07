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
    print("SYSTEMIC NEWS v2")
    print("=" * 60)

    print("[1/8] Fetching headlines...")
    db = DatabaseManager()
    candidates = sources.fetch_top_candidates()

    if not candidates:
        print("[ERROR] No headlines found.")
        db.close()
        return

    top_group = None

    for group in candidates:
        try:
            article = group["items"][0]
        except Exception:
            # skip groups with no items
            continue

        if not db.is_duplicate(
            article.get("title", ""),
            article.get("url", ""),
        ):
            top_group = group
            break

    if top_group is None:
        print("[INFO] No new articles found.")
        db.close()
        return

    article = top_group["items"][0]

    topic_title = article.get("title", "")
    article_url = article.get("url", "")
    source = article.get("source", "")

    print()
    print("[SELECTED]")
    print(topic_title)
    print()

    print("[2/8] Downloading image...")

    image_path = None

    try:
        image_url = image_fetcher.get_article_image(article_url)

        if image_url:
            image_path = image_fetcher.download_image(image_url)

    except Exception as e:
        print("[IMAGE]", e)

    print("[3/8] Researching story...")

    articles = sources.gather_deep_dive_texts(topic_title)

    print(f"[INFO] {len(articles)} articles collected.")

    print("[4/8] Extracting verified facts...")

    facts = fact_extractor.build_fact_sheet(articles)

    print("[5/8] Writing article...")

    report = summarizer.build_report(facts)
    summary = ""

    paragraphs = report.split("\n")

    for p in paragraphs:
        p = p.strip()
        if len(p) > 40:
            summary = p
            break

    print("[6/8] Detecting category...")

    news_category = category.detect(topic_title, report)

    status = breaking.detect(topic_title, report)

    tags = hashtags.generate(topic_title, news_category)

    card = image_path

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

    print("[7/8] Posting to Telegram...")

    telegram_poster.post_to_channel(full_post, card)

    website_manager.publish_article(
        title=topic_title,
        summary=summary,
        article=report,
        category=news_category,
        image=card,
        facts=facts.get("verified_facts", []),
        timeline=facts.get("timeline", []),
        sources=list(facts.get("sources", {}).keys()),
        confidence=facts.get("confidence", 100),
    )

    print("[8/8] Saving database...")

    db.save_article(
        title=topic_title,
        url=article_url,
        source=source,
        category=news_category,
        confidence=facts.get("confidence", 100),
    )

    db.sync(f"News: {topic_title}")
    db.close()

    print()
    print("✅ News posted successfully.")


if __name__ == "__main__":
    main()
