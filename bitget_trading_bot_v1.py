#!/usr/bin/env python3
"""
BITGET TRADING BOT v1.0 - STABLE WEBHOOK ENGINE
"""

import os
import sys
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

# LOGGING SETUP
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.getenv('PORT', 10000))
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()

BOT_STATUS = {
    "status": "çalışıyor",
    "daily_trades": "1/10",
    "daily_loss": "0$/20$",
    "leverage": "10x",
    "positions": [
        {
            "symbol": "BTCUSDT",
            "side": "LONG",
            "entry_price": 67250.0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Açık"
        }
    ]
}

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "<h1>Bitget Bot Engine Aktif</h1>"

@app.route('/api/status')
def status():
    return jsonify({
        "status": BOT_STATUS["status"],
        "daily_trades": BOT_STATUS["daily_trades"],
        "daily_loss": BOT_STATUS["daily_loss"],
        "leverage": BOT_STATUS["leverage"],
        "positions": BOT_STATUS["positions"]
    })

# TELEGRAM MANUEL POLLING ENGINE (NO LIBRARY CONFLICT)
def telegram_worker():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")
        return

    logger.info("Telegram Dinleme Motoru Başlatıldı...")
    offset = 0
    
    # Eski birikmiş mesajları temizle ve bağlantıyı doğrula
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1", timeout=5)
    except Exception as e:
        logger.error(f"Telegram baglanti hatasi: {e}")

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=10"
            response = requests.get(url, timeout=15).json()
            
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"].strip()
                        
                        # Komut Kontrolleri
                        if text in ["/start", "/help"]:
                            reply = (
                                "🤖 *Bitget Trading Bot v1.0 Başlatıldı!*\n\n"
                                "Kullanabileceğiniz Komutlar:\n"
                                "📊 `/durum` - Botun anlık çalışma durumunu gösterir.\n"
                                "📈 `/sinyal` - Teknik analiz sinyalini tetikler.\n"
                                "💼 `/islemler` - Son açılan pozisyonları listeler."
                            )
                        elif text == "/durum":
                            reply = (
                                f"ℹ️ *Bot Durumu:* {BOT_STATUS['status'].upper()}\n"
                                f"🔄 *Günlük İşlem:* {BOT_STATUS['daily_trades']}\n"
                                f"📉 *Günlük Kayıp:* {BOT_STATUS['daily_loss']}\n"
                                f"⚙️ *Kaldıraç:* {BOT_STATUS['leverage']}"
                            )
                        elif text in ["/sinyal", "/islemler"]:
                            reply = "📋 *Son İşlemler:*\n\n"
                            for t in BOT_STATUS["positions"]:
                                icon = "🟢 LONG" if t['side'] == "LONG" else "🔴 SHORT"
                                msg_line = f"▪️ *{t['symbol']}* -> {icon}\nGiriş: {t['entry_price']}\nDurum: {t['status']}\n"
                                reply += msg_line
                        else:
                            continue
                            
                        # Cevap Gönder
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
                        
        except Exception as e:
            pass

if __name__ == '__main__':
    # Telegram motorunu ayrı bir kanalda güvenli bir şekilde çalıştırıyoruz
    t = threading.Thread(target=telegram_worker, daemon=True)
    t.start()
    
    # Flask sunucusunu ana kanalda ayağa kaldırıyoruz
    logger.info(f"Flask web sunucusu {PORT} portunda baslatiliyor...")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
