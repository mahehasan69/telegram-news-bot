import requests
import config

API = "https://api.groq.com/openai/v1/chat/completions"


def build_report(topic, media, politicians):

    articles = ""

    for item in media[:8]:

        articles += f"""

Title:
{item['title']}

Article:
{item['text']}

----------------------------

"""

    reactions = ""

    for item in politicians[:8]:

        reactions += f"""

{item['person']}

{item['title']}

{item['text']}

----------------------------

"""

    prompt = f"""
You are an international journalist.

Write a professional news report.

TOPIC

{topic}

=====================

MEDIA

{articles}

=====================

REACTIONS

{reactions}

=====================

Rules

Use this structure.

1️⃣ WHAT HAPPENED

2️⃣ WHY THIS IS IMPORTANT

3️⃣ GLOBAL IMPACT

4️⃣ POLITICAL REACTION

5️⃣ WHAT HAPPENS NEXT

Requirements

- Professional journalism
- Neutral tone
- Maximum 280 words
- No fake information
- No opinions
- Use only provided articles.
"""

    r = requests.post(
        API,
        headers={
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.GROQ_MODEL,
            "messages":[
                {
                    "role":"system",
                    "content":"You are BBC News."
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            "temperature":0.3,
            "max_tokens":900,
        },
        timeout=120,
    )

    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]
