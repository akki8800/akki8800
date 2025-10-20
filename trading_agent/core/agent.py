# trading_agent/core/agent.py

import time
import pandas as pd
from data.data_handler import DataHandler
from core.strategy import TradingStrategy
from ml_models.predictor import MLPredictor
from news.sentiment_analyzer import SentimentAnalyzer
from config.config import Config
from datetime import datetime
import sys

# "Trading in the Zone" Principles for the Agent:
# - Objectivity: The agent follows its rules without emotional interference.
# - Discipline: Execute signals as per the strategy.
# - Patience: Wait for high-probability setups defined by the strategy.
# - Adaptability (long-term): While the prototype is fixed, a real agent might adapt its strategy over time (learn).

class TradingAgent:
    def __init__(self, symbols: list = None, time_frame: str = '1h', 
                 capital: float = 10000.0, use_ml: bool = True, 
                 use_sentiment: bool = True, exchange_id: str = 'binance',
                 testnet: bool = True):
        """
        Initializes the Advanced Trading Agent with ML and Sentiment Analysis.

        Args:
            symbols: List of trading symbols to monitor (e.g., ['BTC/USDT', 'ETH/USDT'])
            time_frame: Time frame for market data (e.g., '1h', '4h')
            capital: Initial trading capital
            use_ml: Whether to use ML predictions
            use_sentiment: Whether to use sentiment analysis
            exchange_id: Exchange to connect to
            testnet: Whether to use testnet mode
        """
        self.symbols = symbols or Config.SYMBOLS_TO_TRADE
        self.time_frame = time_frame
        self.capital = capital
        self.portfolio = {symbol: 0.0 for symbol in self.symbols}
        self.cash = capital
        self.active_trades = {symbol: [] for symbol in self.symbols}
        
        print("=" * 60)
        print("  ADVANCED CRYPTOCURRENCY TRADING BOT")
        print("=" * 60)
        print(f"Initializing agent for symbols: {self.symbols}")
        print(f"Initial capital: ${capital:.2f}")
        print(f"Time frame: {time_frame}")
        print(f"Exchange: {exchange_id} ({'TESTNET' if testnet else 'LIVE'})")
        
        # Initialize data handler with real exchange connection
        self.data_handler = DataHandler(
            exchange_id=exchange_id,
            testnet=testnet,
            api_key=Config.API_KEY,
            api_secret=Config.API_SECRET
        )
        
        # Initialize ML predictor if enabled
        self.ml_predictor = None
        if use_ml:
            print("\nInitializing ML models...")
            self.ml_predictor = MLPredictor(
                model_type=Config.ML_MODEL_TYPE,
                lookback_period=Config.LOOKBACK_PERIOD
            )
        
        # Initialize sentiment analyzer if enabled
        self.sentiment_analyzer = None
        if use_sentiment:
            print("\nInitializing sentiment analyzer...")
            self.sentiment_analyzer = SentimentAnalyzer(
                news_api_key=Config.NEWS_API_KEY
            )
        
        # Initialize strategies for each symbol
        self.strategies = {}
        print("\nInitializing trading strategies...")
        for symbol in self.symbols:
            self.strategies[symbol] = TradingStrategy(
                symbol=symbol,
                risk_per_trade=Config.RISK_PER_TRADE,
                ml_predictor=self.ml_predictor,
                sentiment_analyzer=self.sentiment_analyzer
            )
        
        print("\n" + "=" * 60)
        print("  AGENT INITIALIZED SUCCESSFULLY")
        print("=" * 60)
        print(f"Agent Mindset: Objective, Disciplined, Patient.")
        print(f"(Inspired by 'Trading in the Zone')")
        print("=" * 60 + "\n")

    def check_for_signals(self):
        """
        Checks for trading signals for all monitored symbols using ML and sentiment.
        """
        print(f"\n{'='*60}")
        print(f"  CHECKING FOR SIGNALS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for symbol in self.symbols:
            print(f"\n{'─'*60}")
            print(f"  Analyzing: {symbol}")
            print(f"{'─'*60}")
            
            try:
                # 1. Fetch market data
                raw_data = self.data_handler.fetch_market_data(
                    symbol, 
                    self.time_frame,
                    limit=200,  # More data for ML training
                    use_real_data=False  # Set to True when exchange API is configured
                )
                
                if raw_data.empty:
                    print(f"⚠ No data fetched for {symbol}. Skipping.")
                    continue

                # 2. Preprocess data and add technical indicators
                processed_data = self.data_handler.preprocess_data(raw_data, add_indicators=True)
                
                # 3. Train/update ML model if needed
                if self.ml_predictor and not self.ml_predictor.is_trained:
                    print(f"Training ML model for {symbol}...")
                    self.ml_predictor.train(processed_data)

                # 4. Update strategy with new data
                self.strategies[symbol].update_data(processed_data)

                # 5. Generate signal (incorporates ML + sentiment + technical analysis)
                signal, entry_price, stop_loss, take_profit = self.strategies[symbol].generate_signal()

                # 6. Display current market info
                current_price = processed_data['close'].iloc[-1]
                print(f"\n📊 Current Market Data:")
                print(f"   Price: ${current_price:.2f}")
                
                if 'RSI' in processed_data.columns:
                    rsi = processed_data['RSI'].iloc[-1]
                    print(f"   RSI: {rsi:.2f}")
                
                if 'MACD_diff' in processed_data.columns:
                    macd_diff = processed_data['MACD_diff'].iloc[-1]
                    print(f"   MACD Diff: {macd_diff:.4f}")

                # 7. Execute trade if signal is generated
                if signal == "BUY":
                    print(f"\n🟢 BUY SIGNAL GENERATED")
                    if len(self.active_trades[symbol]) < Config.MAX_POSITIONS:
                        self.execute_trade(symbol, "BUY", entry_price, stop_loss, take_profit, current_price)
                    else:
                        print(f"⚠ Maximum positions reached for {symbol}")
                        
                elif signal == "SELL":
                    print(f"\n🔴 SELL SIGNAL GENERATED")
                    # For this version, focusing on long trades
                    print(f"ℹ SELL signal for {symbol} noted but not executing (long-only strategy)")
                else:
                    print(f"\n⚪ HOLD - No trade signal for {symbol}")

                # 8. Manage existing trades
                self.manage_active_trades(
                    symbol, 
                    current_price,
                    processed_data['high'].iloc[-1],
                    processed_data['low'].iloc[-1]
                )

            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
                import traceback
                traceback.print_exc()

    def execute_trade(self, symbol: str, side: str, entry_price: float, 
                     stop_loss: float, take_profit: float, current_market_price: float):
        """
        Executes a trade with proper risk management.

        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            entry_price: Desired entry price from signal
            stop_loss: Stop loss price
            take_profit: Take profit price
            current_market_price: Current market price
        """
        # Risk management calculation
        risk_amount_per_trade = self.cash * self.strategies[symbol].risk_per_trade
        
        if entry_price == 0 or abs(entry_price - stop_loss) == 0:
             print(f"❌ Trade aborted: Invalid entry/SL price")
             return

        position_size_units = risk_amount_per_trade / abs(entry_price - stop_loss)
        trade_cost = position_size_units * current_market_price

        if trade_cost > self.cash:
            print(f"❌ Insufficient funds: Need ${trade_cost:.2f}, Have ${self.cash:.2f}")
            return

        if side == "BUY":
            self.cash -= trade_cost
            self.portfolio[symbol] += position_size_units
            
            trade_info = {
                "side": "BUY",
                "entry_price": current_market_price,
                "size": position_size_units,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "OPEN",
                "entry_time": datetime.now().isoformat()
            }
            self.active_trades[symbol].append(trade_info)
            
            print(f"\n✅ TRADE EXECUTED")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Size: {position_size_units:.6f} units")
            print(f"   Entry: ${current_market_price:.2f}")
            print(f"   Cost: ${trade_cost:.2f}")
            print(f"   Stop Loss: ${stop_loss:.2f}")
            print(f"   Take Profit: ${take_profit:.2f}")
            print(f"   Risk: ${risk_amount_per_trade:.2f}")
            print(f"   Remaining Cash: ${self.cash:.2f}")

    def manage_active_trades(self, symbol: str, current_price: float, 
                            current_high: float, current_low: float):
        """
        Manages active trades by checking for SL/TP hits.
        """
        trades_to_remove = []
        
        for i, trade in enumerate(self.active_trades[symbol]):
            if trade["status"] == "OPEN":
                closed = False
                
                # Check Stop Loss
                if trade["side"] == "BUY" and current_low <= trade["stop_loss"]:
                    pnl = trade["size"] * (trade["stop_loss"] - trade["entry_price"])
                    print(f"\n🛑 STOP LOSS HIT - {symbol}")
                    print(f"   Entry: ${trade['entry_price']:.2f}")
                    print(f"   Exit: ${trade['stop_loss']:.2f}")
                    print(f"   P&L: ${pnl:.2f}")
                    
                    self.cash += trade["size"] * trade["stop_loss"]
                    self.portfolio[symbol] -= trade["size"]
                    trade["status"] = "CLOSED_SL"
                    closed = True
                    
                # Check Take Profit
                elif trade["side"] == "BUY" and current_high >= trade["take_profit"]:
                    pnl = trade["size"] * (trade["take_profit"] - trade["entry_price"])
                    print(f"\n🎯 TAKE PROFIT HIT - {symbol}")
                    print(f"   Entry: ${trade['entry_price']:.2f}")
                    print(f"   Exit: ${trade['take_profit']:.2f}")
                    print(f"   P&L: ${pnl:.2f}")
                    
                    self.cash += trade["size"] * trade["take_profit"]
                    self.portfolio[symbol] -= trade["size"]
                    trade["status"] = "CLOSED_TP"
                    closed = True

                if closed:
                    trades_to_remove.append(i)
                    print(f"   Updated Cash: ${self.cash:.2f}")

        # Remove closed trades
        for i in sorted(trades_to_remove, reverse=True):
            del self.active_trades[symbol][i]

    def run(self, interval_seconds: int = 3600):
        """
        Main loop for the agent. Fetches data and checks signals periodically.

        Args:
            interval_seconds: Time in seconds between checks
        """
        print(f"\n{'='*60}")
        print(f"  AGENT STARTED")
        print(f"{'='*60}")
        print(f"Check interval: {interval_seconds} seconds ({interval_seconds/60:.0f} minutes)")
        print(f"Press Ctrl+C to stop the agent")
        print(f"{'='*60}\n")
        
        try:
            cycle = 0
            while True:
                cycle += 1
                print(f"\n\n{'#'*60}")
                print(f"  CYCLE {cycle}")
                print(f"{'#'*60}")
                
                self.check_for_signals()
                self.display_portfolio()
                
                print(f"\n{'='*60}")
                print(f"  Waiting {interval_seconds//60} minutes for next check...")
                print(f"{'='*60}\n")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print("  AGENT STOPPING...")
            print(f"{'='*60}")
        finally:
            self.display_portfolio()
            print(f"\n{'='*60}")
            print("  AGENT SHUTDOWN COMPLETE")
            print(f"{'='*60}\n")

    def display_portfolio(self):
        """Display current portfolio status."""
        print(f"\n{'='*60}")
        print(f"  PORTFOLIO STATUS")
        print(f"{'='*60}")
        print(f"💰 Cash: ${self.cash:.2f}")
        print(f"💼 Initial Capital: ${self.capital:.2f}")
        
        # Calculate total portfolio value
        total_holdings_value = 0.0
        print(f"\n📊 Holdings:")
        has_holdings = False
        
        for symbol, quantity in self.portfolio.items():
            if quantity > 0:
                has_holdings = True
                # Estimate value (in real system, fetch current price)
                print(f"   {symbol}: {quantity:.6f} units")
                
        if not has_holdings:
            print(f"   No current holdings")

        # Calculate P&L
        total_value = self.cash + total_holdings_value
        pnl = total_value - self.capital
        pnl_percent = (pnl / self.capital) * 100
        
        print(f"\n📈 Performance:")
        print(f"   Total Value: ${total_value:.2f}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)")
        
        # Display active trades
        print(f"\n🔄 Active Trades:")
        has_active_trades = False
        
        for symbol, trades in self.active_trades.items():
            if trades:
                has_active_trades = True
                print(f"   {symbol}:")
                for j, trade in enumerate(trades, 1):
                    print(f"     #{j} {trade['side']} | "
                          f"Entry: ${trade['entry_price']:.2f} | "
                          f"Size: {trade['size']:.6f} | "
                          f"SL: ${trade['stop_loss']:.2f} | "
                          f"TP: ${trade['take_profit']:.2f}")
                    
        if not has_active_trades:
            print(f"   No active trades")
            
        print(f"{'='*60}\n")


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
