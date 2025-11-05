from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
import time

app = Flask(__name__)

# URL Shopee boleh diubah
product_url = "https://shopee.com.my/product/482293451/25715198120"

# Status global
last_checked = "Belum disemak"
stock_status = "⏳ Menunggu semakan pertama..."

# Fungsi semak stok
def check_stock():
    global last_checked, stock_status
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

    try:
        r = requests.get(product_url, headers=headers, timeout=15)
        last_checked = datetime.datetime.now(malaysia_tz).strftime("%d/%m/%Y %H:%M:%S")

        if r.status_code != 200:
            stock_status = f"❗ Gagal akses Shopee ({r.status_code})"
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Semak pelbagai keyword untuk stok habis
        keywords_habis = ["out of stock", "sold out", "habis dijual", "kuantiti habis"]
        out_of_stock = soup.find_all(string=lambda text: text and any(k in text.lower() for k in keywords_habis))

        if out_of_stock:
            stock_status = "❌ Tiada stok (OUT OF STOCK)"
            print(stock_status)
            return False
        else:
            stock_status = "✅ Ada stok!"
            print(stock_status)
            return True

    except Exception as e:
        stock_status = f"⚠️ Ralat sambungan: {e}"
        return None


# Fungsi utama Flask
@app.route('/')
def home():
    check_stock()  # Semak stok setiap kali laman dibuka
    html = f"""
    <html>
    <head>
        <title>Semakan Stok Shopee</title>
        <meta http-equiv="refresh" content="300"> <!-- auto refresh setiap 5 minit -->
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                color: #333;
                text-align: center;
                padding-top: 50px;
            }}
            .card {{
                background: white;
                display: inline-block;
                padding: 30px 50px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #ff6600; }}
            .status {{
                font-size: 20px;
                margin-top: 15px;
                font-weight: bold;
            }}
            .time {{
                font-size: 16px;
                color: #666;
            }}
            input {{
                width: 400px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }}
            button {{
                padding: 10px 20px;
                background-color: #ff6600;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin-left: 10px;
            }}
            button:hover {{
                background-color: #ff4400;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔍 Semakan Stok Shopee</h1>
            <form method="POST" action="/set_url">
                <input type="text" name="url" placeholder="Masukkan link Shopee baru" required>
                <button type="submit">Tukar Produk</button>
            </form>
            <div class="status">{stock_status}</div>
            <div class="time">⏰ Disemak pada: {last_checked}</div>
            <p>🔗 <a href="{product_url}" target="_blank">{product_url}</a></p>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/set_url', methods=['POST'])
def set_url():
    global product_url
    new_url = request.form.get('url')
    if new_url:
        product_url = new_url
        return f"""
        <h2>✅ Link produk ditukar!</h2>
        <p><a href='/'>Kembali</a></p>
        <p>Produk baru: {product_url}</p>
        """
    else:
        return "<h3>❌ Tiada URL dimasukkan</h3>"


# Untuk Render, guna ini sebagai start command
if __name__ == '__main__':
    # Jalankan server Flask
    app.run(host='0.0.0.0', port=10000)
