from flask import Flask, request, render_template_string
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
import os

# === CONFIG ===
DEFAULT_PRODUCT_URL = "https://shopee.com.my/product/724335/2212828002"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 300  # 5 minit

# === VARIABLES ===
product_url = DEFAULT_PRODUCT_URL
last_checked = "Belum disemak"
stock_status = "⏳ Belum diketahui"

app = Flask(__name__)

# HTML TEMPLATE
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shopee Stock Checker</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f8fafc; color: #333; text-align: center; margin-top: 50px; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 400px; margin: auto; }
        h1 { color: #e85d04; }
        .status { font-size: 1.5em; margin: 15px 0; }
        form input { width: 80%; padding: 8px; border: 1px solid #ccc; border-radius: 5px; }
        form button { padding: 8px 12px; background: #0d6efd; color: white; border: none; border-radius: 5px; cursor: pointer; }
        form button:hover { background: #0b5ed7; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Shopee Stock Checker</h1>
        <p><strong>Current Product:</strong><br><a href="{{ product_url }}" target="_blank">{{ product_url }}</a></p>
        <p class="status"><strong>Status:</strong> {{ stock_status }}</p>
        <p><strong>Last Checked:</strong> {{ last_checked }}</p>
        <form method="POST">
            <input type="text" name="new_url" placeholder="Paste Shopee link baru" required>
            <button type="submit">Tukar Produk</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    global product_url
    if request.method == "POST":
        new_url = request.form.get("new_url")
        if "shopee.com" in new_url:
            product_url = new_url
            send_telegram(f"🔄 Produk baru ditetapkan:\n{product_url}")
        else:
            return "❌ URL bukan Shopee link!", 400
    return render_template_string(TEMPLATE, product_url=product_url, stock_status=stock_status, last_checked=last_checked)

def check_stock():
    global last_checked, stock_status
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(product_url, headers=headers, timeout=15)
        last_checked = time.strftime("%d/%m/%Y %H:%M:%S")
        if r.status_code != 200:
            stock_status = f"❗ Gagal akses Shopee ({r.status_code})"
            return None
    except Exception as e:
        stock_status = f"⚠️ Ralat sambungan: {e}"
        return None

    if "sold out" in r.text.lower() or "habis dijual" in r.text.lower():
        stock_status = "❌ Tiada stok"
        print(stock_status)
        return False
    else:
        stock_status = "✅ Ada stok!"
        print(stock_status)
        return True

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
        print("📩 Telegram dihantar.")
    except Exception as e:
        print("Ralat Telegram:", e)

def stock_checker_loop():
    notified = False
    while True:
        status = check_stock()
        if status and not notified:
            send_telegram(f"🚨 Barang Shopee dah ada stok!\n👉 <a href='{product_url}'>Klik sini untuk beli</a>")
            notified = True
        elif status is False:
            notified = False
        time.sleep(CHECK_INTERVAL)

def run_background():
    t = Thread(target=stock_checker_loop)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    run_background()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
