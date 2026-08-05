import json
try:
    import ollama
except ModuleNotFoundError as e:
    raise RuntimeError(
        "Missing dependency 'ollama'. Add 'ollama' to bot/requirements.txt or install it in CI (pip install ollama)."
    ) from e

import config

SYSTEM_PROMPT = """
You are the Editor-in-Chief of SYSTEMIC NEWS.

Your articles should feel like they were written by a journalist with 30 years of experience.

You are not allowed to write generic AI summaries.

Every paragraph must provide value.

When information is uncertain,
say it is uncertain.

When facts conflict,
say they conflict.

Never hide uncertainty.

Never repeat information.

Always explain:

Why

How

What changes

Who benefits

Who is affected

What happens next

Always sound human.

Never mention AI.

Never mention prompts.

Output only the article.
"""
EDITOR_PROMPT = """
You are the Senior Editor of SYSTEMIC NEWS.

Your job is NOT to rewrite everything.

Your job is to improve the article.

Checklist:

• Remove robotic writing.
• Remove repeated ideas.
• Improve flow.
• Improve transitions.
• Improve readability.
• Make every paragraph interesting.
• Add missing context if supported by the facts.
• Keep every fact accurate.
• Never invent information.
• Never exaggerate.

The finished article should feel like it was written by an award-winning journalist.

Return ONLY the final article.
"""
def build_fact_text(facts):

    text = ""

    text += "HEADLINE\n"

    text += facts.get(
        "headline",
        "",
    )

    text += "\n\n"

    text += "VERIFIED FACTS\n"

    for fact in facts.get(
        "verified_facts",
        [],
    ):

        text += f"• {fact}\n"

    text += "\n"

    text += "TIMELINE\n"

    for event in facts.get(
        "timeline",
        [],
    ):

        text += f"• {event}\n"

    text += "\n"

    text += "PEOPLE\n"

    text += ", ".join(
        facts.get(
            "people",
            [],
        )
    )

    text += "\n\n"

    text += "ORGANIZATIONS\n"

    text += ", ".join(
        facts.get(
            "organizations",
            [],
        )
    )

    text += "\n\n"

    text += "LOCATIONS\n"

    text += ", ".join(
        facts.get(
            "locations",
            [],
        )
    )

    text += "\n\n"

    text += "CAUSES\n"

    for item in facts.get(
        "causes",
        [],
    ):

        text += f"• {item}\n"

    text += "\n"

    text += "EFFECTS\n"

    for item in facts.get(
        "effects",
        [],
    ):

        text += f"• {item}\n"

    text += "\n"

    text += "NEXT EVENTS\n"

    for item in facts.get(
        "next_events",
        [],
    ):

        text += f"• {item}\n"

    return text

USER_PROMPT = """
Write a world-class news article.

Do NOT summarize.

Write like an experienced journalist.

The reader should understand the event without reading any other article.

Structure:

1. Powerful headline

2. Lead
Explain the most important information immediately.

3. What happened
Explain the event in chronological order.

4. Why this matters
Explain why readers should care.

5. Bigger picture
Explain historical, political, economic or technological context.

6. What happens next
Explain likely next official steps.

7. Key Takeaway
End with one memorable paragraph.

Rules:

• Never invent facts.
• Never exaggerate.
• Never repeat yourself.
• Never sound like AI.
• Never use clickbait.
• Explain difficult things simply.
• Every paragraph should teach the reader something new.

Write naturally.

Maximum 900 words.
"""
def generate_article(facts):

    prompt = build_fact_text(facts)

    response = ollama.chat(

        model=config.AI_MODEL,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },

            {
                "role": "user",
                "content": USER_PROMPT + "\n\n" + prompt,
            },

        ],

        options={
            "temperature": 0.35,
            "top_p": 0.9,
        },

    )

    return response["message"]["content"]

def edit_article(article):

    response = ollama.chat(

        model=config.AI_MODEL,

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

        options={

            "temperature": 0.2,

            "top_p": 0.9,

        },

    )

    return response["message"]["content"]

def article_statistics(article):

    words = len(article.split())

    paragraphs = len(
        [p for p in article.split("\n") if p.strip()]
    )

    print()
    print("======= ARTICLE =======")
    print("Words      :", words)
    print("Paragraphs :", paragraphs)
    print("=======================")
    print()

def build_report(facts):

    print("[AI] Writing article...")

    draft = generate_article(facts)

    print("[AI] Editing article...")

    final = edit_article(draft)

    article_statistics(final)

    return final
