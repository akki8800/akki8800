# trading_agent/config/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the trading bot.
    Manages API keys, trading parameters, and system settings.
    """
    
    # Exchange API Configuration
    EXCHANGE_ID = os.getenv('EXCHANGE_ID', 'binance')  # Default to Binance
    API_KEY = os.getenv('API_KEY', '')
    API_SECRET = os.getenv('API_SECRET', '')
    TESTNET = os.getenv('TESTNET', 'True').lower() == 'true'  # Use testnet by default
    
    # News API Configuration
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Trading Configuration
    SYMBOLS_TO_TRADE = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
    TIME_FRAME = '1h'  # Common time frames: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    INITIAL_CAPITAL = 10000.0
    RUN_INTERVAL_SECONDS = 3600  # Check every hour
    
    # Risk Management
    RISK_PER_TRADE = 0.02  # 2% risk per trade
    MAX_POSITIONS = 4  # Maximum concurrent positions
    STOP_LOSS_PERCENT = 0.02  # 2% stop loss
    TAKE_PROFIT_PERCENT = 0.04  # 4% take profit (2:1 reward:risk)
    
    # Machine Learning Configuration
    ML_MODEL_TYPE = 'ensemble'  # Options: 'lstm', 'random_forest', 'ensemble'
    LOOKBACK_PERIOD = 60  # Number of periods to look back for ML predictions
    RETRAIN_INTERVAL_DAYS = 7  # Retrain models every 7 days
    
    # Technical Indicators
    USE_INDICATORS = ['RSI', 'MACD', 'BB', 'EMA', 'SMA', 'VOLUME']
    
    # Sentiment Analysis
    USE_SENTIMENT = True
    SENTIMENT_WEIGHT = 0.3  # Weight of sentiment in final decision (0-1)
    
    # Data Storage
    DB_PATH = 'trading_data.db'
    SAVE_PREDICTIONS = True
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'trading_bot.log'
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.TESTNET and (not cls.API_KEY or not cls.API_SECRET):
            raise ValueError("API_KEY and API_SECRET must be set for live trading")
        
        if cls.USE_SENTIMENT and not cls.NEWS_API_KEY:
            print("Warning: NEWS_API_KEY not set. Sentiment analysis will be limited.")
        
        return True

if __name__ == '__main__':
    print("Trading Bot Configuration:")
    print(f"Exchange: {Config.EXCHANGE_ID}")
    print(f"Testnet Mode: {Config.TESTNET}")
    print(f"Symbols: {Config.SYMBOLS_TO_TRADE}")
    print(f"Time Frame: {Config.TIME_FRAME}")
    print(f"ML Model: {Config.ML_MODEL_TYPE}")
    print(f"Use Sentiment: {Config.USE_SENTIMENT}")
    Config.validate()
    print("Configuration validated successfully!")
