import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "5164001184"

def send_test():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": "✅ Test message from GitHub Actions"
    })
    print(r.text)

if name == "__main__":
    print("Bot started")
    send_test()
