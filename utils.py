"""
Utility functions for Bitget Trading Bot
Technical indicators, data processing, helpers
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import hashlib
import hmac
from base64 import b64encode
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

class TechnicalIndicators:
    """Technical indicators calculations"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> np.ndarray:
        """Simple Moving Average"""
        return pd.Series(data).rolling(window=period).mean().values
    
    @staticmethod
    def ema(data: List[float], period: int) -> np.ndarray:
        """Exponential Moving Average"""
        return pd.Series(data).ewm(span=period, adjust=False).mean().values
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> np.ndarray:
        """Relative Strength Index (0-100)"""
        delta = np.diff(data)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi_values = 100 - (100 / (1 + rs))
        
        return rsi_values.values
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def atr(highs: List[float], lows: List[float], 
            closes: List[float], period: int = 14) -> np.ndarray:
        """Average True Range (volatility)"""
        tr1 = np.array(highs) - np.array(lows)
        tr2 = np.abs(np.array(highs) - np.array(closes[:-1] + [closes[0]]))
        tr3 = np.abs(np.array(lows) - np.array(closes[:-1] + [closes[0]]))
        
        tr = np.max([tr1, tr2, tr3], axis=0)
        atr_values = pd.Series(tr).rolling(window=period).mean()
        
        return atr_values.values
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, 
                        std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands"""
        sma_values = TechnicalIndicators.sma(data, period)
        std = pd.Series(data).rolling(window=period).std()
        
        upper_band = sma_values + (std * std_dev)
        lower_band = sma_values - (std * std_dev)
        
        return upper_band, sma_values, lower_band
    
    @staticmethod
    def stochastic(highs: List[float], lows: List[float], 
                   closes: List[float], period: int = 14, 
                   smooth_k: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic Oscillator"""
        highest = pd.Series(highs).rolling(window=period).max()
        lowest = pd.Series(lows).rolling(window=period).min()
        
        k_percent = 100 * (np.array(closes) - lowest) / (highest - lowest + 1e-10)
        k_smooth = pd.Series(k_percent).rolling(window=smooth_k).mean()
        d_smooth = pd.Series(k_smooth).rolling(window=smooth_k).mean()
        
        return k_smooth.values, d_smooth.values
    
    @staticmethod
    def volume_weighted_average_price(highs: List[float], lows: List[float],
                                     closes: List[float], volumes: List[float]) -> np.ndarray:
        """VWAP - Volume Weighted Average Price"""
        typical_price = (np.array(highs) + np.array(lows) + np.array(closes)) / 3
        vwap = np.cumsum(typical_price * np.array(volumes)) / np.cumsum(volumes)
        
        return vwap

# ============================================================================
# PRICE ACTION PATTERNS
# ============================================================================

class PriceAction:
    """Price action pattern detection"""
    
    @staticmethod
    def is_hammer(open_: float, high: float, low: float, close: float,
                  atr: float) -> bool:
        """Detect hammer candlestick pattern"""
        body = abs(close - open_)
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low
        
        return (lower_wick > 2 * body and 
                upper_wick < 0.5 * body and
                body < atr * 0.3)
    
    @staticmethod
    def is_engulfing(prev_open: float, prev_close: float, 
                    curr_open: float, curr_close: float) -> Tuple[bool, str]:
        """Detect engulfing pattern (bullish/bearish)"""
        prev_body = prev_close - prev_open
        curr_body = curr_close - curr_open
        
        # Bullish engulfing
        if (curr_body > 0 and prev_body < 0 and
            curr_open < prev_close and curr_close > prev_open):
            return True, "BULLISH_ENGULFING"
        
        # Bearish engulfing
        elif (curr_body < 0 and prev_body > 0 and
              curr_open > prev_close and curr_close < prev_open):
            return True, "BEARISH_ENGULFING"
        
        return False, "NONE"
    
    @staticmethod
    def is_doji(open_: float, close: float, high: float, low: float,
               atr: float) -> bool:
        """Detect doji (indecision) pattern"""
        body = abs(close - open_)
        range_ = high - low
        
        return body < range_ * 0.05  # Body < 5% of range

# ============================================================================
# MARKET REGIME DETECTION
# ============================================================================

