import os
import numpy as np
from src.data_loader import fetch_data
from src.preprocess import preprocess_data_for_inference

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'lstm_model.h5')

_model = None

def load_model():
    """Load the trained LSTM model (singleton pattern caching)."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
            
        print(f"Loading TensorFlow model from: {MODEL_PATH}")
        from tensorflow.keras.models import load_model as keras_load_model
        # Sometimes Keras complains about compile state on loaded models used only for inference
        _model = keras_load_model(MODEL_PATH, compile=False)
        
    return _model

def predict_stock_price(symbol, interval='1d', custom_df=None):
    """
    Multivariate prediction pipeline accommodating multiple timeframe topologies and custom datasets.
    """
    model = load_model()
    
    if custom_df is not None:
        raw_data = custom_df
    else:
        # Map valid Yahoo Finance periods for high-freq and low-freq intervals
        if interval == '1mo' or interval == '3mo':
            period = '10y'
        elif interval == '1wk':
            period = '5y'
        elif interval == '1d':
            period = '1y'
        elif interval == '1h':
            period = '1mo'
        else: # 15m, 5m
            period = '5d'
            
        raw_data = fetch_data(symbol, period=period, interval=interval)
    
    # Preprocess Data
    # sequence is (1, 60, num_features)
    # scaler is the fitted scaler from joblib
    # last_price is the actual last closing price
    sequence, scaler, last_price = preprocess_data_for_inference(raw_data)
    
    # Predict scaled Output
    print(f"Generating prediction for sequence shape {sequence.shape}...")
    scaled_prediction = model.predict(sequence, verbose=0)
    
    # Inverse transform to get actual price
    dummy_features = np.zeros(shape=(1, sequence.shape[2]))
    dummy_features[0][0] = scaled_prediction[0][0]
    
    predicted_val = scaler.inverse_transform(dummy_features)[0][0]
    # Return the entire parsed historical period (1 year natively for daily) for deeper chart context
    recent_history = raw_data.dropna()
    
    # Capture Full Date and Time for Sub-Day Intervals
    historical_dates = recent_history.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
    
    historical_open = recent_history['Open'].tolist()
    historical_high = recent_history['High'].tolist()
    historical_low = recent_history['Low'].tolist()
    historical_close = recent_history['Close'].tolist()
    
    change = predicted_val - last_price
    percent_change = (change / last_price) * 100
    
    if percent_change > 0.8:
        recommendation = "STRONG BUY"
        target_price = predicted_val
        stop_loss = last_price * 0.98
    elif percent_change > 0.2:
        recommendation = "BUY"
        target_price = predicted_val
        stop_loss = last_price * 0.985
    elif percent_change < -0.8:
        recommendation = "STRONG SELL"
        target_price = predicted_val
        stop_loss = last_price * 1.02
    elif percent_change < -0.2:
        recommendation = "SELL"
        target_price = predicted_val
        stop_loss = last_price * 1.015
    else:
        recommendation = "HOLD"
        target_price = last_price * 1.015
        stop_loss = last_price * 0.985

    
    company_name = symbol
    analyst_rating = "N/A"
    analyst_count = 0
    analyst_target = "N/A"
    
    if custom_df is None or symbol != "CUSTOM":
        try:
            import yfinance as yf
            # Attempt quick info fetch for company name and analyst insights
            info = yf.Ticker(symbol).info
            company_name = info.get('shortName', symbol)
            
            # Analyst Insights
            analyst_rating = info.get('recommendationKey', 'N/A').upper()
            analyst_count = info.get('numberOfAnalystOpinions', 0)
            if info.get('targetMeanPrice'):
                analyst_target = round(float(info.get('targetMeanPrice')), 2)
        except Exception as e:
            print(f"Warning: Failed to fetch yfinance supplemental info: {e}")
            pass
    
    return {
        "last_price": round(float(last_price), 2),
        "predicted_price": round(float(predicted_val), 2),
        "historical_dates": historical_dates,
        "historical_open": historical_open,
        "historical_high": historical_high,
        "historical_low": historical_low,
        "historical_close": historical_close,
        "change": round(float(change), 2),
        "percent_change": round(float(percent_change), 2),
        "recommendation": recommendation,
        "target_price": round(float(target_price), 2),
        "stop_loss": round(float(stop_loss), 2),
        "company_name": company_name,
        "analyst_rating": analyst_rating,
        "analyst_count": analyst_count,
        "analyst_target": analyst_target,
        "last_open": round(float(historical_open[-1]), 2),
        "last_high": round(float(historical_high[-1]), 2),
        "last_low": round(float(historical_low[-1]), 2)
    }
