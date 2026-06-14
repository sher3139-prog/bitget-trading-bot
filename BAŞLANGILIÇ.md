# 🤖 BITGET TRADING BOT v1.0 - BAŞLAMAÇ REHBERI

**Profesyonel Edition** | Hybrid ARMY PRO + SMC + ICT Sinyal Sistemi

---

## ✅ TÜM DOSYALAR HAZIR!

Bot tamamen yazılmış ve production-ready. İçeriyor:

```
📁 Bitget Trading Bot v1.0
├── bitget_trading_bot_v1.py      ⭐ Ana bot dosyası (32KB)
├── config.py                      ⚙️ Konfigürasyon (11KB)
├── utils.py                       🔧 Yardımcı fonksiyonlar (17KB)
├── requirements.txt               📦 Dependencies
├── Procfile                       🚀 Render deployment
├── render.yaml                    🔗 Render config
├── README.md                      📚 Tam dokümantasyon
├── SETUP.md                       👨‍🏫 Step-by-step kurulum
├── DEPLOYMENT.md                  🌐 Render deployment rehberi
├── .env.example                   🔐 Env template
└── .gitignore                     🛡️ Git ignore
```

---

## 🚀 3 ADIMDA BAŞLA

### ADIM 1: Bitget API Al (5 dakika)

1. https://www.bitget.com/ → Login
2. Account → Settings → API Management
3. **Create API Key** klik et
4. Permissions seç:
   - ✅ Trade
   - ✅ Account Info
   - ❌ Withdraw (UNCHECKED!)
5. Ekrana yazdır (copy et):
   ```
   BITGET_API_KEY = ...
   BITGET_SECRET_KEY = ...
   BITGET_PASSPHRASE = ...
   ```

### ADIM 2: Telegram Bot Yap (2 dakika)

1. Telegram'da @BotFather ara
2. `/newbot` gönder
3. Bot name + username ver
4. **Token** kopyala:
   ```
   TELEGRAM_BOT_TOKEN = 123456789:ABCdef...
   ```
5. @userinfobot ara → User ID kopyala:
   ```
   TELEGRAM_CHAT_ID = 987654321
   ```

### ADIM 3: Render'a Deploy (5 dakika)