class MarketRegime:
    """Detect market regime (trend/range/volatility)"""
    
    @staticmethod
    def detect_trend(closes: List[float], period: int = 20) -> str:
        """Detect if market is in uptrend, downtrend, or ranging"""
        recent_closes = np.array(closes[-period:])
        
        slope = np.polyfit(range(len(recent_closes)), recent_closes, 1)[0]
        
        if slope > 0.0001:
            return "UPTREND"
        elif slope < -0.0001:
            return "DOWNTREND"
        else:
            return "RANGING"
    
    @staticmethod
    def detect_volatility_regime(atr: List[float], 
                                period: int = 20) -> str:
        """Detect volatility regime"""
        recent_atr = np.array(atr[-period:])
        mean_atr = np.mean(recent_atr)
        current_atr = recent_atr[-1]
        
        if current_atr > mean_atr * 1.3:
            return "HIGH_VOLATILITY"
        elif current_atr < mean_atr * 0.7:
            return "LOW_VOLATILITY"
        else:
            return "NORMAL_VOLATILITY"
    
    @staticmethod
    def is_breakout(closes: List[float], highs: List[float], 
                   lows: List[float], period: int = 20) -> Tuple[bool, str]:
        """Detect if price is breaking out of range"""
        recent_high = max(highs[-period:])
        recent_low = min(lows[-period:])
        current = closes[-1]
        
        if current > recent_high * 1.001:  # 0.1% above
            return True, "BREAKOUT_UP"
        elif current < recent_low * 0.999:  # 0.1% below
            return True, "BREAKOUT_DOWN"
        
        return False, "NONE"

# ============================================================================
# CONFLUENCE DETECTION
# ============================================================================

class Confluence:
    """Multiple factor confluence detection"""
    
    @staticmethod
    def count_factors(factors: Dict[str, bool]) -> Tuple[int, float]:
        """Count how many factors are confirmed"""
        total = len(factors)
        confirmed = sum([1 for v in factors.values() if v])
        confidence = (confirmed / total * 100) if total > 0 else 0
        
        return confirmed, confidence
    
    @staticmethod
    def get_strong_signal(factors: Dict[str, bool], 
                         min_factors: int = 3) -> Tuple[bool, float]:
        """Check if confluence is strong (at least min_factors)"""
        confirmed, confidence = Confluence.count_factors(factors)
        return confirmed >= min_factors, confidence

# ============================================================================
# DATA PROCESSING
# ============================================================================

class DataProcessor:
    """Data cleaning and processing"""
    
    @staticmethod
    def parse_klines(klines: List) -> Dict:
        """Parse Bitget kline format"""
        if not klines:
            return {}
        
        # Bitget format: [timestamp, open, high, low, close, volume, quote_asset_volume]
        return {
            'timestamp': int(klines[0]),
            'open': float(klines[1]),
            'high': float(klines[2]),
            'low': float(klines[3]),
            'close': float(klines[4]),
            'volume': float(klines[5]),
            'quote_asset_volume': float(klines[6]) if len(klines) > 6 else 0,
        }
    
    @staticmethod
    def batch_parse_klines(klines_list: List) -> List[Dict]:
        """Parse multiple klines"""
        return [DataProcessor.parse_klines(k) for k in klines_list]
    
    @staticmethod
    def extract_ohlcv(klines_list: List[Dict]) -> Tuple:
        """Extract OHLCV from parsed klines"""
        opens = [k['open'] for k in klines_list]
        highs = [k['high'] for k in klines_list]
        lows = [k['low'] for k in klines_list]
        closes = [k['close'] for k in klines_list]
        volumes = [k['volume'] for k in klines_list]
        
        return opens, highs, lows, closes, volumes
    
    @staticmethod
    def fill_gaps(data: List[float], method: str = 'linear') -> List[float]:
        """Fill NaN gaps in data"""
        series = pd.Series(data)
        
        if method == 'linear':
            filled = series.interpolate(method='linear')
        elif method == 'forward':
            filled = series.fillna(method='ffill')
        elif method == 'backward':
            filled = series.fillna(method='bfill')
        else:
            filled = series
        
        return filled.fillna(series.mean()).tolist()

# ============================================================================
# RISK CALCULATIONS
# ============================================================================

