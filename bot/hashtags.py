"""
Automatic Hashtag Generator
"""

import re


STOP_WORDS = {
    "the",
    "a",
    "an",
    "of",
    "for",
    "and",
    "to",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "has",
    "have",
    "had",
}


def generate(title, category):

    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", title)

    hashtags = []

    for word in words:

        if len(word) < 4:
            continue

        if word.lower() in STOP_WORDS:
            continue

        tag = "#" + word.replace("-", "")

        if tag not in hashtags:
            hashtags.append(tag)

    if "AI" in category:
        hashtags.append("#AI")

    elif "Technology" in category:
        hashtags.append("#Technology")

    elif "Finance" in category:
        hashtags.append("#Finance")

    elif "Crypto" in category:
        hashtags.append("#Crypto")

    elif "Sports" in category:
        hashtags.append("#Sports")

    elif "Science" in category:
        hashtags.append("#Science")

    elif "Health" in category:
        hashtags.append("#Health")

    elif "World" in category:
        hashtags.append("#WorldNews")

    hashtags.append("#SystemicNews")

    return " ".join(dict.fromkeys(hashtags))