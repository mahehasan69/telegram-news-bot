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

    # Regional
    "straitstimes.com": 93,
    "japantimes.co.jp": 93,
    "hindustantimes.com": 90,
    "thehindu.com": 94,
    "timesofindia.indiatimes.com": 89,
    "dawn.com": 92,
    "arabnews.com": 90,
    "haaretz.com": 94,

    # Bangladesh
    "thedailystar.net": 93,
    "bdnews24.com": 92,
    "dhakatribune.com": 90,
    "prothomalo.com": 94,
    "daily-sun.com": 86,
    "newagebd.net": 89,

    # Misc
    "yahoo.com": 85,
    "msn.com": 84,

    # Europe
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

    # Canada
    "cbc.ca": 95,
    "ctvnews.ca": 91,
    "globalnews.ca": 90,
    "nationalpost.com": 89,

    # Australia & NZ
    "abc.net.au": 95,
    "smh.com.au": 91,
    "theage.com.au": 91,
    "news.com.au": 88,
    "nzherald.co.nz": 89,

    # Asia
    "straitstimes.com": 93,
    "channelnewsasia.com": 93,
    "scmp.com": 94,
    "japantimes.co.jp": 93,
    "japantoday.com": 90,
    "nikkei.com": 97,
    "koreatimes.co.kr": 89,
    "koreaherald.com": 89,
    "chinadaily.com.cn": 84,
    "globaltimes.cn": 82,

    # India
    "thehindu.com": 95,
    "hindustantimes.com": 92,
    "indianexpress.com": 94,
    "livemint.com": 93,
    "moneycontrol.com": 90,
    "ndtv.com": 90,
    "timesofindia.indiatimes.com": 89,
    "firstpost.com": 87,
    "news18.com": 87,

    # Pakistan
    "dawn.com": 94,
    "tribune.com.pk": 89,
    "geo.tv": 88,

    # Middle East
    "arabnews.com": 90,
    "timesofisrael.com": 92,
    "jerusalempost.com": 90,
    "haaretz.com": 95,
    "middleeasteye.net": 88,

    # Official Government & International
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

    # Health & Medical
    "who.int": 100,
    "cdc.gov": 100,
    "nih.gov": 100,
    "fda.gov": 99,
    "ema.europa.eu": 99,
    "nejm.org": 100,
    "thelancet.com": 100,
    "bmj.com": 99,
    "jamanetwork.com": 99,
    "mayoclinic.org": 98,

    # Science & Space
    "nasa.gov": 100,
    "esa.int": 99,
    "noaa.gov": 99,
    "usgs.gov": 99,
    "nature.com": 100,
    "science.org": 100,
    "newscientist.com": 96,
    "sciencedaily.com": 93,
    "phys.org": 93,
    "space.com": 92,
    "cern.ch": 100,

    # Artificial Intelligence
    "openai.com": 100,
    "anthropic.com": 99,
    "deepmind.google": 99,
    "ai.google": 99,
    "huggingface.co": 96,
    "stability.ai": 94,
    "x.ai": 95,
    "perplexity.ai": 94,

    # Big Tech
    "apple.com": 98,
    "newsroom.apple.com": 99,
    "about.google": 99,
    "blog.google": 98,
    "microsoft.com": 99,
    "news.microsoft.com": 99,
    "meta.com": 98,
    "about.fb.com": 98,
    "amazon.com": 98,
    "aws.amazon.com": 98,
    "nvidia.com": 99,
    "intel.com": 97,
    "amd.com": 97,
    "tesla.com": 96,
    "spacex.com": 98,

    # Finance
    "federalreserve.gov": 100,
    "ecb.europa.eu": 100,
    "bankofengland.co.uk": 99,
    "bis.org": 99,
    "sec.gov": 100,
    "nyse.com": 98,
    "nasdaq.com": 98,
    "coinmarketcap.com": 90,
    "coingecko.com": 90,
    # Cybersecurity
    "cisa.gov": 100,
    "nist.gov": 100,
    "mitre.org": 100,
    "cve.org": 100,
    "attack.mitre.org": 100,
    "securityweek.com": 96,
    "darkreading.com": 96,
    "bleepingcomputer.com": 96,
    "krebsonsecurity.com": 99,
    "thehackernews.com": 93,
    "theregister.com": 94,
    "infosecurity-magazine.com": 93,
    "helpnetsecurity.com": 93,
    "cyberscoop.com": 94,
    "hackread.com": 89,
    "securityaffairs.com": 92,
    "portswigger.net": 98,
    "rapid7.com": 98,
    "tenable.com": 97,
    "crowdstrike.com": 98,
    "mandiant.com": 99,
    "sentinelone.com": 96,
    "paloaltonetworks.com": 97,
    "checkpoint.com": 96,
    "fortinet.com": 95,
    "trendmicro.com": 95,
    "kaspersky.com": 94,
    "eset.com": 94,
    "malwarebytes.com": 94,
    "sans.org": 99,

    # Developer
    "github.blog": 98,
    "github.com": 96,
    "gitlab.com": 94,
    "stackoverflow.blog": 94,
    "developer.mozilla.org": 98,
    "developers.googleblog.com": 98,
    "developer.apple.com": 98,
    "learn.microsoft.com": 99,
    "aws.amazon.com": 98,
    "cloud.google.com": 98,
    "azure.microsoft.com": 98,
    "oracle.com": 95,
    "docker.com": 97,
    "kubernetes.io": 99,
    "python.org": 99,
    "golang.org": 99,
    "rust-lang.org": 99,
    "nodejs.org": 98,
    "openjdk.org": 98,

    # Linux
    "ubuntu.com": 97,
    "debian.org": 98,
    "archlinux.org": 97,
    "redhat.com": 97,
    "fedora.org": 97,
    "kali.org": 98,
    "linuxfoundation.org": 99,

    # Cloud
    "aws.amazon.com": 99,
    "cloud.google.com": 99,
    "azure.microsoft.com": 99,
    "cloudflare.com": 98,
    "digitalocean.com": 95,
    "linode.com": 94,
    "vercel.com": 95,
    "netlify.com": 94,

    # Open Source
    "apache.org": 98,
    "gnu.org": 98,
    "eclipse.org": 96,
    "mozilla.org": 97,
    "wikimedia.org": 96,

    # Gaming
    "ign.com": 94,
    "gamespot.com": 94,
    "pcgamer.com": 93,
    "eurogamer.net": 93,
    "kotaku.com": 90,
    "rockpapershotgun.com": 91,
    "polygon.com": 91,
    "gameinformer.com": 90,
    "steamcommunity.com": 88,
    "steampowered.com": 95,
    "epicgames.com": 94,
    "playstation.com": 95,
    "xbox.com": 95,
    "nintendo.com": 95,

    # Entertainment
    "imdb.com": 94,
    "rottentomatoes.com": 92,
    "metacritic.com": 92,
    "variety.com": 95,
    "hollywoodreporter.com": 95,
    "deadline.com": 95,
    "screenrant.com": 90,
    "empireonline.com": 91,
    "collider.com": 90,
    "billboard.com": 94,
    "rollingstone.com": 93,
    "people.com": 89,
    "tmz.com": 80,

    # Sports
    "espn.com": 96,
    "skysports.com": 95,
    "theathletic.com": 96,
    "fifa.com": 99,
    "uefa.com": 99,
    "nba.com": 98,
    "nfl.com": 98,
    "mlb.com": 98,
    "nhl.com": 98,
    "formula1.com": 99,
    "cricbuzz.com": 92,
    "icc-cricket.com": 99,
    "olympics.com": 99,

    # Weather
    "weather.gov": 100,
    "metoffice.gov.uk": 99,
    "accuweather.com": 93,
    "weather.com": 94,
    "windy.com": 93,
    "wunderground.com": 92,

    # Aviation
    "flightglobal.com": 94,
    "simpleflying.com": 90,
    "aviationweek.com": 95,
    "icao.int": 100,
    "iata.org": 99,
    "faa.gov": 100,

    # Automotive
    "tesla.com": 97,
    "motortrend.com": 93,
    "caranddriver.com": 94,
    "autocar.co.uk": 93,
    "topgear.com": 93,
    "insideevs.com": 92,
    "electrek.co": 91,

    # Crypto
    "coindesk.com": 94,
    "cointelegraph.com": 91,
    "decrypt.co": 90,
    "theblock.co": 92,
    "bitcoinmagazine.com": 89,
    "binance.com": 92,
    "coinbase.com": 93,
    "kraken.com": 92,

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

        for entry in feed.entries[:config.TOP_CANDIDATES_PER_FEED]:

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

                source=urlparse(
                    item.get("link", "")
                ).netloc,

                summary=item.get("summary", ""),

                published=item.get(
                    "published", ""
                ),

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

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10,
        )

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

            quote = '"' if '"' in tag else "'"

            end = html.find(quote, start)

            image = html[start:end]

            if image.startswith("http"):
                return image

    except Exception:

        pass

    return None

     def enrich_articles(articles):

    enriched = []

    for article in articles:

        print(
            "[READING]",
            article["title"][:80]
        )

        article["url"] = resolve_google_url(
            article["url"]
        )

        body = download_article(
            article["url"]
        )

        if body:

            article["text"] = body[:6000]

        else:

            article["text"] = article.get(
                "summary",
                "",
            )

        article["image"] = get_article_image(
            article["url"]
        )

       if len(article["text"]) > 500:

        enriched.append(article)

        time.sleep(0.2)

    return enriched

     def remove_duplicates(articles):

    seen = set()

    cleaned = []

    for article in articles:

        title = article["title"].lower().strip()

        title = (
            title.replace(",", "")
            .replace(".", "")
            .replace(":", "")
            .replace("-", " ")
        )

        if title in seen:
            continue

        seen.add(title)

        cleaned.append(article)

    return cleaned
    def similarity(a, b):

    stop_words = {

        "the","a","an","to","of","and","for",
        "in","on","with","at","is","are","was",
        "were","has","have","had","from"

    }

    sa = {

        word.lower()

        for word in a.split()

        if len(word) > 2

        and word.lower() not in stop_words

    }

    sb = {

        word.lower()

        for word in b.split()

        if len(word) > 2

        and word.lower() not in stop_words

    }

    if not sa or not sb:

        return 0

    return len(sa & sb) / min(len(sa), len(sb))

    def group_candidates(candidates):

    groups = []

    for article in candidates:

        matched = False

        for group in groups:

            if similarity(
                article["title"],
                group["title"],
            ) > 0.45:

                group["items"].append(article)

                matched = True

                break

        if not matched:

            groups.append(

                {

                    "title": article["title"],

                    "items": [article],

                }

            )

    return groups

