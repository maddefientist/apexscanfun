import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from typing import Dict

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the dataframe.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        DataFrame with added indicators
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Add RSI (14 period)
    # Make sure we have enough data for RSI calculation (at least 14 periods)
    if len(df) >= 14:
        rsi = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi.rsi()
    else:
        # Not enough data for RSI
        df['rsi'] = pd.Series([np.nan] * len(df), index=df.index)
    
    # Add MACD
    # MACD requires at least 26 periods of data (for the slow period)
    if len(df) >= 26:
        macd = MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
    else:
        # Not enough data for MACD
        df['macd'] = pd.Series([np.nan] * len(df), index=df.index)
        df['macd_signal'] = pd.Series([np.nan] * len(df), index=df.index)
        df['macd_histogram'] = pd.Series([np.nan] * len(df), index=df.index)
    
    # Add Bollinger Bands
    bollinger = BollingerBands(close=df['close'])
    df['bb_upper'] = bollinger.bollinger_hband()
    df['bb_middle'] = bollinger.bollinger_mavg()
    df['bb_lower'] = bollinger.bollinger_lband()
    
    # Add Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()
    
    return df

def plot_rsi(ax, df: pd.DataFrame):
    """
    Plot RSI indicator on the given axis.
    
    Args:
        ax: Matplotlib axis to plot on
        df: DataFrame with RSI data
    """
    ax.plot(df.index, df['rsi'], color='purple', linewidth=1)
    ax.axhline(y=70, color='r', linestyle='--', alpha=0.5)
    ax.axhline(y=30, color='g', linestyle='--', alpha=0.5)
    ax.fill_between(df.index, df['rsi'], 70, where=(df['rsi'] >= 70), color='r', alpha=0.3)
    ax.fill_between(df.index, df['rsi'], 30, where=(df['rsi'] <= 30), color='g', alpha=0.3)
    ax.set_ylim(0, 100)
    ax.set_ylabel('RSI')

def plot_macd(ax, df: pd.DataFrame):
    """
    Plot MACD indicator on the given axis.
    
    Args:
        ax: Matplotlib axis to plot on
        df: DataFrame with MACD data
    """
    ax.plot(df.index, df['macd'], color='blue', linewidth=1, label='MACD')
    ax.plot(df.index, df['macd_signal'], color='red', linewidth=1, label='Signal')
    
    # Plot histogram
    colors = ['g' if val >= 0 else 'r' for val in df['macd_histogram']]
    ax.bar(df.index, df['macd_histogram'], color=colors, alpha=0.5, width=0.8)
    
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.2)
    ax.set_ylabel('MACD')
    ax.legend(loc='upper left', fontsize='small')

def get_indicator_signals(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generate trading signals based on indicators.
    
    Args:
        df: DataFrame with indicators
        
    Returns:
        Dictionary of signals and their values
    """
    signals = {}
    
    # RSI signals
    latest_rsi = df['rsi'].iloc[-1]
    if pd.isna(latest_rsi):
        signals['RSI'] = "Neutral (nan)"
    elif latest_rsi > 70:
        signals['RSI'] = f"Overbought ({latest_rsi:.1f})"
    elif latest_rsi < 30:
        signals['RSI'] = f"Oversold ({latest_rsi:.1f})"
    else:
        signals['RSI'] = f"Neutral ({latest_rsi:.1f})"
    
    # MACD signals
    latest_macd = df['macd'].iloc[-1]
    latest_signal = df['macd_signal'].iloc[-1]
    latest_hist = df['macd_histogram'].iloc[-1]
    prev_hist = df['macd_histogram'].iloc[-2] if len(df) > 1 else 0
    
    if pd.isna(latest_macd) or pd.isna(latest_signal) or pd.isna(latest_hist):
        signals['MACD'] = "Insufficient Data"
    elif latest_macd > latest_signal:
        if latest_hist > 0 and prev_hist <= 0:
            signals['MACD'] = "Bullish Crossover"
        else:
            signals['MACD'] = "Bullish"
    else:
        if latest_hist < 0 and prev_hist >= 0:
            signals['MACD'] = "Bearish Crossover"
        else:
            signals['MACD'] = "Bearish"
    
    # Trend signals based on moving averages
    latest_close = df['close'].iloc[-1]
    latest_sma20 = df['sma_20'].iloc[-1]
    latest_sma50 = df['sma_50'].iloc[-1]
    
    # Check if we have enough data for at least SMA20
    if pd.notna(latest_sma20):
        if pd.notna(latest_sma50):
            # We have both SMAs
            if latest_close > latest_sma20 and latest_sma20 > latest_sma50:
                signals['Trend'] = "Strong Uptrend"
            elif latest_close > latest_sma20:
                signals['Trend'] = "Uptrend"
            elif latest_close < latest_sma20 and latest_sma20 < latest_sma50:
                signals['Trend'] = "Strong Downtrend"
            elif latest_close < latest_sma20:
                signals['Trend'] = "Downtrend"
            else:
                signals['Trend'] = "Sideways"
        else:
            # We only have SMA20
            if latest_close > latest_sma20:
                signals['Trend'] = "Uptrend"
            elif latest_close < latest_sma20:
                signals['Trend'] = "Downtrend"
            else:
                signals['Trend'] = "Sideways"
    else:
        signals['Trend'] = "Insufficient Data"
    
    return signals