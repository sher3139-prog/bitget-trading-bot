# 🤖 BITGET TRADING BOT v1.0

**Professional Edition** | Hybrid ARMY PRO + SMC + ICT Signal System

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## ✨ Overview

**Bitget Trading Bot** adalah bot trading otomatis profesional untuk Bitget Futures dengan sistem sinyal hybrid yang menggabungkan:

- **ARMY PRO Methodology** - Supply/Demand zones, contraction entries, fixed risk management
- **SMC (Smart Money Concepts)** - Break of Structure, Order Blocks, Change of Character
- **ICT (Inner Circle Trader)** - Multi-timeframe confirmation (4H/1H/15M)
- **Technical Indicators** - EMA, RSI, MACD untuk konfirmasi tambahan

---

## 🎯 Key Features

### ✅ Intelligent Signal Generation
```
Multi-factor confluence detection:
✓ ARMY PRO supply/demand zones
✓ Contraction candle recognition
✓ SMC structure validation
✓ ICT 3-timeframe confirmation
✓ Technical indicator confluence
```

### ✅ Automated Trading
```
Complete automation:
✓ 24/7 market analysis (every 30 min)
✓ Automatic order placement on Bitget
✓ Stop-loss & take-profit management
✓ Position sizing based on risk
✓ Real-time Telegram notifications
```

### ✅ Risk Management
```
Strict risk controls:
✓ Max $20 loss per day (daily limit)
✓ Max 10 trades per day
✓ $20 fixed risk per trade
✓ 10x leverage (adjustable)
✓ Automatic position sizing
✓ Hard daily cutoff
```

### ✅ Monitoring & Control
```
Real-time visibility:
✓ Web dashboard
✓ Telegram bot notifications
✓ Trade history & statistics
✓ Daily P&L tracking
✓ Signal confidence scoring
```

### ✅ Monitoring 20 Top Coins
```
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, LINK, MATIC,
ARB, OP, LIT, BC, APT, SUI, PERP, GMX, AAVE, UNI
```

---

## 📊 System Architecture

```
┌─────────────────────────────────┐
│     BITGET TRADING BOT v1.0     │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│   Signal Engine (Hybrid)        │
├─────────────────────────────────┤
│ • ARMY PRO Analyzer             │
│ • SMC Detection                 │
│ • ICT Multi-TF Confirmation     │
│ • Technical Indicators          │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│    Risk Manager                 │
├─────────────────────────────────┤
│ • Position Sizing               │
│ • SL/TP Calculation             │
│ • Daily Limits                  │
│ • Trade Logging                 │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│    Bitget API Executor          │
├─────────────────────────────────┤
│ • Place Orders                  │
│ • Set Leverage                  │
│ • Manage Positions              │
│ • Fetch Market Data             │
└─────────────────────────────────┘
            ↓
    ┌──────────┴──────────┐
    ↓                     ↓
┌─────────────┐    ┌──────────────┐
│ Telegram    │    │ Web Dashboard│
│ Notifications    │ Monitoring   │
└─────────────┘    └──────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Bitget Futures account
- Telegram account (for notifications)
- Render.com account (for 24/7 hosting)

### 2. Installation

```bash
# Clone/download the bot
git clone <repo>
cd bitget-trading-bot

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### 3. Configuration

Edit `.env`:
```bash
BITGET_API_KEY=your_api_key
BITGET_SECRET_KEY=your_secret_key
BITGET_PASSPHRASE=your_passphrase
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
BOT_MODE=paper  # or 'live'
```

### 4. Deploy to Render (Recommended)

```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Connect to Render
# https://render.com → New Web Service → Connect GitHub
```

See `DEPLOYMENT.md` for detailed instructions.

### 5. Local Testing

```bash
# Test in paper mode
export BOT_MODE=paper
python bitget_trading_bot_v1.py
```

---

## 📈 Configuration

Edit `config.py` for:

```python
# Risk settings
RISK_PER_TRADE = 20          # $20 per trade
LEVERAGE = 10                 # 10x leverage
MAX_DAILY_TRADES = 10        # Max trades/day
MAX_DAILY_LOSS = 20          # Max loss/day

# Monitoring
INTERVAL = 1800              # 30 minutes
TOP_COINS = 20               # Monitor top 20 coins

# Profit targets
TP_RATIO_1 = 2               # 1:2 risk/reward
TP_RATIO_2 = 4               # 1:4 risk/reward

# Signal thresholds
MIN_CONFIDENCE = 60          # Min 60% confidence
```

---

## 📱 Telegram Commands

```
/status    → Bot status & daily stats
/pause     → Pause trading
/resume    → Resume trading
/history   → Last 10 trades
/settings  → Adjust parameters
```

---

## 🌐 Web Dashboard

Access at: `https://bitget-trading-bot.onrender.com/`

**Real-time monitoring:**
- Current status
- Daily trades count
- Daily loss amount
- Recent trades
- Statistics

---

## 📊 Signal Algorithm

### Long Entry Example

```
1. 4H Trend: UPTREND (EMA7 > EMA25)
2. 1H Zone: Price in demand zone
3. 15M Entry: Contraction candle
4. Confluence: EMA + RSI + MACD confirm
5. SMC: BOS towards demand confirmed
6. RESULT: 🟢 LONG signal (78% confidence)

Entry: 45250.50
SL: 45100.00 (below demand zone)
TP1: 45550.50 (1:2 RR)
TP2: 45850.50 (1:4 RR)
Risk: $20 (fixed)
Position: 0.0234 BTC @ 10x
```

