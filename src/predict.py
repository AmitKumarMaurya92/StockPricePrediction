import os
import numpy as np
import pandas as pd
from src.data_loader import fetch_data
from src.preprocess import preprocess_data_for_inference
import functools

@functools.lru_cache(maxsize=50)
def get_ticker_info(symbol):
    import yfinance as yf
    return yf.Ticker(symbol).info

@functools.lru_cache(maxsize=50)
def get_ticker_fast_info(symbol):
    import yfinance as yf
    return yf.Ticker(symbol).fast_info

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'lstm_model.h5')

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
    
print(f"Loading TensorFlow model from: {MODEL_PATH}")
from tensorflow.keras.models import load_model as keras_load_model
_model = keras_load_model(MODEL_PATH, compile=False)

def predict_stock_price(symbol, interval='1d', custom_df=None):
    """
    Multivariate prediction pipeline accommodating multiple timeframe topologies and custom datasets.
    """
    model = _model
    
    if custom_df is not None:
        raw_data = custom_df
    else:
        # Map valid Yahoo Finance periods for high-freq and low-freq intervals
        if interval == '1mo' or interval == '3mo':
            period = 'max'
        elif interval == '1wk':
            period = '10y'
        elif interval == '1d':
            # Use 1y instead of 2y for daily data for maximum performance
            # 1 year (250+ days) is more than enough for 200 DMA and 60-day LSTM window
            period = '1y'
        elif interval == '1h':
            period = '730d'
        else: # 15m, 5m
            period = '60d'
            
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
    
    # Calculate Moving Averages (DMAs)
    recent_history['DMA50'] = recent_history['Close'].rolling(window=50, min_periods=1).mean()
    recent_history['DMA200'] = recent_history['Close'].rolling(window=200, min_periods=1).mean()
    
    # Capture Full Date and Time for Sub-Day Intervals
    historical_dates = recent_history.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
    
    historical_open = recent_history['Open'].tolist()
    historical_high = recent_history['High'].tolist()
    historical_low = recent_history['Low'].tolist()
    historical_close = recent_history['Close'].tolist()
    historical_volume = recent_history.get('Volume', pd.Series([0]*len(recent_history))).tolist()
    
    dma_50 = recent_history['DMA50'].round(2).fillna('N/A').tolist()
    dma_200 = recent_history['DMA200'].round(2).fillna('N/A').tolist()
    
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
    
    # Fundamental Stats for UI
    market_cap = "N/A"
    fifty_two_high = "N/A"
    fifty_two_low = "N/A"
    stock_pe = "N/A"
    book_value = "N/A"
    dividend_yield = "N/A"
    roe = "N/A"
    roce = "N/A"
    about_text = "N/A"
    website = ""
    
    if custom_df is None or symbol != "CUSTOM":
        try:
            # Attempt quick info fetch for company name and analyst insights
            info = get_ticker_info(symbol)
            
            # If info comes back completely empty (which happens when Yahoo blocks the IP softly but doesn't raise exception)
            if not info or len(info) <= 2:
                raise ValueError("Info payload empty due to cloudflare or rate limiting")
                
            company_name = info.get('shortName', symbol)
            
            # Analyst Insights
            analyst_rating = info.get('recommendationKey', 'N/A')
            if isinstance(analyst_rating, str): analyst_rating = analyst_rating.upper()
            analyst_count = info.get('numberOfAnalystOpinions', 0)
            if info.get('targetMeanPrice'):
                analyst_target = round(float(info.get('targetMeanPrice')), 2)
                
            # Fundamental Data
            market_cap = info.get('marketCap', 'N/A')
            fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
            fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
            stock_pe = info.get('trailingPE', info.get('forwardPE', 'N/A'))
            book_value = info.get('bookValue', 'N/A')
            
            dy = info.get('dividendYield', 'N/A')
            if dy and dy != 'N/A': dividend_yield = round(float(dy) * 100, 2)
            
            r_eq = info.get('returnOnEquity', 'N/A')
            if r_eq and r_eq != 'N/A': roe = round(float(r_eq) * 100, 2)
            
            r_ass = info.get('returnOnAssets', 'N/A')
            if r_ass and r_ass != 'N/A': roce = round(float(r_ass) * 100, 2)
            
            about_text = info.get('longBusinessSummary', 'N/A')
            website = info.get('website', '')
            
        except Exception as e:
            print(f"Warning: Primary yfinance info failed ({e}). Attempting fast_info and meta fallbacks...")
            try:
                import requests
                
                f_info = get_ticker_fast_info(symbol)
                
                market_cap = f_info.get('marketCap', 'N/A')
                fifty_two_high = f_info.get('yearHigh', 'N/A')
                fifty_two_low = f_info.get('yearLow', 'N/A')
                
                # Raw API Fallback for missing company name
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "*/*"}
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    meta = res.json().get('chart', {}).get('result', [{}])[0].get('meta', {})
                    company_name = meta.get('shortName', meta.get('longName', symbol))
            except Exception as inner_e:
                print(f"Notice: Fallback also partially failed: {inner_e}")
                pass
    
    return {
        "last_price": round(float(last_price), 2),
        "predicted_price": round(float(predicted_val), 2),
        "historical_dates": historical_dates,
        "historical_open": historical_open,
        "historical_high": historical_high,
        "historical_low": historical_low,
        "historical_close": historical_close,
        "historical_volume": historical_volume,
        "dma_50": dma_50,
        "dma_200": dma_200,
        "change": round(float(change), 2),
        "percent_change": round(float(percent_change), 2),
        "recommendation": recommendation,
        "target_price": round(float(target_price), 2),
        "stop_loss": round(float(stop_loss), 2),
        "company_name": company_name,
        "analyst_rating": analyst_rating,
        "analyst_count": analyst_count,
        "analyst_target": analyst_target,
        "market_cap": market_cap,
        "fifty_two_high": fifty_two_high,
        "fifty_two_low": fifty_two_low,
        "stock_pe": stock_pe,
        "book_value": book_value,
        "dividend_yield": dividend_yield,
        "roe": roe,
        "roce": roce,
        "about_text": about_text,
        "website": website,
        "last_open": round(float(historical_open[-1]), 2),
        "last_high": round(float(historical_high[-1]), 2),
        "last_low": round(float(historical_low[-1]), 2)
    }
