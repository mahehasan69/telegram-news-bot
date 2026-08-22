import re
import time
import urllib.parse
from collections import defaultdict
from urllib.parse import urlparse

import feedparser
import requests
import trafilatura

import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36"
    )
}

SOURCE_SCORE = {

    # Wire Services
    "reuters.com": 100,
    "apnews.com": 100,
    "afp.com": 99,
    "dpa.com": 98,
    "efe.com": 97,

    # International
    "bbc.com": 99,
    "bbc.co.uk": 99,
    "nytimes.com": 98,
    "wsj.com": 98,
    "bloomberg.com": 98,
    "economist.com": 98,
    "ft.com": 98,
    "theguardian.com": 97,
    "washingtonpost.com": 97,
    "cnn.com": 96,
    "abcnews.go.com": 96,
    "cbsnews.com": 96,
    "nbcnews.com": 96,
    "usatoday.com": 95,
    "news.sky.com": 95,
    "aljazeera.com": 95,
    "euronews.com": 94,
    "dw.com": 94,
    "france24.com": 94,

    # Business
    "cnbc.com": 96,
    "marketwatch.com": 94,
    "investing.com": 92,
    "businessinsider.com": 92,
    "fortune.com": 94,
    "forbes.com": 93,
    "morningstar.com": 93,
    "thestreet.com": 90,

    # Technology
    "techcrunch.com": 94,
    "theverge.com": 94,
    "arstechnica.com": 95,
    "wired.com": 94,
    "engadget.com": 91,
    "zdnet.com": 92,
    "tomshardware.com": 91,
    "9to5mac.com": 90,
    "androidauthority.com": 89,
    "gsmarena.com": 89,
    "macrumors.com": 90,

    # Science
    "nature.com": 100,
    "science.org": 100,
    "newscientist.com": 96,
    "sciencedaily.com": 93,
    "livescience.com": 92,
    "space.com": 92,
    "nasa.gov": 100,
    "esa.int": 99,

    # Health
    "who.int": 100,
    "cdc.gov": 100,
    "nih.gov": 100,
    "mayoclinic.org": 98,
    "webmd.com": 90,

    # Cybersecurity
    "bleepingcomputer.com": 95,
    "theregister.com": 93,
    "securityweek.com": 95,
    "darkreading.com": 95,
    "thehackernews.com": 92,
    "krebsonsecurity.com": 99,

    # Crypto
    "coindesk.com": 92,
    "cointelegraph.com": 89,
    "decrypt.co": 88,

    # Sports
    "espn.com": 95,
    "skysports.com": 94,
    "theathletic.com": 95,

    # Entertainment
    "hollywoodreporter.com": 94,
    "variety.com": 94,
    "deadline.com": 94,

    # Regional (examples)
    "straitstimes.com": 93,
    "japantimes.co.jp": 93,
    "hindustantimes.com": 90,
    "thehindu.com": 94,
    "timesofindia.indiatimes.com": 89,
    "dawn.com": 92,
    "arabnews.com": 90,
    "haaretz.com": 94,

    # Misc / Dev / Cloud / etc.
    "yahoo.com": 85,
    "msn.com": 84,
    "lemonde.fr": 94,
    "lefigaro.fr": 91,
    "elpais.com": 91,
    "corriere.it": 90,
    "ansa.it": 92,
    "tagesschau.de": 95,
    "spiegel.de": 95,
    "faz.net": 92,
    "zeit.de": 92,
    "svt.se": 90,
    "nrk.no": 90,
    "yle.fi": 89,
    "rte.ie": 89,
    "swissinfo.ch": 92,

    "cbc.ca": 95,
    "ctvnews.ca": 91,
    "globalnews.ca": 90,
    "nationalpost.com": 89,

    "abc.net.au": 95,
    "smh.com.au": 91,
    "theage.com.au": 91,
    "news.com.au": 88,
    "nzherald.co.nz": 89,

    "channelnewsasia.com": 93,
    "scmp.com": 94,
    "japantoday.com": 90,
    "nikkei.com": 97,
    "koreatimes.co.kr": 89,
    "koreaherald.com": 89,
    "chinadaily.com.cn": 84,
    "globaltimes.cn": 82,

    "indianexpress.com": 94,
    "livemint.com": 93,
    "moneycontrol.com": 90,
    "ndtv.com": 90,
    "firstpost.com": 87,
    "news18.com": 87,

    "tribune.com.pk": 89,
    "geo.tv": 88,

    "timesofisrael.com": 92,
    "jerusalempost.com": 90,
    "middleeasteye.net": 88,

    # Official / Organizations
    "whitehouse.gov": 100,
    "state.gov": 99,
    "defense.gov": 99,
    "europa.eu": 99,
    "ec.europa.eu": 99,
    "un.org": 100,
    "unicef.org": 99,
    "undp.org": 98,
    "unesco.org": 98,
    "imf.org": 99,
    "worldbank.org": 99,
    "weforum.org": 94,
    "oecd.org": 98,
    "wto.org": 98,
    "europol.europa.eu": 99,
    "interpol.int": 100,
}

