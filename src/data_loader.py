import yfinance as yf
import pandas as pd
import requests
import functools

@functools.lru_cache(maxsize=50)
def fetch_data(symbol, period='3mo', interval='1d'):
    """
    Fetch historical stock data using Yahoo Finance with a robust generic fallback.
    """
    print(f"Fetching data for {symbol} at {interval} interval over {period} period...")
    
    try:
        import concurrent.futures
        stock = yf.Ticker(symbol)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: stock.history(period=period, interval=interval))
            data = future.result(timeout=5)
            
        if not data.empty:
            return data
    except Exception as e:
        print(f"yfinance native fetch failed ({e}). Attempting raw fallback...")
        
    # Raw API Fallback for Cloud/Render datacenters where yfinance curl_cffi might fail
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval={interval}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    
    res = requests.get(url, headers=headers, timeout=5)
    if res.status_code != 200:
        raise ValueError(f"No data found for symbol {symbol}. Both native yfinance and fallback API failed (Status {res.status_code}).")
        
    json_data = res.json()
    result = json_data.get('chart', {}).get('result', [])
    if not result:
        raise ValueError(f"No data found for symbol {symbol}. API returned empty result.")
        
    timestamps = result[0].get('timestamp', [])
    quote = result[0].get('indicators', {}).get('quote', [{}])[0]
    
    if not timestamps or not quote:
        raise ValueError(f"Incomplete data returned for symbol {symbol}.")
        
    df = pd.DataFrame({
        'Open': quote.get('open', []),
        'High': quote.get('high', []),
        'Low': quote.get('low', []),
        'Close': quote.get('close', []),
        'Volume': quote.get('volume', [])
    }, index=pd.to_datetime(timestamps, unit='s', utc=True))
    
    df.index.name = 'Date'
    df.dropna(inplace=True)
    return df

