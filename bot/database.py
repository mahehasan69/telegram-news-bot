import hashlib
import os
import sqlite3
from datetime import datetime


DB_NAME = "systemic_news.db"


class NewsDatabase:

    def __init__(self, repo_path):

        self.repo_path = repo_path

        self.db_path = os.path.join(
            repo_path,
            DB_NAME,
        )

        self.conn = sqlite3.connect(
            self.db_path
        )

        self.conn.row_factory = sqlite3.Row

        self.create_tables()

    # ============================================================
    # CREATE TABLES
    # ============================================================

    def create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posted_news(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                hash TEXT UNIQUE,

                title TEXT,

                url TEXT UNIQUE,

                source TEXT,

                category TEXT,

                published TEXT,

                confidence INTEGER,

                telegram_message_id TEXT,

                website_article_id INTEGER,

                created_at TEXT

            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_hash
            ON posted_news(hash)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_url
            ON posted_news(url)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_created
            ON posted_news(created_at)
            """
        )

        self.conn.commit()

        print("[DB] Database ready.")

    # ============================================================
    # NORMALIZE TEXT
    # ============================================================

    def normalize(self, text):

        if not text:
            return ""

        return (
            text.lower()
            .replace('"', "")
            .replace("'", "")
            .replace(",", "")
            .replace(".", "")
            .replace(":", "")
            .replace("-", " ")
            .strip()
        )

    # ============================================================
    # GENERATE ARTICLE HASH
    # ============================================================

    def generate_hash(self, title, url):

        value = (
            self.normalize(title)
            + "|"
            + url.strip().lower()
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    # ============================================================
    # CHECK DUPLICATE
    # ============================================================

    def is_duplicate(self, title, url):

        cursor = self.conn.cursor()

        news_hash = self.generate_hash(
            title,
            url,
        )

        # Check hash
        cursor.execute(
            """
            SELECT id
            FROM posted_news
            WHERE hash=?
            LIMIT 1
            """,
            (news_hash,),
        )

        if cursor.fetchone():

            print("[DB] Duplicate hash found.")

            return True

        # Check URL
        cursor.execute(
            """
            SELECT id
            FROM posted_news
            WHERE url=?
            LIMIT 1
            """,
            (url,),
        )

        if cursor.fetchone():

            print("[DB] Duplicate URL found.")

            return True

        return False

    # ============================================================
    # SAVE ARTICLE
    # ============================================================

    def save_article(
        self,
        title,
        url,
        source,
        category,
        confidence,
        telegram_message_id=None,
        website_article_id=None,
    ):

        cursor = self.conn.cursor()

        news_hash = self.generate_hash(
            title,
            url,
        )

        now = datetime.utcnow().isoformat()

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # We insert exactly 10 columns:
        #
        # hash
        # title
        # url
        # source
        # category
        # published
        # confidence
        # telegram_message_id
        # website_article_id
        # created_at
        #
        # Therefore we need exactly 10 placeholders.
        # --------------------------------------------------------

        cursor.execute(
            """
            INSERT INTO posted_news(

                hash,
                title,
                url,
                source,
                category,
                published,
                confidence,
                telegram_message_id,
                website_article_id,
                created_at

            )

            VALUES(

                ?,?,?,?,?,?,?,?,?,?

            )
            """,
            (
                news_hash,
                title,
                url,
                source,
                category,
                now,
                confidence,
                telegram_message_id,
                website_article_id,
                now,
            ),
        )

        self.conn.commit()

        print(
            "[DB] Article saved successfully."
        )

    # ============================================================
    # TOTAL ARTICLES
    # ============================================================

    def total_articles(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM posted_news
            """
        )

        return cursor.fetchone()[0]

    # ============================================================
    # LATEST ARTICLE
    # ============================================================

    def latest_article(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM posted_news
            ORDER BY id DESC
            LIMIT 1
            """
        )

        return cursor.fetchone()

    # ============================================================
    # CLOSE DATABASE
    # ============================================================

    def close(self):

        if self.conn:

            self.conn.commit()

            self.conn.close()

            print(
                "[DB] Database connection closed."
            )
