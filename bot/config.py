import os

# =========================
# Telegram
# =========================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

if not TELEGRAM_CHANNEL_ID:
    raise RuntimeError("TELEGRAM_CHANNEL_ID is not set.")

# =========================
# Groq / Model
# =========================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set.")

GROQ_MODEL = "openai/gpt-oss-120b"

# Backwards-compatible alias expected by other modules
AI_MODEL = os.environ.get("AI_MODEL", GROQ_MODEL)

# =========================
# RSS Feeds
# =========================

RSS_FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "AP": "https://apnews.com/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NYTimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
}

# =========================
# Settings
# =========================

TOP_CANDIDATES_PER_FEED = 5

DEEP_DIVE_ARTICLE_LIMIT = 8

POLITICIAN_REACTION_LIMIT = 2

STATE_FILE = "posted_state.json"

# =========================
# Politicians
# =========================

POLITICIANS = [
    "Donald Trump",
    "Joe Biden",
    "Volodymyr Zelenskyy",
    "Vladimir Putin",
    "Xi Jinping",
    "Narendra Modi",
    "Keir Starmer",
]
