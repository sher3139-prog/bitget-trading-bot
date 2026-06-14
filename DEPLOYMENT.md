# 🤖 BITGET TRADING BOT v1.0 - DEPLOYMENT GUIDE

Professional Edition | Hybrid ARMY PRO + SMC + ICT Signal System

---

## 📋 QUICK START

### Step 1: Prepare Bitget API Keys

1. Login to Bitget: https://www.bitget.com/
2. Go to Account → API Management
3. Create New API Key with these permissions:
   - **Trade** (place/cancel orders)
   - **Withdraw** (NO - uncheck!)
   - **Account Info** (YES)
4. Copy 3 values:
   - `API Key`
   - `Secret Key`
   - `Passphrase`

⚠️ **SECURITY**: Store these safely. Never commit to GitHub!

---

### Step 2: Create Telegram Bot

1. Open Telegram, find **@BotFather**
2. Send: `/newbot`
3. Follow prompts to create bot
4. Copy the **Token** (example: `123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefg`)

5. Get your **Chat ID**:
   - Find your bot in Telegram
   - Send: `/start`
   - Open: `https://api.telegram.org/bot<YOUR_TOKEN>/getMe`
   - Look for `"id": <YOUR_CHAT_ID>`

---

### Step 3: Deploy to Render.com

#### Option A: One-Click Deploy (Easiest)

1. Go to: https://render.com
2. Sign up (free account)
3. Click: **+ New** → **Web Service**
4. Connect GitHub repo (or create new)
5. Fill in:
   - **Name**: `bitget-trading-bot`
   - **Runtime**: Python 3.10
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bitget_trading_bot_v1.py`

6. **Add Environment Variables** (click "Add Environment Variable"):
   ```
   BITGET_API_KEY = (your API key)
   BITGET_SECRET_KEY = (your secret key)
   BITGET_PASSPHRASE = (your passphrase)
   TELEGRAM_BOT_TOKEN = (your bot token)
   TELEGRAM_CHAT_ID = (your chat ID)
   BOT_MODE = paper  (change to 'live' after testing)
   ```

7. Click **Create Web Service**
8. Wait ~3-5 minutes for deployment

#### Option B: Manual GitHub Deploy

```bash
# 1. Create GitHub repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/bitget-trading-bot.git
git push -u origin main

# 2. Connect to Render
# Go to render.com → New Web Service → Connect GitHub
# Select your repo and follow prompts
```

---

### Step 4: Verify Deployment

1. Go to Render dashboard
2. Click on `bitget-trading-bot` service
3. Check **Logs** tab - should see:
   ```
   Bot initialized. Monitoring 20 coins
   Starting main loop...
   Analysis cycle started at ...
   ```

4. Open bot URL: `https://bitget-trading-bot.onrender.com/`
5. Should see dashboard with status

---

## 🔧 BOT FEATURES

### Signal System (Hybrid)

```
✅ ARMY PRO:
   - Supply/Demand Zone Detection
   - Contraction Candle Recognition
   - 1:2 & 1:4 Risk:Reward Entry

✅ SMC (Smart Money Concepts):
   - Break of Structure (BOS) Detection
   - Order Block (OB) Identification
   - Change of Character (CHoCH)

✅ ICT (3-Timeframe):
   - 4H: Trend Bias (HTF)
   - 1H: Zone Definition
   - 15M: Entry Trigger

✅ Technical Indicators:
   - EMA7/25 Trend Filter
   - RSI Extremes (30/70)
   - MACD Momentum
```

### Risk Management

```
📊 Daily Limits:
   - Max 10 trades/day
   - Max $20 loss/day
   - $20 risk per trade

💰 Position Sizing:
   - 10x leverage
   - Auto SL calculation
   - TP1 (1:2 RR) + TP2 (1:4 RR)
```

### Monitored Coins (Top 20)

```
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, LINK, MATIC,
ARB, OP, LIT, BC, APT, SUI, PERP, GMX, AAVE, UNI
```

### Monitoring Interval

```
⏱️ Analysis runs every 30 minutes
   - Fetches 4H/1H/15M candles
   - Analyzes signals for all 20 coins
   - Executes trades if conditions met
   - Sends Telegram notifications
```

---

## 📊 DASHBOARD

Access at: `https://bitget-trading-bot.onrender.com/`

**Real-Time Monitoring:**
- Daily trade count
- Daily loss amount
- Current leverage
- Risk per trade

