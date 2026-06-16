#!/usr/bin/env python3
"""
UTILS V2 - Advanced Technical Indicators & Analysis
===================================================

Includes:
- ADX (Average Directional Index) for market regime detection
- Confluence Zone Analyzer for multi-level confluence
- Enhanced Price Action analysis
- Risk Calculations
- Data Processor
"""

import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ==================== DATA PROCESSOR ====================
class DataProcessor:
    """Process and validate OHLCV data from Bitget"""
    
    @staticmethod
    def process_klines(klines: List[Dict]) -> pd.DataFrame:
        """
        Convert Bitget klines to DataFrame
        
        Bitget format: [timestamp, open, high, low, close, volume, usdtVolume]
        """
        if not klines:
            return pd.DataFrame()
        
        try:
            # Reverse to get oldest first
            klines = list(reversed(klines))
            
            df = pd.DataFrame({
                'timestamp': [int(k[0]) for k in klines],
                'open': [float(k[1]) for k in klines],
                'high': [float(k[2]) for k in klines],
                'low': [float(k[3]) for k in klines],
                'close': [float(k[4]) for k in klines],
                'volume': [float(k[5]) for k in klines],
                'usdt_volume': [float(k[6]) for k in klines] if len(k) > 6 else 0
            })
            
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            logger.error(f"Error processing klines: {e}")
            return pd.DataFrame()

# ==================== TECHNICAL INDICATORS ====================
class TechnicalIndicators:
    """Collection of technical indicators"""
    
    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """
        Average True Range
        Measures market volatility
        """
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            df['atr'] = atr
            return atr.iloc[-1] if not atr.empty else 0
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0
    
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> float:
        """
        Relative Strength Index
        Measures overbought/oversold conditions
        """
        try:
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not rsi.empty else 50
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50
    
    @staticmethod
    def calculate_adx(klines: List[Dict], period: int = 14) -> float:
        """
        Average Directional Index
        
        Detects market trend strength:
        ADX > 25 = TRENDING (strong trend)
        ADX < 20 = RANGING (consolidating)
        
        Returns: ADX value (0-100)
        """
        try:
            df = DataProcessor.process_klines(klines)
            if df.empty or len(df) < period:
                return 0
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Calculate +DM and -DM
            plus_dm = high.diff()
            minus_dm = -low.diff()
            
            # Handle conditions
            plus_dm = plus_dm.where(
                (plus_dm > 0) & (plus_dm > minus_dm),
                0
            )
            minus_dm = minus_dm.where(
                (minus_dm > 0) & (minus_dm > plus_dm),
                0
            )
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Smooth with ATR
            atr = tr.rolling(window=period).mean()
            
            # Calculate DI+
            di_plus = 100 * (plus_dm.rolling(window=period).mean() / atr)
            di_minus = 100 * (minus_dm.rolling(window=period).mean() / atr)
            
            # Calculate DX
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
            
            # Calculate ADX
            adx = dx.rolling(window=period).mean()
            
            return adx.iloc[-1] if not adx.empty else 0
        
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return 0
    
    @staticmethod
    def calculate_macd(series: pd.Series) -> Tuple[float, float, float]:
        """
        MACD (Moving Average Convergence Divergence)
        Returns: (macd, signal, histogram)
        """
        try:
            ema_12 = TechnicalIndicators.calculate_ema(series, 12)
            ema_26 = TechnicalIndicators.calculate_ema(series, 26)
            
            macd = ema_12 - ema_26
            signal = TechnicalIndicators.calculate_ema(macd, 9)
            histogram = macd - signal
            
            return (
                macd.iloc[-1] if not macd.empty else 0,
                signal.iloc[-1] if not signal.empty else 0,
                histogram.iloc[-1] if not histogram.empty else 0
            )
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return (0, 0, 0)

# ==================== PRICE ACTION ====================
class PriceAction:
    """Price Action analysis for trading signals"""
    
    @staticmethod
    def find_supply_demand(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float]:
        """
        Find supply (resistance) and demand (support) zones
        
        Supply: Highest high in lookback period
        Demand: Lowest low in lookback period
        
        Returns: (supply_level, demand_level)
        """
        try:
            if len(df) < lookback:
                return (df['high'].max(), df['low'].min())
            
            supply = df['high'].tail(lookback).max()
            demand = df['low'].tail(lookback).min()
            
            return (supply, demand)
        except Exception as e:
            logger.error(f"Error finding supply/demand: {e}")
            return (0, 0)
    
    @staticmethod
    def detect_contraction_candle(candle: pd.Series) -> bool:
        """
        Detect contraction candle
        
        Characteristics:
        - Small body (close - open)
        - Long lower shadow (entry signal)
        - Small upper shadow
        """
        try:
            body = abs(candle['close'] - candle['open'])
            lower_shadow = candle['open'] - candle['low']
            upper_shadow = candle['high'] - candle['close']
            total_range = candle['high'] - candle['low']
            
            # Contraction = body < 20% of range, lower shadow > 40% of range
            if total_range == 0:
                return False
            
            body_ratio = body / total_range
            lower_shadow_ratio = lower_shadow / total_range
            
            is_contraction = (body_ratio < 0.25) and (lower_shadow_ratio > 0.3)
            
            return is_contraction
        except Exception as e:
            logger.error(f"Error detecting contraction: {e}")
            return False
    
    @staticmethod
    def detect_bos(df: pd.DataFrame, lookback: int = 20) -> Dict[str, bool]:
        """
        Detect Break of Structure (BOS)
        
        Bullish BOS: Price breaks above previous swing high
        Bearish BOS: Price breaks below previous swing low
        """
        try:
            if len(df) < lookback:
                return {'bullish': False, 'bearish': False}
            
            current_high = df['high'].iloc[-1]
            current_low = df['low'].iloc[-1]
            
            previous_high = df['high'].tail(lookback).max()
            previous_low = df['low'].tail(lookback).min()
            
            bullish_bos = current_high > previous_high
            bearish_bos = current_low < previous_low
            
            return {
                'bullish': bullish_bos,
                'bearish': bearish_bos,
                'last_high': previous_high,
                'last_low': previous_low
            }
        except Exception as e:
            logger.error(f"Error detecting BOS: {e}")
            return {'bullish': False, 'bearish': False}
    
    @staticmethod
    def detect_order_block(df: pd.DataFrame, lookback: int = 5) -> Dict:
        """
        Detect Order Block (OB)
        
        Area where institutional orders likely placed
        """
        try:
            if len(df) < lookback:
                return {'found': False}
            
            # OB = zone where last impulse move started
            recent = df.tail(lookback)
            
            ob_high = recent['high'].max()
            ob_low = recent['low'].min()
            ob_mid = (ob_high + ob_low) / 2
            
            return {
                'found': True,
                'high': ob_high,
                'low': ob_low,
                'mid': ob_mid
            }
        except Exception as e:
            logger.error(f"Error detecting OB: {e}")
            return {'found': False}

