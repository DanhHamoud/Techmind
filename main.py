import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta

# ====== ENV ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RUN_MAIN = os.environ.get("RUN_MAIN", "true")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

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

# ====== TELEGRAM ======
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

def get_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url, timeout=15)
    return r.json().get("result", [])

# ====== HELPERS ======
def is_tech_content(text):
    text = text.lower()
    return any(word in text for word in TECH_KEYWORDS)

def light_summary(text, max_sentences=2):
    text = re.sub("<.*?>", "", text)
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:max_sentences])

# ====== CORE ======
def check_feeds(chat_id):
    sent_count = 0

    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = entry.title
            summary = entry.get("summary", "")
            link = entry.link

            published = entry.get("published_parsed")
            if published:
                published_time = datetime(*published[:6], tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - published_time > timedelta(hours=24):
                    continue

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
            sent_count += 1

    if sent_count == 0:
        send_telegram(chat_id, "ℹ️ لا توجد أخبار تقنية جديدة حاليًا.")

# ====== COMMANDS ======
def handle_commands():
    updates = get_updates()

    for update in updates:
        if "message" not in update:
            continue

        text = update["message"].get("text", "")
        chat_id = update["message"]["chat"]["id"]

        if text == "/start":
            send_telegram(chat_id, "🚀 تم تشغيل البوت، جاري جلب أحدث الأخبار التقنية...")
            check_feeds(chat_id)

# ====== ENTRY POINT ======
if RUN_MAIN.lower() == "true":
    print("🚀 Bot running")
    handle_commands()
