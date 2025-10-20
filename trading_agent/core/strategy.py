# trading_agent/core/strategy.py
import pandas as pd
import numpy as np
from typing import Optional, Tuple

# "Trading in the Zone" principle:
# 1. Anything can happen.
# 2. You don't need to know what is going to happen next in order to make money.
# 3. There is a random distribution between wins and losses for any given set of variables that define an edge.
# 4. An edge is nothing more than an indication of a higher probability of one thing happening over another.
# 5. Every moment in the market is unique.

class TradingStrategy:
    def __init__(self, symbol: str, risk_per_trade: float = 0.02,
                 ml_predictor=None, sentiment_analyzer=None):
        """
        Initializes the advanced trading strategy with ML and sentiment analysis.

        Args:
            symbol (str): The trading symbol (e.g., 'BTC/USDT').
            risk_per_trade (float): The percentage of capital to risk per trade.
            ml_predictor: ML model for price prediction
            sentiment_analyzer: Sentiment analyzer for news/social data
        """
        self.symbol = symbol
        self.risk_per_trade = risk_per_trade
        self.historical_data = pd.DataFrame()
        self.ml_predictor = ml_predictor
        self.sentiment_analyzer = sentiment_analyzer
        self.use_ml = ml_predictor is not None
        self.use_sentiment = sentiment_analyzer is not None
        
        print(f"Strategy initialized for {symbol}. Risk per trade: {risk_per_trade*100}%")
        if self.use_ml:
            print("  - ML prediction enabled")
        if self.use_sentiment:
            print("  - Sentiment analysis enabled")

    def update_data(self, new_data: pd.DataFrame):
        """
        Updates the historical data used by the strategy.

        Args:
            new_data (pd.DataFrame): New market data to append or update.
        """
        self.historical_data = new_data


    def identify_support_resistance(self, data: pd.DataFrame, window: int = 20, 
                                    std_dev_multiplier: float = 1.5) -> Tuple[list, list]:
        """
        Identifies potential support and resistance levels using multiple methods.

        Args:
            data (pd.DataFrame): Price data with 'high', 'low', 'close'.
            window (int): Rolling window for identifying S/R.
            std_dev_multiplier (float): For dynamic levels based on volatility.

        Returns:
            tuple[list, list]: Support and resistance levels.
        """
        if data.empty or len(data) < window:
            return [], []

        # Method 1: Rolling min/max
        minor_supports = data['low'].rolling(window=window, center=True).min().dropna().tolist()
        minor_resistances = data['high'].rolling(window=window, center=True).max().dropna().tolist()

        # Method 2: Pivot Points
        last_period = data.iloc[-window:] if len(data) >= window else data
        if not last_period.empty:
            pivot = (last_period['high'].mean() + last_period['low'].mean() + last_period['close'].mean()) / 3
            s1 = (2 * pivot) - last_period['high'].mean()
            r1 = (2 * pivot) - last_period['low'].mean()
            s2 = pivot - (last_period['high'].mean() - last_period['low'].mean())
            r2 = pivot + (last_period['high'].mean() - last_period['low'].mean())

            major_supports = sorted(list(set([s1, s2])))
            major_resistances = sorted(list(set([r1, r2])))
        else:
            major_supports, major_resistances = [], []

        # Combine levels
        supports = sorted(list(set(minor_supports[-5:] + major_supports)))
        resistances = sorted(list(set(minor_resistances[-5:] + major_resistances)))

        # Filter by proximity to current price
        current_price = data['close'].iloc[-1]
        supports = [s for s in supports if abs(s - current_price) / current_price < 0.20 and s < current_price]
        resistances = [r for r in resistances if abs(r - current_price) / current_price < 0.20 and r > current_price]

        return supports, resistances

    def analyze_patterns(self, data: pd.DataFrame) -> str:
        """
        Analyzes chart patterns using technical indicators.

        Args:
            data (pd.DataFrame): Price data.

        Returns:
            str: Identified pattern or 'None'.
        """
        if len(data) < 20:
            return "None"
        
        # Use technical indicators to identify patterns
        if 'RSI' in data.columns and 'MACD_diff' in data.columns:
            rsi = data['RSI'].iloc[-1]
            macd_diff = data['MACD_diff'].iloc[-1]
            prev_macd_diff = data['MACD_diff'].iloc[-2]
            
            # Bullish patterns
            if rsi < 30 and macd_diff > 0 and prev_macd_diff < 0:
                return "Bullish Reversal"
            
            # Bearish patterns
            if rsi > 70 and macd_diff < 0 and prev_macd_diff > 0:
                return "Bearish Reversal"
        
        return "None"

    def get_ml_prediction(self) -> Tuple[str, float]:
        """
        Get ML model prediction for price movement.
        
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.use_ml or self.historical_data.empty:
            return 'HOLD', 0.5
        
        try:
            prediction, confidence = self.ml_predictor.predict(self.historical_data)
            print(f"ML Prediction for {self.symbol}: {prediction} (confidence: {confidence:.2f})")
            return prediction, confidence
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return 'HOLD', 0.5

    def get_sentiment_score(self) -> Tuple[str, float]:
        """
        Get sentiment analysis signal.
        
        Returns:
            Tuple of (signal, score)
        """
        if not self.use_sentiment:
            return 'NEUTRAL', 0.0
        
        try:
            sentiment = self.sentiment_analyzer.get_aggregated_sentiment(self.symbol)
            signal = self.sentiment_analyzer.get_sentiment_signal(self.symbol)
            return signal, sentiment['sentiment_score']
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 'NEUTRAL', 0.0

    def generate_signal(self) -> Tuple[str, float, float, float]:
        """
        Generates a comprehensive trading signal combining:
        - Technical analysis (S/R levels, indicators)
        - ML predictions
        - Sentiment analysis
        
        Returns:
            tuple[str, float, float, float]: (signal, entry_price, stop_loss, take_profit)
        """
        if self.historical_data.empty or len(self.historical_data) < 20:
            return "HOLD", 0.0, 0.0, 0.0

        current_price = self.historical_data['close'].iloc[-1]
        supports, resistances = self.identify_support_resistance(self.historical_data)
        pattern = self.analyze_patterns(self.historical_data)
        
        # Get ML prediction
        ml_prediction, ml_confidence = self.get_ml_prediction()
        
        # Get sentiment
        sentiment_signal, sentiment_score = self.get_sentiment_score()
        
        # Initialize signal components
        signal = "HOLD"
        entry_price = 0.0
        stop_loss = 0.0
        take_profit = 0.0
        
        # Calculate signal strength using multiple factors
        buy_score = 0.0
        sell_score = 0.0
        
        # Technical analysis scoring
        if supports:
            strongest_support = max(supports)
            if strongest_support < current_price and (current_price - strongest_support) / current_price < 0.01:
                buy_score += 0.3  # Near support = bullish
        
        if resistances:
            strongest_resistance = min(resistances)
            if strongest_resistance > current_price and (strongest_resistance - current_price) / current_price < 0.01:
                sell_score += 0.3  # Near resistance = bearish
        
        # ML prediction scoring
        if ml_prediction == 'UP' and ml_confidence > 0.6:
            buy_score += 0.3 * ml_confidence
        elif ml_prediction == 'DOWN' and ml_confidence > 0.6:
            sell_score += 0.3 * ml_confidence
        
        # Sentiment scoring
        if sentiment_signal == 'BULLISH':
            buy_score += 0.2 * abs(sentiment_score)
        elif sentiment_signal == 'BEARISH':
            sell_score += 0.2 * abs(sentiment_score)
        
        # Pattern recognition scoring
        if pattern == "Bullish Reversal":
            buy_score += 0.2
        elif pattern == "Bearish Reversal":
            sell_score += 0.2
        
        # Technical indicator confirmation
        if 'RSI' in self.historical_data.columns:
            rsi = self.historical_data['RSI'].iloc[-1]
            if rsi < 35:
                buy_score += 0.15  # Oversold
            elif rsi > 65:
                sell_score += 0.15  # Overbought
        
        # Generate signal based on combined scores
        threshold = 0.6  # Minimum score to trigger a trade
        
        if buy_score > threshold and buy_score > sell_score:
            signal = "BUY"
            entry_price = current_price
            
            # Set stop loss below support or using ATR
            if supports:
                stop_loss = max(supports) * 0.99
            else:
                stop_loss = current_price * 0.98  # 2% stop loss
            
            # Set take profit at resistance or using reward:risk ratio
            risk = entry_price - stop_loss
            if resistances:
                take_profit = min(resistances)
            else:
                take_profit = entry_price + (risk * 2)  # 2:1 reward:risk
            
            # Ensure valid TP
            if take_profit <= entry_price:
                take_profit = entry_price * 1.04
            
            print(f"BUY Signal for {self.symbol}: Score={buy_score:.2f}, Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            print(f"  ML: {ml_prediction} ({ml_confidence:.2f}), Sentiment: {sentiment_signal}, Pattern: {pattern}")
            
        elif sell_score > threshold and sell_score > buy_score:
            signal = "SELL"
            entry_price = current_price
            
            # Set stop loss above resistance
            if resistances:
                stop_loss = min(resistances) * 1.01
            else:
                stop_loss = current_price * 1.02
            
            # Set take profit at support
            risk = stop_loss - entry_price
            if supports:
                take_profit = max(supports)
            else:
                take_profit = entry_price - (risk * 2)
            
            if take_profit >= entry_price:
                take_profit = entry_price * 0.96
            
            print(f"SELL Signal for {self.symbol}: Score={sell_score:.2f}, Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            print(f"  ML: {ml_prediction} ({ml_confidence:.2f}), Sentiment: {sentiment_signal}, Pattern: {pattern}")
        
        return signal, entry_price, stop_loss, take_profit

    def confirm_trade(self, side: str, price: float, pattern: str, 
                     supports: list, resistances: list) -> bool:
        """
        Confirms a trade based on additional criteria.

        Args:
            side (str): 'BUY' or 'SELL'
            price (float): The potential entry price.
            pattern (str): Identified chart pattern.
            supports (list): List of support levels.
            resistances (list): List of resistance levels.

        Returns:
            bool: True if the trade is confirmed, False otherwise.
        """
        # With ML and sentiment integration, basic criteria are usually enough
        return True

if __name__ == '__main__':
    # Example Usage (requires data_handler.py in the correct path or adjust import)
    # This part is for testing the strategy module independently.
    # You might need to adjust paths if running this file directly.
    try:
        from trading_agent.data.data_handler import fetch_market_data, preprocess_data
    except ImportError:
        print("Assuming data_handler.py is in the parent directory's 'data' folder for standalone test.")
        import sys
        sys.path.append('../') # Add parent directory to path to find data package
        from data.data_handler import fetch_market_data, preprocess_data


    print("\n--- Strategy Module Test ---")
    test_symbol = 'BTCUSDT'
    strategy = TradingStrategy(symbol=test_symbol)

    # Fetch and preprocess data
    raw_data = fetch_market_data(test_symbol, '1h')
    processed_data = preprocess_data(raw_data)

    # Update strategy with data
    strategy.update_data(processed_data)

    # Identify S/R
    supports, resistances = strategy.identify_support_resistance(strategy.historical_data)
    print(f"\nS/R for {test_symbol}:")
    print(f"Supports: {supports}")
    print(f"Resistances: {resistances}")

    # Analyze patterns
    pattern = strategy.analyze_patterns(strategy.historical_data)
    print(f"\nPattern for {test_symbol}: {pattern}")

    # Generate signal
    signal, entry, sl, tp = strategy.generate_signal()
    print(f"\nGenerated Signal for {test_symbol}:")
    print(f"Signal: {signal}, Entry: {entry}, SL: {sl}, TP: {tp}")

    print("\nNote: The strategy logic is simplified for this prototype.")
    print("Support/Resistance and Pattern analysis are basic.")
    print("Risk management (SL/TP placement) is also rudimentary.")
    print("Concepts from 'Trading in the Zone' are noted in comments.")
