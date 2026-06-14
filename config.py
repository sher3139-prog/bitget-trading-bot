"""
Configuration file for Bitget Trading Bot v1.0
Centralized settings management
"""

import os
from enum import Enum
from typing import List, Dict

# ============================================================================
# BOT CONFIGURATION
# ============================================================================

class BotMode(Enum):
    """Bot operating modes"""
    PAPER = "paper"      # Dry run - no real trades
    LIVE = "live"        # Execute real trades
    BACKTEST = "backtest"

# Get mode from environment
BOT_MODE = BotMode(os.getenv('BOT_MODE', 'paper'))

# ============================================================================
# TRADING CONFIGURATION
# ============================================================================

TRADING_CONFIG = {
    # Leverage & Risk
    'LEVERAGE': 10,              # 10x leverage
    'RISK_PER_TRADE': 20,       # $20 risk per trade
    'MAX_DAILY_TRADES': 10,     # Max trades per day
    'MAX_DAILY_LOSS': 20,       # Max loss per day ($)
    
    # Timeframes & Intervals
    'INTERVAL': 1800,           # Analysis interval: 30 min (seconds)
    'HTF': '4h',               # Higher timeframe
    'MTF': '1h',               # Middle timeframe
    'ETF': '15m',              # Entry timeframe
    
    # Position Sizing
    'TP_RATIO_1': 2,           # First take profit 1:2 RR
    'TP_RATIO_2': 4,           # Second take profit 1:4 RR
    'PARTIAL_CLOSE_1': 0.5,    # Close 50% at TP1
    'PARTIAL_CLOSE_2': 0.5,    # Close 50% at TP2
    
    # Signal Thresholds
    'MIN_CONFIDENCE': 60,       # Minimum signal confidence (%)
    'TREND_EMA_SHORT': 7,       # Fast EMA period
    'TREND_EMA_LONG': 25,       # Slow EMA period
    'RSI_PERIOD': 14,           # RSI period
    'MACD_FAST': 12,            # MACD fast EMA
    'MACD_SLOW': 26,            # MACD slow EMA
    'MACD_SIGNAL': 9,           # MACD signal line
    
    # Zone Detection
    'ZONE_LOOKBACK': 50,        # Candles to analyze for zones
    'ZONE_RECENT': 20,          # Recent candles for current level
    'ZONE_WIDTH_MULTIPLIER': 0.5,  # ATR multiplier for zone width
}

# ============================================================================
# COINS TO MONITOR (Top 20 from top 100)
# ============================================================================

MONITORED_COINS = [
    # Tier 1 - Major caps (BTC, ETH)
    'BTCUSDT',
    'ETHUSDT',
    
    # Tier 2 - Large caps
    'BNBUSDT',
    'SOLUSDT',
    'XRPUSDT',
    'ADAUSDT',
    'DOGEUSDT',
    'AVAXUSDT',
    
    # Tier 3 - Mid caps
    'LINKUSDT',
    'MATICUSDT',
    'ARBUSDT',
    'OPUSDT',
    'LITUSDT',
    'BCUSDT',
    'APTUSDT',
    'SUIUSDT',
    'PERPUSDT',
    'GMXUSDT',
    
    # Tier 4 - DeFi
    'AAVEUSDT',
    'UNIUSDT',
]

# Extended coin list (available for expansion)
EXTENDED_COINS = [
    'FILUSDT', 'ATOMUSDT', 'NEARUSDT', 'GALAUSDT', 'ENSUSDT',
    'WIFUSDT', 'NOTUSDT', 'JUPUSDT', 'DOGUSDT', 'PEPEUSDT',
    'SANDUSDT', 'MANAUSDT', 'AXLUSDT', 'ETHFIUSDT', 'ARUSDT',
]

# ============================================================================
# BITGET API CONFIGURATION
# ============================================================================

