import yfinance as yf

def check_stock_symbols(symbols):
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            # Try fetching some historical data (like the last 5 days)
            data = stock.history(period="1y")
            print(data)
            if not data.empty:
                print(f"Success: {symbol} is listed and data is available.")
            else:
                print(f"Warning: {symbol} is listed, but no historical data found.")
        
        except Exception as e:
            print(f"Error: {symbol} may not be listed or there was an issue fetching data. {e}")

# List of stock symbols to check
symbols = ['HINDUNILVR.NS']

# Check if each stock symbol is listed
check_stock_symbols(symbols)
