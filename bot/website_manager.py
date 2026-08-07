import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
import math

WEBSITE_REPO = os.getenv("WEBSITE_REPO")
WEBSITE_TOKEN = os.getenv("WEBSITE_TOKEN")

if not WEBSITE_REPO or not WEBSITE_TOKEN:
    raise EnvironmentError("Environment variables WEBSITE_REPO and WEBSITE_TOKEN must be set")

MAX_NEWS = 100

BRANCH = "main"

def clone_repo():
    temp = tempfile.mkdtemp()
    print("WEBSITE_REPO =", WEBSITE_REPO) 
    url = (
        f"https://x-access-token:{WEBSITE_TOKEN}"
        f"@github.com/{WEBSITE_REPO}.git"
    )

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            url,
            temp,
        ],
        check=True,
    )

    return temp


def news_file(repo):
    return os.path.join(
        repo,
        "news",
        "news.json",
    )


def load_news(repo):
    file = news_file(repo)

    if not os.path.exists(file):
        return []

    with open(
        file,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_news(repo, news):
    os.makedirs(
        os.path.dirname(
            news_file(repo)
        ),
        exist_ok=True,
    )

    with open(
        news_file(repo),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            news,
            f,
            ensure_ascii=False,
            indent=2,
        )


def publish_article(
    title,
    summary,
    article,
    category,
    image,
    facts,
    timeline,
    sources,
    confidence,
):
    repo = clone_repo()

    news = load_news(repo)

    article_id = len(news) + 1

    data = {
        "id": article_id,
        "title": title,
        "summary": summary,
        "content": article,
        "category": category,
        "image": f"assets/images/{os.path.basename(image)}" if image else "assets/images/placeholder.jpg",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "reading_time": f"{max(1, math.ceil(len(article.split()) / 200))} min read",
        "author": "SYSTEMIC NEWS",
        "confidence": confidence,
        "facts": facts,
        "timeline": timeline,
        "sources": sources,
        "url": f"article.html?id={article_id}",
        "featured": True,
    }

    for item in news:
        item["featured"] = False

    news.insert(
        0,
        data,
    )

    news = news[:MAX_NEWS]

    save_news(
        repo,
        news,
    )

    if image and os.path.exists(image):
        image_dir = os.path.join(
            repo,
            "assets",
            "images",
        )

        os.makedirs(
            image_dir,
            exist_ok=True,
        )

        shutil.copy2(
            image,
            os.path.join(
                image_dir,
                os.path.basename(image),
            ),
        )

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "config",
            "user.name",
            "SYSTEMIC NEWS",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "config",
            "user.email",
            "bot@systemicnews.ai",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "add",
            ".",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "commit",
            "-m",
            f"📰 {title}",
        ],
        check=False,
    )

    result = subprocess.run(

    [

        "git",

        "-C",

        repo,

        "push",

        "origin",

        BRANCH,

    ],

    capture_output=True,

    text=True,

)

    print(result.stdout)

    print(result.stderr)

    result.check_returncode()
