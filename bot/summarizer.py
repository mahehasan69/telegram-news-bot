import json
import logging

# Try to import ollama; fall back gracefully if it's not available or not running.
try:
    import ollama
    from ollama._client import ConnectionError as OllamaConnectionError
    OLLAMA_AVAILABLE = True
except Exception:
    ollama = None
    OllamaConnectionError = Exception
    OLLAMA_AVAILABLE = False

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


def _fallback_generate_article(facts):
    """Deterministic fallback generator used when ollama is unavailable or unreachable."""
    headline = facts.get("headline") or "Automated News Update"

    parts = [f"{headline}\n"]

    # Lead: use the most salient verified fact or the first timeline entry
    verified = facts.get("verified_facts", [])
    timeline = facts.get("timeline", [])

    lead = verified[0] if verified else (timeline[0] if timeline else "No verified facts available.")
    parts.append(lead + "\n\n")

    # What happened
    if timeline:
        parts.append("What happened:\n")
        for ev in timeline[:5]:
            parts.append(f"• {ev}\n")
        parts.append("\n")

    # Why this matters
    if verified:
        parts.append("Why this matters:\n")
        parts.append((verified[0] if verified else "No details available.") + "\n\n")

    # Bigger picture: include organizations/locations
    orgs = facts.get("organizations", [])
    locs = facts.get("locations", [])
    if orgs or locs:
        bp = "Bigger picture:\n"
        if orgs:
            bp += "Organizations involved: " + ", ".join(orgs) + ".\n"
        if locs:
            bp += "Locations: " + ", ".join(locs) + ".\n"
        parts.append(bp + "\n")

    # Next events
    next_events = facts.get("next_events", [])
    if next_events:
        parts.append("What happens next:\n")
        for ev in next_events[:3]:
            parts.append(f"• {ev}\n")
        parts.append("\n")

    # Key takeaway
    parts.append("Key takeaway: This report is autogenerated due to AI service unavailability. Check original sources for full detail.")

    return "\n".join(parts)


def _fallback_edit_article(article: str) -> str:
    # Minimal edit: trim excessive whitespace and ensure length <= 900 words
    words = article.split()
    if len(words) > 900:
        article = " ".join(words[:900]) + "..."
    # Remove repeated blank lines
    lines = [l.rstrip() for l in article.splitlines()]
    cleaned = []
    prev_blank = False
    for l in lines:
        if not l.strip():
            if not prev_blank:
                cleaned.append("")
            prev_blank = True
        else:
            cleaned.append(l)
            prev_blank = False
    return "\n".join(cleaned).strip()


def generate_article(facts):

    prompt = build_fact_text(facts)

    if not OLLAMA_AVAILABLE:
        logging.warning("ollama package not installed; using fallback generator.")
        return _fallback_generate_article(facts)

    try:
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

    except OllamaConnectionError as e:
        logging.warning("Failed to connect to Ollama: %s. Falling back to local generator.", e)
        return _fallback_generate_article(facts)
    except Exception as e:
        logging.exception("Unexpected error while calling Ollama; falling back. %s", e)
        return _fallback_generate_article(facts)


def edit_article(article):

    if not OLLAMA_AVAILABLE:
        logging.warning("ollama package not installed; using fallback editor.")
        return _fallback_edit_article(article)

    try:
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

    except OllamaConnectionError as e:
        logging.warning("Failed to connect to Ollama editor: %s. Using fallback editor.", e)
        return _fallback_edit_article(article)
    except Exception as e:
        logging.exception("Unexpected error while calling Ollama editor; using fallback. %s", e)
        return _fallback_edit_article(article)


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
