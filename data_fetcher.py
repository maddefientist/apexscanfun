import requests
import pandas as pd
import logging
from typing import Dict, Optional, Tuple, List, Union, Any

from config import GECKO_API_BASE, TIMEFRAMES, DEFAULT_TIMEFRAME, CHART_SETTINGS
from charting import generate_token_chart, format_signals_text

def get_token_symbol(token_data: Optional[Dict[str, Any]]) -> str:
    """
    Extract the token symbol from token data.
    
    Args:
        token_data: Token data from the API
        
    Returns:
        Token symbol or a shortened address
    """
    if not token_data:
        return "Unknown"
    
    attributes = token_data.get('attributes', {})
    symbol = attributes.get('symbol')
    
    if symbol:
        return symbol
    
    # Fallback to address
    address = token_data.get('id', '')
    if address:
        return address[:5] + "..."
    
    return "Unknown"

def check_token_exists(token_address: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if a token exists on the network.
    
    Args:
        token_address: Token address
        
    Returns:
        Tuple of (exists, token_data)
    """
    try:
        url = f"{GECKO_API_BASE}/networks/solana/tokens/{token_address}"
        logging.info(f"Checking if token exists: {url}")
        
        response = requests.get(url, timeout=10)
        
        # If we get a 200 response, the token exists
        if response.status_code == 200:
            data = response.json()
            token_data = data.get('data', {})
            logging.info(f"Token exists: {token_address}")
            return True, token_data
        
        # If we get a 404, the token doesn't exist
        if response.status_code == 404:
            logging.warning(f"Token not found: {token_address}")
            return False, None
        
        # For other status codes, log the error
        logging.error(f"Error checking token: {response.status_code} - {response.text}")
        return False, None
        
    except requests.exceptions.Timeout:
        logging.error(f"Timeout occurred while checking token: {token_address}")
        return False, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error checking token: {e}")
        return False, None
    except Exception as e:
        logging.error(f"Unexpected error checking token: {e}")
        return False, None

def get_top_pools_for_token(token_address: str) -> List[Dict]:
    """
    Get the top liquidity pools for a token.
    
    Args:
        token_address: Token address
        
    Returns:
        List of pool dictionaries with pool data
    """
    try:
        url = f"{GECKO_API_BASE}/networks/solana/tokens/{token_address}/pools"
        logging.info(f"Fetching pools from: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        pools = data.get('data', [])
        
        # Log the first pool for debugging
        if pools and len(pools) > 0:
            logging.info(f"First pool data: {pools[0]}")
        
        # Sort pools by liquidity (if available)
        if pools:
            pools.sort(key=lambda x: float(x.get('attributes', {}).get('reserve_in_usd', 0) or 0), reverse=True)
        
        return pools
    except requests.exceptions.Timeout:
        logging.error(f"Timeout occurred while fetching pools for token: {token_address}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error fetching pools: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error fetching pools: {e}")
        return []

def fetch_pool_ohlcv_data(network: str, pool_address: str, timeframe: str,
                          aggregate: int = 1, limit: int = 100) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data for a specific pool.
    
    Args:
        network: Network name (e.g., 'solana')
        pool_address: Pool address
        timeframe: Timeframe (minute, hour, day)
        aggregate: Number of units to aggregate
        limit: Number of data points to return
        
    Returns:
        DataFrame with OHLCV data or None if fetch failed
    """
    try:
        # Construct the API URL
        url = f"{GECKO_API_BASE}/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
        params = {
            'aggregate': aggregate,
            'limit': limit,
            'currency': 'usd'
        }
        
        logging.info(f"Fetching OHLCV data from: {url} with params: {params}")
        
        # Make the API request
        response = requests.get(url, params=params)
        
        # Log the response status and URL for debugging
        logging.info(f"Response status: {response.status_code}, URL: {response.url}")
        logging.debug(f"Response content: {response.text}")
        
        # Check if the response is successful
        if response.status_code != 200:
            logging.error(f"API error: {response.status_code} - {response.text}")
            return None
            
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        ohlcv_data = data.get('data', {}).get('attributes', {}).get('ohlcv_list', [])
        
        if not ohlcv_data:
            logging.warning(f"No OHLCV data returned for pool {pool_address}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Check if we have enough data
        if len(df) < 5:  # Require at least 5 data points
            logging.warning(f"Insufficient data points ({len(df)}) for pool {pool_address}")
            return None
            
        # Convert types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Limit to the window size
        if len(df) > CHART_SETTINGS["window_size"]:
            df = df.iloc[-CHART_SETTINGS["window_size"]:]
            
        # Check for NaN values
        if df.isna().any().any():
            logging.warning(f"NaN values detected in data for pool {pool_address}")
            # Fill NaN values with forward fill then backward fill
            df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except (KeyError, ValueError) as e:
        logging.error(f"Data parsing failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None

def fetch_token_data(token_address: str, timeframe: str = DEFAULT_TIMEFRAME) -> Optional[pd.DataFrame]:
    """
    Fetch token OHLCV data from GeckoTerminal API by finding the top pool and getting its data.
    
    Args:
        token_address: Token address
        timeframe: Timeframe for the data (e.g., "1h", "4h", "1d")
        
    Returns:
        DataFrame with OHLCV data or None if fetch failed
    """
    # Get the top pools for the token
    pools = get_top_pools_for_token(token_address)
    
    if not pools:
        logging.error(f"No pools found for token {token_address}")
        return None
    
    # Get the timeframe settings
    timeframe_settings = TIMEFRAMES.get(timeframe, TIMEFRAMES[DEFAULT_TIMEFRAME])
    endpoint = timeframe_settings["endpoint"]
    aggregate = timeframe_settings.get("aggregate", 1)
    
    # Try each pool until we find one that works
    for i, pool in enumerate(pools[:3]):  # Try up to 3 pools
        pool_id = pool.get('id')
        
        if not pool_id:
            logging.warning(f"Pool ID not found in pool data at index {i}")
            continue
        
        # Log the pool ID for debugging
        logging.info(f"Trying pool ID: {pool_id} (pool {i+1} of {min(3, len(pools))})")
        
        # The pool ID in the API response might include the network prefix (e.g., "solana_address")
        # Extract just the address part if needed
        if '_' in pool_id:
            pool_address = pool_id.split('_', 1)[1]
        else:
            pool_address = pool_id
        
        logging.info(f"Extracted pool address: {pool_address}")
        
        # Fetch OHLCV data for this pool
        df = fetch_pool_ohlcv_data('solana', pool_address, endpoint, aggregate=aggregate)
        
        # If we got data, return it
        if df is not None and not df.empty:
            logging.info(f"Successfully fetched data from pool {i+1}")
            return df
        
        logging.warning(f"Failed to get data from pool {i+1}, trying next pool if available")
    
    # If we get here, all pools failed
    logging.error("All pools failed to provide OHLCV data")
    return None

def get_token_chart_data(token_address: str, timeframe: str = DEFAULT_TIMEFRAME) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate chart for a token and return the image path and analysis text.
    
    Args:
        token_address: Token address
        timeframe: Timeframe for the chart
        
    Returns:
        Tuple of (image_path, analysis_text) or (None, None) if failed
    """
    try:
        # First check if the token exists
        token_exists, token_data = check_token_exists(token_address)
        if not token_exists:
            logging.error(f"Token does not exist: {token_address}")
            return None, f"TOKEN_NOT_FOUND:{token_address[:8]}..."
        
        # Get token symbol
        token_symbol = get_token_symbol(token_data)
        logging.info(f"Token symbol: {token_symbol}")
        
        # Get pool information
        pools = get_top_pools_for_token(token_address)
        if not pools:
            logging.error(f"No pools found for token {token_address} ({token_symbol})")
            return None, f"NO_POOLS_FOUND:{token_symbol}"
        
        # Store all pools for reference
        all_pools = {pool.get('id'): pool.get('attributes', {}) for pool in pools if pool.get('id')}
        
        # Fetch token data (this will try multiple pools if needed)
        df = fetch_token_data(token_address, timeframe)
        if df is None or df.empty:
            logging.error(f"No data available for token {token_address} ({token_symbol})")
            return None, f"NO_DATA_AVAILABLE:{token_symbol}"
            
        # Log data shape for debugging
        logging.info(f"Data shape for {token_symbol}: {df.shape}")
        logging.info(f"Data columns: {df.columns.tolist()}")
        logging.info(f"Data index: {df.index[0]} to {df.index[-1]}")
        logging.info(f"Data sample: {df.head(1).to_dict()}")
        
        # Since we don't know which pool succeeded, we'll use the first pool's info as a fallback
        pool_info = pools[0].get('attributes', {})
        pool_name = pool_info.get('name', 'Unknown Pool')
        pool_liquidity = pool_info.get('reserve_in_usd', 'Unknown')
        
        # Generate chart and get signals
        img_path, signals = generate_token_chart(df, token_address, timeframe, pool_name=pool_name)
        
        # Add pool information to signals
        signals['Pool'] = pool_name
        if pool_liquidity != 'Unknown':
            try:
                liquidity_float = float(pool_liquidity)
                signals['Liquidity'] = f"${liquidity_float:,.2f}"
            except (ValueError, TypeError):
                signals['Liquidity'] = pool_liquidity
        
        # Format signals into text
        analysis_text = format_signals_text(signals, token_address)
        
        return img_path, analysis_text
    
    except Exception as e:
        logging.error(f"Chart generation failed: {e}")
        return None, None

def get_token_metadata(token_address: str) -> Optional[Dict]:
    """
    Get token metadata (symbol, name, etc.) from Solana token list.
    This is a placeholder for future implementation.
    
    Args:
        token_address: Token address
        
    Returns:
        Dictionary with token metadata or None if not found
    """
    # TODO: Implement token metadata fetching
    # For now, return a placeholder
    return {
        "symbol": token_address[:5] + "...",
        "name": "Unknown Token",
        "address": token_address
    }
