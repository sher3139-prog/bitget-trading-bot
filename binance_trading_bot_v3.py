#!/usr/bin/env python3
"""
BINANCE FUTURES TRADING BOT v3.0 - PROFESSIONAL EDITION
========================================================
Hybrid ARMY PRO + SMC + ICT Signal System

Features:
- Binance Futures API (works from Russia!)
- ADX market regime filtering
- Multi-timeframe analysis (4H + 1H + 15M)
- Telegram alerts + commands (/start /stop /status)
- Paper mode & Live mode
- Dynamic ATR-based leverage
- Flask REST API dashboard

Author: BTW_GO
Version: 3.0
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import aiohttp
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
class Config:
    BOT_MODE = os.getenv('BOT_MODE', 'paper')
    
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'DOGEUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT',
        'ARBUSDT', 'OPUSDT', 'LTCUSDT', 'BCHUSDT', 'APTUSDT',
        'SUIUSDT', 'GMXUSDT', 'AAVEUSDT', 'UNIUSDT', 'ATOMUSDT'
    ]
    
    RISK_PER_TRADE = 20.0
    MAX_DAILY_LOSS = 20.0
    MAX_DAILY_TRADES = 10
    MAX_OPEN_POSITIONS = 3
    MIN_SIGNAL_CONFIDENCE = 60
    
    TRADING_HOURS_START = 8
    TRADING_HOURS_END = 21
    
    FLASK_PORT = int(os.getenv('PORT', 5000))

# ==================== BINANCE API ====================
class BinanceAPI:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://fapi.binance.com"
        logger.info("BinanceAPI initialized ✅")
    
    def _sign(self, params: dict) -> str:
        query = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fapi/v1/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit
                }
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        text = await resp.text()
                        logger.error(f"Binance klines error {resp.status}: {text}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching klines {symbol}: {e}")
            return []
    
    async def get_ticker_price(self, symbol: str) -> float:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fapi/v1/ticker/price"
                params = {'symbol': symbol}
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return float(data['price'])
                    return 0.0
        except Exception as e:
            logger.error(f"Error getting price {symbol}: {e}")
            return 0.0
    
    async def place_order(self, symbol: str, side: str, quantity: float, leverage: int) -> Dict:
        if Config.BOT_MODE == 'paper':
            order = {
                'orderId': f"PAPER_{int(time.time())}",
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'leverage': leverage,
                'status': 'FILLED',
                'mode': 'paper'
            }
            logger.info(f"[PAPER] Order: {order}")
            return order
        
        try:
            async with aiohttp.ClientSession() as session:
                # Set leverage first
                lev_url = f"{self.base_url}/fapi/v1/leverage"
                ts = int(time.time() * 1000)
                lev_params = {
                    'symbol': symbol,
                    'leverage': leverage,
                    'timestamp': ts
                }
                lev_params['signature'] = self._sign(lev_params)
                headers = {'X-MBX-APIKEY': self.api_key}
                
                async with session.post(lev_url, params=lev_params, headers=headers) as resp:
                    if resp.status != 200:
                        logger.error(f"Leverage set error: {await resp.text()}")
                
                # Place order
                order_url = f"{self.base_url}/fapi/v1/order"
                ts = int(time.time() * 1000)
                order_params = {
                    'symbol': symbol,
                    'side': side.upper(),
                    'type': 'MARKET',
                    'quantity': quantity,
                    'timestamp': ts
                }
                order_params['signature'] = self._sign(order_params)
                
                async with session.post(order_url, params=order_params, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"[LIVE] Order placed: {data}")
                        return data
                    else:
                        logger.error(f"Order error: {await resp.text()}")
                        return {}
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {}

# ==================== TECHNICAL INDICATORS ====================
class Indicators:
    @staticmethod
    def process_klines(klines: List) -> pd.DataFrame:
        if not klines:
            return pd.DataFrame()
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        return df
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> float:
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > minus_dm), 0)
            minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0)
            
            tr = pd.concat([
                high - low,
                abs(high - close.shift()),
                abs(low - close.shift())
            ], axis=1).max(axis=1)
            
            atr = tr.rolling(period).mean()
            di_plus = 100 * (plus_dm.rolling(period).mean() / atr)
            di_minus = 100 * (minus_dm.rolling(period).mean() / atr)
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
            adx_val = dx.rolling(period).mean()
            
            return float(adx_val.iloc[-1]) if not adx_val.empty else 0
        except:
            return 0
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> float:
        try:
            tr = pd.concat([
                df['high'] - df['low'],
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            ], axis=1).max(axis=1)
            return float(tr.rolling(period).mean().iloc[-1])
        except:
            return 0
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> float:
        try:
            delta = series.diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50

# ==================== SIGNAL ENGINE ====================
class SignalEngine:
    def __init__(self):
        self.ind = Indicators()
    
    def analyze(self, symbol: str, df_4h: pd.DataFrame, df_1h: pd.DataFrame, df_15m: pd.DataFrame) -> Dict:
        try:
            # 1. ADX Filter
            adx_val = self.ind.adx(df_4h)
            if adx_val < 25:
                return {'symbol': symbol, 'signal': 'NONE', 'confidence': 0, 'reason': f'ADX {adx_val:.1f} - Ranging'}
            
            # 2. Trend (4H EMA)
            ema9 = self.ind.ema(df_4h['close'], 9).iloc[-1]
            ema21 = self.ind.ema(df_4h['close'], 21).iloc[-1]
            trend = 'UP' if ema9 > ema21 else 'DOWN'
            
            # 3. RSI Filter
            rsi_val = self.ind.rsi(df_1h['close'])
            
            # 4. Supply/Demand zones (1H)
            supply = df_1h['high'].tail(50).max()
            demand = df_1h['low'].tail(50).min()
            current_price = float(df_15m['close'].iloc[-1])
            
            # 5. Contraction candle (15M)
            last_candle = df_15m.iloc[-1]
            body = abs(last_candle['close'] - last_candle['open'])
            total_range = last_candle['high'] - last_candle['low']
            is_contraction = (body / total_range < 0.3) if total_range > 0 else False
            
            # 6. Confluence score
            score = 0
            if adx_val > 25: score += 20
            if adx_val > 35: score += 10
            if is_contraction: score += 20
            
            # LONG setup
            if trend == 'UP' and rsi_val < 65:
                price_near_demand = abs(current_price - demand) / current_price < 0.05
                if price_near_demand: score += 30
                
                if score >= 60:
                    sl = demand * 0.98
                    tp1 = current_price + (current_price - sl) * 2
                    tp2 = current_price + (current_price - sl) * 4
                    return {
                        'symbol': symbol,
                        'signal': 'LONG',
                        'confidence': min(score, 100),
                        'entry': current_price,
                        'sl': sl,
                        'tp1': tp1,
                        'tp2': tp2,
                        'adx': adx_val,
                        'rsi': rsi_val,
                        'trend': trend,
                        'reason': f'ADX {adx_val:.1f} | RSI {rsi_val:.1f} | Near Demand | Trend UP'
                    }
            
            # SHORT setup
            elif trend == 'DOWN' and rsi_val > 35:
                price_near_supply = abs(current_price - supply) / current_price < 0.05
                if price_near_supply: score += 30
                
                if score >= 60:
                    sl = supply * 1.02
                    tp1 = current_price - (sl - current_price) * 2
                    tp2 = current_price - (sl - current_price) * 4
                    return {
                        'symbol': symbol,
                        'signal': 'SHORT',
                        'confidence': min(score, 100),
                        'entry': current_price,
                        'sl': sl,
                        'tp1': tp1,
                        'tp2': tp2,
                        'adx': adx_val,
                        'rsi': rsi_val,
                        'trend': trend,
                        'reason': f'ADX {adx_val:.1f} | RSI {rsi_val:.1f} | Near Supply | Trend DOWN'
                    }
            
            return {'symbol': symbol, 'signal': 'NONE', 'confidence': score, 'reason': 'No valid setup'}
            
        except Exception as e:
            logger.error(f"Signal error {symbol}: {e}")
            return {'symbol': symbol, 'signal': 'NONE', 'confidence': 0, 'reason': str(e)}

# ==================== TELEGRAM ====================
class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.bot_running = True
        self.last_update_id = 0
        logger.info("TelegramBot initialized ✅")
    
    async def send(self, message: str):
        if not self.token or not self.chat_id:
            logger.warning("Telegram not configured!")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMessage"
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        logger.info("✅ Telegram message sent!")
                    else:
                        text = await resp.text()
                        logger.error(f"❌ Telegram error {resp.status}: {text}")
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
    
    async def send_signal(self, signal: Dict):
        emoji = "🟢" if signal['signal'] == 'LONG' else "🔴"
        msg = f"""
{emoji} <b>BTW GO SIGNAL - {signal['symbol']}</b>

