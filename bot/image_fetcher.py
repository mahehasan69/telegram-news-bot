import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137 Safari/537.36"
    )
}


def get_article_image(url):

    try:

        html = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        ).text

        soup = BeautifulSoup(html, "html.parser")

        candidates = []

        # OpenGraph
        for tag in soup.find_all("meta", property="og:image"):
            if tag.get("content"):
                candidates.append(tag["content"])

        # Secure OpenGraph
        for tag in soup.find_all("meta", property="og:image:secure_url"):
            if tag.get("content"):
                candidates.append(tag["content"])

        # Twitter
        for tag in soup.find_all("meta", attrs={"name": "twitter:image"}):
            if tag.get("content"):
                candidates.append(tag["content"])

        # JSON-LD
        for tag in soup.find_all("meta", itemprop="image"):
            if tag.get("content"):
                candidates.append(tag["content"])

        # Images inside article
        article = soup.find("article")

        if article:

            for img in article.find_all("img"):

                src = (
                    img.get("data-src")
                    or img.get("data-original")
                    or img.get("data-lazy-src")
                    or img.get("src")
                )

                if src:
                    candidates.append(src)

        # Whole page
        for img in soup.find_all("img"):

            src = (
                img.get("data-src")
                or img.get("data-original")
                or img.get("src")
            )

            if src:
                candidates.append(src)

        cleaned = []

        for img in candidates:

            img = urljoin(url, img)

            if any(x in img.lower() for x in [
                "logo",
                "avatar",
                "icon",
                "sprite",
                "ads",
                "advert",
                "favicon",
            ]):
                continue

            cleaned.append(img)

        if cleaned:
            return cleaned[0]

    except Exception as e:
        print(e)

    return None


def download_image(image_url, filename="news.jpg"):

    if not image_url:
        return None

    try:

        r = requests.get(
            image_url,
            headers=HEADERS,
            timeout=30,
            stream=True,
        )

        if r.status_code != 200:
            return None

        with open(filename, "wb") as f:

            for chunk in r.iter_content(8192):

                if chunk:
                    f.write(chunk)

        return filename

    except Exception as e:

        print(e)

        return None
        
