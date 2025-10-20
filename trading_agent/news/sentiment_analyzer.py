# trading_agent/news/sentiment_analyzer.py

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob


class SentimentAnalyzer:
    """
    Analyzes news and social sentiment for cryptocurrency markets.
    Fetches news from various sources and performs sentiment analysis.
    """
    
    def __init__(self, news_api_key: str = ''):
        """
        Initialize the sentiment analyzer.
        
        Args:
            news_api_key: API key for NewsAPI service
        """
        self.news_api_key = news_api_key
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.base_url = "https://newsapi.org/v2/everything"
        
    def fetch_news(self, symbol: str, days_back: int = 1) -> List[Dict]:
        """
        Fetch recent news articles about a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            days_back: Number of days to look back for news
            
        Returns:
            List of news articles with metadata
        """
        if not self.news_api_key:
            print("Warning: No NEWS_API_KEY provided. Using mock sentiment.")
            return self._generate_mock_news(symbol)
        
        try:
            # Extract base symbol (BTC from BTC/USDT)
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
            
            # Crypto name mapping
            crypto_names = {
                'BTC': 'Bitcoin',
                'ETH': 'Ethereum',
                'BNB': 'Binance Coin',
                'SOL': 'Solana',
                'ADA': 'Cardano',
                'XRP': 'Ripple',
                'DOGE': 'Dogecoin'
            }
            
            query = crypto_names.get(base_symbol, base_symbol)
            from_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            params = {
                'q': f'{query} OR {base_symbol}',
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.news_api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                print(f"Fetched {len(articles)} news articles for {symbol}")
                return articles[:20]  # Limit to 20 most recent
            else:
                print(f"Error fetching news: {response.status_code}")
                return self._generate_mock_news(symbol)
                
        except Exception as e:
            print(f"Error in fetch_news: {e}")
            return self._generate_mock_news(symbol)
    
    def _generate_mock_news(self, symbol: str) -> List[Dict]:
        """Generate mock news data for testing."""
        mock_articles = [
            {
                'title': f'{symbol} shows strong momentum in latest trading session',
                'description': 'Market analysis suggests positive outlook',
                'content': 'Technical indicators show bullish patterns'
            },
            {
                'title': f'Institutional investors increase {symbol} holdings',
                'description': 'Major funds show confidence in crypto markets',
                'content': 'Growing institutional interest drives market sentiment'
            },
            {
                'title': f'{symbol} market volatility expected amid global events',
                'description': 'Traders advised to exercise caution',
                'content': 'Market uncertainty creates mixed signals'
            }
        ]
        return mock_articles
    
    def analyze_sentiment_vader(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER (Valence Aware Dictionary and sEntiment Reasoner).
        Better for social media and short texts.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        scores = self.vader_analyzer.polarity_scores(text)
        return scores
    
    def analyze_sentiment_textblob(self, text: str) -> Dict:
        """
        Analyze sentiment using TextBlob.
        Better for longer, well-formed text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with polarity and subjectivity
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1
            'subjectivity': blob.sentiment.subjectivity  # 0 to 1
        }
    
    def get_aggregated_sentiment(self, symbol: str, days_back: int = 1) -> Dict:
        """
        Get aggregated sentiment score for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with aggregated sentiment metrics
        """
        articles = self.fetch_news(symbol, days_back)
        
        if not articles:
            return {
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        vader_scores = []
        textblob_scores = []
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if text.strip():
                vader = self.analyze_sentiment_vader(text)
                vader_scores.append(vader['compound'])
                
                textblob = self.analyze_sentiment_textblob(text)
                textblob_scores.append(textblob['polarity'])
        
        if not vader_scores:
            return {
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        # Calculate aggregated scores
        avg_vader = sum(vader_scores) / len(vader_scores)
        avg_textblob = sum(textblob_scores) / len(textblob_scores)
        
        # Combined sentiment (weighted average)
        combined_sentiment = (avg_vader * 0.6 + avg_textblob * 0.4)
        
        # Classify articles
        positive = sum(1 for s in vader_scores if s > 0.05)
        negative = sum(1 for s in vader_scores if s < -0.05)
        neutral = len(vader_scores) - positive - negative
        
        # Calculate confidence based on consistency
        import numpy as np
        confidence = 1.0 - (np.std(vader_scores) if len(vader_scores) > 1 else 0.5)
        
        result = {
            'sentiment_score': combined_sentiment,  # -1 to 1
            'confidence': confidence,  # 0 to 1
            'article_count': len(articles),
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'vader_avg': avg_vader,
            'textblob_avg': avg_textblob
        }
        
        print(f"Sentiment for {symbol}: {combined_sentiment:.3f} "
              f"(+{positive}/-{negative}/={neutral}, confidence: {confidence:.2f})")
        
        return result
    
    def get_sentiment_signal(self, symbol: str) -> str:
        """
        Get a simple trading signal based on sentiment.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        sentiment = self.get_aggregated_sentiment(symbol)
        
        score = sentiment['sentiment_score']
        confidence = sentiment['confidence']
        
        # Only give strong signals if confidence is high
        if confidence > 0.6:
            if score > 0.2:
                return 'BULLISH'
            elif score < -0.2:
                return 'BEARISH'
        
        return 'NEUTRAL'


if __name__ == '__main__':
    print("=== Sentiment Analysis Module Test ===\n")
    
    analyzer = SentimentAnalyzer()
    
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    for symbol in test_symbols:
        print(f"\n--- Analyzing {symbol} ---")
        sentiment = analyzer.get_aggregated_sentiment(symbol)
        signal = analyzer.get_sentiment_signal(symbol)
        
        print(f"Overall Sentiment: {sentiment['sentiment_score']:.3f}")
        print(f"Signal: {signal}")
        print(f"Articles analyzed: {sentiment['article_count']}")
