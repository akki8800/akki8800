# trading_agent/data/data_handler.py

import pandas as pd
import numpy as np
import ccxt
from datetime import datetime, timedelta
from typing import Optional
import ta

class DataHandler:
    """
    Advanced data handler that connects to real cryptocurrency exchanges
    and provides comprehensive market data with technical indicators.
    """
    
    def __init__(self, exchange_id: str = 'binance', testnet: bool = True, 
                 api_key: str = '', api_secret: str = ''):
        """
        Initialize the data handler with exchange connection.
        
        Args:
            exchange_id: The exchange to connect to (e.g., 'binance', 'coinbase')
            testnet: Whether to use testnet/sandbox mode
            api_key: API key for the exchange
            api_secret: API secret for the exchange
        """
        self.exchange_id = exchange_id
        self.testnet = testnet
        
        try:
            # Initialize exchange
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'} if testnet else {}
            })
            
            if testnet:
                # Set testnet URLs if available
                if hasattr(self.exchange, 'set_sandbox_mode'):
                    self.exchange.set_sandbox_mode(True)
                    print(f"Connected to {exchange_id} TESTNET")
                else:
                    print(f"Warning: Testnet not available for {exchange_id}, using simulation mode")
                    self.exchange = None
            else:
                print(f"Connected to {exchange_id} LIVE")
                
        except Exception as e:
            print(f"Error connecting to exchange: {e}")
            print("Falling back to simulation mode")
            self.exchange = None
    
    def fetch_market_data(self, symbol: str, time_frame: str = '1h', 
                         limit: int = 100, use_real_data: bool = True) -> pd.DataFrame:
        """
        Fetches historical market data for a given symbol and time frame.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            time_frame: Time frame for the data (e.g., '1h', '4h', '1d')
            limit: Number of data points to fetch
            use_real_data: Whether to use real exchange data or simulated data
            
        Returns:
            DataFrame with OHLCV data
        """
        if use_real_data and self.exchange:
            try:
                print(f"Fetching real market data for {symbol} ({time_frame})...")
                ohlcv = self.exchange.fetch_ohlcv(symbol, time_frame, limit=limit)
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                return df
                
            except Exception as e:
                print(f"Error fetching real data: {e}. Using simulated data.")
                return self._generate_simulated_data(symbol, time_frame, limit)
        else:
            return self._generate_simulated_data(symbol, time_frame, limit)
    
    def _generate_simulated_data(self, symbol: str, time_frame: str, limit: int) -> pd.DataFrame:
        """Generate simulated market data for testing."""
        print(f"Generating simulated data for {symbol} ({time_frame})...")
        
        # Generate dates based on timeframe
        dates = pd.date_range(end=pd.Timestamp.now(), periods=limit, freq='H')
        
        # Generate realistic price data with trend and volatility
        base_price = 40000  # Base for BTC
        trend = np.linspace(0, np.random.uniform(-0.1, 0.1), limit)
        volatility = np.random.normal(0, 0.02, limit)
        
        close_prices = base_price * (1 + trend + volatility)
        
        data = {
            'timestamp': dates,
            'open': close_prices * (1 + np.random.uniform(-0.005, 0.005, limit)),
            'high': close_prices * (1 + np.random.uniform(0.005, 0.015, limit)),
            'low': close_prices * (1 + np.random.uniform(-0.015, -0.005, limit)),
            'close': close_prices,
            'volume': np.random.uniform(100, 1000, limit)
        }
        df = pd.DataFrame(data)
        
        # Ensure OHLC consistency
        df['high'] = df[['high', 'open', 'close']].max(axis=1)
        df['low'] = df[['low', 'open', 'close']].min(axis=1)
        
        # Adjust for different symbols
        if 'ETH' in symbol.upper():
            df[['open', 'high', 'low', 'close']] *= 0.05
        elif 'BNB' in symbol.upper():
            df[['open', 'high', 'low', 'close']] *= 0.01
        elif 'SOL' in symbol.upper():
            df[['open', 'high', 'low', 'close']] *= 0.0025
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame, add_indicators: bool = True) -> pd.DataFrame:
        """
        Preprocesses market data and adds technical indicators.
        
        Args:
            df: Raw market data
            add_indicators: Whether to add technical indicators
            
        Returns:
            Processed DataFrame with indicators
        """
        print("Preprocessing data and adding technical indicators...")
        
        # Ensure data types
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        if add_indicators:
            df = self.add_technical_indicators(df)
        
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds comprehensive technical indicators to the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        try:
            # Trend Indicators
            df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['SMA_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['EMA_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['EMA_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            df['MACD_diff'] = macd.macd_diff()
            
            # Momentum Indicators
            df['RSI'] = ta.momentum.rsi(df['close'], window=14)
            df['Stoch_RSI'] = ta.momentum.stochrsi(df['close'], window=14)
            
            # Volatility Indicators
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['BB_upper'] = bollinger.bollinger_hband()
            df['BB_middle'] = bollinger.bollinger_mavg()
            df['BB_lower'] = bollinger.bollinger_lband()
            df['BB_width'] = bollinger.bollinger_wband()
            
            # ATR (Average True Range)
            df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Volume Indicators
            df['Volume_SMA'] = ta.volume.volume_weighted_average_price(
                df['high'], df['low'], df['close'], df['volume']
            )
            
            # Trend strength
            df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'])
            
            # Fill NaN values with forward fill then backward fill
            df = df.fillna(method='ffill').fillna(method='bfill')
            
        except Exception as e:
            print(f"Error adding technical indicators: {e}")
            print("Continuing with basic data...")
        
        return df


# Legacy functions for backward compatibility
def fetch_market_data(symbol: str, time_frame: str = '1h') -> pd.DataFrame:
    """Legacy function - creates a DataHandler and fetches data."""
    handler = DataHandler()
    return handler.fetch_market_data(symbol, time_frame, use_real_data=False)


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function - creates a DataHandler and preprocesses data."""
    handler = DataHandler()
    return handler.preprocess_data(df)

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