BITGET_CONFIG = {
    'BASE_URL': 'https://api.bitget.com',
    'API_VERSION': 'v2',
    'ENDPOINTS': {
        'KLINES': '/api/v2/public/market/candles',
        'TICKER': '/api/v2/public/market/ticker',
        'PLACE_ORDER': '/api/v2/mix/orders/place-order',
        'CANCEL_ORDER': '/api/v2/mix/orders/cancel-order',
        'ACCOUNT_INFO': '/api/v2/mix/account/account',
        'SET_LEVERAGE': '/api/v2/mix/account/set-leverage',
        'POSITIONS': '/api/v2/mix/positions',
    },
    'TIMEFRAME_MAP': {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '4h': '4h',
        '12h': '12h',
        '1d': '1d',
    }
}

# ============================================================================
# SIGNAL PARAMETERS (ARMY PRO + SMC + ICT)
# ============================================================================

SIGNAL_CONFIG = {
    # ARMY PRO Settings
    'ARMY': {
        'CONTRACTION_BODY_RATIO': 0.3,      # Body < 30% of range
        'CONTRACTION_WICK_RATIO': 0.4,      # Wick > 40% of range
        'DEMAND_ZONE_LOOKBACK': 20,         # Recent candles for demand
        'SUPPLY_ZONE_LOOKBACK': 20,         # Recent candles for supply
    },
    
    # SMC Settings
    'SMC': {
        'BOS_LOOKBACK': 20,                 # Candles to check for BOS
        'CHoCH_CONFIRMATION': True,         # Require CHoCH confirmation
        'OB_DETECTION': True,               # Detect Order Blocks
    },
    
    # ICT Settings
    'ICT': {
        'REQUIRE_4H_BIAS': True,            # Require 4H trend confirmation
        '4H_LOOKBACK': 100,                 # 4H candles to analyze
        '1H_LOOKBACK': 100,                 # 1H candles to analyze
        '15M_LOOKBACK': 100,                # 15M candles to analyze
        'MULTI_TF_WEIGHT': {
            '4h': 0.4,                      # 40% weight
            '1h': 0.35,                     # 35% weight
            '15m': 0.25,                    # 25% weight
        }
    }
}

# ============================================================================
# TELEGRAM CONFIGURATION
# ============================================================================

