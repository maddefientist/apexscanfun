import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import os
from typing import Dict, Optional, Tuple

from indicators import add_indicators, plot_rsi, plot_macd, get_indicator_signals
from support_resistance import detect_support_resistance, plot_support_resistance

def generate_token_chart(df: pd.DataFrame, token_address: str, timeframe: str = "1h",
                         pool_name: str = None) -> Tuple[str, Dict[str, str]]:
    """
    Generate a comprehensive chart for a token with indicators.
    
    Args:
        df: DataFrame with OHLCV data
        token_address: Token address
        timeframe: Chart timeframe (e.g., "1h", "4h", "1d")
        pool_name: Name of the liquidity pool (optional)
        
    Returns:
        Tuple of (image_path, signals_dict)
    """
    # Check if we have enough data
    if df.empty or len(df) < 5:  # Require at least 5 data points
        # Create a basic chart with a message
        fig = plt.figure(figsize=(12, 10))
        plt.text(0.5, 0.5, "Insufficient data to generate chart",
                 horizontalalignment='center', verticalalignment='center', fontsize=14)
        plt.axis('off')
        
        # Save chart
        os.makedirs('charts', exist_ok=True)
        img_path = f"charts/chart_{token_address[:8]}.png"
        plt.savefig(img_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Return minimal signals
        signals = {
            'RSI': 'Neutral (nan)',
            'MACD': 'Insufficient Data',
            'Trend': 'Insufficient Data'
        }
        return img_path, signals
    
    # Add indicators
    df = add_indicators(df)
    
    # Detect support and resistance levels
    support_levels, resistance_levels = detect_support_resistance(df)
    
    # Get signals
    signals = get_indicator_signals(df)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(12, 10), constrained_layout=True)
    gs = GridSpec(4, 1, height_ratios=[3, 1, 1, 0.5], figure=fig)
    
    # Main price chart
    ax1 = fig.add_subplot(gs[0])
    
    # Set title and labels
    token_symbol = token_address[:5] + "..."  # Placeholder for token symbol
    title = f"{token_symbol} ({timeframe}) - Solana SPL Token"
    if pool_name:
        title += f" - {pool_name}"
    ax1.set_title(title, fontsize=14)
    ax1.set_ylabel('Price')
    ax1.grid(True, alpha=0.3)
    
    try:
        # Plot candlesticks
        mpf.plot(df, type='candle', style='yahoo', ax=ax1, volume=False, show_nontrading=False)
        
        # Add moving averages if available
        if not df['sma_20'].isna().all():
            ax1.plot(df.index, df['sma_20'], color='blue', linewidth=1, label='SMA 20')
        if not df['sma_50'].isna().all():
            ax1.plot(df.index, df['sma_50'], color='orange', linewidth=1, label='SMA 50')
        
        # Add Bollinger Bands if available
        if not df['bb_upper'].isna().all():
            ax1.plot(df.index, df['bb_upper'], 'k--', alpha=0.3)
            ax1.plot(df.index, df['bb_middle'], 'k-', alpha=0.3)
            ax1.plot(df.index, df['bb_lower'], 'k--', alpha=0.3)
        
        # Add support and resistance levels
        plot_support_resistance(ax1, support_levels, resistance_levels, df.index[0], df.index[-1])
        
        ax1.legend(loc='upper left')
        
        # Volume subplot
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        mpf.plot(df, type='candle', style='yahoo', ax=ax2, volume=ax2, show_nontrading=False)
        ax2.set_ylabel('Volume')
        
        # RSI subplot
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        plot_rsi(ax3, df)
        
        # MACD subplot
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        plot_macd(ax4, df)
        
        # Format x-axis dates
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.xticks(rotation=45)
        
    except Exception as e:
        # If plotting fails, add error message to the chart
        plt.clf()  # Clear the figure
        plt.text(0.5, 0.5, f"Error generating chart: {str(e)}",
                 horizontalalignment='center', verticalalignment='center', fontsize=12)
        plt.axis('off')
        # Save error chart
        os.makedirs('charts', exist_ok=True)
        img_path = f"charts/chart_{token_address[:8]}_error.png"
        plt.savefig(img_path, dpi=100, bbox_inches='tight')
        plt.close()
        return img_path, {
            'RSI': 'Error',
            'MACD': 'Error',
            'Trend': 'Error'
        }
    
    # Adjust layout
    plt.tight_layout()
    
    # Create directory if it doesn't exist
    os.makedirs('charts', exist_ok=True)
    
    # Save chart
    img_path = f"charts/chart_{token_address[:8]}.png"
    plt.savefig(img_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return img_path, signals

def format_signals_text(signals: Dict[str, str], token_address: str) -> str:
    """
    Format signals dictionary into a readable text.
    
    Args:
        signals: Dictionary of signals
        token_address: Token address
        
    Returns:
        Formatted text
    """
    text = f"*Analysis for {token_address[:8]}...*\n\n"
    
    # First display pool information if available
    pool_info = []
    for key in ['Pool', 'Liquidity']:
        if key in signals:
            pool_info.append(f"*{key}*: {signals[key]}")
            signals.pop(key)
    
    if pool_info:
        text += "📊 *Pool Information*\n"
        text += "\n".join(pool_info)
        text += "\n\n"
    
    # Then display technical indicators
    text += "📈 *Technical Indicators*\n"
    for indicator, signal in signals.items():
        text += f"*{indicator}*: {signal}\n"
    
    text += "\n⚠️ This is not financial advice. Always do your own research."
    
    return text