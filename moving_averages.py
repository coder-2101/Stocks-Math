import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import logging
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress the NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("moving_averages.log"),
        logging.StreamHandler()
    ]
)

def calculate_moving_averages(stock_data):
    """
    Calculate various moving averages and add them to the stock_data DataFrame.
    """
    # Ensure 'OHLC4' column exists
    if 'OHLC4' not in stock_data.columns:
        stock_data['OHLC4'] = (stock_data['Open'] + stock_data['High'] +
                               stock_data['Low'] + stock_data['Close']) / 4

    # List of moving averages and indicators to calculate
    indicators = {
        'ALMA': ta.alma(stock_data['Close'], length=20, sigma=6, offset=0.85),
        'DEMA': ta.dema(stock_data['Close'], length=20),
        'EMA': ta.ema(stock_data['Close'], length=20),
        'FWMA': ta.wma(stock_data['Close'], length=20),
        'HILO': ta.hilo(stock_data['High'], stock_data['Low'], stock_data['Close'], length=13),
        'HMA': ta.hma(stock_data['Close'], length=20),
        'HWMA': ta.hwma(stock_data['Close'], length=20),
        'KAMA': ta.kama(stock_data['Close'], length=20, fast=2, slow=30),
        'LINREG': ta.linreg(stock_data['Close'], length=20),
        'MA_SMA': ta.sma(stock_data['Close'], length=20),
        'MIDPOINT': ta.midpoint(stock_data['Close'], length=20),
        'MIDPRICE': ta.midprice(stock_data['High'], stock_data['Low'], length=20),
        'OHLC4': stock_data['OHLC4'],
        'PWMA': ta.pwma(stock_data['Close'], length=20),
        'RMA': ta.rma(stock_data['Close'], length=20),
        'SINWMA': ta.sinwma(stock_data['Close'], length=14),
        'SMA': ta.sma(stock_data['Close'], length=20),
        'SSF': ta.ssf(stock_data['Close'], length=20),
        'SUPERTREND': ta.supertrend(stock_data['High'], stock_data['Low'], stock_data['Close']),
        'SWMA': ta.swma(stock_data['Close'], length=20),
        'T3': ta.t3(stock_data['Close'], length=20),
        'TEMA': ta.tema(stock_data['Close'], length=20),
        'TRIMA': ta.trima(stock_data['Close'], length=20),
        'VIDYA': ta.vidya(stock_data['Close'], length=20, alpha=0.2),
        'VWAP': ta.vwap(stock_data['High'], stock_data['Low'], stock_data['Close'], stock_data['Volume']),
        'VWMA': ta.vwma(stock_data['Close'], volume=stock_data['Volume'], length=20),
        'WCP': ta.wcp(stock_data['High'], stock_data['Low'], stock_data['Close']),
        'WMA': ta.wma(stock_data['Close'], length=20),
        'ZLMA': ta.zlma(stock_data['Close'], length=20),
    }

    # Add indicators to the DataFrame
    for name, indicator in indicators.items():
        if isinstance(indicator, pd.DataFrame):
            for col in indicator.columns:
                stock_data[f"{name}_{col}"] = indicator[col]
        else:
            stock_data[name] = indicator

    return stock_data, indicators

def calculate_bollinger_percentages(stock_data, indicators):
    bollinger_percentages = {}
    for name, indicator in indicators.items():
        length = 20  # Adjust if needed
        std_dev = stock_data['OHLC4'].rolling(window=length).std()

        if isinstance(indicator, pd.Series):
            upper_band = indicator + 2 * std_dev
            lower_band = indicator - 2 * std_dev
            bollinger_b = ((stock_data['OHLC4'] - lower_band) / (upper_band - lower_band)) * 100
            stock_data[f'Boll_%b_{name}'] = bollinger_b
            bollinger_percentages[name] = bollinger_b.iloc[-1]
        elif isinstance(indicator, pd.DataFrame):
            for col in indicator.columns:
                series = indicator[col]
                upper_band = series + 2 * std_dev
                lower_band = series - 2 * std_dev
                bollinger_b = ((stock_data['OHLC4'] - lower_band) / (upper_band - lower_band)) * 100
                stock_data[f'Boll_%b_{name}_{col}'] = bollinger_b
                bollinger_percentages[f'{name}_{col}'] = bollinger_b.iloc[-1]
        else:
            continue  # Skip if indicator is neither Series nor DataFrame

    return stock_data, bollinger_percentages

def print_moving_averages(stock_data, bollinger_percentages):
    latest_data = stock_data.iloc[-1]
    print("\nLatest Moving Averages and Bollinger %b:")
    for column in stock_data.columns:
        if column in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'OHLC4']:
            continue
        ma_value = latest_data.get(column, np.nan)
        boll_percent = bollinger_percentages.get(column, np.nan)
        if pd.notna(ma_value):
            if pd.notna(boll_percent):
                print(f"{column}: {ma_value:.2f}, Boll %b: {boll_percent:.2f}%")
            else:
                print(f"{column}: {ma_value:.2f}")

def main():
    # List of stock symbols to monitor
    stock_symbols = [
        'DEEPAKFERT.NS',
        # Add other stock symbols as needed
    ]

    # Fetch and process data for each stock symbol
    for symbol in stock_symbols:
        logging.info(f"Processing {symbol}")
        try:
            # Fetch stock data with a 1-minute interval for the past 5 days
            stock_data = yf.download(symbol, period="5d", interval="2m", progress=False)

            if stock_data.empty:
                logging.error(f"No data fetched for {symbol}.")
                continue

            # Calculate moving averages and indicators
            stock_data, indicators = calculate_moving_averages(stock_data)

            # Calculate Bollinger %b
            stock_data, bollinger_percentages = calculate_bollinger_percentages(stock_data, indicators)

            # Print the latest moving averages and Bollinger %b
            print(f"\nStock: {symbol}")
            print_moving_averages(stock_data, bollinger_percentages)

        except Exception as e:
            logging.error(f"An error occurred for {symbol}: {e}")

if __name__ == "__main__":
    main()