def get_source_score(url):
    domain = urlparse(url).netloc.lower()
    domain = domain.replace("www.", "")

    for site, score in SOURCE_SCORE.items():
        if site in domain:
            return score

    return 50


class ResearchArticle:
    def __init__(
        self,
        title,
        url,
        source,
        summary="",
        text="",
        image=None,
        published="",
    ):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary
        self.text = text
        self.image = image
        self.published = published

        self.score = get_source_score(url)

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "text": self.text,
            "image": self.image,
            "published": self.published,
            "score": self.score,
        }


def fetch_top_candidates():
    articles = []

    for source, rss in config.RSS_FEEDS.items():
        try:
            feed = feedparser.parse(rss)
        except Exception:
            continue

        for entry in feed.entries[: config.TOP_CANDIDATES_PER_FEED]:
            articles.append(
                ResearchArticle(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    source=source,
                    summary=entry.get("summary", ""),
                    published=entry.get("published", ""),
                ).to_dict()
            )

    return articles


def google_news_search(query, limit=30):
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    articles = []

    for item in feed.entries[:limit]:
        articles.append(
            ResearchArticle(
                title=item.get("title", ""),
                url=item.get("link", ""),
                source=urlparse(item.get("link", "")).netloc,
                summary=item.get("summary", ""),
                published=item.get("published", ""),
            ).to_dict()
        )

    return articles


def download_article(url, retries=3):
    for attempt in range(retries):
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                continue

            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                include_links=False,
                include_images=False,
            )

            if text:
                return text.strip()

        except Exception:
            pass

        time.sleep(1)

    return ""


