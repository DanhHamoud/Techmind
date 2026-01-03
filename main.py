import os
import json
import re
import requests
import feedparser

# ====== ENV ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID not set in environment variables")

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

SENT_FILE = "sent_items.json"

TECH_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "cyber", "security", "software",
    "programming", "data", "robot", "cloud"
]

# ====== HELPERS ======
def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_sent(sent_links):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_links), f, ensure_ascii=False)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=10,
    )
    response.raise_for_status()


def is_tech_content(text):
    text = text.lower()
    return any(word in text for word in TECH_KEYWORDS)


def light_summary(text, max_sentences=2):
    text = re.sub("<.*?>", "", text)
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:max_sentences])


# ====== CORE ======
def check_feeds():
    sent_links = load_sent()

    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            link = entry.link
            title = entry.title
            summary = entry.get("summary", "")

            if link in sent_links:
                continue

            if is_tech_content(title + " " + summary):
                tag = "🔬 Research" if "arxiv.org" in link else "🧠 Tech News"
                message = (
                    f"{tag}\n\n"
                    f"{title}\n\n"
                    f"📝 Summary:\n{light_summary(summary)}\n\n"
                    f"🔗 {link}"
                )

                send_telegram(message)
                sent_links.add(link)
                save_sent(sent_links)


# ====== ENTRY POINT ======
if __name__ == "__main__":  
    print("🚀 Bot started")  
    check_feeds()
    # تصحيح الخطأ: استدعاء الدالة بشكل صحيح  # ✅ الآن تعليق
    send_telegram("✅ Bot test run successfully")
