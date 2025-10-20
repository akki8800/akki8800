# Advanced Cryptocurrency Trading Bot

An advanced, AI-powered cryptocurrency trading bot that uses machine learning, technical analysis, and sentiment analysis to make automated trading decisions. This bot integrates multiple data sources and advanced algorithms to identify high-probability trading opportunities in the cryptocurrency market.

## 🌟 Key Features

### 🤖 Machine Learning Models
- **Multiple ML Algorithms**: Random Forest, Gradient Boosting, and ensemble methods
- **Price Prediction**: Predicts next market movement based on historical patterns
- **Automatic Training**: Trains models on historical data and periodically retrains
- **Feature Engineering**: Extracts 20+ features from market data for predictions

### 📊 Technical Analysis
- **Advanced Indicators**: RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX
- **Support & Resistance**: Automatic identification of key price levels
- **Pattern Recognition**: Detects bullish/bearish reversal patterns
- **Multi-timeframe Analysis**: Analyzes different timeframes for confirmation

### 📰 Sentiment Analysis
- **News Integration**: Fetches real-time crypto news from multiple sources
- **Sentiment Scoring**: Uses VADER and TextBlob for sentiment analysis
- **Social Media Trends**: Analyzes market sentiment and trends
- **Confidence Metrics**: Provides confidence scores for sentiment signals

### 🔄 Exchange Integration
- **Multi-Exchange Support**: Connects to major exchanges via CCXT library
- **Real-time Data**: Fetches live market data and order book information
- **Testnet Support**: Safe testing environment before live trading
- **API Management**: Secure API key management and rate limiting

### 🛡️ Risk Management
- **Position Sizing**: Calculates optimal position size based on risk
- **Stop-Loss/Take-Profit**: Automatic SL/TP placement and management
- **Risk Per Trade**: Configurable risk percentage (default: 2%)
- **Max Positions**: Limits concurrent open positions
- **Portfolio Tracking**: Real-time portfolio value and P&L tracking

### 🎯 Trading Strategy
- **Multi-Factor Signals**: Combines ML, technical analysis, and sentiment
- **Scoring System**: Weights different signals for final decision
- **Confirmation Rules**: Multiple confirmation criteria before trade execution
- **Adaptive Thresholds**: Adjusts signal thresholds based on market conditions

## 📁 Project Structure

