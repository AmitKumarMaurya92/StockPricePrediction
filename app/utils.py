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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def resolve_ticker(query, market='IN'):
    """
    Search Yahoo Finance to resolve a company name (e.g. 'Google') into its proper ticker (e.g. 'GOOG').
    If nothing is found, return the original query.
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}"
        res = requests.get(url, headers=HEADERS, timeout=3)
        data = res.json()
        quotes = data.get('quotes', [])
        
        # Try to find a ticker that matches the requested market first
        for q in quotes:
            symbol = q.get('symbol')
            if not symbol: continue
            
            if market == 'IN' and (symbol.endswith('.NS') or symbol.endswith('.BO')):
                return symbol
            elif market != 'IN' and not (symbol.endswith('.NS') or symbol.endswith('.BO')):
                return symbol

        if quotes and len(quotes) > 0:
            return quotes[0].get('symbol', query)
    except:
        pass
    return query

def get_autocomplete_suggestions(query, market='IN'):
    """
    Search Yahoo Finance to return autocomplete suggestions based on market.
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}"
        res = requests.get(url, headers=HEADERS, timeout=3)
        data = res.json()
        quotes = data.get('quotes', [])
        
        suggestions = []
        for q in quotes:
            symbol = q.get('symbol')
            if not symbol:
                continue
                
            # Filter by market
            if market == 'IN':
                if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
                    continue
            else:
                # Exclude Indian stocks if US market is selected
                if symbol.endswith('.NS') or symbol.endswith('.BO'):
                    continue

            if q.get('quoteType') in ['EQUITY', 'ETF', 'MUTUALFUND']:
                name = q.get('shortname') or q.get('longname') or symbol
                exchange = q.get('exchDisp', '')
                
                # Remove suffix for sleek display (e.g., RELIANCE.NS -> RELIANCE)
                display_symbol = symbol.split('.')[0]
                
                suggestions.append({
                    'raw_symbol': symbol,
                    'symbol': display_symbol,
                    'name': name,
                    'exchange': exchange
                })
        
        # Fallback if strict equities list is empty
        if not suggestions:
            for q in quotes:
                symbol = q.get('symbol')
                if not symbol: continue
                # Match market
                if market == 'IN' and not (symbol.endswith('.NS') or symbol.endswith('.BO')): continue
                if market == 'US' and (symbol.endswith('.NS') or symbol.endswith('.BO')): continue
                
                name = q.get('shortname') or q.get('longname') or symbol
                exchange = q.get('exchDisp', '')
                display_symbol = symbol.split('.')[0]
                
                suggestions.append({'raw_symbol': symbol, 'symbol': display_symbol, 'name': name, 'exchange': exchange})
                    
        return suggestions[:8]
    except Exception as e:
        print(f"Error in autocomplete: {e}")
    return []
