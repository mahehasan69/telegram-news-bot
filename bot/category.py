"""
Automatic News Category Detector
"""

import re


CATEGORIES = {
    "🤖 AI & Technology": [
        "ai",
        "artificial intelligence",
        "openai",
        "chatgpt",
        "gpt",
        "groq",
        "google",
        "microsoft",
        "apple",
        "meta",
        "amazon",
        "nvidia",
        "intel",
        "amd",
        "technology",
        "software",
        "robot",
        "chip",
        "quantum",
        "tesla",
        "cyber",
        "hacker",
        "malware",
    ],

    "💰 Finance": [
        "stock",
        "market",
        "economy",
        "bank",
        "interest",
        "inflation",
        "oil",
        "gold",
        "trade",
        "investment",
        "finance",
        "nasdaq",
        "dow",
        "s&p",
    ],

    "₿ Crypto": [
        "bitcoin",
        "ethereum",
        "crypto",
        "blockchain",
        "binance",
        "coinbase",
        "solana",
        "bnb",
        "web3",
    ],

    "⚽ Sports": [
        "football",
        "soccer",
        "cricket",
        "fifa",
        "uefa",
        "nba",
        "ipl",
        "world cup",
        "olympics",
        "tennis",
    ],

    "🧬 Science": [
        "nasa",
        "space",
        "science",
        "research",
        "mars",
        "moon",
        "planet",
        "biology",
        "physics",
    ],

    "🏥 Health": [
        "covid",
        "virus",
        "health",
        "hospital",
        "vaccine",
        "who",
        "medical",
        "disease",
    ],

    "🌍 World": [
        "war",
        "ukraine",
        "russia",
        "china",
        "israel",
        "gaza",
        "iran",
        "india",
        "pakistan",
        "bangladesh",
        "government",
        "president",
        "minister",
        "election",
        "un",
        "nato",
    ],

    "🎬 Entertainment": [
        "movie",
        "film",
        "actor",
        "actress",
        "hollywood",
        "bollywood",
        "netflix",
        "disney",
        "music",
        "concert",
    ],
}


def detect(title, report=""):

    text = (title + " " + report).lower()

    scores = {}

    for category, words in CATEGORIES.items():

        score = 0

        for word in words:

            if re.search(r"\b" + re.escape(word) + r"\b", text):
                score += 1

        scores[category] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "📰 General"

    return best