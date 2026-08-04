import os

# ---------------- TELEGRAM ----------------
TELEGRAM_BOT_TOKEN = os.environ.get("8866845152:AAHD7nVTuvtV7v49Vrn-k4F_4DOrvt16uRs")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@SYSTEMICNEWS")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. Please set it as an environment variable."
    )

# ---------------- GROQ ----------------
GROQ_API_KEY = os.environ.get("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")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Please set it as an environment variable."
    )

# Best free model
GROQ_MODEL = "llama-3.3-70b-versatile"