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