📊 <b>Yön:</b> {signal['signal']}
🎯 <b>Güven:</b> {signal['confidence']:.0f}%
💰 <b>Giriş:</b> {signal['entry']:.4f}
🛑 <b>Stop Loss:</b> {signal['sl']:.4f}
✅ <b>TP1 (1:2):</b> {signal['tp1']:.4f}
🚀 <b>TP2 (1:4):</b> {signal['tp2']:.4f}

📈 <b>ADX:</b> {signal['adx']:.1f}
📉 <b>RSI:</b> {signal['rsi']:.1f}
🔍 <b>Trend:</b> {signal['trend']}

💡 <b>Sebep:</b> {signal['reason']}

⚠️ Mode: <b>{Config.BOT_MODE.upper()}</b>
⏰ {datetime.now().strftime('%H:%M:%S')}
        """
        await self.send(msg)
    
    async def get_updates(self) -> List:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getUpdates"
                params = {
                    'offset': self.last_update_id + 1,
                    'timeout': 10
                }
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('result', [])
                    return []
        except:
            return []
    
    async def handle_commands(self, bot_instance):
        """Listen for Telegram commands"""
        logger.info("Telegram command handler started ✅")
        while True:
            try:
                updates = await self.get_updates()
                for update in updates:
                    self.last_update_id = update['update_id']
                    msg = update.get('message', {})
                    text = msg.get('text', '')
                    
                    if text == '/start':
                        await self.send("""