def research_story(title):

    print("[RESEARCH]", title)

    articles = google_news_search(
        title,
        limit=30,
    )

    articles = enrich_articles(
        articles
    )

    articles = remove_duplicates(
    articles
    )

    articles = unique_sources(
    articles
    )

    articles.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    research_statistics(
        articles
    )

    return articles

    def pick_top_story(candidates, already_posted):

    groups = group_candidates(candidates)

    final_groups = []

    for group in groups:

        group["items"] = remove_duplicates(
            group["items"]
        )

        if not group["items"]:
            continue

        title = group["title"]

        if any(
            similarity(title, old) > 0.65
            for old in already_posted
        ):
            continue

        score = 0

        # Number of news sources
        score += len(group["items"]) * 40

        # Best source reputation
        score += max(
            article["score"]
            for article in group["items"]
        )

        # Image bonus
        if any(
            article.get("image")
            for article in group["items"]
        ):
            score += 30

        # Long article bonus
        if any(
            len(article.get("text", "")) > 3000
            for article in group["items"]
        ):
            score += 25

        group["score"] = score

        final_groups.append(group)

    if not final_groups:
        return None

    final_groups.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    print("\n===== STORY SCORES =====")

    for group in final_groups[:10]:

        print(
            f"{group['score']:>4} | "
            f"{len(group['items'])} sources | "
            f"{group['title'][:80]}"
        )

    print("========================\n")

    return final_groups[0]
    def gather_deep_dive_texts(title):

    articles = research_story(title)

    data = []

    for article in articles:

        data.append({

            "title": article["title"],

            "text": article["text"],

            "source": article["source"],

            "url": article["url"],

            "image": article["image"],

            "score": article["score"],

        })

    return data
  def gather_politician_reactions(title):

    reactions = []

    for person in config.POLITICIANS:

        query = f"{person} {title}"

        news = google_news_search(
            query,
            limit=3,
        )

        for article in news:

            reactions.append({

                "person": person,

                "title": article["title"],

                "text": article["summary"],

                "source": article["source"],

            })

        time.sleep(0.2)

    return reactions
def resolve_google_url(url):

    try:

        response = requests.get(

            url,

            headers=HEADERS,

            timeout=10,

            allow_redirects=True,

        )

        return response.url

    except Exception:

        return url

def unique_sources(articles):

    used = set()

    result = []

    for article in articles:

        source = article["source"]

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

    return max(

        articles,

        key=lambda x: x["score"],

    )["source"]

    def best_url(articles):

    if not articles:

        return ""

    return max(

        articles,

        key=lambda x: x["score"],

    )["url"]