# ==================== CONFLUENCE ANALYZER ====================
class ConfluenceAnalyzer:
    """Analyze multiple confluence levels for signal quality"""
    
    @staticmethod
    def analyze_confluence(
        symbol: str,
        df_4h: pd.DataFrame,
        df_1h: pd.DataFrame,
        df_15m: pd.DataFrame,
        supply_4h: float,
        demand_4h: float
    ) -> float:
        """
        Analyze confluence zones
        
        Confluence = Multiple indicators at same level
        
        Scoring:
        - Fibonacci level + OB + previous swing = high confluence
        - Only OB or only Fibonacci = medium
        - No confluence = low (< 60%)
        """
        
        confluence_score = 0
        confluence_levels = []
        
        try:
            price_4h = df_4h['close'].iloc[-1]
            price_1h = df_1h['close'].iloc[-1]
            price_15m = df_15m['close'].iloc[-1]
            
            # ===== 1. FIBONACCI LEVELS =====
            fib_levels = ConfluenceAnalyzer._calculate_fibonacci(df_4h)
            current_price = price_15m
            
            for fib_name, fib_level in fib_levels.items():
                if abs(current_price - fib_level) / current_price < 0.02:  # Within 2%
                    confluence_score += 15
                    confluence_levels.append(f"Fibonacci {fib_name}")
            
            # ===== 2. ORDER BLOCK (OB) =====
            ob_4h = PriceAction.detect_order_block(df_4h)
            if ob_4h['found']:
                if ob_4h['low'] <= current_price <= ob_4h['high']:
                    confluence_score += 20
                    confluence_levels.append("Order Block (4H)")
            
            # ===== 3. PREVIOUS SWING =====
            swing_high = df_4h['high'].tail(10).max()
            swing_low = df_4h['low'].tail(10).min()
            
            if abs(current_price - swing_high) / current_price < 0.03:  # Within 3%
                confluence_score += 15
                confluence_levels.append("Swing High")
            
            if abs(current_price - swing_low) / current_price < 0.03:
                confluence_score += 15
                confluence_levels.append("Swing Low")
            
            # ===== 4. MOVING AVERAGES =====
            ema_20 = TechnicalIndicators.calculate_ema(df_4h['close'], 20).iloc[-1]
            if abs(current_price - ema_20) / current_price < 0.02:
                confluence_score += 10
                confluence_levels.append("EMA 20 (4H)")
            
            # ===== 5. SUPPLY/DEMAND ZONE =====
            if abs(current_price - demand_4h) / current_price < 0.03:
                confluence_score += 20
                confluence_levels.append("Demand Zone (4H)")
            
            if abs(current_price - supply_4h) / current_price < 0.03:
                confluence_score += 20
                confluence_levels.append("Supply Zone (4H)")
            
            # Cap at 100
            confluence_score = min(confluence_score, 100)
            
            logger.info(f"{symbol} Confluence: {confluence_score:.0f}% - {confluence_levels}")
            
            return confluence_score
        
        except Exception as e:
            logger.error(f"Error analyzing confluence for {symbol}: {e}")
            return 50  # Default medium score
    
    @staticmethod
    def _calculate_fibonacci(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Fibonacci levels"""
        try:
            high = df['high'].tail(50).max()
            low = df['low'].tail(50).min()
            
            range_val = high - low
            
            return {
                '0.618': low + range_val * 0.618,
                '0.5': low + range_val * 0.5,
                '0.382': low + range_val * 0.382
            }
        except:
            return {}

# ==================== RISK CALCULATIONS ====================
class RiskCalculations:
    """Risk management calculations"""
    
    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_per_trade: float,
        entry: float,
        sl: float,
        leverage: int = 10
    ) -> float:
        """
        Calculate position size based on risk
        
        Formula:
        Position Size = (Risk Amount / Price Diff) * Leverage
        """
        try:
            price_diff = abs(entry - sl)
            if price_diff == 0:
                return 0
            
            position_value = (risk_per_trade / price_diff) * leverage
            return position_value
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    @staticmethod
    def calculate_risk_reward(entry: float, sl: float, tp: float) -> float:
        """
        Calculate Risk/Reward ratio
        
        Returns: RR ratio (e.g., 2.0 for 1:2)
        """
        try:
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            
            if risk == 0:
                return 0
            
            return reward / risk
        except Exception as e:
            logger.error(f"Error calculating RR: {e}")
            return 0
