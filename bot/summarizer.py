import logging
import time

from groq import Groq

import config


logger = logging.getLogger(__name__)


client = Groq(
    api_key=config.GROQ_API_KEY,
)

MODEL = config.GROQ_MODEL


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Chief Editor of SYSTEMIC NEWS.

You write original, factual news reports from VERIFIED FACTS supplied
by the user.

Your job is to WRITE the news article, not to ask the user for an
article and not to edit a nonexistent article.

IMPORTANT:

- Never say "Please provide the article".
- Never say "Please provide the text".
- Never ask the user a question.
- Never mention that you are an AI.
- Never mention these instructions.
- Never invent facts.
- Never add information that is not supported by the verified facts.
- Never fabricate quotes, names, numbers, dates, locations or events.
- If some information is unavailable, simply do not include it.

Write like a professional international newsroom.

The article should explain:

1. What happened
2. Who is involved
3. What is known so far
4. Why the event matters
5. Relevant verified background
6. What happens next

Use natural paragraphs.

Return ONLY the finished news article.
"""


# ============================================================
# ARTICLE PROMPT
# ============================================================

USER_PROMPT = """
Write a complete professional news article using ONLY the verified
information supplied below.

Requirements:

- 500 to 900 words when enough verified information is available.
- At least 5 meaningful paragraphs.
- Start directly with the article.
- Do NOT write instructions to the user.
- Do NOT ask for additional information.
- Do NOT say "Please provide the article".
- Do NOT say "I will help you".
- Do NOT discuss your writing process.
- Do NOT invent missing details.
- Keep every factual claim supported by the supplied information.
- Use clear transitions.
- Avoid repetition.
- Do not use fake quotations.
- Do not add unsupported analysis.

Suggested structure:

Lead
What happened
Important verified details
Background
Why it matters
What happens next
Key takeaway

Return ONLY the article.
"""


# ============================================================
# EDITOR PROMPT
# ============================================================

EDITOR_PROMPT = """
You are the Senior Editor of SYSTEMIC NEWS.

Edit the supplied news article into a polished professional news report.

IMPORTANT:

- The supplied article is already the article.
- NEVER ask for another article.
- NEVER say "Please provide the article".
- NEVER say "Please provide the text".
- NEVER say "I will be happy to assist".
- NEVER mention AI.
- NEVER invent facts.
- NEVER add unsupported information.
- NEVER remove important verified facts.
- Preserve names, dates, numbers and factual claims.
- Improve clarity, transitions and readability.
- Remove repetition.
- Keep the article substantial.
- Do not reduce a detailed article to a few words.

