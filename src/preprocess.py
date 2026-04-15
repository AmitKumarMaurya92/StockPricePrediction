import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'scaler.pkl')
TIME_STEPS = 60

def add_technical_indicators(df):
    """Add RSI, MACD, and Bollinger Bands to the DataFrame."""
    df = df.copy()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10) # Avoid divide by zero
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['20_SMA'] = df['Close'].rolling(window=20).mean()
    df['20_Std'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['20_SMA'] + (df['20_Std'] * 2)
    df['Lower_Band'] = df['20_SMA'] - (df['20_Std'] * 2)
    
    # Drop NaNs that come from rolling windows
    df.dropna(inplace=True)
    return df

def get_features(df):
    """Extract and order features predictably."""
    df = add_technical_indicators(df)
    features = ['Close', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Lower_Band']
    return df[features].values

def prepare_data_for_training(df):
    """Scale data and create sequences for LSTM training."""
    data = get_features(df)
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Save the scaler
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler saved to {SCALER_PATH}")
    
    X, y = [], []
    for i in range(TIME_STEPS, len(scaled_data)):
        X.append(scaled_data[i-TIME_STEPS:i])
        # We predict the 'Close' price, which is index 0 in our features list
        y.append(scaled_data[i, 0])
        
    return np.array(X), np.array(y)

def preprocess_data_for_inference(df):
    """Preprocess real-time data for inference using dynamic scaling."""
    data = get_features(df)
    
    if len(data) < TIME_STEPS:
        raise ValueError(f"Not enough data points after indicator drop. Need {TIME_STEPS}, got {len(data)}.")
        
    # Dynamically fit the scaler to the given 6-month historical payload
    # This correctly scales ₹3000 prices down to (0, 1) without blowing up the LSTM gradients
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # We only need the last TIME_STEPS for a single prediction
    scaled_recent_data = scaled_data[-TIME_STEPS:]
    
    # Reshape for LSTM [samples, time steps, features]
    sequence = np.reshape(scaled_recent_data, (1, TIME_STEPS, scaled_recent_data.shape[1]))
    
    # Return both the sequence for prediction and the scaler to inverse-transform the result
    return sequence, scaler, data[-1][0] 
