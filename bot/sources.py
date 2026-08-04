import time
import urllib.parse

import feedparser
import trafilatura

import config


def fetch_top_candidates():
    candidates = []

    for source, url in config.RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue

        for entry in feed.entries[: config.TOP_CANDIDATES_PER_FEED]:

            candidates.append(
                {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "source": source,
                }
            )

    return candidates


def similarity(a, b):

    stop = {
        "the",
        "a",
        "an",
        "to",
        "of",
        "and",
        "for",
        "in",
        "on",
        "with",
        "at",
        "is",
        "are",
    }

    sa = {
        x.lower()
        for x in a.split()
        if len(x) > 2 and x.lower() not in stop
    }

    sb = {
        x.lower()
        for x in b.split()
        if len(x) > 2 and x.lower() not in stop
    }

    if not sa or not sb:
        return 0

    return len(sa & sb) / min(len(sa), len(sb))


def pick_top_story(candidates, already_posted):

    groups = []

    for item in candidates:

        if any(similarity(item["title"], old) > 0.6 for old in already_posted):
            continue

        matched = False

        for g in groups:

            if similarity(item["title"], g["title"]) > 0.45:
                g["items"].append(item)
                matched = True
                break

        if not matched:
            groups.append(
                {
                    "title": item["title"],
                    "items": [item],
                }
            )

    if not groups:
        return None

    groups.sort(key=lambda x: len(x["items"]), reverse=True)

    return groups[0]


def google_news(query):

    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(url)

    result = []

    for item in feed.entries[: config.DEEP_DIVE_ARTICLE_LIMIT]:

        result.append(
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "link": item.get("link", ""),
            }
        )

    return result


def extract_text(url):

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        text = trafilatura.extract(downloaded)

        return text or ""

    except Exception:
        return ""


def gather_deep_dive_texts(title):

    news = google_news(title)

    articles = []

    for article in news:

        body = extract_text(article["link"])

        if not body:
            body = article["summary"]

        articles.append(
            {
                "title": article["title"],
                "text": body[:2000],
            }
        )

        time.sleep(0.2)

    return articles


def gather_politician_reactions(title):

    reactions = []

    for person in config.POLITICIANS:

        query = person + " " + title

        news = google_news(query)[: config.POLITICIAN_REACTION_LIMIT]

        for article in news:

            reactions.append(
                {
                    "person": person,
                    "title": article["title"],
                    "text": article["summary"][:600],
                }
            )

        time.sleep(0.2)

    return reactions
