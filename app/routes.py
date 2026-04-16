from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from src.predict import predict_stock_price
from app.utils import get_currency_symbol, format_error_message, resolve_ticker, get_autocomplete_suggestions

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip()
    market = request.args.get('market', 'IN').strip()
    if not query:
        return jsonify([])
    suggestions = get_autocomplete_suggestions(query, market)
    return jsonify(suggestions)

@bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        raw_symbol = data.get('symbol', '').strip().upper()
        market = data.get('market', 'IN')
        interval = data.get('interval', '1d')
        
        if not raw_symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required'}), 400
            
        # Use Yahoo Finance search to automatically resolve "Google" to "GOOG"
        symbol = resolve_ticker(raw_symbol)
        
        # Append .NS automatically for Indian Market if no suffix exists
        if market == 'IN' and not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol += '.NS'
            
        print(f"Received prediction request for: {symbol}")
        
        # This mirrors the workflow expected:
        # Load Model -> Fetch Data -> Preprocess -> Predict Output -> Send Result UI
        result = predict_stock_price(symbol, interval=interval)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prediction': result['predicted_price'],
            'last_price': result['last_price'],
            'currency_symbol': get_currency_symbol(symbol),
            'historical_dates': result['historical_dates'],
            'historical_open': result['historical_open'],
            'historical_high': result['historical_high'],
            'historical_low': result['historical_low'],
            'historical_close': result['historical_close'],
            'change': result['change'],
            'percent_change': result['percent_change'],
            'recommendation': result['recommendation'],
            'target_price': result['target_price'],
            'stop_loss': result['stop_loss'],
            'company_name': result['company_name'],
            'analyst_rating': result['analyst_rating'],
            'analyst_count': result['analyst_count'],
            'analyst_target': result['analyst_target'],
            'last_open': result['last_open'],
            'last_high': result['last_high'],
            'last_low': result['last_low']
        })
        
    except Exception as e:
        error_msg = format_error_message(str(e), symbol, market if 'market' in locals() else 'US')
        print(f"Error during prediction: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@bp.route('/predict_file', methods=['POST'])
def predict_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
            
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'error': 'Unsupported format. Use CSV or Excel.'}), 400
            
        # Dynamic Header Discovery (For files like Screener.in with metadata at the top)
        current_cols = [str(c).strip().lower() for c in df.columns]
        if 'date' not in current_cols and 'datetime' not in current_cols and 'time' not in current_cols:
            header_idx = -1
            for i, row in df.head(30).iterrows():
                row_vals = [str(v).strip().lower() for v in row.values]
                if 'date' in row_vals or 'datetime' in row_vals or 'time' in row_vals:
                    header_idx = i
                    break
            if header_idx != -1:
                df.columns = df.iloc[header_idx]
                df = df.iloc[header_idx + 1:].reset_index(drop=True)
                
        # Normalize column names (e.g. 'date' -> 'Date', 'close' -> 'Close')
        df.columns = [str(c).strip().title() for c in df.columns]
        
        # Alias 'Price' to 'Close' for typical flat exports
        if 'Price' in df.columns and 'Close' not in df.columns:
            df.rename(columns={'Price': 'Close'}, inplace=True)
            
        # Parse Dates
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df.set_index('Date', inplace=True)
        elif 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df.set_index('Datetime', inplace=True)
        elif 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            df.set_index('Time', inplace=True)
        elif 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df.set_index('Timestamp', inplace=True)
        else:
            return jsonify({'success': False, 'error': 'Dataset must contain a "Date", "Datetime", or "Time" column. Found: ' + str(list(df.columns))}), 400
            
        # Ensure minimum columns safely
        if 'Close' not in df.columns:
            return jsonify({'success': False, 'error': f'Missing primary Price/Close column. Found: {list(df.columns)}'}), 400
            
        # Auto-fill missing chart columns to prevent crashing
        if 'Open' not in df.columns: df['Open'] = df['Close']
        if 'High' not in df.columns: df['High'] = df['Close']
        if 'Low' not in df.columns: df['Low'] = df['Close']
                
        # Handle numeric conversion for the values securely
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Drop rows where index (Date) is NaT (Not a Time)
        df = df[df.index.notnull()]
        
        df.ffill(inplace=True)
        df.dropna(inplace=True)
        
        print(f"Received custom dataset '{file.filename}'. Shape: {df.shape}")
        
        result = predict_stock_price("CUSTOM", interval='1d', custom_df=df)
        
        return jsonify({
            'success': True,
            'symbol': file.filename,
            'prediction': result['predicted_price'],
            'last_price': result['last_price'],
            'currency_symbol': '', 
            'historical_dates': result['historical_dates'],
            'historical_open': result['historical_open'],
            'historical_high': result['historical_high'],
            'historical_low': result['historical_low'],
            'historical_close': result['historical_close'],
            'change': result['change'],
            'percent_change': result['percent_change'],
            'recommendation': result['recommendation'],
            'target_price': result['target_price'],
            'stop_loss': result['stop_loss'],
            'company_name': file.filename,
            'analyst_rating': result['analyst_rating'],
            'analyst_count': result['analyst_count'],
            'analyst_target': result['analyst_target'],
            'last_open': result['last_open'],
            'last_high': result['last_high'],
            'last_low': result['last_low']
        })
        
    except Exception as e:
        print(f"Error during file prediction: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
