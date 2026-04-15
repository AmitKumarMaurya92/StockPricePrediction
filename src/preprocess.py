def preprocess_data(data):
    """
    Clean and scale the data.
    """
    print("Preprocessing data...")
    # Extract 'Close' prices
    close_prices = data['Close'].values
    
    # In a real scenario, we would scale the data using MinMaxScaler 
    # and create sequences for the LSTM model.
    # For this skeleton, we just return the most recent price.
    last_price = close_prices[-1]
    
    return {"last_price": float(last_price)}