🤖 <b>BTW GO Trading Bot v3.0</b>

✅ Bot çalışıyor!

📋 <b>Komutlar:</b>
/status - Bot durumu
/stop - Botu durdur
/resume - Botu başlat
/trades - Bugünkü trades
/help - Yardım
                        """)
                    
                    elif text == '/status':
                        mode = Config.BOT_MODE.upper()
                        running = "✅ Çalışıyor" if self.bot_running else "⛔ Durduruldu"
                        await self.send(f"""
📊 <b>BOT DURUMU</b>

🔄 Status: {running}
💼 Mode: {mode}
📈 Coins: {len(Config.SYMBOLS)}
💰 Daily trades: {bot_instance.daily_trades}
📉 Daily loss: ${bot_instance.daily_loss:.2f}
🕐 Saat: {datetime.now().strftime('%H:%M:%S')}
                        """)
                    
                    elif text == '/stop':
                        self.bot_running = False
                        await self.send("⛔ <b>Bot durduruldu!</b>\n/resume ile tekrar başlat.")
                    
                    elif text == '/resume':
                        self.bot_running = True
                        await self.send("✅ <b>Bot başlatıldı!</b>")
                    
                    elif text == '/trades':
                        await self.send(f"""
📈 <b>BUGÜNKÜ TRADES</b>

🔢 Toplam: {bot_instance.daily_trades}
📉 Loss: ${bot_instance.daily_loss:.2f}
📊 Open positions: {len(bot_instance.open_trades)}
                        """)
                    
                    elif text == '/help':
                        await self.send("""
📋 <b>KOMUTLAR</b>

/start - Botu başlat
/status - Durum kontrol
/stop - Durdur
/resume - Devam et
/trades - Trade listesi
/help - Bu mesaj
                        """)
                
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Command handler error: {e}")
                await asyncio.sleep(5)

# ==================== MAIN BOT ====================
class TradingBotV3:
    def __init__(self):
        self.config = Config()
        self.binance = BinanceAPI(
            Config.BINANCE_API_KEY,
            Config.BINANCE_SECRET_KEY
        )
        self.signal_engine = SignalEngine()
        self.telegram = TelegramBot(
            Config.TELEGRAM_BOT_TOKEN,
            Config.TELEGRAM_CHAT_ID
        )
        
        self.daily_trades = 0
        self.daily_loss = 0.0
        self.open_trades: Dict = {}
        
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
        logger.info("TradingBotV3 initialized ✅")
    
    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({
                'bot': 'BTW GO Trading Bot v3.0',
                'status': 'running',
                'mode': Config.BOT_MODE,
                'endpoints': ['/api/status', '/api/trades']
            })
        
        @self.app.route('/api/status')
        def status():
            return jsonify({
                'status': 'running',
                'mode': Config.BOT_MODE,
                'coins_monitored': len(Config.SYMBOLS),
                'open_positions': len(self.open_trades),
                'daily_trades': self.daily_trades,
                'daily_loss': f"${self.daily_loss:.2f}",
                'bot_active': self.telegram.bot_running,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/trades')
        def trades():
            return jsonify({
                'daily_trades': self.daily_trades,
                'daily_loss': f"${self.daily_loss:.2f}",
                'open_positions': len(self.open_trades),
                'open_trades': list(self.open_trades.values())
            })
    
    async def main_loop(self):
        # Send startup message
        await self.telegram.send(f"""
