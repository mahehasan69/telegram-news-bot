import requests
import config

API_URL = "https://api.groq.com/openai/v1/chat/completions"


def build_report(topic_title, media_texts, politician_reactions):

    media = ""

    for item in media_texts[:8]:
        media += f"""
Title: {item["title"]}

{item["text"]}

--------------------------------
"""

    politicians = ""

    for item in politician_reactions[:10]:
        politicians += f"""
{item["person"]}

{item["title"]}

{item["text"]}

--------------------------------
"""

    prompt = f"""
Today's biggest news:

{topic_title}

MEDIA ARTICLES

{media}

POLITICIAN REACTIONS

{politicians}

Write a professional Telegram post.

Use EXACTLY this structure.

1️⃣ WHAT HAPPENED

2️⃣ HOW THE MEDIA IS COVERING IT

3️⃣ WHAT POLITICIANS ARE SAYING

4️⃣ WHAT PROBLEMS THE WORLD MAY FACE

5️⃣ MY TAKE

Rules

- Professional English
- Under 350 words
- No fake information
- Use only the provided information
"""

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an experienced world news editor.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.4,
            "max_tokens": 900,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]
