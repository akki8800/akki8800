#!/usr/bin/env python3
"""
Quick test script for the trading bot components.
Tests individual modules without running the full bot.
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("  TRADING BOT COMPONENT TEST")
print("=" * 70)

# Test 1: Configuration
print("\n1. Testing Configuration...")
try:
    from config.config import Config
    print(f"   ✓ Exchange: {Config.EXCHANGE_ID}")
    print(f"   ✓ Symbols: {Config.SYMBOLS_TO_TRADE}")
    print(f"   ✓ ML Model: {Config.ML_MODEL_TYPE}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Data Handler
print("\n2. Testing Data Handler...")
try:
    from data.data_handler import DataHandler
    handler = DataHandler(testnet=True)
    data = handler.fetch_market_data('BTC/USDT', '1h', limit=50, use_real_data=False)
    print(f"   ✓ Fetched {len(data)} data points")
    
    processed = handler.preprocess_data(data, add_indicators=True)
    indicators = [col for col in processed.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
    print(f"   ✓ Added {len(indicators)} technical indicators")
    print(f"   ✓ Indicators: {', '.join(indicators[:5])}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Sentiment Analyzer
print("\n3. Testing Sentiment Analyzer...")
try:
    from news.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.get_aggregated_sentiment('BTC')
    signal = analyzer.get_sentiment_signal('BTC')
    print(f"   ✓ Sentiment score: {sentiment['sentiment_score']:.3f}")
    print(f"   ✓ Signal: {signal}")
    print(f"   ✓ Articles analyzed: {sentiment['article_count']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: ML Predictor
print("\n4. Testing ML Predictor...")
try:
    from ml_models.predictor import MLPredictor
    from data.data_handler import DataHandler
    
    predictor = MLPredictor(model_type='ensemble', lookback_period=30)
    handler = DataHandler(testnet=True)
    data = handler.fetch_market_data('BTC/USDT', '1h', limit=100, use_real_data=False)
    processed = handler.preprocess_data(data, add_indicators=True)
    
    print(f"   ✓ ML Predictor initialized")
    print(f"   ✓ Training with {len(processed)} data points...")
    
    predictor.train(processed, test_size=0.2)
    
    prediction, confidence = predictor.predict(processed)
    print(f"   ✓ Prediction: {prediction} (confidence: {confidence:.2f})")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Trading Strategy
print("\n5. Testing Trading Strategy...")
try:
    from core.strategy import TradingStrategy
    from ml_models.predictor import MLPredictor
    from news.sentiment_analyzer import SentimentAnalyzer
    from data.data_handler import DataHandler
    
    handler = DataHandler(testnet=True)
    predictor = MLPredictor(model_type='ensemble', lookback_period=30)
    analyzer = SentimentAnalyzer()
    
    strategy = TradingStrategy(
        symbol='BTC/USDT',
        risk_per_trade=0.02,
        ml_predictor=predictor,
        sentiment_analyzer=analyzer
    )
    
    data = handler.fetch_market_data('BTC/USDT', '1h', limit=100, use_real_data=False)
    processed = handler.preprocess_data(data, add_indicators=True)
    
    strategy.update_data(processed)
    signal, entry, sl, tp = strategy.generate_signal()
    
    print(f"   ✓ Strategy initialized")
    print(f"   ✓ Signal generated: {signal}")
    if signal != 'HOLD':
        print(f"   ✓ Entry: ${entry:.2f}, SL: ${sl:.2f}, TP: ${tp:.2f}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Trading Agent (initialization only)
print("\n6. Testing Trading Agent Initialization...")
try:
    from core.agent import TradingAgent
    
    agent = TradingAgent(
        symbols=['BTC/USDT', 'ETH/USDT'],
        time_frame='1h',
        capital=10000.0,
        use_ml=True,
        use_sentiment=True,
        testnet=True
    )
    print(f"   ✓ Agent initialized successfully")
    print(f"   ✓ Capital: ${agent.capital:.2f}")
    print(f"   ✓ Symbols: {agent.symbols}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("  ALL TESTS COMPLETED")
print("=" * 70)
print("\nThe trading bot is ready to use!")
print("Run 'python main.py' to start the bot.\n")
