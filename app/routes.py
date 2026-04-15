from flask import Blueprint, render_template, request, jsonify
from src.predict import predict_stock_price
from app.utils import get_currency_symbol, format_error_message

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        market = data.get('market', 'IN')
        interval = data.get('interval', '1d')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required'}), 400
            
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
            'last_open': result['last_open'],
            'last_high': result['last_high'],
            'last_low': result['last_low']
        })
        
    except Exception as e:
        error_msg = format_error_message(str(e), symbol, market if 'market' in locals() else 'US')
        print(f"Error during prediction: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
