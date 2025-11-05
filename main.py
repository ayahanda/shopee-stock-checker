from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
import os

# === CONFIG ===
PRODUCT_URL = "https://shopee.com.my/product/724335/2212828002"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 300  # 5 minit

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Shopee Stock Checker is running on Render!"

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(PRODUCT_URL, headers=headers, timeout=15)
        if r.status_code != 200:
            print("❗ Gagal akses Shopee:", r.status_code)
            return None
    except Exception as e:
        print("⚠️ Ralat sambungan:", e)
        return None

    if "sold out" in r.text.lower() or "habis dijual" in r.text.lower():
        print("❌ Masih tiada stok.")
        return False
    else:
        print("✅ Ada stok! Hantar Telegram...")
        return True

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
        print("📩 Notifikasi Telegram dihantar.")
    except Exception as e:
        print("Ralat Telegram:", e)

def stock_checker_loop():
    notified = False
    while True:
        status = check_stock()
        if status and not notified:
            send_telegram(f"🚨 Barang Shopee dah ada stok!\n👉 <a href='{PRODUCT_URL}'>Klik sini untuk beli</a>")
            notified = True
        elif status is False:
            notified = False
        print("⏳ Tunggu 5 minit untuk semakan seterusnya...\n")
        time.sleep(CHECK_INTERVAL)

def run_background():
    t = Thread(target=stock_checker_loop)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    run_background()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
