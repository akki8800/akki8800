# trading_agent/core/agent.py

import time
import pandas as pd
from trading_agent.data.data_handler import fetch_market_data, preprocess_data
from trading_agent.core.strategy import TradingStrategy

# "Trading in the Zone" Principles for the Agent:
# - Objectivity: The agent follows its rules without emotional interference.
# - Discipline: Execute signals as per the strategy.
# - Patience: Wait for high-probability setups defined by the strategy.
# - Adaptability (long-term): While the prototype is fixed, a real agent might adapt its strategy over time (learn).

class TradingAgent:
    def __init__(self, symbols: list[str], time_frame: str = '1h', capital: float = 10000.0):
        """
        Initializes the Trading Agent.

        Args:
            symbols (list[str]): List of trading symbols to monitor (e.g., ['BTCUSDT', 'ETHUSDT']).
            time_frame (str): Time frame for market data (e.g., '1h', '4h').
            capital (float): Initial trading capital.
        """
        self.symbols = symbols
        self.time_frame = time_frame
        self.capital = capital
        self.portfolio = {symbol: 0.0 for symbol in symbols} # Stores quantity of each asset
        self.cash = capital
        self.strategies = {symbol: TradingStrategy(symbol=symbol) for symbol in symbols}
        self.active_trades = {symbol: [] for symbol in symbols} # To store open positions

        print(f"Trading Agent initialized for symbols: {symbols} with capital: ${capital:.2f}")
        print(f"Agent Mindset: Objective, Disciplined, Patient. (Inspired by 'Trading in the Zone')")

    def check_for_signals(self):
        """
        Checks for trading signals for all monitored symbols.
        """
        print("\nChecking for trading signals...")
        for symbol in self.symbols:
            print(f"\n--- {symbol} ---")
            try:
                # 1. Fetch Data
                raw_data = fetch_market_data(symbol, self.time_frame)
                if raw_data.empty:
                    print(f"No data fetched for {symbol}. Skipping.")
                    continue

                processed_data = preprocess_data(raw_data)

                # 2. Update Strategy with Data
                self.strategies[symbol].update_data(processed_data)

                # 3. Generate Signal
                signal, entry_price, stop_loss, take_profit = self.strategies[symbol].generate_signal()

                # 4. Execute Trade (if signal is BUY or SELL and not already in a similar trade)
                if signal == "BUY":
                    # "Trading in the Zone": Accept the risk and execute if the edge is present.
                    self.execute_trade(symbol, "BUY", entry_price, stop_loss, take_profit, processed_data['close'].iloc[-1])
                elif signal == "SELL":
                    # For this prototype, we'll focus on long trades. Short selling can be added later.
                    # self.execute_trade(symbol, "SELL", entry_price, stop_loss, take_profit, processed_data['close'].iloc[-1])
                    print(f"SELL signal for {symbol} identified but not acted upon (prototype focuses on BUYs).")
                else: # HOLD
                    print(f"Signal for {symbol}: HOLD. Current Price: {processed_data['close'].iloc[-1]:.2f}")

                # 5. Manage existing trades for this symbol (check SL/TP)
                self.manage_active_trades(symbol, processed_data['close'].iloc[-1], processed_data['high'].iloc[-1], processed_data['low'].iloc[-1])

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                # In a real system, log this error properly.

    def execute_trade(self, symbol: str, side: str, entry_price: float, stop_loss: float, take_profit: float, current_market_price: float):
        """
        Executes a trade (simulated).

        Args:
            symbol (str): Trading symbol.
            side (str): 'BUY' or 'SELL'.
            entry_price (float): Desired entry price from signal.
            stop_loss (float): Stop loss price.
            take_profit (float): Take profit price.
            current_market_price (float): The actual current market price to execute at (simulating slippage/market order).
        """
        # "Trading in the Zone": Thinking in Probabilities. Not every trade will be a winner.
        # Risk management: Only risk a small portion of capital (defined in strategy)

        # For simplicity, assume we can always trade at the current_market_price
        # and we use a fixed amount of capital per trade or a fixed position size.
        # Let's define position size based on risk_per_trade from strategy

        risk_amount_per_trade = self.cash * self.strategies[symbol].risk_per_trade
        if entry_price == 0 or abs(entry_price - stop_loss) == 0: # Avoid division by zero or invalid SL
             print(f"Trade for {symbol} aborted due to invalid entry/SL price.")
             return

        position_size_units = risk_amount_per_trade / abs(entry_price - stop_loss) # Number of units to buy/sell
        trade_cost = position_size_units * current_market_price

        if trade_cost > self.cash :
            print(f"Not enough cash to execute {side} for {symbol}. Need ${trade_cost:.2f}, Have ${self.cash:.2f}")
            return

        if side == "BUY":
            self.cash -= trade_cost
            self.portfolio[symbol] += position_size_units
            trade_info = {
                "side": "BUY",
                "entry_price": current_market_price, # Actual entry
                "size": position_size_units,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "OPEN"
            }
            self.active_trades[symbol].append(trade_info)
            print(f"EXECUTED BUY: {position_size_units:.4f} {symbol} at ${current_market_price:.2f}. Cost: ${trade_cost:.2f}")
            print(f"  SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

        # Add SELL (short selling) logic here if needed in the future
        # elif side == "SELL":
        #     # Requires margin, more complex portfolio tracking
        #     print(f"Simulating SELL for {symbol} (not fully implemented in portfolio).")

        print(f"Current Cash: ${self.cash:.2f}")

    def manage_active_trades(self, symbol: str, current_price: float, current_high: float, current_low: float):
        """
        Manages active trades by checking for SL/TP hits.
        "Trading in the Zone": Letting the market tell you when your edge is gone (SL) or achieved (TP).
        """
        trades_to_remove = []
        for i, trade in enumerate(self.active_trades[symbol]):
            if trade["status"] == "OPEN":
                closed = False
                # Check Stop Loss
                if trade["side"] == "BUY" and current_low <= trade["stop_loss"]:
                    print(f"STOP LOSS HIT for {symbol} BUY trade. Entry: {trade['entry_price']:.2f}, SL: {trade['stop_loss']:.2f}, Closed at: {trade['stop_loss']:.2f}")
                    self.cash += trade["size"] * trade["stop_loss"] # Sell back at SL price
                    self.portfolio[symbol] -= trade["size"]
                    trade["status"] = "CLOSED_SL"
                    closed = True
                # Check Take Profit
                elif trade["side"] == "BUY" and current_high >= trade["take_profit"]:
                    print(f"TAKE PROFIT HIT for {symbol} BUY trade. Entry: {trade['entry_price']:.2f}, TP: {trade['take_profit']:.2f}, Closed at: {trade['take_profit']:.2f}")
                    self.cash += trade["size"] * trade["take_profit"] # Sell back at TP price
                    self.portfolio[symbol] -= trade["size"]
                    trade["status"] = "CLOSED_TP"
                    closed = True

                # Add logic for SELL trades SL/TP if implemented
                # ...

                if closed:
                    trades_to_remove.append(i)
                    print(f"Updated Cash: ${self.cash:.2f}, Portfolio {symbol}: {self.portfolio[symbol]:.4f}")


        # Remove closed trades (iterating in reverse to handle indices correctly)
        for i in sorted(trades_to_remove, reverse=True):
            del self.active_trades[symbol][i]


    def run(self, interval_seconds: int = 3600):
        """
        Main loop for the agent. Fetches data and checks signals periodically.

        Args:
            interval_seconds (int): Time in seconds between checks.
        """
        print(f"\nAgent started. Checking for signals every {interval_seconds} seconds.")
        print("Press Ctrl+C to stop the agent.")
        try:
            while True:
                self.check_for_signals()
                self.display_portfolio()
                print(f"\nWaiting for {interval_seconds} seconds for the next check...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nAgent stopping. Thank you for using the prototype.")
        finally:
            self.display_portfolio()
            print("Agent shutdown complete.")
            # "Trading in the Zone": Review performance objectively. (Could add a performance summary here)

    def display_portfolio(self):
        print("\n--- Portfolio Status ---")
        print(f"Cash: ${self.cash:.2f}")
        print("Holdings:")
        has_holdings = False
        for symbol, quantity in self.portfolio.items():
            if quantity > 0:
                # To get current value, we'd need latest price again, simplified here
                print(f"  {symbol}: {quantity:.4f} units")
                has_holdings = True
        if not has_holdings:
            print("  No current holdings.")

        print("Active Trades:")
        has_active_trades = False
        for symbol, trades in self.active_trades.items():
            if trades:
                has_active_trades = True
                print(f"  {symbol}:")
                for trade in trades:
                    print(f"    Side: {trade['side']}, Entry: {trade['entry_price']:.2f}, Size: {trade['size']:.4f}, SL: {trade['stop_loss']:.2f}, TP: {trade['take_profit']:.2f}, Status: {trade['status']}")
        if not has_active_trades:
            print("  No active trades.")
        print("------------------------")


if __name__ == '__main__':
    # Example Usage:
    # For quick testing, reduce the interval and use a small number of cycles or manual calls

    # Ensure paths are correct if running directly
    # This setup assumes data_handler and strategy are accessible.

    print("\n--- Trading Agent Module Test ---")
    # symbols_to_trade = ['BTCUSDT', 'ETHUSDT'] # Focus on fewer for faster test
    symbols_to_trade = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
    agent = TradingAgent(symbols=symbols_to_trade, time_frame='1h', capital=10000.00)

    # Simulate a few cycles instead of running indefinitely for testing
    print("\nSimulating a few agent cycles (not running indefinitely)...")
    for i in range(2): # Run 2 cycles
        print(f"\n--- Cycle {i+1} ---")
        agent.check_for_signals()
        agent.display_portfolio()
        if i < 1: # Don't wait after the last cycle in test
             print("Test: Skipping long wait, proceeding to next cycle mock.")
             # time.sleep(2) # Short wait for readability in test output

    print("\n--- Agent Test Simulation Complete ---")
    agent.display_portfolio()
    print("Note: This agent uses placeholder data and simplified logic.")
    print("Market interactions (fetching data, executing trades) are simulated.")
    print("Principles from 'Trading in the Zone' are incorporated conceptually in agent design and comments.")
