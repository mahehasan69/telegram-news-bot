# Systemic News — Telegram News Bot

A lightweight news-aggregation bot that picks the day's biggest story from RSS feeds, deep-dives across additional articles, extracts verified facts, generates a structured article via a model, posts to a Telegram channel and stores a local history database synchronized to a GitHub repo.

Key ideas:
- Aggregates RSS headlines, groups similar headlines, and selects the topic appearing across the most sources.
- Gathers many articles for deeper research and extracts verified facts and a timeline.
- Uses a model to generate a 5-part structured news post.
- Posts the result to a Telegram channel and saves the article to a local SQLite database which can be pushed to a dedicated GitHub repository.

## Highlights / Features
- Multiple RSS sources pre-configured (BBC, Reuters, CNN, AP, Al Jazeera, NYTimes).
- Deep-dive collection of article text, fact extraction, timeline building.
- Image fetching and automated news-card creation.
- Telegram posting (channel bot) with HTML formatting and optional image/card.
- Local SQLite DB for posted articles; DB repo is cloned and pushed back after updates (keeps posted history in a GitHub repo).
- Configurable list of politicians to look for reactions and other tuning parameters.

## Stack
- Language: Python (100%)
- Runtime: CPython 3.8+
- Notable libraries: feedparser, trafilatura, requests, beautifulsoup4, Pillow, groq (client)

## Quickstart — install and run
1. Clone the repo
   ```bash
   git clone https://github.com/<you>/telegram-news-bot.git
   cd telegram-news-bot/bot
   ```

2. Create a virtualenv and install requirements
   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set required environment variables (see next section) and run
   ```bash
   python3 main.py
   ```

If everything is configured correctly the bot will fetch headlines, generate the article, post to Telegram, publish to website (if configured), and save the record into the database repository.

## Required environment variables
Set these before running the bot (export / set in your environment or use a .env helper).

- TELEGRAM_BOT_TOKEN — bot token from @BotFather (required)
- TELEGRAM_CHANNEL_ID — the channel identifier (public username like @channel or private numeric id like -1001234567890) (required)
- GROQ_API_KEY — API key used by the groq client (required by config.py)
  - GROQ_MODEL is set in code to `llama-3.3-70b-versatile` (see config.py). The code also supports the `AI_MODEL` environment variable as a backwards-compatible alias if you want to override the default model.
- DB_REPO — GitHub repository to store the SQLite database (example: username/database-repo or full HTTPS URL) (required)
- DB_TOKEN — GitHub personal access token (used to authenticate pushing the DB repository) (required)

Security note: Do not commit secrets to git. Use environment variables or a secrets manager.

Example (Linux/macOS):
```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-..."
export TELEGRAM_CHANNEL_ID="@your_channel_or_-100id"
export GROQ_API_KEY="sk-..."
export DB_REPO="youruser/your-db-repo"
export DB_TOKEN="ghp_..."
```

## Configuration options (in bot/config.py)
- RSS_FEEDS — dictionary of feed name → RSS URL. Add or remove sources here.
- POLITICIANS — list of names to search for reactions.
- TOP_CANDIDATES_PER_FEED — how many top headlines per feed to consider.
- DEEP_DIVE_ARTICLE_LIMIT — number of articles to fetch for the deep dive.
- POLITICIAN_REACTION_LIMIT — limit to reactions per politician.
- STATE_FILE — file used to track already-posted topics (prevents repeats).

Edit config.py to fine-tune feeds, model name, or the people you track.

## How it works (runtime flow)
Main control loop (main.py):
1. Connects to the database manager (which clones your DB repo locally).
2. Fetches top headline candidates from configured RSS feeds (sources.fetch_top_candidates).
3. Groups similar headlines and picks the top new story (sources.pick_top_story).
4. Selects the best candidate article and attempts to fetch an image (image_fetcher).
5. Performs a deep-dive: gathers many articles (sources.gather_deep_dive_texts).
6. Extracts verified facts and a timeline (fact_extractor.build_fact_sheet).
7. Uses the summarizer to build the 5-part article (summarizer.build_report).
8. Validates the AI-generated article (main.is_valid_article).
9. Creates a news card (news_card.create_news_card) if an image exists.
10. Posts to Telegram (telegram_poster.post_to_channel).
11. Publishes to website (website_manager.publish_article) — optional depending on your setup.
12. Saves the article to a local SQLite DB and pushes the DB repo to GitHub (db_manager -> github_storage).

