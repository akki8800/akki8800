# Quick Start Guide

## Get Started in 5 Minutes

### 1. Install Dependencies
```bash
cd trading_agent
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file to add your API keys (optional for testing)
nano .env
```

**Note**: The bot works in simulation mode by default without any API keys!

### 3. Test the Bot
```bash
# Run comprehensive tests
python test_bot.py
```

### 4. Run the Trading Bot
```bash
# Start the bot in simulation mode
python main.py
```

## What Happens Next?

The bot will:
1. ✅ Initialize ML models (Random Forest, Gradient Boosting)
2. ✅ Connect to data sources (simulated by default)
3. ✅ Fetch market data with technical indicators
4. ✅ Analyze sentiment from news (mock data if no API key)
5. ✅ Generate trading signals every hour
6. ✅ Execute trades based on multi-factor analysis
7. ✅ Manage positions with stop-loss and take-profit

## Understanding the Output

### Signal Generation
- **🟢 BUY**: Strong bullish signal detected
- **🔴 SELL**: Strong bearish signal detected (noted, not executed in long-only mode)
- **⚪ HOLD**: No clear signal, waiting for better setup

### Trade Execution
- Shows entry price, position size, stop-loss, and take-profit
- Displays risk amount and remaining cash
- Tracks all active positions

### Portfolio Status
- Current cash and holdings
- Total portfolio value
- Profit & Loss (P&L)
- Active trades with details

## Stopping the Bot

Press `Ctrl+C` to gracefully stop the bot. It will display final portfolio status.

## Going Live

⚠️ **Warning**: Only proceed if you understand the risks!

1. Get API keys from your exchange (e.g., Binance)
2. Enable testnet mode first: `TESTNET=True`
3. Add keys to `.env` file
4. Test thoroughly in testnet
5. When ready: Set `TESTNET=False` in `.env`
6. Start with small capital
7. Monitor closely

## Common Commands

```bash
# Run tests
python test_bot.py

# Test individual modules
python config/config.py
python data/data_handler.py
python ml_models/predictor.py
python news/sentiment_analyzer.py

# Start trading bot
python main.py

# Check version and config
python -c "from config.config import Config; print(Config.SYMBOLS_TO_TRADE)"
```

## Customization

Edit `config/config.py` or `.env` file to customize:
- Trading pairs (symbols)
- Time frames (1h, 4h, 1d)
- Risk per trade (default 2%)
- ML model type (random_forest, gradient_boosting, ensemble)
- Sentiment weight in decisions

## Getting Help

- Read the full README.md
- Check code comments
- Review test_bot.py output
- Examine example trades in simulation mode

## Next Steps

1. ✅ Test in simulation mode
2. ✅ Understand the signals and logic
3. ✅ Customize parameters for your strategy
4. ✅ Test with testnet API (paper trading)
5. ⚠️ Only then consider live trading with small capital

Remember: **Past performance does not guarantee future results!**
