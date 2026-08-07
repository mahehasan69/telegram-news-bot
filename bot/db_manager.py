import os

from database import NewsDatabase
from github_storage import (
    clone_database_repo,
    push_database,
)


class DatabaseManager:

    def __init__(self):

        self.repo = clone_database_repo()

        self.db = NewsDatabase(
            self.repo
        )

    def is_duplicate(

        self,

        title,

        url,

    ):

        return self.db.is_duplicate(
            title,
            url,
        )

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

        self.db.save_article(

            title=title,

            url=url,

            source=source,

            category=category,

            confidence=confidence,

            telegram_message_id=telegram_message_id,

            website_article_id=website_article_id,

        )

    def total_articles(self):

        return self.db.total_articles()

    def latest_article(self):

        return self.db.latest_article()

    def close(self):

        self.db.close()

    def sync(self, message):

        self.close()

        push_database(

            self.repo,

            message,

        )
