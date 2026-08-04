import os

# ---------------- TELEGRAM ----------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "TELEGRAM_CHANNEL_ID")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. Please set it as an environment variable."
    )

# ---------------- GROQ ----------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Please set it as an environment variable."
    )

# Best free model
GROQ_MODEL = "llama-3.3-70b-versatile"
