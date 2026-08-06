import json
import os
import shutil
import subprocess
import tempfile

from website_publisher import load_news

WEBSITE_REPO = os.environ["WEBSITE_REPO"]

WEBSITE_TOKEN = os.environ["WEBSITE_TOKEN"]

BRANCH = "main"
def clone_repo():

    temp = tempfile.mkdtemp()

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
def save_news_json(repo_path):

    news = load_news()

    news_dir = os.path.join(

        repo_path,

        "news",

    )

    os.makedirs(

        news_dir,

        exist_ok=True,

    )

    with open(

        os.path.join(

            news_dir,

            "news.json",

        ),

        "w",

        encoding="utf-8",

    ) as f:

        json.dump(

            news,

            f,

            ensure_ascii=False,

            indent=2,

        )
def copy_images(repo_path, image_path):

    if not image_path:

        return

    if not os.path.exists(image_path):

        return

    image_dir = os.path.join(

        repo_path,

        "assets",

        "images",

    )

    os.makedirs(

        image_dir,

        exist_ok=True,

    )

    shutil.copy2(

        image_path,

        os.path.join(

            image_dir,

            os.path.basename(image_path),

        ),

    )

def commit_changes(repo_path):

    subprocess.run(

        [

            "git",

            "-C",

            repo_path,

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

            repo_path,

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

            repo_path,

            "add",

            ".",

        ],

        check=True,

    )

    subprocess.run(

        [

            "git",

            "-C",

            repo_path,

            "commit",

            "-m",

            "📰 Auto News Update",

        ],

        check=False,

    )

def push_changes(repo_path):

    subprocess.run(

        [

            "git",

            "-C",

            repo_path,

            "push",

            "origin",

            BRANCH,

        ],

        check=True,

    )

def sync_website(image_path=None):

    print("[WEBSITE] Cloning website repository...")

    repo = clone_repo()

    try:

        print("[WEBSITE] Updating news.json...")

        save_news_json(repo)

        print("[WEBSITE] Copying images...")

        copy_images(

            repo,

            image_path,

        )

        print("[WEBSITE] Committing changes...")

        commit_changes(repo)

        print("[WEBSITE] Pushing changes...")

        push_changes(repo)

        print("[WEBSITE] Website updated successfully.")

    finally:

        shutil.rmtree(

            repo,

            ignore_errors=True,

        )
