# trading_agent/core/strategy.py
import pandas as pd
import numpy as np

# "Trading in the Zone" principle:
# 1. Anything can happen.
# 2. You don't need to know what is going to happen next in order to make money.
# 3. There is a random distribution between wins and losses for any given set of variables that define an edge.
# 4. An edge is nothing more than an indication of a higher probability of one thing happening over another.
# 5. Every moment in the market is unique.

class TradingStrategy:
    def __init__(self, symbol: str, risk_per_trade: float = 0.01):
        """
        Initializes the trading strategy.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            risk_per_trade (float): The percentage of capital to risk per trade.
                                    (Trading in the Zone: Manage risk)
        """
        self.symbol = symbol
        self.risk_per_trade = risk_per_trade
        self.historical_data = pd.DataFrame()
        print(f"Strategy initialized for {symbol}. Risk per trade: {risk_per_trade*100}%")

    def update_data(self, new_data: pd.DataFrame):
        """
        Updates the historical data used by the strategy.

        Args:
            new_data (pd.DataFrame): New market data to append or update.
        """
        # For simplicity, this prototype replaces data. A real system might append.
        self.historical_data = new_data
        # print(f"Data updated for {self.symbol}. Shape: {self.historical_data.shape}")


    def identify_support_resistance(self, data: pd.DataFrame, window: int = 20, std_dev_multiplier: float = 1.5) -> tuple[list, list]:
        """
        Identifies potential support and resistance levels.
        This is a simplified approach using rolling min/max or pivot points.
        A more advanced version would use clustering, peak/trough detection, or volume profiles.

        Args:
            data (pd.DataFrame): Price data with 'high', 'low', 'close'.
            window (int): Rolling window for identifying S/R.
            std_dev_multiplier (float): For dynamic levels based on volatility (e.g. Bollinger Bands concept).

        Returns:
            tuple[list, list]: A tuple containing two lists: support_levels and resistance_levels.
        """
        if data.empty or len(data) < window:
            # print("Not enough data to identify S/R levels.")
            return [], []

        # Method 1: Simple rolling min/max for minor levels
        minor_supports = data['low'].rolling(window=window, center=True).min().dropna().tolist()
        minor_resistances = data['high'].rolling(window=window, center=True).max().dropna().tolist()

        # Method 2: Pivot Points (Classic) - using last period's data typically
        # For simplicity, we'll use the average of the last 'window' period
        last_period = data.iloc[-window:] if len(data) >= window else data
        if not last_period.empty:
            pivot = (last_period['high'].mean() + last_period['low'].mean() + last_period['close'].mean()) / 3
            s1 = (2 * pivot) - last_period['high'].mean()
            r1 = (2 * pivot) - last_period['low'].mean()
            s2 = pivot - (last_period['high'].mean() - last_period['low'].mean())
            r2 = pivot + (last_period['high'].mean() - last_period['low'].mean())

            major_supports = sorted(list(set([s1, s2]))) # Crude major levels
            major_resistances = sorted(list(set([r1, r2])))
        else:
            major_supports, major_resistances = [], []

        # Combine and simplify (remove very close levels)
        # For this prototype, we'll just return a mix. A real version needs refinement.
        supports = sorted(list(set(minor_supports[-5:] + major_supports))) # Take recent minor ones
        resistances = sorted(list(set(minor_resistances[-5:] + major_resistances)))

        # Filter out levels too far from the current price (e.g., > 20% away)
        current_price = data['close'].iloc[-1]
        supports = [s for s in supports if abs(s - current_price) / current_price < 0.20]
        resistances = [r for r in resistances if abs(r - current_price) / current_price < 0.20 and r > current_price]
        supports = [s for s in supports if s < current_price]


        # print(f"Identified S/R for {self.symbol}: Supports: {supports}, Resistances: {resistances}")
        return supports, resistances

    def analyze_patterns(self, data: pd.DataFrame) -> str:
        """
        Analyzes chart patterns.
        Placeholder: In a real system, this would involve complex pattern recognition
        (e.g., head and shoulders, triangles, flags).

        Args:
            data (pd.DataFrame): Price data.

        Returns:
            str: Identified pattern or 'None'.
        """
        # "Trading in the Zone": An edge is just a higher probability. Patterns contribute to this edge.
        # This is highly simplified. Real pattern recognition is complex.
        if len(data) < 3:
            return "None"

        # Example: Simple "double bottom" like pattern (very naive)
        # Look at the last N candles, e.g., 20
        recent_lows = data['low'].tail(20)
        if len(recent_lows) > 10: # Need enough data points
            first_low = recent_lows.iloc[:5].min()
            second_low = recent_lows.iloc[5:10].min() # Simplified check
            current_price = data['close'].iloc[-1]
            # if abs(first_low - second_low) / first_low < 0.01 and current_price > first_low: # Second low is close to first
                 # return "Potential Double Bottom"

        # print(f"Pattern analysis for {self.symbol}: No significant pattern identified (placeholder).")
        return "None" # Placeholder

    def generate_signal(self) -> tuple[str, float, float, float]:
        """
        Generates a trading signal based on the strategy.
        Signal: 'BUY', 'SELL', or 'HOLD'.
        Price: Entry price for BUY/SELL.
        Stop Loss: Price level to exit if trade goes wrong.
        Take Profit: Price level to exit if trade is profitable.

        Returns:
            tuple[str, float, float, float]: (signal, entry_price, stop_loss, take_profit)
        """
        if self.historical_data.empty or len(self.historical_data) < 20: # Need at least 20 periods for S/R
            # print("Not enough historical data to generate a signal.")
            return "HOLD", 0.0, 0.0, 0.0

        current_price = self.historical_data['close'].iloc[-1]
        supports, resistances = self.identify_support_resistance(self.historical_data)
        pattern = self.analyze_patterns(self.historical_data) # Currently a placeholder

        # "Trading in the Zone": Act on your edge without hesitation when conditions are met.
        # Trade Confirmation: Only trade when criteria are met.

        signal = "HOLD"
        entry_price = 0.0
        stop_loss = 0.0
        take_profit = 0.0

        # Simplified Buy Signal: Price is near a strong support level
        if supports:
            strongest_support = max(supports) # Closest support below current price
            # Check if current price is close to this support (e.g., within 0.5% for this prototype)
            if strongest_support < current_price and (current_price - strongest_support) / current_price < 0.005:
                # Confirmation: Add more rules here, e.g., bullish candle pattern, volume increase
                # For prototype, simple proximity is enough
                if self.confirm_trade("BUY", current_price, pattern, supports, resistances):
                    signal = "BUY"
                    entry_price = current_price
                    # "Trading in the Zone": Always define your risk beforehand.
                    stop_loss = strongest_support * 0.99 # Place SL slightly below support
                    # Basic take profit: Aim for the nearest resistance or a fixed R:R ratio
                    if resistances:
                        take_profit = min(resistances) if min(resistances) > entry_price else entry_price * 1.02 # TP at nearest R or 2%
                    else:
                        take_profit = entry_price * 1.02 # Default 2% TP if no resistance found above

                    # Ensure TP offers reasonable reward compared to risk
                    if (take_profit - entry_price) < (entry_price - stop_loss):
                        # print("Buy signal: TP too close, adjusting or holding.")
                        signal = "HOLD" # Or adjust TP/SL based on more complex rules


        # Simplified Sell Signal: Price is near a strong resistance level
        if signal == "HOLD" and resistances: # Only if no buy signal
            strongest_resistance = min(resistances) # Closest resistance above current price
            if strongest_resistance > current_price and (strongest_resistance - current_price) / current_price < 0.005:
                if self.confirm_trade("SELL", current_price, pattern, supports, resistances):
                    signal = "SELL"
                    entry_price = current_price
                    stop_loss = strongest_resistance * 1.01 # Place SL slightly above resistance
                    if supports:
                        take_profit = max(supports) if max(supports) < entry_price else entry_price * 0.98
                    else:
                        take_profit = entry_price * 0.98 # Default 2% TP

                    if (entry_price - take_profit) < (stop_loss - entry_price):
                        # print("Sell signal: TP too close, adjusting or holding.")
                        signal = "HOLD"

        if signal != "HOLD":
            print(f"Signal for {self.symbol}: {signal} at {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

        return signal, entry_price, stop_loss, take_profit

    def confirm_trade(self, side: str, price: float, pattern: str, supports: list, resistances: list) -> bool:
        """
        Confirms a trade based on additional criteria.
        (Placeholder for more complex confirmation logic)

        Args:
            side (str): 'BUY' or 'SELL'
            price (float): The potential entry price.
            pattern (str): Identified chart pattern.
            supports (list): List of support levels.
            resistances (list): List of resistance levels.

        Returns:
            bool: True if the trade is confirmed, False otherwise.
        """
        # "Trading in the Zone": The market doesn't owe you anything. Confirmation helps filter noise.
        # For this prototype, we'll keep it simple.
        # A real system might check:
        # - Volume confirmation
        # - Candlestick patterns (e.g., engulfing, pin bar at S/R)
        # - Indicator confirmation (e.g., RSI divergence, MACD crossover)
        # - Multiple time frame agreement

        # Example: if pattern was "Potential Double Bottom" and side is 'BUY', that's a stronger confirmation.
        # if side == "BUY" and pattern == "Potential Double Bottom":
        #     print(f"Trade Confirmed for {self.symbol} ({side}) based on pattern: {pattern}")
        #     return True

        # For now, all trades meeting basic S/R criteria are "confirmed" for the prototype
        # print(f"Trade Confirmed for {self.symbol} ({side}) based on S/R proximity.")
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
