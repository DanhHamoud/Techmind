%%writefile main.py
!pip install feedparser requests
import feedparser
import time
import requests
import json
import re
BOT_TOKEN = "8525525248:AAFjH3Ec4mNTsUyQpupV4oBkBUlLMcniSYc"
CHAT_ID = "5164001184"

NEWS_FEEDS = [
    # عربي
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/feed/",
    "https://apps-news.com/feed/",

    # إنجليزي
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

CHECK_INTERVAL = 3600  # كل ساعة
SENT_FILE = "sent_items.json"
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    })

# ========= فلترة تقنية =========
def is_tech_content(text):
    text = text.lower()
    return any(word in text for word in TECH_KEYWORDS)

# ========= تلخيص خفيف =========
def light_summary(text, max_sentences=2):
    text = re.sub("<.*?>", "", text)  # إزالة HTML
    sentences = re.split(r'(?<=[.!؟])\s+', text)
    return " ".join(sentences[:max_sentences])
    def save_sent():
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_links), f, ensure_ascii=False)

# ========= فحص المحتوى =========
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

# ========= التشغيل =========
print("⏰ Checking tech news & research (ONE RUN)...")
check_feeds()
print("✅ Done")
send_telegram("✅ Bot is alive and sending messages!")
