import yfinance as yf

def fetch_data(symbol, period='3mo', interval='1d'):
    """
    Fetch historical stock data using Yahoo Finance.
    """
    print(f"Fetching data for {symbol} at {interval} interval over {period} period...")
    
    stock = yf.Ticker(symbol)
    data = stock.history(period=period, interval=interval)
    
    if data.empty:
        raise ValueError(f"No data found for symbol {symbol}. Yahoo Finance might be rate-limiting requests or the ticker is invalid. Please wait a moment and try again.")
        
    return data
