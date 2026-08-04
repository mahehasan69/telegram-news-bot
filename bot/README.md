# Telegram News Bot (free, local AI, no API key)

Scrolls major news RSS feeds, finds today's biggest story (the one covered
by the most outlets), deep-dives it across many more outlets via Google
News search, checks what tracked politicians are saying, then uses a
small **local** AI model to write a 5-part structured post and publish it
to your Telegram channel.

## 1. Create your Telegram bot
1. Open Telegram, message **@BotFather**, send `/newbot`, follow the prompts.
2. Copy the token it gives you (looks like `123456:ABC-...`).
3. Create (or use) your channel, add the bot as an **administrator** of that channel.
4. Your channel ID is either `@your_channel_username` (if public) or a numeric
   id like `-1001234567890` (if private — you can get this by forwarding a
   channel message to `@JsonDumpBot` or similar).

## 2. Install dependencies
```bash
cd news_bot
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> The first run will download the local AI model (`Qwen2.5-1.5B-Instruct`,
> ~3GB). It's cached afterward — no repeated downloads, no API key, no cost.
> If your machine is slow/low on RAM, open `config.py` and change
> `MODEL_NAME` to `"Qwen/Qwen2.5-0.5B-Instruct"` (smaller & faster, a bit
> lower quality).

## 3. Configure
Open `config.py` and either edit directly, or set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-your-token"
export TELEGRAM_CHANNEL_ID="@your_channel_username"
```
You can also edit `RSS_FEEDS` and `POLITICIANS` in `config.py` to add/remove
sources or people to track.

## 4. Test it manually
```bash
python3 main.py
```
Watch the console output — it logs each step (fetching, deep-diving,
generating, posting). Check your channel for the post.

## 5. Schedule it to post 4-5 times a day (cron)
Run `crontab -e` and add a line like this (adjust paths):
```
0 7,10,14,18,22 * * * cd /full/path/to/news_bot && /full/path/to/news_bot/venv/bin/python3 main.py >> run.log 2>&1
```
This runs the bot at 07:00, 10:00, 14:00, 18:00, and 22:00 every day — 5 posts/day.
Each run picks whatever the biggest *new* story is (it won't repeat a topic
already posted that day, tracked in `posted_state.json`).

On Windows, use **Task Scheduler** instead: create 5 triggers at the times
above, action = "Start a program" → point to your `python.exe` and pass
`main.py` as the argument, with "Start in" set to the `news_bot` folder.

## How it decides what to post
- Pulls the top headlines from BBC, Reuters, Al Jazeera, AP, CNN, NYT (RSS).
- Groups similar headlines together — the topic showing up across the most
  feeds is treated as "today's biggest story."
- Searches Google News for that story's title to pull in many more articles
  from outlets beyond the core list, extracting full article text where possible.
- Searches for each tracked politician's name + the topic to find reactions.
- Feeds all of this to the local model with a strict 5-part template:
  1️⃣ What happened
  2️⃣ How the media is covering it
  3️⃣ What politicians are saying
  4️⃣ Problems the world may face
  5️⃣ The bot's own short opinion

## Notes / limitations
- This is a genuinely free, local setup — quality depends on the small
  model used. For noticeably better writing, you can later swap
  `summarizer.py` to call the Claude or OpenAI API instead (happy to add
  that version if you want it).
- Google News RSS and site scraping can occasionally fail or get blocked
  for certain outlets — the bot falls back to the RSS summary text when
  full-article extraction fails.
- Twitter/X statements aren't included directly (X's API isn't free
  anymore) — politician reactions are found via Google News instead, which
  usually covers major statements anyway.
