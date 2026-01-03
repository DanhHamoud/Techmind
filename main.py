import os
import json
import re
import time
import requests
import feedparser
from datetime import datetime, timezone

# ====== ENV ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RUN_MAIN = os.environ.get("RUN_MAIN") == "true"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

STATE_FILE = "state.json"

# ====== FEEDS ======
NEWS_FEEDS = [
    "https://aitnews.com/feed/",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
]

RESEARCH_FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",
    "http://export.arxiv.org/rss/cs.LG",
]

ALL_FEEDS = NEWS_FEEDS + RESEARCH_FEEDS

TECH_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "cyber", "security", "software",
    "programming", "data", "robot", "cloud"
]

# ====== STATE ======
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_run": 0}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

# ====== HELPERS ======
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=10
    )

def is_tech_content(text):
    text = text.lower()
    return any(word in text for word in TECH_KEYWORDS)

def light_summary(text, max_sentences=2):
    text = re.sub("<.*?>", "", text)
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:max_sentences])

def entry_time(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return int(time.mktime(entry.published_parsed))
    return int(time.time())

# ====== CORE ======
def check_feeds(chat_id):
    state = load_state()
    last_run = state["last_run"]
    newest_time = last_run

    sent_any = False

    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            published_time = entry_time(entry)

            if published_time <= last_run:
                continue

            title = entry.title
            summary = entry.get("summary", "")
            link = entry.link

            if not is_tech_content(title + " " + summary):
                continue

            tag = "🔬 Research" if "arxiv.org" in link else "🧠 Tech News"
            message = (
                f"{tag}\n\n"
                f"{title}\n\n"
                f"📝 Summary:\n{light_summary(summary)}\n\n"
                f"🔗 {link}"
            )

            send_telegram(chat_id, message)
            sent_any = True

            if published_time > newest_time:
                newest_time = published_time

    if sent_any:
        save_state({"last_run": newest_time})

# ====== TELEGRAM LISTENER ======
def listen_updates():
    offset = None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    r = requests.get(url, timeout=20)
    data = r.json()

    if not data["result"]:
        return

    update = data["result"][-1]
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        check_feeds(chat_id)

# ====== ENTRY POINT ======
if RUN_MAIN:
    listen_updates()