**API Endpoints:**
```
GET /api/status
GET /api/trades
```

---

## ⚙️ CONFIGURATION

Edit `bitget_trading_bot_v1.py` section:

```python
CONFIG = {
    'LEVERAGE': 10,              # Change to 5x or 20x
    'RISK_PER_TRADE': 20,       # Change to $10, $50, etc
    'MAX_DAILY_TRADES': 10,     # Max trades/day
    'MAX_DAILY_LOSS': 20,       # Max loss/day
    'INTERVAL': 1800,           # 30 minutes (3600 = 1h)
    'TOP_COINS': 20,            # Number of coins to monitor
    'TP_RATIO_1': 2,            # 1:2 RR
    'TP_RATIO_2': 4,            # 1:4 RR
}
```

---

## 🔒 SECURITY BEST PRACTICES

### ❌ DO NOT:
- Commit `.env` file to GitHub
- Use same API key for multiple bots
- Share API credentials
- Enable Withdraw permission

### ✅ DO:
- Use IP whitelist on Bitget (if available)
- Create dedicated API key for bot only
- Rotate keys every 3 months
- Store secrets in Render environment variables
- Test on paper trading first

---

## 🧪 TESTING

### Paper Trading (Recommended)

In Render environment variables:
```
BOT_MODE = paper
```

Bot will:
- Analyze signals
- Log trades to database
- Send Telegram notifications
- **NOT** execute real trades

Monitor for 1 week. When confident → change to:
```
BOT_MODE = live
```

### Monitor Logs

```bash
# Render Dashboard → Logs tab
# Or via API:
curl https://bitget-trading-bot.onrender.com/api/status
```

---

## 🐛 TROUBLESHOOTING

### Bot Not Starting

**Error**: `ModuleNotFoundError: No module named 'aiohttp'`

**Fix**: 
```bash
pip install -r requirements.txt
# Or in Render: Ensure Build Command is set
```

### No Telegram Messages

**Fix**:
1. Verify TELEGRAM_BOT_TOKEN is correct
2. Verify TELEGRAM_CHAT_ID is correct
3. Send `/start` to bot manually
4. Check bot logs for errors

### API Authentication Fails

**Fix**:
1. Regenerate API keys on Bitget
2. Verify Passphrase is correct (case-sensitive!)
3. Check API key permissions (needs Trade)
4. Ensure IP is not blocked

### Too Many Requests

**Fix**: Increase INTERVAL in config (3600 = hourly)

---

## 📈 PERFORMANCE TRACKING

Bot logs all trades to SQLite database (`/tmp/trading.db`):

```sql
-- View trades
SELECT symbol, side, entry_price, entry_time, status FROM trades;

-- Daily stats
SELECT date, total_trades, total_loss FROM daily_stats;
```

Accessible via `/api/trades` endpoint

---

## 📞 MONITORING & ALERTS

**Telegram Notifications Include:**
- 🟢 LONG / 🔴 SHORT entry
- Signal confidence %
- Entry price
- Stop loss level
- Take profit targets (TP1 & TP2)
- Risk amount ($20)
- Leverage (10x)

**Example Alert:**
```
🟢 LONG BTCUSDT
━━━━━━━━━━━━━━
Confidence: 78.5%
Entry: 45250.50
SL: 45100.00
TP1: 45550.50
TP2: 45850.50
━━━━━━━━━━━━━
Leverage: 10x
Risk: $20
```

---

## 🚀 UPGRADES & FEATURES (v1.1+)

- [ ] Automated SL/TP execution on Bitget
- [ ] Multi-account support
- [ ] Advanced position management
- [ ] Live P&L tracking
- [ ] WhatsApp/Discord notifications
- [ ] Custom webhook integration
- [ ] ML signal optimization
- [ ] Backtesting module

---

## 📚 REFERENCES

**ARMY PRO Methodology:**
- Supply/Demand zones
- Contraction candle entries
- Fixed risk management
- SMC confluence

**Resources:**
- https://www.bitget.com/api-docs
- https://www.render.com/docs
- https://pypi.org/project/pyTelegramBotAPI/

---

## 💬 SUPPORT

For issues or questions:
1. Check `/tmp/bot.log` for error messages
2. Review Render dashboard logs
3. Test API keys independently
4. Verify Telegram bot token

---

**Last Updated**: June 2024
**Version**: 1.0
**Status**: Production Ready ✅
