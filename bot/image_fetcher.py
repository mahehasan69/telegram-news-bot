# image_fetcher.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}


def get_article_image(article_url: str):
    """
    Returns the best image URL from a news article.
    """

    try:
        r = requests.get(article_url, headers=HEADERS, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # ---------- Open Graph ----------
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return urljoin(article_url, og["content"])

        # ---------- Twitter ----------
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return urljoin(article_url, tw["content"])

        # ---------- Schema ----------
        schema = soup.find("meta", itemprop="image")
        if schema and schema.get("content"):
            return urljoin(article_url, schema["content"])

        # ---------- Largest image ----------
        imgs = soup.find_all("img")

        for img in imgs:
            src = (
                img.get("data-src")
                or img.get("data-lazy-src")
                or img.get("src")
            )

            if not src:
                continue

            src = urljoin(article_url, src)

            if any(x in src.lower() for x in [
                "logo",
                "icon",
                "avatar",
                "sprite",
                "banner",
                "ads",
                "advert",
            ]):
                continue

            return src

    except Exception as e:
        print(f"[IMAGE] {e}")

    return None


def download_image(image_url, filename="news.jpg"):
    """
    Downloads the image locally.
    Returns filename or None.
    """

    if not image_url:
        return None

    try:
        r = requests.get(image_url, headers=HEADERS, timeout=20)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)

        return filename

    except Exception as e:
        print(f"[DOWNLOAD] {e}")
        return None