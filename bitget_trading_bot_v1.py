#!/usr/bin/env python3
"""
BITGET TRADING BOT v1.0 - PROFESSIONAL EDITION
Hybrid ARMY PRO + SMC + ICT Signal System
Author: Benimle
Deployment: Render.com (24/7)
"""

import os
import json
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from enum import Enum

import aiohttp
import requests
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from telebot import TeleBot, types

# Load environment variables
load_dotenv()

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class SignalType(Enum):
    NONE = 0
    LONG = 1
    SHORT = 2

class TrendDirection(Enum):
    UP = 1
    DOWN = -1
    NEUTRAL = 0

# Configuration
CONFIG = {
    'LEVERAGE': 10,
    'RISK_PER_TRADE': 20,  # USD
    'MAX_DAILY_TRADES': 10,
    'MAX_DAILY_LOSS': 20,  # USD
    'INTERVAL': 1800,  # 30 minutes in seconds
    'TOP_COINS': 20,  # Top 20 from top 100
    'TP_RATIO_1': 2,  # 1:2 RR
    'TP_RATIO_2': 4,  # 1:4 RR
}

# ============================================================================
# BITGET API WRAPPER
# ============================================================================

class BitgetAPI:
    """Bitget Futures API wrapper with async support"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://api.bitget.com"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def _sign_request(self, method: str, path: str, body: str = ""):
        """Sign request with Bitget v2 authentication"""
        import hmac
        import hashlib
        from base64 import b64encode
        
        timestamp = str(int(datetime.utcnow().timestamp() * 1000))
        
        message = timestamp + method.upper() + path
        if body:
            message += body
        
        signature = b64encode(
            hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "User-Agent": "Botv1"
        }
        
        return headers
    
    async def get_klines(self, symbol: str, timeframe: str, limit: int = 100) -> List:
        """Fetch candlestick data"""
        try:
            path = f"/api/v2/public/market/candles?symbol={symbol}&granularity={timeframe}&limit={limit}"
            headers = await self._sign_request("GET", path)
            
            async with self.session.get(self.base_url + path, headers=headers) as resp:
                data = await resp.json()
                if data['code'] == '00000':
                    return data['data']
                else:
                    logger.error(f"Bitget error: {data}")
                    return []
        except Exception as e:
            logger.error(f"get_klines error: {e}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current price and 24h info"""
        try:
            path = f"/api/v2/public/market/ticker?symbol={symbol}"
            headers = await self._sign_request("GET", path)
            
            async with self.session.get(self.base_url + path, headers=headers) as resp:
                data = await resp.json()
                if data['code'] == '00000':
                    return data['data'][0]
                return {}
        except Exception as e:
            logger.error(f"get_ticker error: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: str, size: float, 
                         price: Optional[float] = None) -> Dict:
        """
        Place futures order
        side: 'buy' or 'sell'
        """
        try:
            order_type = "market" if price is None else "limit"
            
            body_dict = {
                "symbol": symbol,
                "margin_coin": symbol.split("USDT")[0] + "USDT" if "USDT" in symbol else symbol,
                "order_type": order_type,
                "position_side": "long" if side == "buy" else "short",
                "side": side,
                "size": str(size),
                "price": str(price) if price else ""
            }
            
            body = json.dumps(body_dict)
            path = "/api/v2/mix/orders/place-order"
            headers = await self._sign_request("POST", path, body)
            
            async with self.session.post(
                self.base_url + path, 
                headers=headers, 
                data=body
            ) as resp:
                data = await resp.json()
                if data['code'] == '00000':
                    logger.info(f"Order placed: {symbol} {side} {size}")
                    return data['data']
                else:
                    logger.error(f"Order failed: {data}")
                    return {}
        except Exception as e:
            logger.error(f"place_order error: {e}")
            return {}
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for symbol"""
        try:
            body_dict = {
                "symbol": symbol,
                "leverage": str(leverage)
            }
            body = json.dumps(body_dict)
            path = "/api/v2/mix/account/set-leverage"
            headers = await self._sign_request("POST", path, body)
            
            async with self.session.post(
                self.base_url + path,
                headers=headers,
                data=body
            ) as resp:
                data = await resp.json()
                return data['code'] == '00000'
        except Exception as e:
            logger.error(f"set_leverage error: {e}")
            return False

# ============================================================================
# SIGNAL ENGINE - ARMY PRO + SMC + ICT
# ============================================================================

class SignalEngine:
    """Hybrid signal generation with ARMY PRO + SMC + ICT"""
    
    def __init__(self):
        self.zones = {}  # Store S/D zones per symbol
        
    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        return pd.Series(data).ewm(span=period).mean().values
    
    def _calculate_rsi(self, data: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Relative Strength Index"""
        delta = np.diff(data)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return np.full_like(data, rsi, dtype=float)
    
    def _calculate_macd(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema12 = self._calculate_ema(data, 12)
        ema26 = self._calculate_ema(data, 26)
        macd = ema12 - ema26
        signal = self._calculate_ema(macd, 9)
        return macd, signal
    
    def detect_supply_demand_zones(self, closes: List[float], highs: List[float], 
                                   lows: List[float]) -> Dict:
        """
        Detect Supply/Demand zones using ARMY PRO methodology
        Returns: {'demand': [high, low], 'supply': [high, low]}
        """
        try:
            recent = 50  # Last 50 candles
            closes = np.array(closes[-recent:])
            highs = np.array(highs[-recent:])
            lows = np.array(lows[-recent:])
            
            # Find local minima (demand) and maxima (supply)
            demand_level = np.min(lows[-20:])  # Recent low
            supply_level = np.max(highs[-20:])  # Recent high
            
            # Zone width (ATR-based)
            atr = np.mean(highs[-14:] - lows[-14:])
            
            return {
                'demand': {
                    'high': demand_level + atr * 0.5,
                    'low': demand_level
                },
                'supply': {
                    'high': supply_level,
                    'low': supply_level - atr * 0.5
                },
                'atr': atr
            }
        except Exception as e:
            logger.error(f"Zone detection error: {e}")
            return {}
    
    def detect_contraction(self, opens: List[float], closes: List[float], 
                          highs: List[float], lows: List[float]) -> bool:
        """
        Detect contraction candle (small body + long lower wick)
        ARMY PRO entry signal
        """
        try:
            last_open = opens[-1]
            last_close = closes[-1]
            last_high = highs[-1]
            last_low = lows[-1]
            
            body = abs(last_close - last_open)
            total_range = last_high - last_low
            lower_wick = min(last_open, last_close) - last_low
            
            # Contraction: body < 30% of range, wick > 40% of range
            is_contraction = (
                body < total_range * 0.3 and 
                lower_wick > total_range * 0.4
            )
            
            return is_contraction
        except:
            return False
    
    def detect_bos(self, closes: List[float], period: int = 20) -> Tuple[bool, str]:
        """
        Detect Break of Structure (BOS) - SMC
        Returns: (has_bos, direction)
        """
        try:
            if len(closes) < period + 2:
                return False, "NONE"
            
            recent = closes[-period:]
            prev = closes[-(period + 1):-1]
            
            # BOS Up: recent high > previous high
            # BOS Down: recent low < previous low
            
            recent_high = max(recent)
            recent_low = min(recent)
            prev_high = max(prev)
            prev_low = min(prev)
            
            if recent_high > prev_high and closes[-1] > closes[-2]:
                return True, "BOS_UP"
            elif recent_low < prev_low and closes[-1] < closes[-2]:
                return True, "BOS_DOWN"
            
            return False, "NONE"
        except:
            return False, "NONE"
    
    def analyze_symbol(self, symbol: str, klines_4h: List, 
                      klines_1h: List, klines_15m: List) -> Dict:
        """
        Comprehensive multi-timeframe analysis
        Returns signal confidence and entry/exit levels
        """
        try:
            if not (klines_4h and klines_1h and klines_15m):
                return {'signal': SignalType.NONE, 'confidence': 0}
            
            # Parse candles: [timestamp, open, high, low, close, volume]
            closes_4h = np.array([float(k[4]) for k in klines_4h])
            opens_4h = np.array([float(k[1]) for k in klines_4h])
            highs_4h = np.array([float(k[2]) for k in klines_4h])
            lows_4h = np.array([float(k[3]) for k in klines_4h])
            
            closes_1h = np.array([float(k[4]) for k in klines_1h])
            opens_1h = np.array([float(k[1]) for k in klines_1h])
            highs_1h = np.array([float(k[2]) for k in klines_1h])
            lows_1h = np.array([float(k[3]) for k in klines_1h])
            
            closes_15m = np.array([float(k[4]) for k in klines_15m])
            opens_15m = np.array([float(k[1]) for k in klines_15m])
            highs_15m = np.array([float(k[2]) for k in klines_15m])
            lows_15m = np.array([float(k[3]) for k in klines_15m])
            
            # === 4H ANALYSIS (HTF Bias) ===
            trend_4h = self._analyze_trend(closes_4h)
            zones_4h = self.detect_supply_demand_zones(closes_4h, highs_4h, lows_4h)
            
            # === 1H ANALYSIS (Mid Timeframe) ===
            trend_1h = self._analyze_trend(closes_1h)
            zones_1h = self.detect_supply_demand_zones(closes_1h, highs_1h, lows_1h)
            bos_1h, bos_dir = self.detect_bos(closes_1h)
            
            # === 15M ANALYSIS (Entry Timeframe) ===
            is_contraction_15m = self.detect_contraction(
                opens_15m.tolist(), closes_15m.tolist(),
                highs_15m.tolist(), lows_15m.tolist()
            )
            bos_15m, _ = self.detect_bos(closes_15m, period=10)
            
            # === CONFIRMATION LOGIC ===
            confidence = 0
            signal = SignalType.NONE
            
            # Long setup
            if (trend_4h == TrendDirection.UP and 
                trend_1h == TrendDirection.UP and
                is_contraction_15m and
                closes_15m[-1] > zones_1h.get('demand', {}).get('high', 0)):
                
                confidence = self._calculate_confidence(
                    trend_4h == trend_1h,
                    is_contraction_15m,
                    bos_15m,
                    closes_15m[-1] > zones_1h['demand']['high']
                )
                signal = SignalType.LONG
            
            # Short setup
            elif (trend_4h == TrendDirection.DOWN and 
                  trend_1h == TrendDirection.DOWN and
                  is_contraction_15m and
                  closes_15m[-1] < zones_1h.get('supply', {}).get('low', 1e6)):
                
                confidence = self._calculate_confidence(
                    trend_4h == trend_1h,
                    is_contraction_15m,
                    bos_15m,
                    closes_15m[-1] < zones_1h['supply']['low']
                )
                signal = SignalType.SHORT
            
            return {
                'signal': signal,
                'confidence': confidence,
                'zones_1h': zones_1h,
                'zones_4h': zones_4h,
                'trend_4h': trend_4h,
                'trend_1h': trend_1h,
                'contraction_15m': is_contraction_15m,
                'bos_15m': bos_15m,
                'current_price': float(closes_15m[-1])
            }
        
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {e}")
            return {'signal': SignalType.NONE, 'confidence': 0}
    
    def _analyze_trend(self, closes: np.ndarray) -> TrendDirection:
        """Determine trend using EMA crossover"""
        if len(closes) < 26:
            return TrendDirection.NEUTRAL
        
        ema7 = self._calculate_ema(closes, 7)
        ema25 = self._calculate_ema(closes, 25)
        
        if ema7[-1] > ema25[-1]:
            return TrendDirection.UP
        elif ema7[-1] < ema25[-1]:
            return TrendDirection.DOWN
        else:
            return TrendDirection.NEUTRAL
    
    def _calculate_confidence(self, *factors) -> float:
        """Calculate signal confidence (0-100)"""
        return sum([1 if f else 0 for f in factors]) / len(factors) * 100 if factors else 0

# ============================================================================
# RISK MANAGER
# ============================================================================

class RiskManager:
    """Position sizing, stop-loss, take-profit management"""
    
    def __init__(self, db_path: str = '/tmp/trading.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            entry_time TIMESTAMP,
            entry_price REAL,
            side TEXT,
            size REAL,
            leverage INTEGER,
            sl_price REAL,
            tp1_price REAL,
            tp2_price REAL,
            exit_price REAL,
            exit_time TIMESTAMP,
            pnl REAL,
            status TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats (
            date DATE PRIMARY KEY,
            total_trades INTEGER,
            total_loss REAL,
            total_profit REAL
        )''')
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self) -> Dict:
        """Get today's trading stats"""
        today = datetime.now().date()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            'SELECT total_trades, total_loss FROM daily_stats WHERE date = ?',
            (today,)
        )
        result = c.fetchone()
        conn.close()
        
        if result:
            return {'trades': result[0], 'loss': result[1]}
        return {'trades': 0, 'loss': 0}
    
    def can_trade(self) -> bool:
        """Check if bot can execute trade based on limits"""
        stats = self.get_daily_stats()
        
        if stats['trades'] >= CONFIG['MAX_DAILY_TRADES']:
            logger.warning("Max daily trades reached")
            return False
        
        if stats['loss'] >= CONFIG['MAX_DAILY_LOSS']:
            logger.warning("Max daily loss reached")
            return False
        
        return True
    
    def calculate_position_size(self, entry_price: float, sl_price: float) -> float:
        """
        Calculate position size based on risk
        risk = $20, leverage = 10x
        """
        risk_amount = CONFIG['RISK_PER_TRADE']
        leverage = CONFIG['LEVERAGE']
        
        price_risk = abs(entry_price - sl_price)
        if price_risk == 0:
            return 0
        
        position_size = (risk_amount * leverage) / price_risk
        return round(position_size, 4)
    
    def log_trade(self, symbol: str, side: str, entry_price: float, 
                 sl_price: float, tp1: float, tp2: float, size: float):
        """Log trade to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO trades 
                   (symbol, entry_time, entry_price, side, size, leverage, 
                    sl_price, tp1_price, tp2_price, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (symbol, datetime.now(), entry_price, side, size, 
                  CONFIG['LEVERAGE'], sl_price, tp1, tp2, 'OPEN'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Trade logged: {symbol} {side} @ {entry_price}")

# ============================================================================
# TELEGRAM BOT
# ============================================================================

class TelegramHandler:
    """Telegram notifications and control"""
    
    def __init__(self, token: str, chat_id: str, risk_manager: RiskManager):
        self.bot = TeleBot(token)
        self.chat_id = chat_id
        self.risk_manager = risk_manager
    
    def send_signal(self, symbol: str, signal_type: SignalType, 
                   entry: float, sl: float, tp1: float, tp2: float, 
                   confidence: float):
        """Send signal notification"""
        direction = "🟢 LONG" if signal_type == SignalType.LONG else "🔴 SHORT"
        
        message = f"""
{direction} {symbol}
━━━━━━━━━━━━━━━━━━━━
Confidence: {confidence:.1f}%
Entry: {entry:.8f}
SL: {sl:.8f}
TP1: {tp1:.8f} (1:2)
TP2: {tp2:.8f} (1:4)
━━━━━━━━━━━━━━━━━━━━
Leverage: 10x
Risk: $20
        """
        
        try:
            self.bot.send_message(self.chat_id, message)
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
    
    def send_status(self, text: str):
        """Send status message"""
        try:
            self.bot.send_message(self.chat_id, text)
        except Exception as e:
            logger.error(f"Telegram status error: {e}")

# ============================================================================
# MAIN BOT
# ============================================================================

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        self.signal_engine = SignalEngine()
        self.risk_manager = RiskManager()
        self.telegram = TelegramHandler(
            os.getenv('TELEGRAM_BOT_TOKEN'),
            os.getenv('TELEGRAM_CHAT_ID'),
            self.risk_manager
        )
        
        self.bitget_api = None
        self.monitored_coins = []
        self.last_run = None
    
    async def initialize(self):
        """Initialize bot"""
        api_key = os.getenv('BITGET_API_KEY')
        secret_key = os.getenv('BITGET_SECRET_KEY')
        passphrase = os.getenv('BITGET_PASSPHRASE')
        
        self.bitget_api = BitgetAPI(api_key, secret_key, passphrase)
        
        # Load top coins (you can expand this list)
        self.monitored_coins = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT',
            'ARBUSDT', 'OPUSDT', 'LITUSDT', 'BCUSDT', 'APTUSDT',
            'SUIUSDT', 'PERPUSDT', 'GMXUSDT', 'AAVEUSDT', 'UNIUSDT'
        ]
        
        logger.info(f"Bot initialized. Monitoring {len(self.monitored_coins)} coins")
    
    async def fetch_candles(self, symbol: str, timeframe: str) -> List:
        """Fetch candles from Bitget"""
        async with BitgetAPI(
            os.getenv('BITGET_API_KEY'),
            os.getenv('BITGET_SECRET_KEY'),
            os.getenv('BITGET_PASSPHRASE')
        ) as api:
            # Map timeframe to Bitget format
            tf_map = {'4h': '4h', '1h': '1h', '15m': '15m'}
            return await api.get_klines(symbol, tf_map.get(timeframe, timeframe))
    
    async def analyze_all_coins(self) -> List[Dict]:
        """Analyze all monitored coins"""
        signals = []
        
        async with BitgetAPI(
            os.getenv('BITGET_API_KEY'),
            os.getenv('BITGET_SECRET_KEY'),
            os.getenv('BITGET_PASSPHRASE')
        ) as api:
            
            for symbol in self.monitored_coins:
                try:
                    klines_4h = await api.get_klines(symbol, '4h', limit=100)
                    klines_1h = await api.get_klines(symbol, '1h', limit=100)
                    klines_15m = await api.get_klines(symbol, '15m', limit=100)
                    
                    analysis = self.signal_engine.analyze_symbol(
                        symbol, klines_4h, klines_1h, klines_15m
                    )
                    
                    if analysis['signal'] != SignalType.NONE and analysis['confidence'] > 60:
                        analysis['symbol'] = symbol
                        signals.append(analysis)
                        logger.info(f"Signal found: {symbol} {analysis['signal'].name} "
                                  f"({analysis['confidence']:.1f}%)")
                
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
        
        return signals
    
    async def execute_trade(self, signal: Dict):
        """Execute trade based on signal"""
        if not self.risk_manager.can_trade():
            logger.warning(f"Cannot trade {signal['symbol']}: limits reached")
            return
        
        symbol = signal['symbol']
        side = 'buy' if signal['signal'] == SignalType.LONG else 'sell'
        entry_price = signal['current_price']
        zones = signal['zones_1h']
        
        # Calculate SL & TP
        if signal['signal'] == SignalType.LONG:
            sl_price = zones['demand']['low']
            tp1_price = entry_price + (entry_price - sl_price) * CONFIG['TP_RATIO_1']
            tp2_price = entry_price + (entry_price - sl_price) * CONFIG['TP_RATIO_2']
        else:
            sl_price = zones['supply']['high']
            tp1_price = entry_price - (sl_price - entry_price) * CONFIG['TP_RATIO_1']
            tp2_price = entry_price - (sl_price - entry_price) * CONFIG['TP_RATIO_2']
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(entry_price, sl_price)
        
        if position_size == 0:
            logger.error(f"Invalid position size for {symbol}")
            return
        
        # Log trade
        self.risk_manager.log_trade(
            symbol, side, entry_price, sl_price, tp1_price, tp2_price, position_size
        )
        
        # Send Telegram notification
        self.telegram.send_signal(
            symbol, signal['signal'], entry_price, sl_price, tp1_price, tp2_price,
            signal['confidence']
        )
        
        logger.info(f"Trade prepared: {symbol} {side} {position_size} @ {entry_price}")
        
        # TODO: Execute actual order on Bitget (enable in live mode)
        # async with self.bitget_api as api:
        #     await api.set_leverage(symbol, CONFIG['LEVERAGE'])
        #     await api.place_order(symbol, side, position_size)
    
    async def main_loop(self):
        """Main bot loop - runs every 30 minutes"""
        await self.initialize()
        
        logger.info("Starting main loop...")
        
        while True:
            try:
                logger.info(f"Analysis cycle started at {datetime.now()}")
                
                # Analyze all coins
                signals = await self.analyze_all_coins()
                
                # Execute trades
                for signal in signals:
                    await self.execute_trade(signal)
                
                logger.info(f"Analysis cycle completed. Found {len(signals)} signals")
                
                # Sleep for 30 minutes
                await asyncio.sleep(CONFIG['INTERVAL'])
            
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)

# ============================================================================
# FLASK WEB DASHBOARD
# ============================================================================

app = Flask(__name__)
CORS(app)

bot_instance = None

@app.route('/api/status')
def get_status():
    """Get bot status"""
    try:
        stats = bot_instance.risk_manager.get_daily_stats()
        return jsonify({
            'status': 'running',
            'last_update': datetime.now().isoformat(),
            'daily_trades': stats['trades'],
            'daily_loss': stats['loss'],
            'max_trades': CONFIG['MAX_DAILY_TRADES'],
            'max_loss': CONFIG['MAX_DAILY_LOSS'],
            'leverage': CONFIG['LEVERAGE'],
            'risk_per_trade': CONFIG['RISK_PER_TRADE']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    try:
        conn = sqlite3.connect('/tmp/trading.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM trades ORDER BY entry_time DESC LIMIT 20')
        trades = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify(trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bitget Trading Bot</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .stat-card { background: #333; padding: 15px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
            th { background: #2a2a2a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bitget Trading Bot v1.0</h1>
            <div class="status">
                <h2>Status</h2>
                <div id="status-content">Loading...</div>
            </div>
            <h2>Recent Trades</h2>
            <table id="trades-table">
                <tr>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Entry Price</th>
                    <th>Entry Time</th>
                    <th>Status</th>
                </tr>
            </table>
        </div>
        <script>
            async function updateStatus() {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('status-content').innerHTML = `
                    <div class="stats">
                        <div class="stat-card">
                            <strong>Status:</strong> ${data.status}
                        </div>
                        <div class="stat-card">
                            <strong>Daily Trades:</strong> ${data.daily_trades}/${data.max_trades}
                        </div>
                        <div class="stat-card">
                            <strong>Daily Loss:</strong> $${data.daily_loss}/$${data.max_loss}
                        </div>
                        <div class="stat-card">
                            <strong>Leverage:</strong> ${data.leverage}x
                        </div>
                    </div>
                `;
            }
            
            async function updateTrades() {
                const res = await fetch('/api/trades');
                const data = await res.json();
                const tbody = document.getElementById('trades-table');
                data.forEach(trade => {
                    const row = `<tr>
                        <td>${trade.symbol}</td>
                        <td>${trade.side}</td>
                        <td>${trade.entry_price}</td>
                        <td>${new Date(trade.entry_time).toLocaleString()}</td>
                        <td>${trade.status}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            }
            
            updateStatus();
            updateTrades();
            setInterval(updateStatus, 5000);
        </script>
    </body>
    </html>
    '''

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    bot_instance = TradingBot()
    
    # Start Flask in background thread
    import threading
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False),
        daemon=True
    )
    flask_thread.start()
    
    # Run async bot loop
    asyncio.run(bot_instance.main_loop())
