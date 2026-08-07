import os
import shutil
import subprocess
import tempfile

DB_REPO = os.getenv("DB_REPO")
DB_TOKEN = os.getenv("DB_TOKEN")

BRANCH = "main"


def _build_repo_url(db_repo: str, db_token: str | None) -> str:
    """Construct a safe Git clone URL.

    - If db_repo looks like a full URL, return it (ensure it ends with .git).
    - Otherwise, if a token is provided, use x-access-token auth for private repos.
    - If no token is provided, assume the repo is public and use the https GitHub URL.
    """
    if db_repo.startswith("http://") or db_repo.startswith("https://"):
        return db_repo if db_repo.endswith(".git") else db_repo + ".git"

    if db_token:
        return f"https://x-access-token:{db_token}@github.com/{db_repo}.git"

    return f"https://github.com/{db_repo}.git"


def clone_database_repo():

    if not DB_REPO:
        # Fail fast with a clear message so CI logs point to missing configuration
        raise EnvironmentError(
            "DB_REPO environment variable is not set. Set DB_REPO to '<owner>/<repo>' or a full repo URL."
        )

    temp_dir = tempfile.mkdtemp()

    repo_url = _build_repo_url(DB_REPO, DB_TOKEN)

    print(f"[DB] Cloning database repository from {repo_url}...")

    try:
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
    except subprocess.CalledProcessError as e:
        # Provide a helpful error message including the repo used so it's easier to debug in CI logs
        # Avoid printing secrets (DB_TOKEN) — repo_url will include token if set, so hide it here.
        safe_repo_display = repo_url
        if DB_TOKEN and "@" in repo_url:
            # hide token portion
            safe_repo_display = repo_url.split("@", 1)[1]
            safe_repo_display = f"https://{safe_repo_display}"

        raise RuntimeError(
            f"Failed to clone database repository '{safe_repo_display}': {e}. "
            "Ensure DB_REPO (and DB_TOKEN for private repos) are set correctly in your workflow secrets."
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
