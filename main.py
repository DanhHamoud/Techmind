import feedparser
import time
import requests
import json
import re
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "5164001184"

NEWS_FEEDS = [
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/feed/",
    "https://apps-news.com/feed/",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss"
]

RESEARCH_FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",
    "http://export.arxiv.org/rss/cs.LG",
    "http://export.arxiv.org/rss/cs.CR",
    "http://export.arxiv.org/rss/cs.SE",
    "http://export.arxiv.org/rss/cs.CV"
]

ALL_FEEDS = NEWS_FEEDS + RESEARCH_FEEDS

TECH_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "neural", "robot", "automation",
    "cloud", "cyber", "data", "software"
]

CHECK_INTERVAL = 3600
SENT_FILE = "sent_items.json"

# تحميل الروابط المرسلة
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent_links = set(json.load(f))
else:
    sent_links = set()

def save_sent():
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_links), f, ensure_ascii=False)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    })

def is_tech_content(text):
    text = text.lower()
    return any(word in text for word in TECH_KEYWORDS)

def light_summary(text, max_sentences=2):
    text = re.sub("<.*?>", "", text)
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:max_sentences])

def check_feeds():
    for feed_url in ALL_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            link = entry.link
            title = entry.title
            summary = entry.get("summary", "")

            if link in sent_links:
                continue

            text = title + " " + summary

            if is_tech_content(text):
                tag = "🔬 Research" if "arxiv.org" in link else "🧠 Tech News"
                short_summary = light_summary(summary)

                message = (
                    f"{tag}\n\n"
                    f"{title}\n\n"
                    f"📝 Summary:\n{short_summary}\n\n"
                    f"🔗 {link}"
                )

                send_telegram(message)
                sent_links.add(link)
                save_sent()

print("🤖 Bot started")
send_telegram("✅ Bot is running")

while True:
    check_feeds()
    time.sleep(CHECK_INTERVAL)
