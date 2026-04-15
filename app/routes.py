from flask import Blueprint, render_template, request, jsonify
from src.predict import predict_stock_price

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required'}), 400
            
        print(f"Received prediction request for: {symbol}")
        
        # This mirrors the workflow expected:
        # Load Model -> Fetch Data -> Preprocess -> Predict Output -> Send Result UI
        result = predict_stock_price(symbol.upper())
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'prediction': result['predicted_price'],
            'last_price': result['last_price']
        })
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