```
trading_agent/
├── config/
│   └── config.py              # Configuration management
├── core/
│   ├── agent.py              # Main trading agent
│   └── strategy.py           # Trading strategy logic
├── data/
│   └── data_handler.py       # Market data fetching and processing
├── ml_models/
│   └── predictor.py          # ML prediction models
├── news/
│   └── sentiment_analyzer.py # News and sentiment analysis
├── utils/                     # Utility functions
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/akki8800/akki8800.git
cd akki8800/trading_agent
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Note: Some packages like TA-Lib may require additional system dependencies:
- **Ubuntu/Debian**: `sudo apt-get install ta-lib`
- **MacOS**: `brew install ta-lib`
- **Windows**: Download from [TA-Lib website](http://ta-lib.org/)

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

### Step 4: Get API Keys

#### Exchange API (Required for live trading)
1. Create account on supported exchange (Binance, Coinbase, etc.)
2. Generate API key and secret
3. Enable testnet/sandbox mode for safe testing
4. Add keys to `.env` file

#### News API (Optional, for sentiment analysis)
1. Sign up at [NewsAPI.org](https://newsapi.org/)
2. Get free API key (limited to 100 requests/day)
3. Add key to `.env` file

## ⚙️ Configuration

Edit `config/config.py` or set environment variables in `.env`:

### Trading Settings
- `SYMBOLS_TO_TRADE`: List of trading pairs (e.g., BTC/USDT, ETH/USDT)
- `TIME_FRAME`: Candlestick timeframe (1m, 5m, 15m, 1h, 4h, 1d)
- `INITIAL_CAPITAL`: Starting capital for trading
- `RUN_INTERVAL_SECONDS`: How often to check for signals

### Risk Management
- `RISK_PER_TRADE`: Percentage of capital to risk per trade (default: 2%)
- `MAX_POSITIONS`: Maximum concurrent positions (default: 4)
- `STOP_LOSS_PERCENT`: Stop loss percentage (default: 2%)
- `TAKE_PROFIT_PERCENT`: Take profit percentage (default: 4%)

### Machine Learning
- `ML_MODEL_TYPE`: Model type ('random_forest', 'gradient_boosting', 'ensemble')
- `LOOKBACK_PERIOD`: Number of periods for feature engineering (default: 60)
- `RETRAIN_INTERVAL_DAYS`: Days between model retraining (default: 7)

### Features
- `USE_SENTIMENT`: Enable/disable sentiment analysis
- `SENTIMENT_WEIGHT`: Weight of sentiment in final decision (0-1)

## 🎮 Usage

### Run the Trading Bot
```bash
cd trading_agent
python main.py
```

### Testnet Mode (Recommended for first use)
The bot runs in testnet mode by default. Set `TESTNET=True` in `.env` to use simulated trading.

### Live Trading
⚠️ **Warning**: Live trading involves real money and risk of loss.

1. Set `TESTNET=False` in `.env`
2. Ensure API keys have trading permissions
3. Start with small capital
4. Monitor closely initially

### Monitor Performance
The bot displays:
- Current signals and market analysis
- Active trades and positions
- Portfolio value and P&L
- ML predictions and confidence
- Sentiment analysis results

## 📊 How It Works

### Signal Generation Process

1. **Data Collection**
   - Fetches historical and real-time market data
   - Calculates technical indicators
   - Retrieves news and sentiment data

2. **Feature Engineering**
   - Creates 20+ features from market data
   - Normalizes and scales features
   - Handles missing data

3. **ML Prediction**
   - Runs ensemble of ML models
   - Generates price movement prediction
   - Calculates confidence score

4. **Technical Analysis**
   - Identifies support/resistance levels
   - Detects chart patterns
   - Evaluates indicator signals

5. **Sentiment Analysis**
   - Fetches recent news articles
   - Analyzes sentiment (positive/negative/neutral)
   - Calculates aggregated sentiment score

6. **Signal Scoring**
   - Combines all factors with weights
   - Calculates buy/sell scores
   - Applies confirmation rules

7. **Trade Execution**
   - Validates signal strength
   - Calculates position size
   - Places order with SL/TP

8. **Trade Management**
   - Monitors active positions
   - Executes stop-loss/take-profit
   - Updates portfolio

## 🧪 Testing

### Backtest Mode
Test strategies on historical data before live trading:
```python
# Coming soon: Backtesting framework
```

### Paper Trading
Use testnet mode for risk-free testing with real market data.

## 📈 Performance Metrics

The bot tracks:
- Total P&L and percentage return
- Win rate and average win/loss
- Maximum drawdown
- Sharpe ratio (planned)
- Individual trade performance

## 🔐 Security

- API keys stored in environment variables
- Never commit `.env` file to version control
- Use API keys with trading restrictions
- Enable IP whitelisting on exchange
- Use 2FA on exchange accounts

## ⚠️ Disclaimer

**This trading bot is for educational and research purposes only.**

- Cryptocurrency trading involves substantial risk of loss
- Past performance does not guarantee future results
- Do not invest money you cannot afford to lose
- The developers are not responsible for any financial losses
- Use at your own risk
- This is not financial advice

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install --upgrade -r requirements.txt
```

**TA-Lib Installation**
If TA-Lib fails to install, you can use the `ta` library instead (already in requirements).

**Exchange Connection Issues**
- Verify API keys are correct
- Check internet connection
- Ensure exchange API is accessible from your location

**Low Signal Generation**
- Markets may not always have clear signals
- Adjust scoring thresholds in strategy
- Check if enough historical data is available

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional ML models (LSTM, Transformer)
- More technical indicators
- Advanced chart pattern recognition
- Multi-timeframe strategies
- Backtesting framework
- Web dashboard for monitoring
- Mobile notifications

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by "Trading in the Zone" by Mark Douglas
- Built with Python, Scikit-learn, TensorFlow, CCXT, and other open-source libraries
- Thanks to the cryptocurrency and open-source communities

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review documentation and code comments

---

**Remember**: Trade responsibly. Never invest more than you can afford to lose. Always do your own research and understand the risks involved in cryptocurrency trading.

---

*Last Updated: 2024*
*Version: 2.0 - Advanced ML & Sentiment Integration*
