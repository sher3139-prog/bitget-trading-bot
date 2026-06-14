# 🚀 SETUP GUIDE - Bitget Trading Bot v1.0

Detailed step-by-step setup instructions for Windows/Mac/Linux

---

## 📋 Pre-Setup Checklist

- [ ] Bitget Futures account (verified)
- [ ] Telegram account
- [ ] Render.com account (free)
- [ ] Git installed (optional, for GitHub)
- [ ] Python 3.8+ installed
- [ ] Text editor (VS Code, Sublime, etc.)

---

## STEP 1: Get Bitget API Credentials

### 1.1 Login to Bitget

1. Go to https://www.bitget.com/
2. Click **Sign In** (top right)
3. Enter email/password or use social login
4. Complete 2FA verification

### 1.2 Create API Key

1. Click **Account** (top right) → **Settings**
2. Left sidebar: **API Management**
3. Click **+ Create API Key**
4. Select permissions:
   ```
   ✅ Trade (place/cancel orders)
   ✅ Account Info (read account data)
   ❌ Withdraw (UNCHECK - security risk)
   ```
5. Set IP whitelist (optional but recommended):
   - If using Render: Add `*.onrender.com` or `0.0.0.0/0`
   - If local: Add your IP address

### 1.3 Copy Credentials

You'll see 3 values (save securely!):
```
API Key:        8d2x3f4g5h6j7k8l9m0n
Secret Key:     a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Passphrase:     MyPassphrase123
```

⚠️ **Save these somewhere safe!** You won't see them again.

---

## STEP 2: Create Telegram Bot

### 2.1 Create Bot with @BotFather

1. Open Telegram app or https://web.telegram.org
2. Search for **@BotFather** (Telegram official bot)
3. Start chat and type: `/newbot`
4. Follow instructions:
   - Give bot a name: `Bitget Trading Bot`
   - Give bot a username: `bitget_trading_bot_YOUR_NAME`
5. You'll receive:
   ```
   Done! Congratulations on your new bot. 
   Here are your bot's token:
   123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefg
   ```

### 2.2 Get Your Chat ID

1. Search for **@userinfobot** in Telegram
2. Start chat - it will show your User ID
   ```
   You are: @username
   User ID: 987654321
   ```
   (This is your TELEGRAM_CHAT_ID)

**Summary:**
```
TELEGRAM_BOT_TOKEN = 123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefg
TELEGRAM_CHAT_ID = 987654321
```

---

## STEP 3: Download Bot Files

### Option A: GitHub (Recommended)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/bitget-trading-bot.git
cd bitget-trading-bot

# Or download as ZIP
# Go to GitHub repo → Code → Download ZIP
# Extract and open folder
```

### Option B: Manual Download

1. Download files from repository
2. Create folder: `bitget-trading-bot`
3. Extract all files into folder

---

## STEP 4: Setup Environment File

### 4.1 Create `.env` file

In your bot folder, create file: `.env`

```bash
# Windows: Create new text file, rename to .env
# Mac/Linux: 
touch .env
```

### 4.2 Add Credentials

Edit `.env` and paste:

```ini
# ===== BITGET API =====
BITGET_API_KEY=8d2x3f4g5h6j7k8l9m0n
BITGET_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
BITGET_PASSPHRASE=MyPassphrase123

# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefg
TELEGRAM_CHAT_ID=987654321

# ===== BOT MODE =====
BOT_MODE=paper

# ===== PORT =====
PORT=5000
```

**Important:** 
- Never commit `.env` to GitHub!
- This file contains secrets - keep private!
- Windows notepad may add .txt - ensure it's just `.env`

---

## STEP 5: Install Dependencies

### Windows

```bash
# Open Command Prompt in bot folder
# cd C:\path\to\bitget-trading-bot

pip install -r requirements.txt
```

### Mac/Linux

```bash
# Open Terminal in bot folder

pip3 install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

**Wait for installation to complete** (~2-3 minutes)

---

## STEP 6: Test Locally (Paper Mode)

### 6.1 Run Bot

```bash
# Windows
python bitget_trading_bot_v1.py

# Mac/Linux
python3 bitget_trading_bot_v1.py
```

### 6.2 Check Logs

You should see:
```
INFO - Bot initialized. Monitoring 20 coins
INFO - Starting main loop...
INFO - Analysis cycle started at 2024-06-10 14:30:00
```

### 6.3 Test Telegram

Bot should send message to Telegram chat:
```
🤖 Bot started in PAPER mode
Ready to analyze...
```

### 6.4 Check Web Dashboard

Open browser: http://localhost:5000

Should show:
- Bot status: "running"
- Daily trades: 0
- Daily loss: $0

---

## STEP 7: Deploy to Render.com

### 7.1 Create Render Account

1. Go to https://render.com
2. Sign up (free account)
3. Verify email

### 7.2 Connect GitHub

1. In Render dashboard: **+ New** → **Web Service**
2. Click **Connect account** next to GitHub
3. Authorize Render to access GitHub
4. Select your `bitget-trading-bot` repository
5. Allow access

