import json
import math
import os
import shutil
import subprocess
import tempfile

from datetime import datetime


# ==========================================
# CONFIG
# ==========================================

WEBSITE_REPO = os.getenv("WEBSITE_REPO")
WEBSITE_TOKEN = os.getenv("WEBSITE_TOKEN")

BRANCH = "main"

MAX_NEWS = 0

NEWS_FOLDER = "news"
IMAGE_FOLDER = "assets/images"


if not WEBSITE_REPO:
    raise RuntimeError(
        "Missing WEBSITE_REPO environment variable."
    )

if not WEBSITE_TOKEN:
    raise RuntimeError(
        "Missing WEBSITE_TOKEN environment variable."
    )


# ==========================================
# GIT
# ==========================================

def clone_repo():

    temp_dir = tempfile.mkdtemp()

    repo_url = (
        f"https://x-access-token:{WEBSITE_TOKEN}"
        f"@github.com/{WEBSITE_REPO}.git"
    )

    print("[WEBSITE] Cloning website...")

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            repo_url,
            temp_dir,
        ],
        check=True,
    )

    return temp_dir


# ==========================================
# PATHS
# ==========================================

def get_news_file(repo):

    return os.path.join(
        repo,
        NEWS_FOLDER,
        "news.json",
    )


def get_image_folder(repo):

    return os.path.join(
        repo,
        IMAGE_FOLDER,
    )


# ==========================================
# JSON
# ==========================================

def load_news(repo):

    news_file = get_news_file(repo)

    if not os.path.exists(news_file):

        return []

    with open(
        news_file,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_news(repo, news):

    news_file = get_news_file(repo)

    os.makedirs(
        os.path.dirname(news_file),
        exist_ok=True,
    )

    with open(
        news_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            news,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("[WEBSITE] news.json updated.")

# ==========================================
# PUBLISH ARTICLE
# ==========================================

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

    try:

        news = load_news(repo)

        article_id = max(
            (
                item.get("id", 0)
                for item in news
            ),
            default=0,
        ) + 1

        # Remove featured from old articles
        for item in news:
            item["featured"] = False

        image_name = "placeholder.jpg"

        if image and os.path.exists(image):

            image_name = os.path.basename(image)

            image_folder = get_image_folder(repo)

            os.makedirs(
                image_folder,
                exist_ok=True,
            )

            shutil.copy2(
                image,
                os.path.join(
                    image_folder,
                    image_name,
                ),
            )

            print(
                "[WEBSITE] Image copied."
            )

        reading_time = max(
            1,
            math.ceil(
                len(article.split()) / 200
            ),
        )

        data = {

            "id": article_id,

            "title": title,

            "summary": summary,

            "content": article,

            "category": category,

            "image": f"assets/images/{image_name}",

            "date": datetime.now().strftime(
                "%Y-%m-%d"
            ),

            "time": datetime.now().strftime(
                "%H:%M"
            ),

            "reading_time":
                f"{reading_time} min read",

            "author":
                "SYSTEMIC NEWS",

            "confidence":
                confidence,

            "facts":
                facts,

            "timeline":
                timeline,

            "sources":
                sources,

            "url":
                f"article.html?id={article_id}",

            "featured":
                True,

        }

        news.insert(
            0,
            data,
        )

        if MAX_NEWS > 0:
    news = news[:MAX_NEWS]
        save_news(
            repo,
            news,
        )

        print(
            "[WEBSITE] Article saved."
        )

        # ==========================================
        # GIT CONFIG
        # ==========================================

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

        # ==========================================
        # ADD FILES
        # ==========================================

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

        # ==========================================
        # COMMIT
        # ==========================================

        commit = subprocess.run(
            [
                "git",
                "-C",
                repo,
                "commit",
                "-m",
                f"📰 {title}",
            ],
            capture_output=True,
            text=True,
        )

        if commit.returncode == 0:

            print("[WEBSITE] Commit created.")

        else:

            output = (
                commit.stdout +
                commit.stderr
            ).lower()

            if "nothing to commit" in output:

                print(
                    "[WEBSITE] Nothing changed."
                )

            else:

                print(commit.stdout)
                print(commit.stderr)

                raise RuntimeError(
                    "Git commit failed."
                )

        # ==========================================
        # PUSH
        # ==========================================

        print(
            "[WEBSITE] Pushing..."
        )

        push = subprocess.run(
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

        if push.returncode != 0:

            print(push.stdout)
            print(push.stderr)

            raise RuntimeError(
                "Git push failed."
            )

        print(
            "[WEBSITE] Website updated successfully."
        )

    finally:

        if os.path.exists(repo):

            shutil.rmtree(
                repo,
                ignore_errors=True,
            )

            print(
                "[WEBSITE] Temporary files removed."
            )