1. https://render.com → Sign up (free)
2. **+ New Web Service** klik
3. GitHub connect (repo'yu seç)
4. **Add Environment Variables**:
   - BITGET_API_KEY
   - BITGET_SECRET_KEY
   - BITGET_PASSPHRASE
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - BOT_MODE=paper
5. **Create Web Service** klik
6. 3-5 dakika bekle
7. Dashboard'unuz: `https://bitget-trading-bot.onrender.com/`

---

## 🎯 BOT NEYİ YAPIYOR?

### Sinyal Sistemi (Hybrid)
```
✅ ARMY PRO:
   • Supply/Demand zone detection
   • Contraction candle entries
   • Fixed $20 risk per trade

✅ SMC:
   • Break of Structure detection
   • Order block identification

✅ ICT (3-Timeframe):
   • 4H trend confirmation
   • 1H zone definition
   • 15M entry trigger

✅ Technical Indicators:
   • EMA7/25 trend filter
   • RSI extremes
   • MACD confirmation
```

### Otomatik Trading
```
🔄 Her 30 dakikada:
   1. Top 20 coin'i analiz et
   2. Sinyal var mı bak?
   3. Güven >60% mi?
   4. Risk manager check et
   5. Otomatik order aç
   6. SL/TP set et
   7. Telegram'a bildir
```

### Risk Management
```
📊 Günlük Limitler:
   • Max 10 trade/gün
   • Max $20 zarar/gün
   • $20 risk per trade
   • 10x leverage
```

---

## 📱 TELEGRAM AYARLARI

Bot sana şu gibi mesaj gönderecek:

```
🟢 LONG BTCUSDT
━━━━━━━━━━━━━━━
Confidence: 78%
Entry: 45250.50
SL: 45100.00
TP1: 45550.50 (1:2)
TP2: 45850.50 (1:4)
━━━━━━━━━━━━━━━
Leverage: 10x | Risk: $20
```

---

## 🌐 DASHBOARD

Şu URL'de bot'unuz:
```
https://bitget-trading-bot.onrender.com/
```

Real-time görebilirsiniz:
- Bot status
- Bugünün trade sayısı
- Bugünün zararı
- Son işlemler
- İstatistikler

---

## ⚙️ KONFİGÜRASYON AYARLARI

`config.py` dosyasını düzenle:

```python
# Risk ayarları
TRADING_CONFIG = {
    'LEVERAGE': 10,              # Leverage (5-20 arasında)
    'RISK_PER_TRADE': 20,       # Risk per trade ($)
    'MAX_DAILY_TRADES': 10,     # Max trade/gün
    'MAX_DAILY_LOSS': 20,       # Max zarar/gün
    'INTERVAL': 1800,           # 30 dakika (3600=1 saat)
}

# Monitore etmek istediğin coin'ler
MONITORED_COINS = [
    'BTCUSDT', 'ETHUSDT', ...
]

# Take profit oranları
'TP_RATIO_1': 2,    # 1:2 risk reward
'TP_RATIO_2': 4,    # 1:4 risk reward
```

---

## 📊 MONITORE EDILEN COİN'LER (20 adet)

```
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, LINK, MATIC,
ARB, OP, LIT, BC, APT, SUI, PERP, GMX, AAVE, UNI
```

---

## 🧪 TEST ETME (Paper Mode)

İlk hafta **paper mode**'da bırak:

```ini
BOT_MODE=paper
```

Bot:
- ✅ Sinyal analiz eder
- ✅ Trade'leri simulate eder
- ✅ Telegram alert gönderir
- ❌ Gerçek para harcanmaz

1 hafta sonra, eğer iyi gidiyorsa:

```ini
BOT_MODE=live
```

---

## 🔒 GÜVENLIK

### ✅ YAP:
- API key'i private tut
- `.env` dosyası commit etme
- IP whitelist yap (Bitget'te)
- Daily bot logs'ları kontrol et
- Telegram alerts'leri oku

### ❌ YAPMA:
- `.env` dosyasını GitHub'a koy
- API key'i kimseye gösterme
- Withdraw permission açma
- Bir accountta birden fazla bot
- Yapamadığın parayla trade et

---

## 📈 TRADE ÖRNEĞI

Bot şöyle işlem açıyor:

```
BTCUSDT - LONG Setup
═══════════════════════════════════

1. 4H Analiz:
   ✓ Trend: UP (EMA7 > EMA25)
   ✓ Zone: Supply/Demand detected
   
2. 1H Analiz:
   ✓ Price in demand zone
   
3. 15M Analiz:
   ✓ Contraction candle found
   ✓ EMA/RSI/MACD all confirm
   
RESULT: 🟢 LONG SIGNAL (78% confidence)

═══════════════════════════════════
Entry:      45250.50
SL:         45100.00 (risk = $50)
TP1:        45550.50 (1:2 RR = $100)
TP2:        45850.50 (1:4 RR = $200)
Risk:       $20 (fixed)
Leverage:   10x
Position:   0.04 BTC
═══════════════════════════════════
```

---

## 🐛 SÖZLEŞME SORUNU

### Problem: Bot başlamıyor

**Çözüm:**
```bash
pip install -r requirements.txt
python bitget_trading_bot_v1.py
```

### Problem: API auth hatası

**Kontrol et:**
- API key doğru mu?
- Secret key doğru mu?
- Passphrase doğru mu? (büyük harf duyarlı!)
- Trade permission enabled mi?

### Problem: Telegram mesajı gelmiyor

**Kontrol et:**
- Bot token doğru mu?
- Chat ID doğru mu?
- `/start` komutunu bot'a gönderdim mi?

### Problem: Sinyal gelmiyor

**Normal!**
- Sinyaller seçicidir (>60% confidence)
- Market şartları setup'a uymalı
- Logs'ları oku, ne analiz ediyor bak

---

## 📊 İZLEME

### Telegram Commands

```
/status     → Bot status
/pause      → Trading durdur
/resume     → Trading başlat
/history    → Son 10 trade
```

### Logs Kontrol

Render dashboard'da → **Logs** tab

Görmeli:
```
Bot initialized. Monitoring 20 coins
Starting main loop...
Analysis cycle started at ...
```

### Web Dashboard

https://bitget-trading-bot.onrender.com/

Görmeli:
- Status: running
- Daily trades: 0-10
- Daily loss: $0-20

---

## 📚 DOSYALAR AÇIKLAMA

| Dosya | Açıklama |
|-------|----------|
| `bitget_trading_bot_v1.py` | Ana bot - signal engine, risk manager, API |
| `config.py` | Tüm ayarlar - risk, coin'ler, limitler |
| `utils.py` | Yardımcı - indicators, calculations |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render deployment config |
| `render.yaml` | Render one-click deploy |
| `README.md` | Tam dokümantasyon |
| `SETUP.md` | Step-by-step kurulum |
| `DEPLOYMENT.md` | Render deploy rehberi |
| `.env.example` | Environment template |
| `.gitignore` | Git ignore (secrets) |

---

## 🎯 NEXT STEPS

### Hemen:
1. [ ] Bitget API al
2. [ ] Telegram bot yap
3. [ ] Render'a deploy et
4. [ ] Dashboard'u aç

### İlk hafta:
1. [ ] Paper mode'da bot'u izle
2. [ ] Telegram alerts'leri oku
3. [ ] Log'larda sinyal analiz'ini gör
4. [ ] Config ayarlarını iyileştir

### 1 hafta sonra:
1. [ ] İyi sinyal kalitesi mi? (80%+)
2. [ ] Trade mantığı doğru mu?
3. [ ] Risk yönetimi çalışıyor mu?
4. [ ] Live mode'a geç (small capital)

### Devam eden:
1. [ ] Daily trade journal tut
2. [ ] Performance track et
3. [ ] Risk'i yavaş yavaş arttır
4. [ ] Bot'u optimize et

---

## 💬 NASIL ÇALIŞIR?

### Signal Flow

```
Market Data (Bitget API)
    ↓
4H Analiz (Trend + Zone)
1H Analiz (Zone + SMC)
15M Analiz (Entry + Contraction)
    ↓
Confluence Check
(EMA + RSI + MACD + ARMY + SMC + ICT)
    ↓
Signal Confidence > 60%?
    ↓
Risk Manager Check
(Daily limits, position size)
    ↓
Order Execution
    ↓
Telegram Alert
    ↓
Trade Journal
```

---

## 🚀 BAŞARILI KURULUM IŞARETLERI

✅ Render'dan email: "Build succeeded"
✅ Dashboard açılıyor: https://...onrender.com/
✅ Telegram mesaj geliyor: "Bot started in PAPER mode"
✅ Logs'ta görmek: "Bot initialized. Monitoring 20 coins"
✅ Dashboard'ta: "Status: running"

---

## ⚠️ DİKKAT

**Trading crypto futures HIGH RISK!**

- Kaybettiğin para başlangıç parasından fazla olabilir
- Geçmiş performance gelecek garantisi değildir
- Hep proper risk management yap
- Paper mode'da en az 1 hafta test et
- Sadece yapabileceğin parayla trade et
- Profesyonel tavsiye al

---

## 📞 SORULAR?

1. `README.md` oku → Full dokümantasyon
2. `SETUP.md` oku → Step-by-step kurulum
3. `DEPLOYMENT.md` oku → Render details
4. `config.py` kontrol et → Settings
5. Logs'ları oku → Debug info

---

## 🎉 TAMAMLANDI!

Senin bot hazır:
- ✅ ARMY PRO + SMC + ICT hybrid signals
- ✅ Top 20 coin otomatik monitoring
- ✅ Risk management (max $20/day loss)
- ✅ Telegram notifications
- ✅ Web dashboard
- ✅ 24/7 Render hosting

**Şimdi deploy et ve trade etmeye başla!** 🚀

---

**Başarılar!** 💪

Senin
Bot v1.0 Team

---

**Last Updated**: June 2024 | v1.0.0 Production Ready ✅
