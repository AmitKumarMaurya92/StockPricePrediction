import os
from src.data_loader import fetch_data
from src.preprocess import preprocess_data

def load_model():
    """
    Load the trained LSTM model.
    """
    model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'lstm_model.h5')
    print(f"Loading model from: {model_path}")
    
    # In a real app we'd load the .h5 model using tensorflow
    # import tensorflow as tf
    # return tf.keras.models.load_model(model_path)
    
    return "Dummy Model Instance"

def predict_stock_price(symbol):
    """
    Main prediction pipeline.
    """
    # 1. Load Model
    model = load_model()
    
    # 2. Fetch Data
    raw_data = fetch_data(symbol)
    
    # 3. Preprocess Data
    processed_data = preprocess_data(raw_data)
    
    # 4. Predict Output
    print("Generating prediction...")
    last_price = processed_data['last_price']
    
    # Dummy prediction logic: let's assume a 1.5% increase for demonstration
    # Real logic: prediction = model.predict(processed_data['sequences'])
    predicted_price = last_price * 1.015
    
    return {
        "last_price": round(last_price, 2),
        "predicted_price": round(predicted_price, 2)
    }
