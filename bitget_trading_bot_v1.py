#!/usr/bin/env python3
"""
BITGET TRADING BOT v2.0 - PROFESSIONAL EDITION
==============================================
Hybrid ARMY PRO + SMC + ICT Signal System with Advanced Filters

Features:
- ADX-based market regime filtering (trending/ranging detection)
- Confluence zones for higher accuracy
- ATR-based dynamic leverage (volatility adjusted)
- Time-based filters (London/NY session priority)
- Trade validity counter (max bars auto-close)
- Notion integration for trade journaling
- Professional logging and error handling
- Telegram real-time alerts
- Flask REST API dashboard

Author: BTW_GO
Version: 2.0
Status: PAPER MODE (Test only)
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from config_v2 import Config
from utils_v2 import (
    TechnicalIndicators,
    PriceAction,
    RiskCalculations,
    DataProcessor,
    ConfluenceAnalyzer,
)

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== BITGET API CLIENT ====================
class BitgetAPI:
    """Bitget Futures API v2 client with async support"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://api.bitget.com"
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("BitgetAPI initialized")
    
    async def get_klines(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Fetch OHLCV candles from Bitget"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v2/mix/market/candles"
                params = {
                    'symbol': symbol,
                    'granularity': timeframe,
                    'limit': limit
                }
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('data', [])
                    else:
                        logger.error(f"Bitget API error: {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return []
    
    async def place_order(self, symbol: str, side: str, size: float, leverage: int) -> Dict:
        """Place futures order (paper mode simulation)"""
        try:
            # In paper mode, simulate order placement
            order = {
                'orderId': f"PAPER_{datetime.now().timestamp()}",
                'symbol': symbol,
                'side': side,
                'size': size,
                'leverage': leverage,
                'timestamp': datetime.now().isoformat(),
                'status': 'filled',
                'mode': 'paper'  # Paper mode marker
            }
            logger.info(f"[PAPER] Order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {}
    
    async def close_position(self, symbol: str, side: str) -> Dict:
        """Close position (paper mode simulation)"""
        try:
            close_order = {
                'orderId': f"PAPER_CLOSE_{datetime.now().timestamp()}",
                'symbol': symbol,
                'side': 'sell' if side == 'long' else 'buy',
                'status': 'closed',
                'timestamp': datetime.now().isoformat(),
                'mode': 'paper'
            }
            logger.info(f"[PAPER] Position closed: {close_order}")
            return close_order
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return {}

# ==================== SIGNAL ENGINE V2 ====================
class SignalEngineV2:
    """
    Advanced signal engine with:
    - ADX market regime filtering
    - Confluence zone analysis
    - Multi-timeframe confirmation
    - Professional scoring system
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.indicators = TechnicalIndicators()
        self.price_action = PriceAction()
        self.confluence = ConfluenceAnalyzer()
        self.data_processor = DataProcessor()
        logger.info("SignalEngineV2 initialized")
    
    def analyze_symbol(
        self, 
        symbol: str, 
        klines_4h: List[Dict],
        klines_1h: List[Dict],
        klines_15m: List[Dict]
    ) -> Dict:
        """
        Complete symbol analysis with multi-timeframe confirmation
        
        Returns: {
            'symbol': str,
            'signal': 'LONG' | 'SHORT' | 'NONE',
            'confidence': 0-100,
            'entry_level': float,
            'sl_level': float,
            'tp1_level': float,
            'tp2_level': float,
            'market_regime': 'TRENDING' | 'RANGING',
            'confluence_score': 0-100,
            'reasons': List[str]
        }
        """
        
        reasons = []
        
        try:
            # ===== 1. MARKET REGIME CHECK (ADX) =====
            adx_4h = self.indicators.calculate_adx(klines_4h, period=14)
            market_regime = 'TRENDING' if adx_4h > 25 else 'RANGING'
            
            if market_regime == 'RANGING':
                logger.warning(f"{symbol}: ADX {adx_4h:.1f} - RANGING mode, skipping signals")
                return {
                    'symbol': symbol,
                    'signal': 'NONE',
                    'confidence': 0,
                    'market_regime': 'RANGING',
                    'reasons': ['ADX < 25: Ranging market, signals disabled']
                }
            
            reasons.append(f"✅ ADX {adx_4h:.1f} - Trending market")
            
            # ===== 2. TIMEFRAME ANALYSIS =====
            # 4H: Trend direction
            df_4h = self.data_processor.process_klines(klines_4h)
            ema_fast_4h = self.indicators.calculate_ema(df_4h['close'], 9)
            ema_slow_4h = self.indicators.calculate_ema(df_4h['close'], 21)
            
            trend_4h = 'UP' if ema_fast_4h.iloc[-1] > ema_slow_4h.iloc[-1] else 'DOWN'
            
            # 1H: Entry zone
            df_1h = self.data_processor.process_klines(klines_1h)
            supply_1h, demand_1h = self.price_action.find_supply_demand(df_1h)
            
            # 15M: Entry point
            df_15m = self.data_processor.process_klines(klines_15m)
            is_contraction = self.price_action.detect_contraction_candle(df_15m.iloc[-1])
            
            if not is_contraction:
                return {
                    'symbol': symbol,
                    'signal': 'NONE',
                    'confidence': 0,
                    'market_regime': market_regime,
                    'reasons': ['No contraction candle on 15M']
                }
            
            reasons.append("✅ Contraction candle detected on 15M")
            
            # ===== 3. CONFLUENCE ZONE ANALYSIS =====
            confluence_score = self.confluence.analyze_confluence(
                symbol=symbol,
                df_4h=df_4h,
                df_1h=df_1h,
                df_15m=df_15m,
                supply_4h=supply_1h,  # Use 1H as reference
                demand_4h=demand_1h
            )
            
            if confluence_score < 60:
                reasons.append(f"⚠️ Confluence score {confluence_score:.0f} - Low quality")
                confidence = confluence_score
            else:
                reasons.append(f"✅ Confluence score {confluence_score:.0f} - High quality")
                confidence = confluence_score
            
            # ===== 4. SIGNAL DETERMINATION =====
            current_price = float(df_15m['close'].iloc[-1])
            
            if trend_4h == 'UP' and current_price <= demand_1h and confluence_score >= 60:
                signal = 'LONG'
                entry_level = current_price
                sl_level = demand_1h * 0.98  # 2% below demand
                tp1_level = current_price + (current_price - sl_level) * 2
                tp2_level = current_price + (current_price - sl_level) * 4
                
                reasons.append(f"✅ LONG signal: Trend UP, price at demand zone")
                
            elif trend_4h == 'DOWN' and current_price >= supply_1h and confluence_score >= 60:
                signal = 'SHORT'
                entry_level = current_price
                sl_level = supply_1h * 1.02  # 2% above supply
                tp1_level = current_price - (sl_level - current_price) * 2
                tp2_level = current_price - (sl_level - current_price) * 4
                
                reasons.append(f"✅ SHORT signal: Trend DOWN, price at supply zone")
                
            else:
                signal = 'NONE'
                confidence = 0
                entry_level = sl_level = tp1_level = tp2_level = 0
                reasons.append("❌ No valid LONG/SHORT signal")
            
            # ===== 5. FINAL CONFIDENCE SCORE =====
            final_confidence = confidence if signal != 'NONE' else 0
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': final_confidence,
                'entry_level': entry_level,
                'sl_level': sl_level,
                'tp1_level': tp1_level,
                'tp2_level': tp2_level,
                'market_regime': market_regime,
                'confluence_score': confluence_score,
                'adx': adx_4h,
                'trend_4h': trend_4h,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'signal': 'NONE',
                'confidence': 0,
                'error': str(e)
            }

# ==================== RISK MANAGER V2 ====================
class RiskManagerV2:
    """
    Advanced risk management with:
    - ATR-based dynamic leverage
    - Daily loss tracking
    - Trade validity counter
    - Position sizing
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.risk_calc = RiskCalculations()
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.open_trades: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        logger.info("RiskManagerV2 initialized")
    
    def calculate_leverage(self, symbol: str, atr: float, avg_atr: float) -> int:
        """
        Calculate dynamic leverage based on volatility (ATR ratio)
        
        High volatility (ATR > 2x avg) -> 3x leverage
        Medium volatility -> 5x leverage
        Low volatility -> 10x leverage
        """
        atr_ratio = atr / avg_atr if avg_atr > 0 else 1.0
        
        if atr_ratio > 2.0:
            leverage = 3
            logger.info(f"{symbol}: High volatility (ATR ratio {atr_ratio:.2f}) -> 3x leverage")
        elif atr_ratio > 1.5:
            leverage = 5
            logger.info(f"{symbol}: Medium volatility (ATR ratio {atr_ratio:.2f}) -> 5x leverage")
        else:
            leverage = 10
            logger.info(f"{symbol}: Low volatility (ATR ratio {atr_ratio:.2f}) -> 10x leverage")
        
        return leverage
    
    def can_open_trade(self, symbol: str, signal_confidence: float) -> Tuple[bool, str]:
        """Check if trade can be opened based on risk limits"""
        
        # Check daily loss limit
        if self.daily_loss >= self.config.MAX_DAILY_LOSS:
            return False, f"Daily loss limit reached: ${self.daily_loss:.2f}"
        
        # Check daily trade limit
        if self.daily_trades >= self.config.MAX_DAILY_TRADES:
            return False, f"Daily trade limit reached: {self.daily_trades}"
        
        # Check open positions limit
        if len(self.open_trades) >= self.config.MAX_OPEN_POSITIONS:
            return False, f"Max open positions reached: {len(self.open_trades)}"
        
        # Check minimum confidence
        if signal_confidence < self.config.MIN_SIGNAL_CONFIDENCE:
            return False, f"Signal confidence {signal_confidence:.0f} < {self.config.MIN_SIGNAL_CONFIDENCE}"
        
        return True, "OK"
    
    def register_trade(
        self,
        symbol: str,
        signal: str,
        entry: float,
        sl: float,
        tp1: float,
        tp2: float,
        leverage: int,
        risk_amount: float
    ) -> Dict:
        """Register opened trade"""
        
        trade_id = f"{symbol}_{datetime.now().timestamp()}"
        trade = {
            'id': trade_id,
            'symbol': symbol,
            'signal': signal,
            'entry': entry,
            'sl': sl,
            'tp1': tp1,
            'tp2': tp2,
            'leverage': leverage,
            'risk_amount': risk_amount,
            'opened_at': datetime.now(),
            'opened_bar': 0,  # Current bar count
            'status': 'OPEN',
            'pnl': 0.0
        }
        
        self.open_trades[trade_id] = trade
        self.daily_trades += 1
        
        logger.info(f"Trade registered: {trade_id}, Risk: ${risk_amount:.2f}, Leverage: {leverage}x")
        return trade
    
    def check_trade_validity(self, max_bars: int = 30) -> List[str]:
        """Check if open trades exceeded max bar count and close them"""
        
        closed_trades = []
        for trade_id, trade in list(self.open_trades.items()):
            trade['opened_bar'] += 1
            
            if trade['opened_bar'] > max_bars:
                logger.warning(f"Trade {trade_id}: Exceeded {max_bars} bars, closing")
                self.open_trades.pop(trade_id)
                closed_trades.append(trade_id)
                trade['status'] = 'CLOSED_TIMEOUT'
        
        return closed_trades
    
    def record_trade_result(self, trade_id: str, pnl: float):
        """Record trade result"""
        
        if trade_id in self.open_trades:
            trade = self.open_trades[trade_id]
            trade['pnl'] = pnl
            trade['status'] = 'CLOSED'
            
            self.daily_loss += pnl if pnl < 0 else 0
            self.trade_history.append(trade)
            
            logger.info(f"Trade closed: {trade_id}, P&L: ${pnl:.2f}, Daily loss: ${self.daily_loss:.2f}")
            
            self.open_trades.pop(trade_id)

# ==================== TELEGRAM HANDLER ====================
class TelegramHandler:
    """Send alerts to Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        logger.info("TelegramHandler initialized")
    
    async def send_message(self, message: str):
        """Send message to Telegram"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                async with session.post(self.api_url, json=data) as resp:
                    if resp.status == 200:
                        logger.info("Telegram message sent")
                    else:
                        logger.error(f"Telegram error: {resp.status}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    async def send_signal(self, signal_data: Dict):
        """Send signal alert"""
        message = f"""
<b>🟢 NEW SIGNAL - {signal_data['symbol']}</b>

<b>Direction:</b> {signal_data['signal']}
<b>Confidence:</b> {signal_data['confidence']:.0f}%
<b>Entry:</b> {signal_data['entry_level']:.4f}
<b>SL:</b> {signal_data['sl_level']:.4f}
<b>TP1 (1:2):</b> {signal_data['tp1_level']:.4f}
<b>TP2 (1:4):</b> {signal_data['tp2_level']:.4f}

<b>Market Regime:</b> {signal_data['market_regime']}
<b>Confluence Score:</b> {signal_data.get('confluence_score', 'N/A')}

<b>Analysis:</b>
{chr(10).join(signal_data['reasons'])}
        """
        await self.send_message(message)

# ==================== MAIN BOT ====================
class TradingBotV2:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.bitget = BitgetAPI(
            config.BITGET_API_KEY,
            config.BITGET_SECRET_KEY,
            config.BITGET_PASSPHRASE
        )
        self.signal_engine = SignalEngineV2(config)
        self.risk_manager = RiskManagerV2(config)
        self.telegram = TelegramHandler(
            config.TELEGRAM_BOT_TOKEN,
            config.TELEGRAM_CHAT_ID
        )
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        logger.info("TradingBotV2 initialized")
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            return jsonify({
                'status': 'running',
                'mode': self.config.BOT_MODE,
                'coins_monitored': len(self.config.SYMBOLS),
                'open_positions': len(self.risk_manager.open_trades),
                'daily_trades': self.risk_manager.daily_trades,
                'daily_loss': f"${self.risk_manager.daily_loss:.2f}",
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/trades', methods=['GET'])
        def trades():
            total_pnl = sum(t['pnl'] for t in self.risk_manager.trade_history)
            win_count = len([t for t in self.risk_manager.trade_history if t['pnl'] > 0])
            
            return jsonify({
                'today_pnl': f"${total_pnl:.2f}",
                'trades_closed': len(self.risk_manager.trade_history),
                'wins': win_count,
                'losses': len(self.risk_manager.trade_history) - win_count,
                'win_rate': f"{(win_count/max(len(self.risk_manager.trade_history), 1))*100:.1f}%",
                'open_positions': len(self.risk_manager.open_trades)
            })
    
    async def main_loop(self):
        """Main bot loop - runs every 30 minutes"""
        
        logger.info(f"Bot started - Mode: {self.config.BOT_MODE}")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Analysis iteration #{iteration} - {datetime.now()}")
                logger.info(f"{'='*60}")
                
                # 1. Check time filter
                current_hour = datetime.now().hour
                if not self._is_trading_hours(current_hour):
                    logger.info(f"Off-trading hours ({current_hour}:00 UTC), skipping analysis")
                    await asyncio.sleep(60 * 30)  # 30 minutes
                    continue
                
                # 2. Check trade validity
                closed_trades = self.risk_manager.check_trade_validity(max_bars=30)
                if closed_trades:
                    await self.telegram.send_message(
                        f"⚠️ <b>{len(closed_trades)}</b> trade(s) closed due to max bars exceeded"
                    )
                
                # 3. Analyze all symbols
                for symbol in self.config.SYMBOLS:
                    try:
                        # Fetch klines for all timeframes
                        klines_4h = await self.bitget.get_klines(symbol, '4h', limit=100)
                        klines_1h = await self.bitget.get_klines(symbol, '1h', limit=50)
                        klines_15m = await self.bitget.get_klines(symbol, '15m', limit=40)
                        
                        if not all([klines_4h, klines_1h, klines_15m]):
                            logger.warning(f"Incomplete data for {symbol}")
                            continue
                        
                        # Analyze
                        signal_data = self.signal_engine.analyze_symbol(
                            symbol, klines_4h, klines_1h, klines_15m
                        )
                        
                        # Log analysis
                        logger.info(f"\n{symbol}:")
                        logger.info(f"  Signal: {signal_data.get('signal', 'ERROR')}")
                        logger.info(f"  Confidence: {signal_data.get('confidence', 0):.0f}%")
                        logger.info(f"  Regime: {signal_data.get('market_regime', 'N/A')}")
                        for reason in signal_data.get('reasons', []):
                            logger.info(f"    {reason}")
                        
                        # Check if valid signal
                        if signal_data['signal'] == 'NONE':
                            continue
                        
                        # Check if can open trade
                        can_open, reason = self.risk_manager.can_open_trade(
                            symbol, signal_data['confidence']
                        )
                        if not can_open:
                            logger.info(f"Cannot open trade: {reason}")
                            continue
                        
                        # Calculate dynamic leverage
                        df = DataProcessor().process_klines(klines_4h)
                        atr = TechnicalIndicators().calculate_atr(df, period=14)
                        avg_atr = df['atr'].tail(20).mean()
                        leverage = self.risk_manager.calculate_leverage(symbol, atr, avg_atr)
                        
                        # Register and open trade
                        trade = self.risk_manager.register_trade(
                            symbol=symbol,
                            signal=signal_data['signal'],
                            entry=signal_data['entry_level'],
                            sl=signal_data['sl_level'],
                            tp1=signal_data['tp1_level'],
                            tp2=signal_data['tp2_level'],
                            leverage=leverage,
                            risk_amount=self.config.RISK_PER_TRADE
                        )
                        
                        # Place order (paper mode)
                        order = await self.bitget.place_order(
                            symbol=symbol,
                            side='buy' if signal_data['signal'] == 'LONG' else 'sell',
                            size=self.config.RISK_PER_TRADE * leverage / signal_data['entry_level'],
                            leverage=leverage
                        )
                        
                        # Send Telegram alert
                        await self.telegram.send_signal(signal_data)
                        
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        continue
                
                # 4. Sleep 30 minutes
                logger.info(f"\nNext analysis in 30 minutes...")
                await asyncio.sleep(60 * 30)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)
    
    def _is_trading_hours(self, hour: int) -> bool:
        """Check if current hour is in trading hours (London + NY sessions)"""
        # London: 8-12 UTC
        # NY: 12-17 UTC
        return 8 <= hour <= 17
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run bot with Flask dashboard"""
        
        # Run main loop in background
        import threading
        bot_thread = threading.Thread(
            target=lambda: asyncio.run(self.main_loop()),
            daemon=True
        )
        bot_thread.start()
        
        # Run Flask
        logger.info(f"Flask dashboard starting on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

# ==================== MAIN ====================
if __name__ == '__main__':
    config = Config()
    bot = TradingBotV2(config)
    
    port = int(os.getenv('PORT', 5000))
    bot.run(host='0.0.0.0', port=port, debug=False)
