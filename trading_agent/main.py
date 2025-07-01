# trading_agent/main.py

from core.agent import TradingAgent

# Configuration
SYMBOLS_TO_TRADE = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
# Common time frames: '1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
TIME_FRAME = '1h' # Time frame for candlestick data
INITIAL_CAPITAL = 10000.00  # Starting capital for the agent
RUN_INTERVAL_SECONDS = 60 * 60 # Check for signals every hour

# "Trading in the Zone" Reminder for the User/Developer:
# The agent operates based on predefined rules and probabilities.
# Success comes from consistent application of a strategy with a positive expectancy over many trades,
# not from any single trade. Manage expectations and focus on the process.

def run_trading_agent():
    """
    Initializes and runs the trading agent.
    """
    print("=============================================")
    print("===      Crypto Trading Agent Prototype   ===")
    print("=============================================")
    print(f"Monitored Symbols: {', '.join(SYMBOLS_TO_TRADE)}")
    print(f"Trading Time Frame: {TIME_FRAME}")
    print(f"Initial Capital: ${INITIAL_CAPITAL:.2f}")
    print(f"Signal Check Interval: {RUN_INTERVAL_SECONDS // 60} minutes")
    print("---")
    print("Disclaimer: This is a prototype for educational purposes.")
    print("It uses SIMULATED data and SIMULATED trading. DO NOT USE FOR REAL TRADING.")
    print("---")

    # Initialize the agent
    agent = TradingAgent(
        symbols=SYMBOLS_TO_TRADE,
        time_frame=TIME_FRAME,
        capital=INITIAL_CAPITAL
    )

    # Run the agent's main loop
    # The agent will periodically fetch data, check for signals, and manage trades.
    try:
        agent.run(interval_seconds=RUN_INTERVAL_SECONDS)
    except Exception as e:
        print(f"An unexpected error occurred in the agent's main loop: {e}")
        # Consider logging the error to a file in a real application
    finally:
        print("\nTrading Agent execution finished or was interrupted.")
        print("Final portfolio status:")
        agent.display_portfolio() # Display final status


if __name__ == "__main__":
    # This is the main entry point of the application.
    run_trading_agent()
