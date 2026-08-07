import os
import shutil
import subprocess
import tempfile

DB_REPO = os.getenv("DB_REPO")
DB_TOKEN = os.getenv("DB_TOKEN")

BRANCH = "main"


def clone_database_repo():

    temp_dir = tempfile.mkdtemp()

    repo_url = (
        f"https://x-access-token:{DB_TOKEN}"
        f"@github.com/{DB_REPO}.git"
    )

    print("[DB] Cloning database repository...")

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


def push_database(repo, message):

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "config",
            "user.name",
            "SYSTEMIC NEWS BOT",
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
            message,
        ],
        check=False,
    )

    subprocess.run(
        [
            "git",
            "-C",
            repo,
            "push",
            "origin",
            BRANCH,
        ],
        check=True,
    )

    shutil.rmtree(
        repo,
        ignore_errors=True,
    )

    print("[DB] Database updated.")
