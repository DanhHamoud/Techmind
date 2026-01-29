import os
import json
import re
import requests
import feedparser

# ====== ENV ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID not set")

SENT_FILE = "sent_links.json"

# ====== FEEDS ======
ARABIC_TECH_FEEDS = [
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/wd/feed/",
    "https://www.arageek.com/feed",
    "https://www.unlimit-tech.com/feed",
]

GENERAL_ARABIC_FEEDS = [
    "https://www.aljazeera.net/aljazeerarss",
    "https://www.alarabiya.net/rss",
    "https://feeds.bbci.co.uk/arabic/rss.xml",
]

GLOBAL_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
]

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

TECH_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "cyber", "security", "software",
    "programming", "data", "robot", "cloud",
    "الذكاء الاصطناعي", "تقنية", "تكنولوجيا",
    "برمجة", "الأمن السيبراني", "البيانات",
    "التحول الرقمي", "روبوت",
]

# ====== STORAGE ======
def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent(data):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)

# ====== HELPERS ======
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
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

def summary(text):
    text = clean_text(text)
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:2])

# ====== CORE ======
def check_feeds():
    sent = load_sent()
    updated = False

    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:8]:
            link = entry.get("link")
            if not link or link in sent:
                continue

            title = entry.get("title", "")
            content = title + " " + entry.get("summary", "")

            if not is_tech_content(content):
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
                f"📝 Summary:\n{summary(entry.get('summary',''))}\n\n"
                f"🔗 {link}"
            )

            send_telegram(message)
            sent.add(link)
            updated = True

    if updated:
        save_sent(sent)

# ====== ENTRY POINT ======
if name == "__main__":
    print("🚀 Bot started")
    check_feeds()
