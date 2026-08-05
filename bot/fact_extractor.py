import json
import ollama


SYSTEM_PROMPT = """
You are SYSTEMIC NEWS FACT ENGINE.

You are not a news writer.

You are an investigative journalist and fact checker.

Your only goal is to discover the truth.

Rules:

• Never invent facts.
• Never guess.
• Ignore opinions.
• Ignore speculation.
• Ignore clickbait.
• If multiple trusted sources agree, treat it as verified.
• If sources disagree, record the disagreement.
• If something is unknown, say it is unknown.
• Preserve dates, names, numbers and locations exactly.

Return ONLY valid JSON.
"""


def build_context(articles):

    context = ""

    for i, article in enumerate(articles, 1):

        context += f"""

ARTICLE {i}

SOURCE:
{article["source"]}

TITLE:
{article["title"]}

TEXT:
{article["text"]}

------------------------------------

"""

    return context

def source_agreement(articles):

    counts = {}

    for article in articles:

        source = article["source"]

        counts[source] = counts.get(source, 0) + 1

    return counts
def trusted_sources(articles):

    trusted = []

    for article in articles:

        if article["score"] >= 95:

            trusted.append(article)

    return trusted 
 def estimate_confidence(articles):

    if not articles:

        return 0

    trusted = len(
        trusted_sources(articles)
    )

    confidence = min(

        100,

        50 + trusted * 5,

    )

    return confidence

USER_PROMPT = """
Study every article carefully.

Do NOT summarize.

Investigate.

Return ONLY valid JSON with the following fields:

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

Rules:

- Every verified fact must be supported by multiple trusted sources.
- Never invent information.
- Never guess.
- If information is missing, put it in unknown_facts.
- Return ONLY JSON.
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
    "confidence": 0
}

 def extract_facts(articles):

    context = build_context(articles)

    response = ollama.chat(

        model="llama3.1",

        messages=[

            {

                "role": "system",

                "content": SYSTEM_PROMPT,

            },

            {

                "role": "user",

                "content": USER_PROMPT + context,

            },

        ],

    )

    return response["message"]["content"]

def parse_facts(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    text = text.replace("```", "")

    try:
        return json.loads(text)

    except Exception:
        return OUTPUT_SCHEMA.copy()
 def print_fact_statistics(facts):

    print()

    print("========== FACT SHEET ==========")

    print("Verified :", len(facts["verified_facts"]))
    print("Unknown  :", len(facts["unknown_facts"]))
    print("Conflicts:", len(facts["conflicting_reports"]))
    print("Timeline :", len(facts["timeline"]))
    print("Confidence:", facts["confidence"])

    print("===============================")

    print()       
def build_fact_sheet(articles):

    raw = extract_facts(articles)

    facts = parse_facts(raw)

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