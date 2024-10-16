import yfinance as yf

# Get Nifty 50 data
nifty50 = yf.Ticker("^NSEI")

# Fetch historical market data
hist = nifty50.history(period="1mo")
print(hist)