### 7.3 Configure Service

Fill in form:

```
Name:               bitget-trading-bot
Environment:        Python 3
Region:             (nearest to you)
Branch:             main
Runtime:            Python 3.10
Build Command:      pip install -r requirements.txt
Start Command:      python bitget_trading_bot_v1.py
```

### 7.4 Add Environment Variables

Click **+ Add Environment Variable** for each:

| Key | Value |
|-----|-------|
| BITGET_API_KEY | (your API key) |
| BITGET_SECRET_KEY | (your secret) |
| BITGET_PASSPHRASE | (your passphrase) |
| TELEGRAM_BOT_TOKEN | (your bot token) |
| TELEGRAM_CHAT_ID | (your chat ID) |
| BOT_MODE | paper |

### 7.5 Deploy

1. Click **Create Web Service**
2. Wait 3-5 minutes for deployment
3. You'll get URL: `https://bitget-trading-bot.onrender.com/`

### 7.6 Verify Deployment

1. Check logs tab - should see startup messages
2. Open service URL - should see dashboard
3. Check Telegram - should receive status message

---

## STEP 8: Monitor & Control

### 8.1 Web Dashboard

Access: `https://bitget-trading-bot.onrender.com/`

**Monitor:**
- Bot status
- Daily trades/loss
- Recent trades
- Statistics

### 8.2 Telegram Commands

```
/status   - Show status
/pause    - Pause trading
/resume   - Resume trading
```

### 8.3 Check Logs

In Render dashboard:
- Go to your service
- Click **Logs** tab
- See real-time output

---

## STEP 9: Switch to Live Mode (OPTIONAL)

⚠️ **Only after 1+ week of paper trading!**

### 9.1 Update Environment

In Render dashboard:

1. Click service name
2. Go to **Environment** tab
3. Edit `BOT_MODE`
4. Change from `paper` to `live`
5. Save

### 9.2 Start Live Trading

Bot will now:
- Execute real orders on Bitget
- Risk real money ($20/trade)
- Send real P&L alerts

---

## 🧪 Testing Checklist

### Before Going Live

- [ ] Ran bot 1+ week in paper mode
- [ ] Received Telegram notifications
- [ ] Verified API connection working
- [ ] Checked web dashboard loads
- [ ] Reviewed trade logic in logs
- [ ] Tested SL/TP calculations
- [ ] Verified risk management limits
- [ ] Confirmed leverage setting
- [ ] Started with small capital

---

## ⚙️ Configuration Options

### Edit in `config.py`:

```python
# Risk settings
TRADING_CONFIG = {
    'LEVERAGE': 10,              # Change to 5, 20, etc
    'RISK_PER_TRADE': 20,       # Change to 10, 50, etc
    'MAX_DAILY_TRADES': 10,     # Max trades/day
    'MAX_DAILY_LOSS': 20,       # Max loss before stop
    'INTERVAL': 1800,           # Analysis interval (seconds)
}

# Coins to monitor
MONITORED_COINS = [
    'BTCUSDT', 'ETHUSDT', ...
]
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'aiohttp'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Bot won't connect to Bitget

**Check:**
1. API key is correct
2. Secret key is correct  
3. Passphrase is correct (case-sensitive!)
4. Passphrase != password
5. API key has "Trade" permission enabled

### Issue: No Telegram messages

**Check:**
1. Bot token is correct
2. Chat ID is correct
3. You've sent `/start` to bot
4. Bot isn't blocked in Telegram

### Issue: Bot runs but no trades

**Normal in early days!**
- Signals are selective (>60% confidence)
- Market conditions must match setup
- Review logs to see analysis results

---

## 📊 Next Steps

After setup:

1. **Monitor** - Watch bot for 1 week
2. **Review** - Check trade quality in logs
3. **Adjust** - Modify coins/risk if needed
4. **Scale** - Increase risk gradually
5. **Track** - Keep trading journal in Notion

---

## 🔒 Security Reminders

✅ **DO:**
- [ ] Keep `.env` file private
- [ ] Never share API keys
- [ ] Use IP whitelist on Bitget
- [ ] Monitor bot activity daily
- [ ] Review Telegram alerts

❌ **DON'T:**
- [ ] Commit `.env` to GitHub
- [ ] Share credentials
- [ ] Use Withdraw permission
- [ ] Run multiple bots same account
- [ ] Trade more than risk tolerance

---

## 📞 Need Help?

1. Check logs: `tail /tmp/bot.log`
2. Review `README.md` for FAQs
3. Check `DEPLOYMENT.md` for details
4. Test config: `python config.py`
5. Verify credentials work

---

**Setup Complete! 🎉**

Your bot is now ready to:
- ✅ Analyze 20 top coins
- ✅ Generate hybrid signals
- ✅ Manage risk automatically
- ✅ Execute trades 24/7
- ✅ Send Telegram alerts
- ✅ Track performance

**Monitor the logs and enjoy automated trading!**

Next: See `README.md` for full documentation.
