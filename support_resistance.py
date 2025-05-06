import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from typing import Tuple, List

def detect_support_resistance(df: pd.DataFrame, window: int = 5, threshold: float = 0.02) -> Tuple[List[float], List[float]]:
    """
    Detect support and resistance levels using peak/trough clustering.
    
    Args:
        df: DataFrame with OHLC data
        window: Window size for peak/trough detection
        threshold: Percentage threshold for clustering levels
        
    Returns:
        Tuple of (support_levels, resistance_levels)
    """
    # Find local maxima and minima
    df['min'] = df.iloc[argrelextrema(df['low'].values, np.less_equal, order=window)[0]]['low']
    df['max'] = df.iloc[argrelextrema(df['high'].values, np.greater_equal, order=window)[0]]['high']
    
    # Collect all levels
    supports = df['min'].dropna().tolist()
    resistances = df['max'].dropna().tolist()
    
    # Cluster levels that are within threshold% of each other
    def cluster_levels(levels: List[float], threshold: float) -> List[float]:
        if not levels:
            return []
            
        levels = sorted(levels)
        clusters = [[levels[0]]]
        
        for level in levels[1:]:
            last_cluster = clusters[-1]
            last_level = last_cluster[-1]
            
            # If within threshold% of the last level, add to the same cluster
            if abs(level - last_level) / last_level <= threshold:
                last_cluster.append(level)
            else:
                clusters.append([level])
        
        # Calculate the average of each cluster
        return [sum(cluster) / len(cluster) for cluster in clusters]
    
    support_levels = cluster_levels(supports, threshold)
    resistance_levels = cluster_levels(resistances, threshold)
    
    return support_levels, resistance_levels

def plot_support_resistance(ax, support_levels: List[float], resistance_levels: List[float], 
                           min_x: pd.Timestamp, max_x: pd.Timestamp):
    """
    Plot support and resistance levels on the given axis.
    
    Args:
        ax: Matplotlib axis to plot on
        support_levels: List of support price levels
        resistance_levels: List of resistance price levels
        min_x: Minimum x-axis value (start date)
        max_x: Maximum x-axis value (end date)
    """
    # Plot support levels
    for level in support_levels:
        ax.plot([min_x, max_x], [level, level], '--', color='green', linewidth=1, alpha=0.7)
    
    # Plot resistance levels
    for level in resistance_levels:
        ax.plot([min_x, max_x], [level, level], '--', color='red', linewidth=1, alpha=0.7)