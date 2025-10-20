# trading_agent/ml_models/predictor.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from typing import Tuple, Optional


class MLPredictor:
    """
    Machine Learning predictor for cryptocurrency price movements.
    Uses ensemble methods (Random Forest, Gradient Boosting) for predictions.
    """
    
    def __init__(self, model_type: str = 'ensemble', lookback_period: int = 60):
        """
        Initialize the ML predictor.
        
        Args:
            model_type: Type of model ('random_forest', 'gradient_boosting', 'ensemble')
            lookback_period: Number of periods to use as features
        """
        self.model_type = model_type
        self.lookback_period = lookback_period
        self.scaler = StandardScaler()
        self.models = {}
        self.is_trained = False
        
        print(f"ML Predictor initialized with {model_type} model")
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features from market data for ML models.
        
        Args:
            df: DataFrame with market data and technical indicators
            
        Returns:
            Tuple of (features, labels)
        """
        # Select relevant columns for features
        feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
            'MACD', 'MACD_signal', 'RSI', 'BB_upper', 'BB_lower', 'ATR'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        if len(available_features) < 5:
            raise ValueError("Not enough features available in the dataframe")
        
        # Create features dataframe
        features_df = df[available_features].copy()
        
        # Add price change features
        features_df['price_change'] = df['close'].pct_change()
        features_df['volume_change'] = df['volume'].pct_change()
        
        # Add momentum features
        for period in [5, 10, 20]:
            features_df[f'return_{period}'] = df['close'].pct_change(period)
            features_df[f'volatility_{period}'] = df['close'].rolling(period).std()
        
        # Create labels: 1 if price goes up in next period, 0 if down
        labels = (df['close'].shift(-1) > df['close']).astype(int)
        
        # Remove NaN values
        features_df = features_df.fillna(method='ffill').fillna(method='bfill')
        
        # Remove last row (no label) and align
        features_df = features_df.iloc[:-1]
        labels = labels.iloc[:-1]
        
        return features_df.values, labels.values
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2):
        """
        Train the ML models on historical data.
        
        Args:
            df: DataFrame with market data and indicators
            test_size: Proportion of data to use for testing
        """
        print("Training ML models...")
        
        try:
            # Prepare features and labels
            X, y = self.prepare_features(df)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models based on type
            if self.model_type in ['random_forest', 'ensemble']:
                print("Training Random Forest...")
                rf_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                rf_model.fit(X_train_scaled, y_train)
                rf_score = rf_model.score(X_test_scaled, y_test)
                self.models['random_forest'] = rf_model
                print(f"Random Forest accuracy: {rf_score:.3f}")
            
            if self.model_type in ['gradient_boosting', 'ensemble']:
                print("Training Gradient Boosting...")
                gb_model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
                gb_model.fit(X_train_scaled, y_train)
                gb_score = gb_model.score(X_test_scaled, y_test)
                self.models['gradient_boosting'] = gb_model
                print(f"Gradient Boosting accuracy: {gb_score:.3f}")
            
            self.is_trained = True
            print("Model training completed successfully!")
            
        except Exception as e:
            print(f"Error during training: {e}")
            self.is_trained = False
    
    def predict(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Predict price movement for the next period.
        
        Args:
            df: DataFrame with current market data
            
        Returns:
            Tuple of (prediction, confidence)
            prediction: 'UP' or 'DOWN'
            confidence: probability score (0-1)
        """
        if not self.is_trained:
            print("Model not trained. Training on provided data...")
            self.train(df)
        
        try:
            # Prepare features from the latest data
            features_df = df[df.columns].copy()
            X, _ = self.prepare_features(features_df)
            
            # Use only the last row for prediction
            X_latest = X[-1:] if len(X) > 0 else X
            X_scaled = self.scaler.transform(X_latest)
            
            # Get predictions from all models
            predictions = []
            probabilities = []
            
            for model_name, model in self.models.items():
                pred = model.predict(X_scaled)[0]
                prob = model.predict_proba(X_scaled)[0]
                predictions.append(pred)
                probabilities.append(max(prob))
            
            # Ensemble prediction (majority vote)
            final_prediction = 1 if sum(predictions) > len(predictions) / 2 else 0
            final_confidence = np.mean(probabilities)
            
            prediction_label = 'UP' if final_prediction == 1 else 'DOWN'
            
            return prediction_label, final_confidence
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return 'HOLD', 0.5
    
    def save_models(self, directory: str = 'models'):
        """Save trained models to disk."""
        if not self.is_trained:
            print("No trained models to save")
            return
        
        os.makedirs(directory, exist_ok=True)
        
        for model_name, model in self.models.items():
            path = os.path.join(directory, f'{model_name}.joblib')
            joblib.dump(model, path)
        
        scaler_path = os.path.join(directory, 'scaler.joblib')
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Models saved to {directory}")
    
    def load_models(self, directory: str = 'models'):
        """Load trained models from disk."""
        try:
            for model_type in ['random_forest', 'gradient_boosting']:
                path = os.path.join(directory, f'{model_type}.joblib')
                if os.path.exists(path):
                    self.models[model_type] = joblib.load(path)
            
            scaler_path = os.path.join(directory, 'scaler.joblib')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            self.is_trained = len(self.models) > 0
            print(f"Loaded {len(self.models)} models from {directory}")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.is_trained = False


class LSTMPredictor:
    """
    LSTM-based predictor for time series forecasting.
    Uses TensorFlow/Keras for deep learning predictions.
    """
    
    def __init__(self, lookback_period: int = 60, forecast_horizon: int = 1):
        """
        Initialize LSTM predictor.
        
        Args:
            lookback_period: Number of time steps to look back
            forecast_horizon: Number of steps to predict ahead
        """
        self.lookback_period = lookback_period
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        print(f"LSTM Predictor initialized (lookback: {lookback_period})")
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training.
        
        Args:
            data: Input data array
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        
        for i in range(len(data) - self.lookback_period - self.forecast_horizon):
            X.append(data[i:(i + self.lookback_period)])
            y.append(data[i + self.lookback_period + self.forecast_horizon - 1])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple):
        """Build LSTM model architecture."""
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            self.model = model
            print("LSTM model built successfully")
            
        except ImportError:
            print("TensorFlow not available. LSTM predictor disabled.")
            print("Install with: pip install tensorflow")
    
    def train(self, df: pd.DataFrame, epochs: int = 50, batch_size: int = 32):
        """Train the LSTM model."""
        print("LSTM training not fully implemented in this version.")
        print("Use MLPredictor with Random Forest/Gradient Boosting instead.")
        self.is_trained = False
    
    def predict(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Predict using LSTM model."""
        return 'HOLD', 0.5


if __name__ == '__main__':
    print("=== ML Predictor Module Test ===\n")
    
    # This would normally use real data
    print("Note: Full testing requires market data with indicators")
    print("ML models support Random Forest and Gradient Boosting")
    print("LSTM support available with TensorFlow installation")
