"""
Breaking News Detector
"""

import re

BREAKING_KEYWORDS = [
    "breaking",
    "just in",
    "developing",
    "urgent",
    "live",
    "alert",
    "explosion",
    "earthquake",
    "attack",
    "missile",
    "war",
    "dies",
    "death",
    "killed",
    "crash",
    "fire",
    "shooting",
    "evacuated",
    "emergency",
    "tsunami",
    "hurricane",
]

IMPORTANT_KEYWORDS = [
    "president",
    "prime minister",
    "government",
    "election",
    "nasa",
    "apple",
    "google",
    "microsoft",
    "tesla",
    "openai",
    "bitcoin",
    "economy",
    "inflation",
    "stock market",
]


def detect(title, report=""):

    text = (title + " " + report).lower()

    for word in BREAKING_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return "🚨 <b>BREAKING NEWS</b>"

    score = 0

    for word in IMPORTANT_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            score += 1

    if score >= 2:
        return "📢 <b>DEVELOPING STORY</b>"

    return "📰 <b>NEWS UPDATE</b>"