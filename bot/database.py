import sqlite3

DB_FILE = "systemic_news.db"


def connect():

    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS posted_news(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

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
        WHERE title=?
           OR url=?
        LIMIT 1
        """,
        (
            title,
            url,
        ),
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
        (
            title,
            url,
            source,
        ),
    )

    conn.commit()

    conn.close()


def get_posted_titles():

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT title
        FROM posted_news
        """
    )

    rows = cur.fetchall()

    conn.close()

    return [
        row[0]
        for row in rows
    ]


def total_posts():

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM posted_news
        """
    )

    count = cur.fetchone()[0]

    conn.close()

    return count


def latest_post():

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            title,
            source,
            created
        FROM posted_news
        ORDER BY created DESC
        LIMIT 1
        """
    )

    row = cur.fetchone()

    conn.close()

    return row


def database_statistics():

    print()

    print("========== DATABASE ==========")

    print(
        "Total Posts :",
        total_posts(),
    )

    latest = latest_post()

    if latest:

        print(
            "Latest      :",
            latest[0],
        )

    print("==============================")

    print()
