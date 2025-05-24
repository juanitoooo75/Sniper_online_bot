import os
import requests
from dotenv import load_dotenv

# Chargement des variables Telegram depuis le .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("📲 Message envoyé sur Telegram.")
        else:
            print(f"⚠️ Erreur envoi Telegram : {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception Telegram : {e}")
