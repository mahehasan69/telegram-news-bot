"""
Fetches candidate stories from major RSS feeds, deep-dives a chosen topic
via Google News RSS search, and extracts readable article text.
"""

import time
import urllib.parse
import feedparser
import trafilatura

import config


def fetch_top_candidates():
    """Pull the top few entries from each configured RSS feed.

    Returns a list of dicts: {title, link, summary, source, published}
    """
    candidates = []
    for source_name, url in config.RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"[warn] could not read feed {source_name}: {e}")
            continue

        for entry in feed.entries[: config.TOP_CANDIDATES_PER_FEED]:
            candidates.append(
                {
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "summary": entry.get("summary", "").strip(),
                    "source": source_name,
                    "published": entry.get("published", ""),
                }
            )
    return candidates


def _keyword_overlap_score(title_a, title_b):
    """Very simple similarity: fraction of shared significant words."""
    stop = {
        "the", "a", "an", "to", "of", "in", "on", "for", "and", "is",
        "at", "as", "by", "with", "after", "over", "amid", "says",
    }
    words_a = {w.lower().strip(".,:;'\"") for w in title_a.split() if w.lower() not in stop and len(w) > 2}
    words_b = {w.lower().strip(".,:;'\"") for w in title_b.split() if w.lower() not in stop and len(w) > 2}
    if not words_a or not words_b:
        return 0.0
    overlap = words_a.intersection(words_b)
    return len(overlap) / min(len(words_a), len(words_b))


def pick_top_story(candidates, already_posted_titles):
    """Group similar headlines together (same real-world story appearing on
    multiple outlets counts as more important), skip anything already
    posted today, and return the story covered by the most outlets.
    """
    groups = []  # each group: {"title": str, "items": [candidate,...]}

    for c in candidates:
        if any(_keyword_overlap_score(c["title"], t) > 0.6 for t in already_posted_titles):
            continue  # skip stories already posted today

        placed = False
        for g in groups:
            if _keyword_overlap_score(c["title"], g["title"]) > 0.45:
                g["items"].append(c)
                placed = True
                break
        if not placed:
            groups.append({"title": c["title"], "items": [c]})

    if not groups:
        return None

    groups.sort(key=lambda g: len(g["items"]), reverse=True)
    top_group = groups[0]
    return top_group


def search_google_news(query, limit=8):
    """Search Google News RSS for a query and return candidate articles."""
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[warn] google news search failed for '{query}': {e}")
        return []

    results = []
    for entry in feed.entries[:limit]:
        results.append(
            {
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "source": entry.get("source", {}).get("title", "Google News") if hasattr(entry, "get") else "Google News",
            }
        )
    return results


def extract_full_text(url, timeout=15):
    """Try to pull full readable article text from a URL. Falls back to
    empty string if extraction fails (bot will use the RSS summary instead).
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded) or ""
        return text.strip()
    except Exception:
        return ""


def gather_deep_dive_texts(topic_title, limit=None):
    """Search Google News widely around the topic and collect readable
    text (or RSS summary fallback) from multiple outlets.
    """
    limit = limit or config.DEEP_DIVE_ARTICLE_LIMIT
    articles = search_google_news(topic_title, limit=limit)

    texts = []
    for art in articles:
        body = extract_full_text(art["link"])
        if not body:
            body = art["summary"]
        if body:
            texts.append({"source": art["source"], "title": art["title"], "text": body[:2000]})
        time.sleep(0.3)  # be polite to servers
    return texts


def gather_politician_reactions(topic_title):
    """For each tracked politician, search for their reaction to the topic."""
    reactions = []
    for name in config.POLITICIANS:
        query = f"{name} {topic_title}"
        results = search_google_news(query, limit=config.POLITICIAN_REACTION_LIMIT)
        for r in results:
            body = r["summary"] or extract_full_text(r["link"])
            if body:
                reactions.append({"person": name, "title": r["title"], "text": body[:800]})
        time.sleep(0.3)
    return reactions