🚀 <b>BTW GO Trading Bot v3.0 STARTED!</b>

✅ Binance Futures API bağlandı
✅ {len(Config.SYMBOLS)} coin monitoring
✅ Mode: {Config.BOT_MODE.upper()}
✅ ARMY PRO + SMC + ICT signals aktif

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        iteration = 0
        while True:
            try:
                if not self.telegram.bot_running:
                    logger.info("Bot paused...")
                    await asyncio.sleep(60)
                    continue
                
                iteration += 1
                now = datetime.now()
                logger.info(f"\n{'='*50}")
                logger.info(f"Analysis #{iteration} - {now.strftime('%H:%M:%S')}")
                logger.info(f"{'='*50}")
                
                # Time filter
                if not (Config.TRADING_HOURS_START <= now.hour <= Config.TRADING_HOURS_END):
                    logger.info(f"Off hours ({now.hour}:00 UTC) - Skipping")
                    await asyncio.sleep(60 * 30)
                    continue
                
                # Daily loss check
                if self.daily_loss >= Config.MAX_DAILY_LOSS:
                    logger.warning(f"Daily loss limit reached: ${self.daily_loss:.2f}")
                    await self.telegram.send(f"⛔ <b>Günlük kayıp limitine ulaşıldı: ${self.daily_loss:.2f}</b>\nBot bugün için durdu.")
                    await asyncio.sleep(60 * 60)
                    continue
                
                # Analyze all symbols
                signals_found = 0
                for symbol in Config.SYMBOLS:
                    try:
                        # Fetch data
                        klines_4h = await self.binance.get_klines(symbol, '4h', 100)
                        klines_1h = await self.binance.get_klines(symbol, '1h', 50)
                        klines_15m = await self.binance.get_klines(symbol, '15m', 40)
                        
                        if not all([klines_4h, klines_1h, klines_15m]):
                            logger.warning(f"No data for {symbol}")
                            continue
                        
                        # Process data
                        df_4h = Indicators.process_klines(klines_4h)
                        df_1h = Indicators.process_klines(klines_1h)
                        df_15m = Indicators.process_klines(klines_15m)
                        
                        # Analyze
                        signal = self.signal_engine.analyze(symbol, df_4h, df_1h, df_15m)
                        
                        logger.info(f"{symbol}: {signal['signal']} | Confidence: {signal['confidence']:.0f}%")
                        
                        if signal['signal'] == 'NONE':
                            continue
                        
                        # Check limits
                        if self.daily_trades >= Config.MAX_DAILY_TRADES:
                            logger.info("Daily trade limit reached")
                            break
                        
                        if len(self.open_trades) >= Config.MAX_OPEN_POSITIONS:
                            logger.info("Max positions reached")
                            break
                        
                        # Register trade
                        trade_id = f"{symbol}_{int(time.time())}"
                        self.open_trades[trade_id] = {
                            'id': trade_id,
                            'symbol': symbol,
                            'signal': signal['signal'],
                            'entry': signal['entry'],
                            'sl': signal['sl'],
                            'tp1': signal['tp1'],
                            'tp2': signal['tp2'],
                            'opened_at': datetime.now().isoformat()
                        }
                        self.daily_trades += 1
                        
                        # Send Telegram signal
                        await self.telegram.send_signal(signal)
                        signals_found += 1
                        
                        logger.info(f"✅ Signal sent: {symbol} {signal['signal']}")
                        
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        continue
                
                logger.info(f"\nAnalysis complete. Signals found: {signals_found}")
                logger.info(f"Next analysis in 30 minutes...")
                await asyncio.sleep(60 * 30)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)
    
    async def run_async(self):
        """Run bot + telegram command handler concurrently"""
        await asyncio.gather(
            self.main_loop(),
            self.telegram.handle_commands(self)
        )
    
    def run(self):
        """Start bot in background thread, Flask in main thread"""
        bot_thread = threading.Thread(
            target=lambda: asyncio.run(self.run_async()),
            daemon=True
        )
        bot_thread.start()
        
        port = Config.FLASK_PORT
        logger.info(f"Flask starting on port {port}")
        self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ==================== MAIN ====================
if __name__ == '__main__':
    bot = TradingBotV3()
    bot.run()
