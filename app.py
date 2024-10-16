from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

stock_symbols = [
        'ABB.NS',
        'ABBOTINDIA.NS',
        'ACC.NS',
        'ADANIENT.NS',
        'ADANIPORTS.NS',
        'AMBUJACEM.NS',
        'APLAPOLLO.NS',
        'APOLLO.NS',
        'APOLLOTYRE.NS',
        'APOLOHOSP.NS',
        'ASIANPAINT.NS',
        'ASKOKLEY.NS',
        'ASTRAL.NS',
        'AWL.NS',
        'AXISBANK.NS',
        'BAJAJ-AUTO.NS',
        'BAJAJFINSV.NS',
        'BAJAJHIND.NS',
        'BAJFINANCE.NS',
        'BALRAMCHIN.NS',
        'BANKBARODA.NS',
        'BATAINDIA.NS',
        'BEL.NS',
        'BERGEPAINT.NS',
        'BHARATFORG.NS',
        'BHARTIARTL.NS',
        'BHEL.NS',
        'BPCL.NS',
        'BRITANNIA.NS',
        'BSOFT.NS',
        'CANBK.NS',
        'CENTRALBK.NS',
        'CHAMBLFERT.NS',
        'CIPLA.NS',
        'COALINDIA.NS',
        'COFORGE.NS',
        'COLPAL.NS',
        'CONCOR.NS',
        'CROMPTON.NS',
        'CUMMINSIND.NS',
        'DABUR.NS',
        'DALBHARAT.NS',
        'DEEPAKFERT.NS',
        'DEVYANI.NS',
        'DIVISLAB.NS',
        'DRREDDY.NS',
        'EICHERMOT.NS',
        'FSL.NS',
        'GAIL.NS',
        'GLENMARK.NS',
        'GODFRYPHLP.NS',
        'GODREJCP.NS',
        'GRANULES.NS',
        'GRASIM.NS',
        'GRSE .NS',
        'HAL.NS',
        'HAVELS.NS',
        'HCLTECH.NS',
        'HDFCBANK.NS',
        'HEROMOTOCO.NS',
        'HGS.NS',
        'HINDALCO.NS',
        'HINDCOPPER.NS',
        'HINDPETRO.NS',
        'HINDUNILVR.NS',
        'HINDZINC.NS',
        'ICICIBANK.NS',
        'IDEA.NS',
        'IDFCFIRSTB.NS',
        'IEX.NS',
        'IGL.NS',
        'INDHOTEL.NS',
        'INDIACEM.NS',
        'INDIAMART.NS',
        'INDUSINDBK.NS',
        'INDUSTOWER.NS',
        'INFY.NS',
        'INTELLECT.NS',
        'IOC.NS',
        'IRCTC.NS',
        'IRFC.NS',
        'ITC.NS',
        'JINDSTEL.NS',
        'JSWSTEEL.NS',
        'KOTAKBANK.NS',
        'KPITECH.NS',
        'LICI.NS',
        'LT.NS',
        'LTIM.NS',
        'LTTS.NS',
        'LUPIN.NS',
        'M&M.NS',
        'MARICO.NS',
        'MARUTI.NS',
        'MCX.NS',
        'MPHASIS.NS',
        'MRF.NS',
        'MRPL.NS',
        'NATIONALUM.NS',
        'NESTLEIND.NS',
        'NMDC.NS',
        'NTPC.NS',
        'NYKAA.NS',
        'ONGC.NS',
        'PETRONET.NS',
        'PFC.NS',
        'PIDLITIND.NS',
        'POLYCAB.NS',
        'POLYPLEX.NS',
        'POWERGRID.NS',
        'RAMCOCEM.NS',
        'RAYMOND.NS',
        'RELIANCE.NS',
        'RENUKA.NS',
        'RVNL.NS',
        'SAIL.NS',
        'SBIN.NS',
        'SIEMENS.NS',
        'SIRCA.NS',
        'SRF.NS',
        'STARCEMENT.NS',
        'SUNPHARMA.NS',
        'SUZLON.NS',
        'TATACHEM.NS',
        'TATACONSUM.NS',
        'TATAELAXI.NS',
        'TATAMOTORS.NS',
        'TATAPOWER.NS',
        'TATASTEEL.NS',
        'TCS.NS',
        'TECHM.NS',
        'TITAN.NS',
        'TORNPHARM.NS',
        'TRENT.NS',
        'TTKPRESTIG.NS',
        'TVSMOTOR.NS',
        'UBL.NS',
        'ULTRACEMCO.NS',
        'UPL.NS',
        'VEDL.NS',
        'VOLTAS.NS',
        'WIPRO.NS',
        'YESBANK.NS',
        'ZENTEC.NS',
        'ZOMATO .NS',
        'ZYDUSWELL.NS',
    ]



# Step 1: Fetch Stock Data
def fetch_stock_data(stock_symbols):
    try:
        # Fetch stock data for all symbols with a 1-hour interval over the last 3 months
        stock_data = yf.download(stock_symbols, period="3mo", interval="1h", group_by='ticker', threads=True)

        if stock_data.empty:
            print(f"Error: No data returned for symbols {stock_symbols}")
            return None
        return stock_data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

