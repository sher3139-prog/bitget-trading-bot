#!/usr/bin/env python3
"""
CONFIG V2 - Bot Settings & Configuration
========================================

All bot parameters in one place for easy modification
"""

import os
from typing import List

class Config:
    """Central configuration for Trading Bot v2"""
    
    # ==================== BOT MODE ====================
    BOT_MODE = os.getenv('BOT_MODE', 'paper')  # 'paper' or 'live'
    
    # ==================== BITGET API ====================
    BITGET_API_KEY = os.getenv('BITGET_API_KEY', '')
    BITGET_SECRET_KEY = os.getenv('BITGET_SECRET_KEY', '')
    BITGET_PASSPHRASE = os.getenv('BITGET_PASSPHRASE', '')
    
    # ==================== TELEGRAM ====================
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # ==================== TRADING SYMBOLS ====================
    # Top 20 cryptocurrencies by market cap
    SYMBOLS: List[str] = [
        'BTCUSDT',      # Bitcoin
        'ETHUSDT',      # Ethereum
        'BNBUSDT',      # Binance Coin
        'XRPUSDT',      # Ripple
        'ADAUSDT',      # Cardano
        'DOGEUSDT',     # Dogecoin
        'SOLUSDT',      # Solana
        'AVAXUSDT',     # Avalanche
        'LINKUSDT',     # Chainlink
        'MATICUSDT',    # Polygon
        'ARBUSDT',      # Arbitrum
        'OPUSDT',       # Optimism
        'LITUSDT',      # Litecoin
        'BCUSDT',       # Bitcoin Cash
        'APTUSDT',      # Aptos
        'SUIUSDT',      # Sui
        'PERPUSDT',     # Perpetual
        'GMXUSDT',      # GMX
        'AAVEUSDT',     # Aave
        'UNIUSDT'       # Uniswap
    ]
    
    # ==================== RISK MANAGEMENT ====================
    RISK_PER_TRADE = 20.0              # Risk amount per trade in USD
    MAX_DAILY_LOSS = 20.0              # Maximum daily loss in USD (hard stop)
    MAX_DAILY_TRADES = 10              # Maximum trades per day
    MAX_OPEN_POSITIONS = 3             # Maximum concurrent open positions
    MIN_SIGNAL_CONFIDENCE = 60          # Minimum confidence % to open trade
    
    # ==================== LEVERAGE SETTINGS ====================
    # Dynamic leverage based on ATR volatility ratio
    # HIGH volatility (ATR > 2x average) -> 3x leverage
    # MEDIUM volatility (1.5x < ATR < 2x) -> 5x leverage
    # LOW volatility (ATR < 1.5x average) -> 10x leverage
    DEFAULT_LEVERAGE = 10               # Default leverage if ATR data unavailable
    
    # ==================== POSITION SIZING ====================
    POSITION_SIZE_MULTIPLIER = 1.0     # Adjust to make positions larger/smaller
    
    # ==================== TECHNICAL ANALYSIS ====================
    # Timeframes (in minutes for API calls, e.g., '4h', '1h', '15m')
    TIMEFRAME_4H = '4h'                # Trend determination timeframe
    TIMEFRAME_1H = '1h'                # Entry zone timeframe
    TIMEFRAME_15M = '15m'              # Entry point timeframe
    
    # Indicator periods
    EMA_FAST_PERIOD = 9                # Fast EMA
    EMA_SLOW_PERIOD = 21               # Slow EMA
    ADX_PERIOD = 14                    # ADX calculation period
    RSI_PERIOD = 14                    # RSI calculation period
    ATR_PERIOD = 14                    # ATR calculation period
    
    # Market Regime (ADX)
    ADX_TRENDING_THRESHOLD = 25         # ADX > 25 = Trending
    ADX_RANGING_THRESHOLD = 20          # ADX < 20 = Ranging
    
    # ==================== SIGNAL FILTERING ====================
    # Confluence zone analysis
    CONFLUENCE_MIN_SCORE = 60           # Minimum confluence score for signal
    FIBONACCI_TOLERANCE = 0.02          # 2% tolerance from Fibonacci level
    SWING_TOLERANCE = 0.03              # 3% tolerance from swing high/low
    OB_TOLERANCE = 0.02                 # 2% tolerance for Order Block
    
    # Supply/Demand zones
    SUPPLY_DEMAND_LOOKBACK = 50        # Periods to look back for S/D zones
    CONTRACTION_BODY_RATIO = 0.25      # Body < 25% of range = contraction
    CONTRACTION_SHADOW_RATIO = 0.30    # Lower shadow > 30% = contraction
    
    # ==================== TIME FILTERS ====================
    # Trading hours (UTC)
    # London session: 08:00-12:00 UTC (4 hours)
    # NY session: 12:00-17:00 UTC (5 hours)
    # Best trading: 08:00-17:00 UTC
    
    TRADING_HOURS_START = 8             # Start hour (UTC)
    TRADING_HOURS_END = 17              # End hour (UTC)
    
    # Skip low liquidity periods
    SKIP_ASIAN_SESSION = True           # Skip 0-8 UTC (low volatility)
    SKIP_WEEKENDS = True                # Skip Saturday-Sunday
    
    # ==================== TRADE MANAGEMENT ====================
    # Trade validity
    MAX_BARS_OPEN = 30                  # Close trade if open > 30 bars
    
    # Take profit levels (in terms of Risk:Reward)
    TP1_REWARD_RATIO = 2.0              # TP1 = Entry + (Entry - SL) * 2
    TP2_REWARD_RATIO = 4.0              # TP2 = Entry + (Entry - SL) * 4
    
    # Stop loss adjustment
    SL_ADJUSTMENT_AFTER_TP1 = True      # Move SL to break-even after TP1 hit
    
    # ==================== PAPER MODE ====================
    # Paper mode settings (simulated trading)
    PAPER_MODE_STARTING_BALANCE = 1000.0    # Starting balance for simulation
    PAPER_MODE_SLIPPAGE = 0.001            # 0.1% slippage on entries
    PAPER_MODE_COMMISSION = 0.0001          # 0.01% per trade
    
    # ==================== API RATE LIMITING ====================
    API_RATE_LIMIT_PER_SECOND = 10      # Bitget API rate limit
    REQUEST_TIMEOUT_SECONDS = 30        # Timeout for API requests
    
    # ==================== DATA ====================
    KLINES_HISTORY_4H = 100             # Number of 4H candles to fetch
    KLINES_HISTORY_1H = 50              # Number of 1H candles to fetch
    KLINES_HISTORY_15M = 40             # Number of 15M candles to fetch
    
    # ==================== LOGGING ====================
    LOG_FILE = 'bot_v2.log'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ==================== FLASK DASHBOARD ====================
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = int(os.getenv('PORT', 5000))
    FLASK_DEBUG = False
    
    # ==================== NOTION INTEGRATION (Optional) ====================
    NOTION_ENABLED = False                  # Set to True to enable Notion journaling
    NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '')
    
    # ==================== VALIDATION ====================
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        
        if not cls.BITGET_API_KEY or not cls.BITGET_SECRET_KEY:
            print("❌ Error: Missing Bitget API credentials")
            return False
        
        if not cls.TELEGRAM_BOT_TOKEN or not cls.TELEGRAM_CHAT_ID:
            print("⚠️ Warning: Telegram not configured (alerts disabled)")
        
        if cls.RISK_PER_TRADE > cls.MAX_DAILY_LOSS:
            print("❌ Error: RISK_PER_TRADE > MAX_DAILY_LOSS")
            return False
        
        if cls.MIN_SIGNAL_CONFIDENCE < 50 or cls.MIN_SIGNAL_CONFIDENCE > 100:
            print("❌ Error: MIN_SIGNAL_CONFIDENCE must be 50-100")
            return False
        
        print("✅ Configuration validated")
        return True
    
    @classmethod
    def summary(cls) -> str:
        """Print configuration summary"""
        
        summary = f"""
        
╔═══════════════════════════════════════════════╗
║    BITGET TRADING BOT v2.0 - CONFIG SUMMARY   ║
╚═══════════════════════════════════════════════╝

📊 BOT SETTINGS
  Mode: {cls.BOT_MODE.upper()}
  Symbols: {len(cls.SYMBOLS)} coins
  Update interval: 30 minutes

💰 RISK MANAGEMENT
  Risk per trade: ${cls.RISK_PER_TRADE}
  Daily loss limit: ${cls.MAX_DAILY_LOSS}
  Max daily trades: {cls.MAX_DAILY_TRADES}
  Max open positions: {cls.MAX_OPEN_POSITIONS}
  Min confidence: {cls.MIN_SIGNAL_CONFIDENCE}%

⚙️ LEVERAGE STRATEGY
  Dynamic: Based on ATR volatility
    High volatility (ATR > 2x): 3x
    Medium volatility (1.5x-2x): 5x
    Low volatility: 10x

📈 TECHNICAL ANALYSIS
  Timeframes: 4H (trend) + 1H (zone) + 15M (entry)
  Indicators: ADX, EMA, RSI, ATR, Fibonacci
  Confluence min score: {cls.CONFLUENCE_MIN_SCORE}%

⏰ TRADING HOURS
  Active: {cls.TRADING_HOURS_START}:00 - {cls.TRADING_HOURS_END}:00 UTC
  (London + NY sessions)

📱 NOTIFICATIONS
  Telegram: {'✅' if cls.TELEGRAM_BOT_TOKEN else '❌'}
  
✨ EXPERIMENTAL FEATURES
  Notion Journal: {'✅' if cls.NOTION_ENABLED else '❌'}
        
        """
        return summary

# ==================== INITIALIZATION ====================
if __name__ == '__main__':
    config = Config()
    print(config.summary())
    config.validate()
