import sqlite3
from pathlib import Path

DB_FILE = "systemic_news.db"


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS posted_news(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        url TEXT UNIQUE,
        source TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn


def already_posted(title, url):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM posted_news
        WHERE
            title=?
            OR url=?
        """,
        (title, url),
    )

    row = cur.fetchone()

    conn.close()

    return row is not None


def save_post(title, url, source):

    conn = connect()

    conn.execute(
        """
        INSERT OR IGNORE INTO posted_news
        (title,url,source)
        VALUES (?,?,?)
        """,
        (title, url, source),
    )

    conn.commit()

    conn.close()