def get_article_image(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        html = response.text

        tags = [
            'property="og:image:secure_url" content="',
            'property="og:image" content="',
            'name="twitter:image" content="',
            'name="twitter:image:src" content="',
            "property='og:image:secure_url' content='",
            "property='og:image' content='",
            "name='twitter:image' content='",
            "name='twitter:image:src' content='",
        ]

        for tag in tags:
            if tag not in html:
                continue

            start = html.find(tag) + len(tag)
            # find the next quote (either single or double) after start
            dq = html.find('"', start)
            sq = html.find("'", start)

            # pick the earliest positive index
            if dq == -1 and sq == -1:
                continue
            if dq == -1:
                end = sq
            elif sq == -1:
                end = dq
            else:
                end = min(dq, sq)

            image = html[start:end].strip()
            if image.startswith("http"):
                return image

    except Exception:
        pass

    return None


def enrich_articles(articles):

    enriched = []

    for article in articles:

        title = article.get("title", "").strip()
        url = article.get("url", "").strip()
        summary = article.get("summary", "").strip()

        print("[READING]", title[:100])

        if not url:
            continue

        # Resolve Google News redirect
        try:
            article["url"] = resolve_google_url(url)
        except Exception:
            article["url"] = url

        final_url = article["url"]

        # Update source and score after resolving Google News URL
try:
    resolved_domain = urlparse(final_url).netloc.lower()
    resolved_domain = resolved_domain.replace("www.", "")

    article["source"] = resolved_domain
    article["score"] = get_source_score(final_url)

except Exception:
    pass

        # Try full article extraction
        body = ""

        try:
            body = download_article(final_url)
        except Exception as e:
            print("[EXTRACT ERROR]", e)

        # Prefer extracted article text
        if body and len(body.strip()) >= 300:

            article["text"] = body.strip()[:8000]

        # If extraction fails, use RSS summary
        elif summary and len(summary.strip()) >= 100:

            print("[FALLBACK] Using RSS summary")

            article["text"] = summary.strip()

        else:

            print("[SKIP] No usable article text")

            continue

        # Image is optional
        try:
            article["image"] = get_article_image(
                final_url
            )
        except Exception:
            article["image"] = None

        enriched.append(article)

        time.sleep(0.2)

    print(
        f"[RESEARCH] Usable articles: {len(enriched)}"
    )

    return enriched


def remove_duplicates(articles):
    seen = set()
    cleaned = []

    for article in articles:
        title = article.get("title", "") or ""
        title = title.lower().strip()
        # remove punctuation and extra whitespace
        title = re.sub(r"[^\w\s]", "", title)
        title = re.sub(r"\s+", " ", title).strip()

        if title in seen:
            continue

        seen.add(title)
        cleaned.append(article)

    return cleaned


def similarity(a, b):
    stop_words = {
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
        "was",
        "were",
        "has",
        "have",
        "had",
        "from",
    }

    sa = {
        word.lower()
        for word in a.split()
        if len(word) > 2 and word.lower() not in stop_words
    }

    sb = {
        word.lower()
        for word in b.split()
        if len(word) > 2 and word.lower() not in stop_words
    }

    if not sa or not sb:
        return 0

    return len(sa & sb) / min(len(sa), len(sb))


def group_candidates(candidates):
    groups = []

    for article in candidates:
        matched = False

        for group in groups:
            if similarity(article["title"], group["title"]) > 0.45:
                group["items"].append(article)
                matched = True
                break

        if not matched:
            groups.append({"title": article["title"], "items": [article]})

    return groups


def research_story(title):
    print("[RESEARCH]", title)

    articles = google_news_search(title, limit=30)
    articles = enrich_articles(articles)
    articles = remove_duplicates(articles)
    articles = unique_sources(articles)

    articles.sort(key=lambda x: x["score"], reverse=True)
    research_statistics(articles)
    return articles


def pick_top_story(candidates, db):
    groups = group_candidates(candidates)
    final_groups = []

    for group in groups:
        group["items"] = remove_duplicates(group["items"])
        if not group["items"]:
            continue

        title = group["title"]

        best_article = max(group["items"], key=lambda x: x["score"])

        if db.is_duplicate(best_article["title"], best_article["url"]):
            continue

        score = 0
        # Number of news sources
        score += len(group["items"]) * 40

        # Best source reputation
        score += max(article["score"] for article in group["items"])

        # Image bonus
        if any(article.get("image") for article in group["items"]):
            score += 30

        # Long article bonus
        if any(len(article.get("text", "")) > 3000 for article in group["items"]):
            score += 25

        group["score"] = score
        final_groups.append(group)

    if not final_groups:
        return None

    final_groups.sort(key=lambda x: x["score"], reverse=True)

    print("\n===== STORY SCORES =====")
    for group in final_groups[:10]:
        print(
            f"{group['score']:>4} | {len(group['items'])} sources | {group['title'][:80]}"
        )
    print("========================\n")

    return final_groups[0]


def gather_deep_dive_texts(title):
    articles = research_story(title)
    data = []

    for article in articles:
        data.append(
            {
                "title": article["title"],
                "text": article["text"],
                "source": article["source"],
                "url": article["url"],
                "image": article["image"],
                "score": article["score"],
            }
        )

    return data


def gather_politician_reactions(title):
    reactions = []

    for person in config.POLITICIANS:
        query = f"{person} {title}"
        news = google_news_search(query, limit=3)

        for article in news:
            reactions.append(
                {
                    "person": person,
                    "title": article["title"],
                    "text": article["summary"],
                    "source": article["source"],
                }
            )

        time.sleep(0.2)

    return reactions


def resolve_google_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return response.url
    except Exception:
        return url


def unique_sources(articles):
    used = set()
    result = []

    for article in articles:
        # normalize source using url if available
        source = (article.get("source") or "").lower()
        source = source.replace("www.", "")
        if not source and article.get("url"):
            source = urlparse(article["url"]).netloc.lower().replace("www.", "")

        if source in used:
            continue

        used.add(source)
        result.append(article)

    return result


def best_image(articles):
    for article in articles:
        if article.get("image"):
            return article["image"]
    return None


def best_source(articles):
    if not articles:
        return ""
    return max(articles, key=lambda x: x["score"])["source"]


def best_url(articles):
    if not articles:
        return ""
    return max(articles, key=lambda x: x["score"])["url"]


# Placeholder for research_statistics used above: keep a minimal implementation
def research_statistics(articles):
    # This function previously existed or was expected. Keep a no-op or log summary.
    try:
        total = len(articles)
        top_scores = [a.get("score", 0) for a in articles[:5]]
        # You can expand logging here if needed
    except Exception:
        pass