### Risk Calculation

```
Risk per trade: $20
Leverage: 10x
SL distance: $50

Position Size = (Risk × Leverage) / SL_distance
              = (20 × 10) / 50
              = 0.04 base units

Example: 0.04 BTC @ 10x = $18,000 notional exposure
```

---

## 📈 Performance Tracking

All trades logged to SQLite database:

```bash
# View recent trades
curl https://your-bot.onrender.com/api/trades

# Check status
curl https://your-bot.onrender.com/api/status
```

### Trade Data

```json
{
  "symbol": "BTCUSDT",
  "side": "buy",
  "entry_price": 45250.50,
  "entry_time": "2024-06-10T14:30:00",
  "sl_price": 45100.00,
  "tp1_price": 45550.50,
  "tp2_price": 45850.50,
  "status": "OPEN"
}
```

---

## ⚙️ Advanced Configuration

### Customizing Coins

Edit `config.py`:

```python
MONITORED_COINS = [
    'BTCUSDT',
    'ETHUSDT',
    # Add more...
]
```

### Adjusting Risk

```python
# More aggressive
RISK_PER_TRADE = 50      # $50 per trade
LEVERAGE = 20            # 20x leverage

# More conservative
RISK_PER_TRADE = 10      # $10 per trade
LEVERAGE = 5             # 5x leverage
```

### Changing Analysis Interval

```python
INTERVAL = 3600  # Analyze hourly instead of 30 min
```

---

## 🔒 Security

### Best Practices

✅ **DO:**
- Store API keys in environment variables
- Use IP whitelist on Bitget
- Test in paper mode first
- Monitor bot logs regularly
- Review trades daily

❌ **DON'T:**
- Commit `.env` to GitHub
- Use multiple bots with same account
- Enable Withdraw permission
- Trade with funds you can't afford to lose
- Run live mode without testing

### Credentials Management

1. **Bitget API Keys:**
   - Create dedicated API key for bot
   - Restrict to IP address (if available)
   - Never enable Withdraw

2. **Telegram Bot Token:**
   - Create with @BotFather
   - Store in environment only
   - Rotate if compromised

3. **Render Secrets:**
   - All env vars encrypted at rest
   - Use Render dashboard for updates
   - Never log sensitive data

---

## 🐛 Troubleshooting

### Bot Won't Start

**Error**: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### API Authentication Failed

**Fix:**
- Verify API key format
- Check Passphrase spelling (case-sensitive)
- Ensure IP not blocked
- Regenerate keys if needed

### No Telegram Alerts

**Fix:**
- Verify bot token
- Verify chat ID
- Ensure bot not blocked
- Check logs for errors

### Too Many Requests

**Fix:**
- Increase INTERVAL in config
- Reduce number of coins
- Use rate limiting

---

## 📚 Resources

### Documentation
- `DEPLOYMENT.md` - Complete deployment guide
- `config.py` - Configuration reference
- `utils.py` - Utility functions reference

### External References
- [Bitget API Docs](https://www.bitget.com/api-docs)
- [Render Docs](https://render.com/docs)
- [ARMY PRO Methodology](https://tradingview.com)

### Learning
- Al Brooks - Trade Price Action
- Steve Nison - Candlestick Analysis
- Mark Douglas - Trading Psychology
- ICT - Smart Money Concepts

---

## 🔄 Updates & Roadmap

### v1.0 ✅ (Current)
- [x] ARMY PRO signal system
- [x] SMC detection
- [x] ICT multi-timeframe
- [x] Risk management
- [x] Telegram integration
- [x] Web dashboard
- [x] Bitget API integration

### v1.1 (Planned)
- [ ] Live order execution
- [ ] Advanced position management
- [ ] ML signal optimization
- [ ] Multi-account support
- [ ] Advanced analytics
- [ ] Discord notifications

### v1.2 (Planned)
- [ ] Backtesting module
- [ ] Paper trading optimizer
- [ ] Custom webhooks
- [ ] Trading journal AI
- [ ] Mobile app

---

## 📞 Support

### Debugging

1. Check logs: `tail -f /tmp/bot.log`
2. Verify config: `python config.py`
3. Test API: See `utils.py` examples
4. Check Telegram: Verify token and chat ID

### Common Issues

| Issue | Solution |
|-------|----------|
| No signals | Check timeframe data, verify coins |
| High loss | Review risk settings, test paper mode |
| API errors | Verify credentials, check IP whitelist |
| Missing trades | Check logs, verify signal thresholds |

---

## 📄 License

MIT License - See LICENSE file

---

## ⚠️ Disclaimer

**This bot is provided for educational and experimental purposes only.**

- Trading crypto futures is highly risky
- You can lose more than your initial investment
- Past performance does not guarantee future results
- Always use proper risk management
- Test extensively in paper mode first
- Never trade with money you can't afford to lose
- Consult financial advisors before live trading

**Use at your own risk. We are not liable for any losses.**

---

## 🤝 Contributing

Contributions welcome! Please:

1. Test thoroughly
2. Document changes
3. Follow code style
4. Submit pull requests

---

## 📧 Contact

For questions or issues:
- Check documentation first
- Review logs for errors
- Test in paper mode
- Open GitHub issue with details

---

**Built with ❤️ for active traders**

Last Updated: June 2024 | v1.0.0
