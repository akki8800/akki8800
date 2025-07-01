# trading_agent/data/data_handler.py

import pandas as pd
import numpy as np

# Placeholder for fetching live market data
# In a real application, this would connect to a crypto exchange API (e.g., Binance, Coinbase)
def fetch_market_data(symbol: str, time_frame: str = '1h') -> pd.DataFrame:
    """
    Fetches historical market data for a given symbol and time frame.
    For this prototype, it returns a DataFrame with random data.

    Args:
        symbol (str): The trading symbol (e.g., 'BTCUSDT').
        time_frame (str): The time frame for the data (e.g., '1h', '4h', '1d').

    Returns:
        pd.DataFrame: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """
    print(f"Fetching placeholder data for {symbol} ({time_frame})...")
    # Generate some random data for demonstration
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='H')
    data = {
        'timestamp': dates,
        'open': np.random.uniform(30000, 60000, size=100),
        'high': np.random.uniform(31000, 61000, size=100),
        'low': np.random.uniform(29000, 59000, size=100),
        'close': np.random.uniform(30000, 60000, size=100),
        'volume': np.random.uniform(100, 1000, size=100)
    }
    df = pd.DataFrame(data)

    # Ensure 'high' is always >= 'open' and 'close', and 'low' is always <= 'open' and 'close'
    df['high'] = df[['high', 'open', 'close']].max(axis=1)
    df['low'] = df[['low', 'open', 'close']].min(axis=1)

    # Simulate data for different symbols with different price ranges
    if "BTC" in symbol.upper():
        df[['open', 'high', 'low', 'close']] *= 1 # Base range
    elif "ETH" in symbol.upper():
        df[['open', 'high', 'low', 'close']] *= 0.05 # ETH ~5% of BTC
    elif "BNB" in symbol.upper():
        df[['open', 'high', 'low', 'close']] *= 0.01 # BNB ~1% of BTC
    elif "SOL" in symbol.upper():
        df[['open', 'high', 'low', 'close']] *= 0.0025 # SOL ~0.25% of BTC
    else:
        df[['open', 'high', 'low', 'close']] *= 0.1 # Generic other


    return df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs any necessary preprocessing on the market data.
    (e.g., calculating indicators, handling missing values)

    Args:
        df (pd.DataFrame): Raw market data.

    Returns:
        pd.DataFrame: Processed market data.
    """
    # For now, just return the DataFrame as is or add simple indicators
    # Example: Calculate a simple moving average (SMA)
    # df['SMA_20'] = df['close'].rolling(window=20).mean()
    print("Preprocessing data...")
    # Ensure data types are correct
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    return df

if __name__ == '__main__':
    # Example usage:
    symbols_to_trade = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
    for sym in symbols_to_trade:
        raw_data = fetch_market_data(sym, '1h')
        processed_data = preprocess_data(raw_data)
        print(f"\nProcessed data for {sym}:")
        print(processed_data.head())
        print(f"Data types for {sym}:\n{processed_data.dtypes}")

    print("\nNote: This data_handler.py uses placeholder data for demonstration purposes.")
    print("In a real trading agent, you would integrate with a cryptocurrency exchange API.")
