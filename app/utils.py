def get_currency_symbol(symbol):
    """Return correct currency symbol based on ticker suffix"""
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return "₹"
    return "$"

def format_error_message(error_msg, symbol, market):
    """Format and simplify error messages for the UI"""
    if "No data found" in error_msg:
        if market == 'IN':
            return f"No data found for '{symbol}'. Please ensure it is a valid NSE ticker (e.g., RELIANCE.NS, TCS.NS)."
        else:
            return f"No data found for '{symbol}'. Use the exact Yahoo Finance ticker (e.g., for Google use GOOGL)."
    return str(error_msg)

import requests
import urllib.parse

def resolve_ticker(query):
    """
    Search Yahoo Finance to resolve a company name (e.g. 'Google') into its proper ticker (e.g. 'GOOG').
    If nothing is found, return the original query.
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3)
        data = res.json()
        quotes = data.get('quotes', [])
        if quotes and len(quotes) > 0:
            return quotes[0].get('symbol', query)
    except:
        pass
    return query