class RiskCalculations:
    """Position and risk calculations"""
    
    @staticmethod
    def calculate_position_size(entry: float, stop_loss: float, 
                               risk_amount: float, leverage: int = 1) -> float:
        """
        Calculate position size based on risk
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            risk_amount: Risk amount in USD
            leverage: Trading leverage
        
        Returns:
            Position size in base currency
        """
        price_risk = abs(entry - stop_loss)
        if price_risk == 0:
            return 0
        
        # Position size = (Risk amount × Leverage) / Price risk
        position_size = (risk_amount * leverage) / price_risk
        return round(position_size, 4)
    
    @staticmethod
    def calculate_take_profit(entry: float, stop_loss: float, 
                             ratio: float) -> float:
        """
        Calculate take profit based on risk:reward ratio
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            ratio: RR ratio (e.g., 2 for 1:2)
        
        Returns:
            Take profit price
        """
        risk = abs(entry - stop_loss)
        reward = risk * ratio
        
        if entry > stop_loss:  # Long
            return entry + reward
        else:  # Short
            return entry - reward
    
    @staticmethod
    def calculate_risk_reward_ratio(entry: float, take_profit: float, 
                                   stop_loss: float) -> float:
        """Calculate actual RR ratio"""
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    @staticmethod
    def calculate_pnl(entry: float, exit_: float, 
                     position_size: float, leverage: int = 1) -> float:
        """Calculate profit/loss in USD"""
        price_change = exit_ - entry
        pnl = price_change * position_size / leverage
        return round(pnl, 2)
    
    @staticmethod
    def calculate_pnl_percent(entry: float, exit_: float) -> float:
        """Calculate P&L percentage"""
        if entry == 0:
            return 0
        return ((exit_ - entry) / entry) * 100

# ============================================================================
# TIME UTILITIES
# ============================================================================

class TimeUtils:
    """Time and date utilities"""
    
    @staticmethod
    def get_candle_start_time(timeframe_minutes: int) -> datetime:
        """Get start time of current candle"""
        now = datetime.utcnow()
        minutes_since_hour = now.minute % timeframe_minutes
        
        return now.replace(
            minute=now.minute - minutes_since_hour,
            second=0,
            microsecond=0
        )
    
    @staticmethod
    def get_candle_end_time(timeframe_minutes: int) -> datetime:
        """Get end time of current candle"""
        start = TimeUtils.get_candle_start_time(timeframe_minutes)
        return start + timedelta(minutes=timeframe_minutes)
    
    @staticmethod
    def time_until_next_candle(timeframe_minutes: int) -> int:
        """Get seconds until next candle"""
        end = TimeUtils.get_candle_end_time(timeframe_minutes)
        delta = end - datetime.utcnow()
        return int(delta.total_seconds())

# ============================================================================
# BITGET API SIGNATURE
# ============================================================================

class BitgetSignature:
    """Bitget API authentication"""
    
    @staticmethod
    def create_signature(timestamp: str, method: str, path: str, 
                        body: str, secret: str) -> str:
        """Create Bitget v2 API signature"""
        message = timestamp + method.upper() + path
        if body:
            message += body
        
        signature = b64encode(
            hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        return signature

# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class LogUtils:
    """Logging helpers"""
    
    @staticmethod
    def format_trade_log(symbol: str, side: str, entry: float, 
                        sl: float, tp: float, size: float) -> str:
        """Format trade information for logging"""
        return (
            f"{symbol} | {side.upper()} | "
            f"Entry: {entry:.8f} | "
            f"SL: {sl:.8f} | "
            f"TP: {tp:.8f} | "
            f"Size: {size:.4f}"
        )
    
    @staticmethod
    def format_pnl_log(symbol: str, entry: float, exit_: float, 
                      pnl: float, pnl_percent: float) -> str:
        """Format P&L information for logging"""
        return (
            f"{symbol} | "
            f"Entry: {entry:.8f} | "
            f"Exit: {exit_:.8f} | "
            f"P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)"
        )

if __name__ == '__main__':
    print("🔧 Utilities Module")
    print("=" * 50)
    
    # Test indicators
    test_data = [100, 101, 102, 101, 103, 104, 103, 105, 106, 105]
    
    ema_result = TechnicalIndicators.ema(test_data, 5)
    print(f"EMA(5): {ema_result[-1]:.2f}")
    
    rsi_result = TechnicalIndicators.rsi(test_data, 5)
    print(f"RSI(5): {rsi_result[-1]:.2f}")
    
    # Test risk calculation
    entry = 100
    sl = 95
    risk = 20
    pos_size = RiskCalculations.calculate_position_size(entry, sl, risk, leverage=10)
    print(f"\nPosition Size: {pos_size:.4f}")
    
    tp = RiskCalculations.calculate_take_profit(entry, sl, 2)
    print(f"TP (1:2): {tp:.2f}")
    
    print("\n✅ Utilities module loaded successfully")
