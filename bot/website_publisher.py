import json
import os
from datetime import datetime

NEWS_FILE = "news/news.json"

MAX_NEWS = 100

def load_news():

    if not os.path.exists(NEWS_FILE):

        return []

    with open(

        NEWS_FILE,

        "r",

        encoding="utf-8",

    ) as f:

        return json.load(f)


def save_news(news):

    with open(

        NEWS_FILE,

        "w",

        encoding="utf-8",

    ) as f:

        json.dump(

            news,

            f,

            ensure_ascii=False,

            indent=2,

        )
def create_article(

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

    news = load_news()

    article_id = len(news) + 1

    data = {

        "id": article_id,

        "title": title,

        "summary": summary,

        "content": article,

        "category": category,

        "image": image,

        "date": datetime.now().strftime("%Y-%m-%d"),

        "time": datetime.now().strftime("%H:%M"),

        "reading_time": f"{max(1, len(article.split())//200)} min read",

        "author": "SYSTEMIC NEWS",

        "confidence": confidence,

        "facts": facts,

        "timeline": timeline,

        "sources": sources,

        "url": f"article.html?id={article_id-1}",

        "featured": True

    }

    for item in news:

        item["featured"] = False

    news.insert(

        0,

        data,

    )

    news = news[:MAX_NEWS]

    save_news(

        news,

    )

    print(

        "[WEBSITE] News saved."

    )
    for item in news:

        item["featured"] = False

    news.insert(

        0,

        data,

    )

    news = news[:MAX_NEWS]

    save_news(

        news,

    )

    print(

        "[WEBSITE] News saved."

    )