TELEGRAM_CONFIG = {
    'SEND_SIGNAL_ALERTS': True,
    'SEND_TRADE_ALERTS': True,
    'SEND_ERROR_ALERTS': True,
    'SEND_STATUS_UPDATES': True,
    'STATUS_INTERVAL': 3600,  # Every hour
    
    'MESSAGES': {
        'LONG_SIGNAL': '🟢 LONG {symbol}\n━━━━━━━━━━━━━\nConfidence: {confidence}%\nEntry: {entry}\nSL: {sl}\nTP1: {tp1}\nTP2: {tp2}',
        'SHORT_SIGNAL': '🔴 SHORT {symbol}\n━━━━━━━━━━━━━\nConfidence: {confidence}%\nEntry: {entry}\nSL: {sl}\nTP1: {tp1}\nTP2: {tp2}',
        'TRADE_OPENED': '✅ Trade Opened\n{symbol} {side} {size} @ {price}',
        'TRADE_CLOSED': '🏁 Trade Closed\n{symbol} PnL: ${pnl}',
        'DAILY_LIMIT': '⚠️ Daily limit reached\n{reason}',
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': '/tmp/bot.log',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'CONSOLE_OUTPUT': True,
    'FILE_OUTPUT': True,
    'MAX_LOG_SIZE': 10 * 1024 * 1024,  # 10 MB
    'LOG_BACKUP_COUNT': 5,
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_CONFIG = {
    'PATH': '/tmp/trading.db',
    'BACKUP_PATH': '/tmp/trading_backup.db',
    'ENABLE_BACKUP': True,
    'BACKUP_INTERVAL': 86400,  # Daily
}

# ============================================================================
# PERFORMANCE & OPTIMIZATION
# ============================================================================

PERFORMANCE_CONFIG = {
    'ASYNC_REQUESTS': True,
    'REQUEST_TIMEOUT': 10,              # seconds
    'MAX_CONCURRENT_API_CALLS': 5,
    'RATE_LIMIT_CALLS': 100,           # per minute
    'CACHE_ENABLED': True,
    'CACHE_DURATION': 60,              # seconds
}

# ============================================================================
# SAFETY LIMITS
# ============================================================================

SAFETY_CONFIG = {
    # Hard limits - never override
    'MAX_LEVERAGE': 20,                 # Never exceed 20x
    'MIN_RISK_AMOUNT': 5,               # Min $5
    'MAX_RISK_AMOUNT': 100,             # Max $100 per trade
    'MIN_POSITION_SIZE': 0.001,         # Minimum position
    'MAX_DAILY_LEVERAGE': 5,            # Max 5x on daily trades
    
    # Circuit breakers
    'STOP_ON_CONSECUTIVE_LOSSES': 3,   # Stop after 3 losses
    'STOP_ON_DAILY_LOSS': True,         # Stop if daily loss reached
    'STOP_ON_DRAWDOWN': 30,             # % drawdown
    
    # Verification
    'REQUIRE_MANUAL_APPROVAL': False,   # Require approval for trades
    'DRY_RUN_FIRST': True,              # Paper trading before live
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config(section: str, key: str = None):
    """Get configuration by section and key"""
    configs = {
        'trading': TRADING_CONFIG,
        'bitget': BITGET_CONFIG,
        'signal': SIGNAL_CONFIG,
        'telegram': TELEGRAM_CONFIG,
        'logging': LOGGING_CONFIG,
        'database': DATABASE_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'safety': SAFETY_CONFIG,
    }
    
    config = configs.get(section.lower())
    if config is None:
        raise ValueError(f"Unknown config section: {section}")
    
    if key:
        return config.get(key)
    return config

def get_coins_list(tier: str = 'all') -> List[str]:
    """Get coin list by tier"""
    if tier.lower() == 'main':
        return MONITORED_COINS[:10]
    elif tier.lower() == 'extended':
        return MONITORED_COINS + EXTENDED_COINS
    else:
        return MONITORED_COINS

def validate_config() -> bool:
    """Validate configuration consistency"""
    errors = []
    
    # Check leverage limits
    if TRADING_CONFIG['LEVERAGE'] > SAFETY_CONFIG['MAX_LEVERAGE']:
        errors.append(f"Leverage {TRADING_CONFIG['LEVERAGE']} exceeds max {SAFETY_CONFIG['MAX_LEVERAGE']}")
    
    # Check risk limits
    if not (SAFETY_CONFIG['MIN_RISK_AMOUNT'] <= 
            TRADING_CONFIG['RISK_PER_TRADE'] <= 
            SAFETY_CONFIG['MAX_RISK_AMOUNT']):
        errors.append(f"Risk amount out of bounds: {TRADING_CONFIG['RISK_PER_TRADE']}")
    
    # Check limits
    if TRADING_CONFIG['MAX_DAILY_LOSS'] > 1000:
        errors.append("Very high daily loss limit")
    
    if errors:
        for error in errors:
            print(f"❌ Config Error: {error}")
        return False
    
    return True

if __name__ == '__main__':
    print("🔧 Configuration Validation")
    print("=" * 50)
    
    if validate_config():
        print("✅ Configuration is valid")
        print(f"\nBot Mode: {BOT_MODE.value}")
        print(f"Leverage: {TRADING_CONFIG['LEVERAGE']}x")
        print(f"Risk/Trade: ${TRADING_CONFIG['RISK_PER_TRADE']}")
        print(f"Monitored Coins: {len(MONITORED_COINS)}")
        print(f"Max Daily Trades: {TRADING_CONFIG['MAX_DAILY_TRADES']}")
        print(f"Max Daily Loss: ${TRADING_CONFIG['MAX_DAILY_LOSS']}")
    else:
        print("❌ Configuration has errors")
