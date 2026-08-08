import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse


DB_REPO = os.getenv("DB_REPO")
DB_TOKEN = os.getenv("DB_TOKEN")

BRANCH = "main"


def _normalize_repo(repo):
    """
    Convert:

        username/repository

    or:

        https://github.com/username/repository

    into:

        username/repository
    """

    if not repo:
        return ""

    repo = repo.strip()

    if repo.startswith("https://") or repo.startswith("http://"):

        parsed = urlparse(repo)

        path = parsed.path.strip("/")

        if path.endswith(".git"):
            path = path[:-4]

        return path

    return repo.rstrip("/").removesuffix(".git")


def _public_repo_url(repo):
    """
    Build normal GitHub HTTPS URL.
    """

    normalized = _normalize_repo(repo)

    return (
        f"https://github.com/"
        f"{normalized}.git"
    )


def _authenticated_repo_url(repo):
    """
    Build authenticated GitHub URL for pushing.
    """

    normalized = _normalize_repo(repo)

    if not DB_TOKEN:

        return _public_repo_url(normalized)

    return (
        "https://x-access-token:"
        f"{DB_TOKEN}"
        "@github.com/"
        f"{normalized}.git"
    )


def _run(command, cwd=None, check=True):

    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        text=True,
    )


def clone_database_repo():

    if not DB_REPO:

        raise EnvironmentError(
            "DB_REPO environment variable is not set."
        )

    if not DB_TOKEN:

        raise EnvironmentError(
            "DB_TOKEN environment variable is not set."
        )

    repo_name = _normalize_repo(DB_REPO)

    if not repo_name:

        raise EnvironmentError(
            "Invalid DB_REPO."
        )

    temp_dir = tempfile.mkdtemp(
        prefix="systemic-news-db-"
    )

    clone_url = _public_repo_url(
        repo_name
    )

    print(
        "[DB] Cloning database repository..."
    )

    print(
        f"[DB] Repository: {clone_url}"
    )

    try:

        # Clone without exposing the token.
        _run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                clone_url,
                temp_dir,
            ]
        )

    except subprocess.CalledProcessError:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )

        raise RuntimeError(
            "Could not clone DB_REPO. "
            "Check DB_REPO."
        )

    # Configure authenticated remote.
    authenticated_url = (
        _authenticated_repo_url(
            repo_name
        )
    )

    _run(
        [
            "git",
            "-C",
            temp_dir,
            "remote",
            "set-url",
            "origin",
            authenticated_url,
        ]
    )

    # ------------------------------------------------
    # IMPORTANT:
    # Empty GitHub repositories have no branch.
    # Force the local branch to main.
    # ------------------------------------------------

    _run(
        [
            "git",
            "-C",
            temp_dir,
            "checkout",
            "-B",
            BRANCH,
        ]
    )

    print(
        "[DB] Database repository ready."
    )

    return temp_dir


def push_database(repo, message):

    if not repo:

        raise ValueError(
            "Database repository path is empty."
        )

    print(
        "[DB] Preparing database commit..."
    )

    # ------------------------------------------------
    # Git identity
    # ------------------------------------------------

    _run(
        [
            "git",
            "-C",
            repo,
            "config",
            "user.name",
            "SYSTEMIC NEWS BOT",
        ]
    )

    _run(
        [
            "git",
            "-C",
            repo,
            "config",
            "user.email",
            "bot@systemicnews.ai",
        ]
    )

    # ------------------------------------------------
    # Make sure we are on main
    # ------------------------------------------------

    _run(
        [
            "git",
            "-C",
            repo,
            "checkout",
            "-B",
            BRANCH,
        ]
    )

    # ------------------------------------------------
    # Check files
    # ------------------------------------------------

    print(
        "[DB] Files before commit:"
    )

    _run(
        [
            "git",
            "-C",
            repo,
            "status",
            "--short",
        ]
    )

    # ------------------------------------------------
    # Add database files
    # ------------------------------------------------

    _run(
        [
            "git",
            "-C",
            repo,
            "add",
            "-A",
        ]
    )

    # ------------------------------------------------
    # Check if anything changed
    # ------------------------------------------------

    status = subprocess.run(
        [
            "git",
            "-C",
            repo,
            "status",
            "--porcelain",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    if not status.stdout.strip():

        print(
            "[DB] No database changes to commit."
        )

        return

    # ------------------------------------------------
    # Commit
    # ------------------------------------------------

    _run(
        [
            "git",
            "-C",
            repo,
            "commit",
            "-m",
            message,
        ]
    )

    # ------------------------------------------------
    # Push main
    # ------------------------------------------------

    print(
        "[DB] Pushing database to GitHub..."
    )

    _run(
        [
            "git",
            "-C",
            repo,
            "push",
            "-u",
            "origin",
            BRANCH,
        ]
    )

    print(
        "[DB] Database updated successfully."
    )

    # ------------------------------------------------
    # Cleanup
    # ------------------------------------------------

    shutil.rmtree(
        repo,
        ignore_errors=True,
    )