## Files of interest
- main.py — entrypoint / orchestrator
- config.py — central configuration (feeds, model, limits)
- sources.py — fetch headlines and deep-dive article collection
- summarizer.py — constructs the article from facts
- fact_extractor.py — builds verified facts & timeline from articles
- image_fetcher.py — finds and downloads article images
- news_card.py — composes an image card for the story
- telegram_poster.py — posts to Telegram channels
- database.py — SQLite schema & helpers
- db_manager.py — clones/pushes DB repo and wraps database operations
- github_storage.py — cloning and pushing the DB repo (requires DB_REPO and DB_TOKEN)
- requirements.txt — python dependencies

## Scheduling / Cron example
Run the bot periodically using cron. Example to post five times/day:
```cron
# run at 07:00, 10:00, 14:00, 18:00, 22:00
0 7,10,14,18,22 * * * cd /full/path/to/telegram-news-bot/bot && /full/path/to/venv/bin/python3 main.py >> run.log 2>&1
```

Windows: use Task Scheduler to run main.py at the desired times.

## Database handling
- The bot expects a separate GitHub repository (DB_REPO) to store the SQLite DB file.
- At startup db_manager.clone_database_repo clones the DB repo into a temporary directory.
- After saving an article the bot commits and pushes changes back to the DB repo using the DB_TOKEN.
- Ensure DB_TOKEN has repo push permissions. Do not store DB_TOKEN in the repo.

## Logging & troubleshooting
- The bot prints progress & errors to stdout — check the run.log when running via cron.
- Common failure points:
  - Missing environment variables → the program raises an error early (see config.py and github_storage.py).
  - Article fetch / scraping may fail (site blocks, network issues) → the bot falls back to RSS summaries in many places and logs the error.
  - AI model / API errors: ensure GROQ_API_KEY is valid and the model name is supported by your account.
  - Git errors when pushing DB: confirm DB_REPO and DB_TOKEN, and that the token has appropriate rights.

## Safety & validation
- The bot runs a validation check on generated articles (main.is_valid_article) to reduce obviously bad AI outputs (length check and filters for known "template" or assistant-like phrases).
- Despite validation, always inspect first posts and tune the model/config before wide distribution.

## Development notes
- To debug locally, run `python3 main.py` and watch stdout.
- Use the code in `sources.py`, `fact_extractor.py`, and `summarizer.py` to change how research and summarization are done.
- If you want to replace the remote model with a different provider, adjust `summarizer.py` and `config.py` and add any required SDKs. The code is structured so the summarizer is the main change point for model/provider swaps.

## Dependencies
See `requirements.txt` (top items):
- feedparser
- trafilatura
- requests
- beautifulsoup4
- Pillow
- groq

Install with:
```bash
pip install -r requirements.txt
```

## Tests
No automated tests are included. For manual testing:
- Run main.py locally with verbose logs.
- Check the DB via the cloned DB repo, and verify a successful commit appears after a posted article.

## Contributing
- Open issues and PRs on the repo.
- When modifying model or posting logic, add clear instructions for configuring keys/tokens.

## License
No license file detected in the repository. Add a LICENSE file (MIT, Apache-2.0, etc.) if you want to allow reuse.

## FAQ / common requests
- How do I track more sources? — Add entries to RSS_FEEDS in config.py.
- How do I stop duplicates? — The bot computes a content hash and uses the DB to detect duplicates; tune thresholds in config.py or the DB logic.
- How do I change post formatting? — Edit the `full_post` format in `main.py` before it is handed to `telegram_poster`.

---

If you want, I can:
- Create and commit this README.md to the repository for you (I will need the target repo/branch confirmation), or
- Produce a shorter README tailored for the GitHub project front page (summary + install only).
