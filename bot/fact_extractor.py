import json
import logging
import re
import time

from groq import Groq

import config

logger = logging.getLogger(__name__)

client = Groq(
    api_key=config.GROQ_API_KEY,
)

MODEL = config.GROQ_MODEL

SYSTEM_PROMPT = """
You are SYSTEMIC NEWS FACT ENGINE.

You are NOT a news writer.

You are an investigative journalist.

Your job is to discover truth.

Rules:

• Never invent facts.
• Ignore opinions.
• Ignore speculation.
• Ignore clickbait.
• Preserve numbers.
• Preserve names.
• Preserve dates.
• Preserve locations.
• If sources disagree,
  record the disagreement.

Return ONLY JSON.
"""

USER_PROMPT = """
Study every article.

Investigate.

Do NOT summarize.

Return ONLY JSON.

Schema:

headline

verified_facts

unknown_facts

conflicting_reports

timeline

people

organizations

locations

countries

numbers

quotes

causes

effects

next_events

confidence
"""

OUTPUT_SCHEMA = {

    "headline": "",

    "verified_facts": [],

    "unknown_facts": [],

    "conflicting_reports": [],

    "timeline": [],

    "people": [],

    "organizations": [],

    "locations": [],

    "countries": [],

    "numbers": [],

    "quotes": [],

    "causes": [],

    "effects": [],

    "next_events": [],

    "confidence": 0,

}
def validate_articles(articles):

    cleaned = []

    for article in articles:

        cleaned.append({

            "title": article.get("title",""),

            "text": article.get("text",""),

            "source": article.get("source","Unknown"),

            "score": article.get("score",50),

        })

    return cleaned


def build_context(articles):

    context = ""

    for i, article in enumerate(articles,1):

        context += f"""

ARTICLE {i}

SOURCE:
{article["source"]}

TITLE:
{article["title"]}

TEXT:
{article["text"]}

-------------------------------------

"""

    return context


def source_agreement(articles):

    result = {}

    for article in articles:

        src = article["source"]

        result[src] = result.get(src,0)+1

    return result


def trusted_sources(articles):

    return [

        a

        for a in articles

        if a["score"]>=95

    ]


def estimate_confidence(articles):

    if not articles:

        return 0

    trusted=len(

        trusted_sources(articles)

    )

    avg=sum(

        a["score"]

        for a in articles

    )/len(articles)

    confidence=min(

        100,

        int(

            40+

            trusted*8+

            avg*0.2

        )

    )

    return confidence
    def extract_facts(articles):

    articles = validate_articles(
        articles
    )

    context = build_context(
        articles
    )

    retries = 3

    for attempt in range(retries):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0.15,

                max_tokens=4096,

                response_format={
                    "type": "json_object"
                },

                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },

                    {
                        "role": "user",
                        "content": USER_PROMPT
                        + "\n\n"
                        + context,
                    },

                ],

            )

            return response.choices[0].message.content

        except Exception as e:

            logger.warning(

                f"Groq Error ({attempt+1}/3): {e}"

            )

            time.sleep(2)

    return ""
    def parse_facts(text):

    if not text:

        return OUTPUT_SCHEMA.copy()

    text = text.strip()

    if text.startswith("```json"):

        text = text.replace(
            "```json",
            "",
        )

    text = text.replace(
        "```",
        "",
    )

    try:

        data = json.loads(text)

    except Exception:

        start = text.find("{")

        end = text.rfind("}")

        if start == -1 or end == -1:

            return OUTPUT_SCHEMA.copy()

        try:

            data = json.loads(
                text[start:end+1]
            )

        except Exception:

            return OUTPUT_SCHEMA.copy()

    result = OUTPUT_SCHEMA.copy()

    for key in result:

        if key in data:

            result[key] = data[key]

    return result
    def print_fact_statistics(facts):

    print()

    print("=" * 50)

    print("FACT EXTRACTION")

    print("=" * 50)

    print(
        "Verified :",
        len(
            facts["verified_facts"]
        ),
    )

    print(
        "Unknown :",
        len(
            facts["unknown_facts"]
        ),
    )

    print(
        "Conflicts :",
        len(
            facts["conflicting_reports"]
        ),
    )

    print(
        "Timeline :",
        len(
            facts["timeline"]
        ),
    )

    print(
        "Confidence :",
        facts["confidence"],
    )

    print("=" * 50)

    print()

def build_fact_sheet(articles):

    articles = validate_articles(
        articles
    )

    print()

    print("=" * 60)
    print("FACT EXTRACTION ENGINE")
    print("=" * 60)

    print(
        f"Reading {len(articles)} articles..."
    )

    raw = extract_facts(
        articles
    )

    facts = parse_facts(
        raw
    )

    facts["confidence"] = estimate_confidence(
        articles
    )

    facts["sources"] = source_agreement(
        articles
    )

    print_fact_statistics(
        facts
    )

    return facts
    if __name__ == "__main__":

    sample = [

        {

            "title": "Example News",

            "text": "Example article text.",

            "source": "BBC",

            "score": 99,

        }

    ]

    facts = build_fact_sheet(sample)

    print(

        json.dumps(

            facts,

            indent=2,

        )

    )
