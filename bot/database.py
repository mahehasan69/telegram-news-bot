
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

    def create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
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
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash
        ON posted_news(hash)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_url
        ON posted_news(url)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created
        ON posted_news(created_at)
        """)

        self.conn.commit()

        print("[DB] Database ready.")

    def normalize(self, text):

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

    def generate_hash(self, title, url):

        value = (
            self.normalize(title)
            + "|"
            + url.strip().lower()
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    def is_duplicate(self, title, url):

        cursor = self.conn.cursor()

        news_hash = self.generate_hash(
            title,
            url,
        )

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

            return True

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

            return True

        return False

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

                self.generate_hash(
                    title,
                    url,
                ),

                title,

                url,

                source,

                category,

                datetime.utcnow().isoformat(),

                confidence,

                telegram_message_id,

                website_article_id,

                datetime.utcnow().isoformat(),

            ),

        )

        self.conn.commit()

        print("[DB] Article saved.")

    def total_articles(self):

        cursor = self.conn.cursor()

        cursor.execute(

            """
            SELECT COUNT(*)
            FROM posted_news
            """

        )

        return cursor.fetchone()[0]

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

    def close(self):

        self.conn.close() 