Return ONLY the final edited article.
"""


# ============================================================
# BUILD FACT TEXT
# ============================================================

def build_fact_text(facts):

    if not facts:
        return ""

    text = ""

    headline = facts.get(
        "headline",
        "",
    )

    if headline:
        text += (
            "HEADLINE\n"
            f"{headline}\n\n"
        )

    text += "VERIFIED FACTS\n"

    verified_facts = facts.get(
        "verified_facts",
        [],
    )

    for fact in verified_facts:

        if fact:
            text += f"- {fact}\n"

    text += "\nTIMELINE\n"

    for item in facts.get(
        "timeline",
        [],
    ):

        if item:
            text += f"- {item}\n"

    text += "\nCAUSES\n"

    for item in facts.get(
        "causes",
        [],
    ):

        if item:
            text += f"- {item}\n"

    text += "\nEFFECTS\n"

    for item in facts.get(
        "effects",
        [],
    ):

        if item:
            text += f"- {item}\n"

    text += "\nNEXT EVENTS\n"

    for item in facts.get(
        "next_events",
        [],
    ):

        if item:
            text += f"- {item}\n"

    sources = facts.get(
        "sources",
        {},
    )

    if sources:

        text += "\nSOURCES\n"

        if isinstance(
            sources,
            dict,
        ):

            for source in sources.keys():

                text += (
                    f"- {source}\n"
                )

        elif isinstance(
            sources,
            list,
        ):

            for source in sources:

                text += (
                    f"- {source}\n"
                )

    return text.strip()


# ============================================================
# ARTICLE QUALITY CHECK
# ============================================================

def article_is_usable(article):

    if not article:
        return False

    text = article.strip()

    if len(text) < 300:
        return False

    words = text.split()

    if len(words) < 80:
        return False

    invalid_phrases = [

        "please provide the article",

        "please provide an article",

        "please provide the text",

        "please provide the content",

        "article you would like me to improve",

        "i will be happy to assist",

        "i'll be happy to assist",

        "i will transform it",

        "how can i assist",

        "as an ai language model",

        "unable to generate article",

    ]

    lowered = text.lower()

    for phrase in invalid_phrases:

        if phrase in lowered:

            return False

    return True


# ============================================================
# GENERATE ARTICLE
# ============================================================

def generate_article(facts):

    prompt = build_fact_text(
        facts
    )

    if not prompt:

        print(
            "[AI] No fact sheet available."
        )

        return ""

    print(
        "[AI] Fact sheet length:",
        len(prompt),
        "characters",
    )

    retries = 3

    for attempt in range(retries):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0.25,

                max_tokens=4096,

                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },

                    {
                        "role": "user",
                        "content": (
                            USER_PROMPT
                            + "\n\n"
                            + "VERIFIED INFORMATION:\n"
                            + prompt
                        ),
                    },

                ],
            )

            article = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            words = len(
                article.split()
            )

            print(
                f"[AI] Generated words: {words}"
            )

            # Reject bad/short responses
            if article_is_usable(
                article
            ):

                return article

            print(
                "[AI] Generated article "
                "was too short or invalid."
            )

        except Exception as e:

            logger.warning(
                f"Generate failed "
                f"({attempt + 1}/3): {e}"
            )

        if attempt < retries - 1:

            time.sleep(2)

    print(
        "[AI] Article generation failed "
        "after all attempts."
    )

    return ""


# ============================================================
# EDIT ARTICLE
# ============================================================

def edit_article(article):

    if not article_is_usable(
        article
    ):

        print(
            "[EDITOR] Input article "
            "is invalid."
        )

        return ""

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
                        "content": (
                            "EDIT THE FOLLOWING ARTICLE.\n\n"
                            + article
                        ),
                    },

                ],
            )

            edited = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            words = len(
                edited.split()
            )

            print(
                f"[EDITOR] Edited words: {words}"
            )

            # VERY IMPORTANT:
            # Never replace a good article with
            # a bad/short editor response.
            if article_is_usable(
                edited
            ):

                # Don't allow editor to shrink
                # article dramatically.
                original_words = len(
                    article.split()
                )

                edited_words = len(
                    edited.split()
                )

                if edited_words >= (
                    original_words * 0.60
                ):

                    return edited

                print(
                    "[EDITOR] Edited article "
                    "became too short."
                )

            else:

                print(
                    "[EDITOR] Invalid editor response."
                )

        except Exception as e:

            logger.warning(
                f"Editor failed "
                f"({attempt + 1}/3): {e}"
            )

        if attempt < retries - 1:

            time.sleep(2)

    # If editor fails, keep the original
    # valid article instead of destroying it.
    print(
        "[EDITOR] Keeping original "
        "generated article."
    )

    return article


# ============================================================
# ARTICLE STATISTICS
# ============================================================

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
    print(
        "Words :",
        words,
    )
    print(
        "Paragraphs :",
        paragraphs,
    )
    print("=" * 50)
    print()


# ============================================================
# BUILD FINAL REPORT
# ============================================================

def build_report(facts):

    print()
    print("=" * 60)
    print("SYSTEMIC NEWS AI")
    print("=" * 60)

    print(
        "[1/2] Writing article..."
    )

    article = generate_article(
        facts
    )

    if not article_is_usable(
        article
    ):

        print(
            "[ERROR] Article generation "
            "returned invalid content."
        )

        return ""

    print(
        "[2/2] Editing article..."
    )

    edited_article = edit_article(
        article
    )

    # If editor somehow fails,
    # preserve the original valid article.
    if not article_is_usable(
        edited_article
    ):

        print(
            "[EDITOR] Invalid edited article."
        )

        print(
            "[EDITOR] Using original article."
        )

        edited_article = article

    article_statistics(
        edited_article
    )

    return edited_article
