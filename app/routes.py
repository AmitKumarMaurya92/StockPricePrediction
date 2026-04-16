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
            
        # Normalize column names (e.g. 'date' -> 'Date', 'close' -> 'Close')
        df.columns = [str(c).strip().title() for c in df.columns]
        
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
            # Maybe the user's CSV didn't have a header, or it's formatted weirdly.
            return jsonify({'success': False, 'error': 'Dataset must contain a "Date", "Datetime", or "Time" column.'}), 400
            
        required_cols = ['Open', 'High', 'Low', 'Close']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'success': False, 'error': f'Missing required column: {col}. Found columns: {list(df.columns)}'}), 400
                
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
