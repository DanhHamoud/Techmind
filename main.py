import os
import json
import re
import time
import requests
import feedparser

# ====== ENV ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RUN_MAIN = os.environ.get("RUN_MAIN") == "true"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

STATE_FILE = "state.json"

# ====== FEEDS ======

# 📰 مواقع تقنية عربية
ARABIC_TECH_FEEDS = [
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/wd/feed/",
    "https://www.arageek.com/feed",
    "https://www.unlimit-tech.com/feed",
]

# 📰 مواقع أخبار عامة (نفلتر منها التقنية فقط)
GENERAL_ARABIC_FEEDS = [
    "https://www.aljazeera.net/aljazeerarss",   # الجزيرة
    "https://www.alarabiya.net/rss",            # العربية
    "https://feeds.bbci.co.uk/arabic/rss.xml",  # BBC عربي
]

# 🌍 مواقع تقنية عالمية
GLOBAL_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
]

# 🔬 أبحاث
RESEARCH_FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",
    "http://export.arxiv.org/rss/cs.LG",
]

ALL_FEEDS = (
    ARABIC_TECH_FEEDS
    + GENERAL_ARABIC_FEEDS
    + GLOBAL_FEEDS
    + RESEARCH_FEEDS
)

# ====== KEYWORDS ======
TECH_KEYWORDS = [
    # English
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "cyber", "security", "software",
    "programming", "data", "robot", "cloud",

    # Arabic
    "الذكاء الاصطناعي", "تقنية", "تكنولوجيا",
    "برمجة", "الأمن السيبراني", "البيانات",
    "الحوسبة", "التحول الرقمي", "روبوت",
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

def clean_text(text):
    return re.sub("<.*?>", "", text)

def light_summary(text, max_sentences=2):
    text = clean_text(text)
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

    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:6]:
            published_time = entry_time(entry)

            if published_time <= last_run:
                continue

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            if not is_tech_content(title + " " + summary):
                continue

            if "arxiv.org" in link:
                tag = "🔬 Research"
            elif feed_url in GENERAL_ARABIC_FEEDS:
                tag = "📰 General Tech"
            elif feed_url in ARABIC_TECH_FEEDS:
                tag = "📰 Arabic Tech"
            else:
                tag = "🌍 Global Tech"

            message = (
                f"{tag}\n\n"
                f"{title}\n\n"
                f"📝 Summary:\n{light_summary(summary)}\n\n"
                f"🔗 {link}"
            )

            send_telegram(chat_id, message)

            if published_time > newest_time:
                newest_time = published_time

    if newest_time > last_run:
        save_state({"last_run": newest_time})

# ====== TELEGRAM LISTENER ======
def listen_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url, timeout=20)
    data = r.json()

    if not data.get("result"):
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
