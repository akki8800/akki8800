# trading_agent/main.py

from core.agent import TradingAgent
from config.config import Config
import sys

# "Trading in the Zone" Reminder for the User/Developer:
# The agent operates based on predefined rules and probabilities.
# Success comes from consistent application of a strategy with a positive expectancy over many trades,
# not from any single trade. Manage expectations and focus on the process.

def run_trading_agent():
    """
    Initializes and runs the advanced cryptocurrency trading agent.
    """
    print("\n" + "=" * 70)
    print("  ADVANCED CRYPTOCURRENCY TRADING BOT")
    print("  Powered by Machine Learning & Sentiment Analysis")
    print("=" * 70)
    print(f"\n📊 Configuration:")
    print(f"   Monitored Symbols: {', '.join(Config.SYMBOLS_TO_TRADE)}")
    print(f"   Trading Time Frame: {Config.TIME_FRAME}")
    print(f"   Initial Capital: ${Config.INITIAL_CAPITAL:.2f}")
    print(f"   Signal Check Interval: {Config.RUN_INTERVAL_SECONDS // 60} minutes")
    print(f"   Exchange: {Config.EXCHANGE_ID} ({'TESTNET' if Config.TESTNET else 'LIVE'})")
    print(f"   ML Model: {Config.ML_MODEL_TYPE.upper()}")
    print(f"   Risk per Trade: {Config.RISK_PER_TRADE * 100}%")
    print(f"   Max Positions: {Config.MAX_POSITIONS}")
    
    print(f"\n🔧 Features:")
    print(f"   ✓ Real-time market data fetching")
    print(f"   ✓ Technical indicator analysis (RSI, MACD, Bollinger Bands, etc.)")
    print(f"   ✓ Machine Learning price prediction")
    print(f"   ✓ News sentiment analysis")
    print(f"   ✓ Multi-factor signal generation")
    print(f"   ✓ Automated risk management")
    print(f"   ✓ Stop-loss & take-profit execution")
    
    print(f"\n⚠️  DISCLAIMER:")
    print(f"   This is an automated trading system. Use at your own risk.")
    if Config.TESTNET:
        print(f"   Currently running in TESTNET/SIMULATION mode.")
        print(f"   No real funds are at risk.")
    else:
        print(f"   ⚠️  LIVE TRADING MODE - Real funds are at risk!")
        print(f"   Ensure you understand the risks before proceeding.")
        
        response = input(f"\n   Continue with LIVE trading? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print(f"   Exiting...")
            sys.exit(0)
    
    print("=" * 70)
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print(f"   Please check your configuration and environment variables.")
        sys.exit(1)
    
    # Initialize the agent
    try:
        agent = TradingAgent(
            symbols=Config.SYMBOLS_TO_TRADE,
            time_frame=Config.TIME_FRAME,
            capital=Config.INITIAL_CAPITAL,
            use_ml=True,
            use_sentiment=Config.USE_SENTIMENT,
            exchange_id=Config.EXCHANGE_ID,
            testnet=Config.TESTNET
        )
    except Exception as e:
        print(f"\n❌ Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Run the agent's main loop
    try:
        agent.run(interval_seconds=Config.RUN_INTERVAL_SECONDS)
    except Exception as e:
        print(f"\n❌ Unexpected error in agent's main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 70)
        print("  TRADING AGENT EXECUTION COMPLETED")
        print("=" * 70)
        print("\n📊 Final Portfolio Status:")
        agent.display_portfolio()
        print("\n" + "=" * 70)
        print("  Thank you for using the Advanced Trading Bot!")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    # This is the main entry point of the application.
    run_trading_agent()
