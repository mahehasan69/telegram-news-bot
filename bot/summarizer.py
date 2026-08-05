import logging
import time

from groq import Groq

import config

logger = logging.getLogger(__name__)

client = Groq(
    api_key=config.GROQ_API_KEY,
)

MODEL = config.GROQ_MODEL

SYSTEM_PROMPT = """
You are the Chief Editor of SYSTEMIC NEWS.

Write like an investigative journalist.

Never sound like AI.

Never summarize.

Every paragraph must answer:

• What happened?

• Why did it happen?

• Why does it matter?

• What changes now?

• What happens next?

Rules:

• Never invent facts.

• Never exaggerate.

• Never repeat yourself.

• Never mention AI.

Write naturally.

Return ONLY the article.
"""

EDITOR_PROMPT = """
You are the Senior Editor.

Improve the article.

Make it emotional.

Make it human.

Improve transitions.

Remove robotic writing.

Never change facts.

Return ONLY the final article.
"""

USER_PROMPT = """
Write a premium quality news article.

Structure:

Headline

Lead

What happened

Why this matters

Background

Next developments

Key Takeaway

Maximum 900 words.

Return ONLY the article.
"""

def build_fact_text(facts):
    text = ""

    text += f"HEADLINE\n{facts.get('headline','')}\n\n"

    text += "VERIFIED FACTS\n"

    for fact in facts.get(
        "verified_facts",
        [],
    ):
        text += f"• {fact}\n"

    text += "\nTIMELINE\n"

    for item in facts.get(
        "timeline",
        [],
    ):
        text += f"• {item}\n"

    text += "\nCAUSES\n"

    for item in facts.get(
        "causes",
        [],
    ):
        text += f"• {item}\n"

    text += "\nEFFECTS\n"

    for item in facts.get(
        "effects",
        [],
    ):
        text += f"• {item}\n"

    text += "\nNEXT EVENTS\n"

    for item in facts.get(
        "next_events",
        [],
    ):
        text += f"• {item}\n"

    return text


def generate_article(facts):
    prompt = build_fact_text(
        facts
    )

    retries = 3

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                temperature=0.35,
                max_tokens=4096,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": USER_PROMPT
                        + "\n\n"
                        + prompt,
                    },
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.warning(
                f"Generate failed ({attempt+1}/3): {e}"
            )
            time.sleep(2)

    return "Unable to generate article."


def edit_article(article):
    retries = 3

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                temperature=0.15,
                max_tokens=4096,
                messages=[
                    {
                        "role": "system",
                        "content": EDITOR_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": article,
                    },
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.warning(
                f"Editor failed ({attempt+1}/3): {e}"
            )
            time.sleep(2)

    return article


def article_statistics(article):
    words = len(
        article.split()
    )

    paragraphs = len(
        [
            p
            for p in article.split("\n")
            if p.strip()
        ]
    )

    print()
    print("=" * 50)
    print("ARTICLE")
    print("=" * 50)
    print("Words :", words)
    print("Paragraphs :", paragraphs)
    print("=" * 50)
    print()


def build_report(facts):
    print()
    print("=" * 60)
    print("SYSTEMIC NEWS AI")
    print("=" * 60)

    print("[1/2] Writing article...")

    article = generate_article(
        facts
    )

    print("[2/2] Editing article...")

    article = edit_article(
        article
    )

    article_statistics(
        article
    )

    return article
