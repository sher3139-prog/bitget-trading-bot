#!/usr/bin/env python3
import os
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import telebot

# LOGGING
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
    return "<h1>Bitget Bot Sistemi Aktif</h1>"

@app.route('/api/status')
def status():
    return jsonify(BOT_STATUS)

# TELEGRAM BOT SETUP
if TOKEN:
    bot = telebot.TeleBot(TOKEN, threaded=False)
    
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 *Bitget Trading Bot v1.0 Başlatıldı!*\n\n"
            "Kullanabileceğiniz Komutlar:\n"
            "📊 `/durum` - Botun anlık çalışma durumunu gösterir.\n"
            "📈 `/sinyal` - Teknik analiz sinyalini tetikler.\n"
            "💼 `/islemler` - Son açılan pozisyonları listeler."
        )
        bot.reply_to(message, welcome_text, parse_mode='Markdown')

    @bot.message_handler(commands=['durum'])
    def send_status(message):
        status_msg = (
            f"ℹ️ *Bot Durumu:* {BOT_STATUS['status'].upper()}\n"
            f"🔄 *Günlük İşlem:* {BOT_STATUS['daily_trades']}\n"
            f"📉 *Günlük Kayıp:* {BOT_STATUS['daily_loss']}\n"
            f"⚙️ *Kaldıraç:* {BOT_STATUS['leverage']}"
        )
        bot.reply_to(message, status_msg, parse_mode='Markdown')

    @bot.message_handler(commands=['sinyal', 'islemler'])
    def send_trades(message):
        msg = "📋 *Son İşlemler:*\n\n"
        for t in BOT_STATUS["positions"]:
            icon = "🟢 LONG" if t['side'] == "LONG" else "🔴 SHORT"
            msg += f"▪️ *{t['symbol']}* -> {icon}\nGiriş: {t['entry_price']}\nDurum: {t['status']}\n"
        bot.reply_to(message, msg, parse_mode='Markdown')
else:
    bot = None
    logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Flask sunucusunu arka planda başlat
    threading.Thread(target=run_flask, daemon=True).start()

    # Telegram botunu ana döngüde çalıştır
    if bot:
        logger.info("Telegram Bot dinleme modu (Polling) başlatılıyor...")
        try:
            # Önceki takılı kalan mesajları temizle
            bot.remove_webhook()
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            logger.error(f"Bot Polling Hatası: {e}")
