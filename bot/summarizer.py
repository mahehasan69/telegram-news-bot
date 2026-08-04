import requests
import config

API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _generate(prompt):

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.GROQ_MODEL,
        "temperature": 0.4,
        "max_tokens": 900,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional news editor writing for a Telegram news channel.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


def build_report(topic_title, media_texts, politician_reactions):

    media_block = "\n\n".join(
        f"[{m['source']}] {m['title']}\n{m['text'][:800]}"
        for m in media_texts[:8]
    )

    if not media_block:
        media_block = "No detailed articles found."

    politician_block = "\n\n".join(
        f"{p['person']}: {p['title']} - {p['text'][:400]}"
        for p in politician_reactions[:10]
    )

    if not politician_block:
        politician_block = "No politician reactions found."

    prompt = f"""
Today's biggest story:

{topic_title}

MEDIA REPORTS

{media_block}

POLITICIAN REACTIONS

{politician_block}

Write a Telegram news report using EXACTLY this structure.

1️⃣ WHAT HAPPENED

2️⃣ HOW THE MEDIA IS COVERING IT

3️⃣ WHAT POLITICIANS ARE SAYING

4️⃣ WHAT PROBLEMS THE WORLD MAY FACE

5️⃣ MY TAKE

Rules:

• factual

• concise

• under 350 words

• no hallucinations

• professional English
"""

    return _generate(prompt)