# Step 2: Calculate Bollinger %b and RSI for a single stock
def calculate_bollinger_and_rsi(data):
    try:
        # Ensure that the index is a DateTimeIndex and sorted
        data = data.sort_index()
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)

        # Calculate OHLC4 for 1-hour data for RSI
        data['OHLC4'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4

        # For Bollinger Band %b, resample data to 2-hour intervals
        data_2h = data.resample('2h').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'OHLC4': 'mean'  # Alternatively, recalculate after resampling
        }).dropna()

        # Check if we have enough data points after resampling
        if len(data_2h) < 20:
            print("Not enough data after resampling to calculate Bollinger Bands")
            return None, None

        # Calculate Bollinger Bands on 2-hour data
        bbands = ta.bbands(data_2h['OHLC4'], length=20, std=2, mamode='ema')
        data_2h = data_2h.join(bbands)

        # Check if Bollinger Bands calculation was successful
        if bbands.isnull().all().all():
            print("Bollinger Bands calculation failed due to insufficient data")
            return None, None

        # Calculate Bollinger %b
        data_2h['Bollinger_%b'] = ((data_2h['OHLC4'] - data_2h['BBL_20_2.0']) /
                                    (data_2h['BBU_20_2.0'] - data_2h['BBL_20_2.0'])) * 100

        # Use the last value of Bollinger %b
        bollinger_b = data_2h['Bollinger_%b'].iloc[-1]

        # For RSI, use the 1-hour data
        data['RSI'] = ta.rsi(data['OHLC4'], length=14)

        # Check if RSI calculation was successful
        if data['RSI'].isnull().all():
            print("RSI calculation failed due to insufficient data")
            return None, None

        rsi = data['RSI'].iloc[-1]

        # Return both
        return bollinger_b, rsi

    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None, None

# Step 3: Process all stocks and compute indicators
def process_stock_data(stock_data, stock_symbols):
    results = {}
    for symbol in stock_symbols:
        try:
            data = stock_data[symbol]
            bollinger_b, rsi = calculate_bollinger_and_rsi(data)
            if bollinger_b is not None and rsi is not None:
                results[symbol] = {
                    'Bollinger_%b': bollinger_b,
                    'RSI': rsi
                }
            else:
                print(f"Insufficient data for {symbol}, skipping...")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
    return results

# Step 4: Emit alerts based on conditions
def check_and_emit_alerts(results):
    for symbol, indicators in results.items():
        bollinger_b = indicators['Bollinger_%b']
        rsi = indicators['RSI']

        # Ensure that bollinger_b and rsi are not None before formatting
        if bollinger_b is not None and rsi is not None:
            # Bollinger %b alerts
            if bollinger_b < 0:
                message = f"ALERT: Bollinger %b for {symbol} has dropped below 0%! | RSI: {rsi:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'blue'})
            elif bollinger_b < -10:
                message = f"ALERT: Bollinger %b for {symbol} has dropped below -10%! | RSI: {rsi:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'green'})
            elif bollinger_b > 100:
                message = f"ALERT: Bollinger %b for {symbol} is above 100%! | RSI: {rsi:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'orange'})
            elif bollinger_b > 120:
                message = f"ALERT: Bollinger %b for {symbol} is above 120%! | RSI: {rsi:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'red'})

            # RSI alerts
            if rsi < 10:
                message = f"ALERT: RSI for {symbol} has dropped below 10! | Bollinger %b: {bollinger_b:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'blue'})
            elif rsi < 5:
                message = f"ALERT: RSI for {symbol} has dropped below 5! | Bollinger %b: {bollinger_b:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'green'})
            elif rsi > 90:
                message = f"ALERT: RSI for {symbol} is above 90! | Bollinger %b: {bollinger_b:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'orange'})
            elif rsi > 95:
                message = f"ALERT: RSI for {symbol} is above 95! | Bollinger %b: {bollinger_b:.2f}"
                socketio.emit('new_alert', {'message': message, 'type': 'red'})
        else:
            print(f"Indicators for {symbol} are None, skipping...")


# Step 5: Main monitoring function
def monitor_stock_indicators():
    
    
    while True:
        stock_data = fetch_stock_data(stock_symbols)
        if stock_data is not None and not stock_data.empty:
            results = process_stock_data(stock_data, stock_symbols)
            if results:
                check_and_emit_alerts(results)
            else:
                print("No valid indicators calculated, retrying...")
        else:
            print("No valid stock data found, retrying...")
        time.sleep(60 * 60)  # Wait for 1 hour before checking again

@app.route('/')
def index():
    return render_template('index.html')

# Create a lock for thread safety
data_processing_lock = threading.Lock()

# (Rest of your functions: fetch_stock_data, calculate_bollinger_and_rsi, etc.)

# Step 5: Main monitoring function
def monitor_stock_indicators():
    while True:
        with data_processing_lock:
            stock_data = fetch_stock_data(stock_symbols)
            if stock_data is not None and not stock_data.empty:
                results = process_stock_data(stock_data, stock_symbols)
                if results:
                    check_and_emit_alerts(results)
                else:
                    print("No valid indicators calculated, retrying...")
            else:
                print("No valid stock data found, retrying...")
        time.sleep(60 * 60)  # Wait for 1 hour before checking again

@socketio.on('refresh_request')
def handle_refresh_request():
    with data_processing_lock:
        try:
            print("Received refresh request from client.")
            stock_data = fetch_stock_data(stock_symbols)
            if stock_data is not None and not stock_data.empty:
                results = process_stock_data(stock_data, stock_symbols)
                if results:
                    check_and_emit_alerts(results)
                    emit('refresh_complete', {'status': 'success'})
                else:
                    print("No valid indicators calculated.")
                    emit('refresh_complete', {'status': 'failure', 'message': 'No valid indicators calculated.'})
            else:
                print("No valid stock data found.")
                emit('refresh_complete', {'status': 'failure', 'message': 'No valid stock data found.'})
        except Exception as e:
            print(f"Error during refresh: {e}")
            emit('refresh_complete', {'status': 'failure', 'message': str(e)})

if __name__ == '__main__':
    # Run stock monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_stock_indicators)
    monitor_thread.daemon = True
    monitor_thread.start()
    socketio.run(app, host='0.0.0.0', port=5001)
    
