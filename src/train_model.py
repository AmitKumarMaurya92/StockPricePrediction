import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from src.data_loader import fetch_data
from src.preprocess import prepare_data_for_training

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'lstm_model.h5')

def build_model(input_shape):
    """Build and compile the multivariate LSTM model."""
    model = Sequential()
    
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    
    model.add(Dense(units=25))
    model.add(Dense(units=1)) # Predicts scaled 'Close' price
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(symbol='AAPL', period='5y'):
    """Fetch history, prepare, train, and save the model."""
    print(f"--- Starting Training Pipeline for target symbol {symbol} ({period}) ---")
    
    # 1. Fetch
    df = fetch_data(symbol, period=period)
    
    # 2. Preprocess (Calculates indicators, scales, and creates sequences)
    X, y = prepare_data_for_training(df)
    print(f"Training data shape: X={X.shape}, y={y.shape}")
    
    # 3. Build Model
    model = build_model((X.shape[1], X.shape[2]))
    
    # 4. Train
    print("Training model (this might take a moment)...")
    # Using small epochs for demonstration/setup, user can tune later
    model.fit(X, y, batch_size=32, epochs=10, validation_split=0.1, verbose=1)
    
    # 5. Save
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    print(f"Model successfully saved to {MODEL_PATH}")

if __name__ == '__main__':
    # Train using a stable tech stock representing a robust multivariate feature space
    train_model(symbol='AAPL', period='5y')
