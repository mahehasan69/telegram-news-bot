import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SYSTEMICNEWS/1.0; "
        "+https://systemicnews.new.tg)"
    )
}

BAD_IMAGE_TERMS = (
    "logo", "avatar", "icon", "sprite", "advert", "ads",
    "favicon", "placeholder", "default", "profile"
)

def _candidate_score(url, source=""):
    lower = url.lower()
    if any(term in lower for term in BAD_IMAGE_TERMS):
        return -100
    score = 0
    if source == "og":
        score += 100
    elif source == "twitter":
        score += 80
    elif source == "jsonld":
        score += 70
    elif source == "article":
        score += 50
    if any(ext in lower for ext in (".jpg", ".jpeg", ".png", ".webp")):
        score += 10
    if any(x in lower for x in ("width=1", "height=1", "1x1")):
        score -= 50
    return score

def get_article_image(url):
    if not url:
        return None
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        candidates = []

        def add(value, source):
            if isinstance(value, str) and value.strip():
                absolute = urljoin(url, value.strip())
                if urlparse(absolute).scheme in ("http", "https"):
                    candidates.append((_candidate_score(absolute, source), absolute))

        for tag in soup.find_all("meta"):
            prop = (tag.get("property") or "").lower()
            name = (tag.get("name") or "").lower()
            itemprop = (tag.get("itemprop") or "").lower()
            content = tag.get("content")
            if prop in ("og:image", "og:image:url", "og:image:secure_url"):
                add(content, "og")
            elif name in ("twitter:image", "twitter:image:src"):
                add(content, "twitter")
            elif itemprop == "image":
                add(content, "jsonld")

        for script in soup.find_all("script", type="application/ld+json"):
            raw = script.string or script.get_text()
            if raw:
                for match in re.findall(r'"image"\s*:\s*(?:"([^"]+)"|\[\s*"([^"]+)"|\{[^}]*"url"\s*:\s*"([^"]+)")', raw, re.I):
                    add(next((part for part in match if part), None), "jsonld")

        article = soup.find("article") or soup
        for img in article.find_all("img"):
            add(
                img.get("data-src") or img.get("data-original")
                or img.get("data-lazy-src") or img.get("src"),
                "article"
            )

        # Try candidates in quality order; reject failed, tiny, or non-image responses.
        seen = set()
        for score, candidate in sorted(candidates, reverse=True):
            if score < 0 or candidate in seen:
                continue
            seen.add(candidate)
            try:
                check = requests.get(candidate, headers=HEADERS, timeout=15, stream=True)
                content_type = check.headers.get("Content-Type", "").lower()
                check.close()
                if check.status_code == 200 and content_type.startswith("image/"):
                    return candidate
            except requests.RequestException:
                continue
    except Exception as exc:
        print(f"[IMAGE EXTRACT] {exc}")
    return None

def download_image(image_url, filename="news.jpg"):
    if not image_url:
        return None
    try:
        response = requests.get(
            image_url, headers=HEADERS, timeout=30, stream=True
        )
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            response.close()
            print(f"[IMAGE] Rejected non-image response: {content_type}")
            return None

        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        temp_name = filename + ".part"
        total = 0
        with open(temp_name, "wb") as output:
            for chunk in response.iter_content(8192):
                if chunk:
                    total += len(chunk)
                    if total > 15 * 1024 * 1024:
                        raise ValueError("Image exceeds 15 MB limit")
                    output.write(chunk)
        response.close()

        with open(temp_name, "rb") as image_file:
            signature = image_file.read(16)
        valid = (
            signature.startswith(b"\xff\xd8\xff")
            or signature.startswith(b"\x89PNG\r\n\x1a\n")
            or signature.startswith(b"RIFF") and signature[8:12] == b"WEBP"
            or signature.startswith((b"GIF87a", b"GIF89a"))
        )
        if not valid:
            os.remove(temp_name)
            print("[IMAGE] Rejected invalid image file.")
            return None
        os.replace(temp_name, filename)
        return filename
    except Exception as exc:
        try:
            if os.path.exists(filename + ".part"):
                os.remove(filename + ".part")
        except OSError:
            pass
        print(f"[IMAGE DOWNLOAD] {exc}")
        return None
