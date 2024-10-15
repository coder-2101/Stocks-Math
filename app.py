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
            # print(f"Current Bollinger %b for {symbol}: {bollinger_b:.2f}%, RSI: {rsi:.2f}")

            # Bollinger %b alerts
            if bollinger_b < 0:
                message = f"ALERT: Bollinger %b for {symbol} has dropped below 0%!"
                socketio.emit('new_alert', {'message': message, 'type': 'alert'})
            elif bollinger_b > 100:
                message = f"WARNING: Bollinger %b for {symbol} is above 100%!"
                socketio.emit('new_alert', {'message': message, 'type': 'alert'})

            # RSI alerts
            if rsi < 10:
                message = f"ALERT: RSI for {symbol} has dropped below 10!"
                socketio.emit('new_alert', {'message': message, 'type': 'alert'})
            elif rsi > 90:
                message = f"WARNING: RSI for {symbol} is above 90!"
                socketio.emit('new_alert', {'message': message, 'type': 'alert'})
        else:
            print(f"Indicators for {symbol} are None, skipping...")

# Step 5: Main monitoring function
def monitor_stock_indicators():
    
    stock_symbols = [
        'DEEPAKFERT.NS',
    'MRPL.NS',
    'APOLLOTYRE.NS',
    'ASKOKLEY.NS',
    'BAJAJ.NS-AUTO',
    'BALKRISIND.NS',
    'BASCHLTD.NS',
    'BHARATFORG.NS',
    'EICHERMOT.NS',
    'HEROMOTOCO.NS',
    'M.NS&M',
    'MARUTI.NS',
    'MOTHERSON.NS',
    'MRF.NS',
    'TATAMOTORS.NS',
    'TATAMTRDVR.NS',
    'TVSMOTOR.NS',
    'AUBANK.NS',
    'AXISBANK.NS',
    'BANDHANBNK.NS',
    'BANKBARODA.NS',
    'CANBK.NS',
    'CENTRALBK.NS',
    'CUB.NS',
    'FEDERALBNK.NS',
    'HDFCBANK.NS',
    'ICICIBANK.NS',
    'IDFCFIRSTB.NS',
    'INDUSINDBK.NS',
    'KOTAKBANK.NS',
    'PNB.NS',
    'RBLBANK.NS',
    'SBIN.NS',
    'YESBANK.NS',
    'ABB.NS',
    'ASTRAL.NS',
    'BEL.NS',
    'BHEL.NS',
    'CROMPTON.NS',
    'CUMMINSIND.NS',
    'DIXON.NS',
    'HAL.NS',
    'HAVELS.NS',
    'LT.NS',
    'POLYCAB.NS',
    'SIEMENS.NS',
    'VOLTAS.NS',
    'ACC.NS',
    'AMBUJACEM.NS',
    'DALBHARAT.NS',
    'GRASIM.NS',
    'INDIACEM.NS',
    'JKCEMENT.NS',
    'RAMCOCEM.NS',
    'SHREECEM.NS',
    'STARCEMENT.NS',
    'ULTRACEMCO.NS',
    'AARTIIND.NS',
    'ATUL.NS',
    'CHAMBLFERT.NS',
    'COROMANDEL.NS',
    'DEEPAKNTR.NS',
    'GNFC.NS',
    'NAVINFLUOR.NS',
    'PIDLITIND.NS',
    'PIIND.NS',
    'TATACHEM.NS',
    'UPL.NS',
    'ABCAPITAL.NS',
    'BAJAJFINSV.NS',
    'BAJFINANCE.NS',
    'CANFINHOME.NS',
    'CHOLAFIN.NS',
    'HDFCAMC.NS',
    'HDFCLIFE.NS',
    'ICICIGI.NS',
    'ICICIPRULI.NS',
    'IDFC.NS',
    'L.NS&TFH',
    'LICHSGFIN.NS',
    'LICI.NS',
    'M.NS&MFIN',
    'MANAPPURAM.NS',
    'MFSL.NS',
    'MUTHOOTFIN.NS',
    'PEL.NS',
    'PFC.NS',
    'RECLTD.NS',
    'SBICARD.NS',
    'SBILIFE.NS',
    'SRIRAMFIN.NS',
    'ASIANPAINT.NS',
    'AWL.NS',
    'BALRAMCHIN.NS',
    'BATAINDIA.NS',
    'BERGEPAINT.NS',
    'BRITANNIA.NS',
    'COLPAL.NS',
    'DABUR.NS',
    'GODFRYPHLP.NS',
    'GODREJCP.NS',
    'HINDUNILVR.NS',
    'INDIAMART.NS',
    'ITC.NS',
    'MARICO.NS',
    'NESTLEIND.NS',
    'SIRCA.NS',
    'TATACONSUM.NS',
    'TITAN.NS',
    'UBL.NS',
    'ZYDUSWELL.NS',
    'ADANIENT.NS',
    'ADANIPORTS.NS',
    'CONCOR.NS',
    'GMRINFRA.NS',
    'INDIGO.NS',
    'IRCTC.NS',
    'APOLLO.NS',
    'BSOFT.NS',
    'COFORGE.NS',
    'FSL.NS',
    'HCLTECH.NS',
    'HGS.NS',
    'INFY.NS',
    'INTELLECT.NS',
    'KPITECH.NS',
    'LTIM.NS',
    'LTTS.NS',
    'MCX.NS',
    'MPHASIS.NS',
    'NAUKRI.NS',
    'OFSS.NS',
    'PERSISTENT.NS',
    'TATAELAXI.NS',
    'TCS.NS',
    'TECHM.NS',
    'WIPRO.NS',
    'ZENTEC.NS',
    'PVRINOX.NS',
    'SUNTV.NS',
    'ZEEL.NS',
    'APLAPOLLO.NS',
    'COALINDIA.NS',
    'HINDALCO.NS',
    'HINDCOPPER.NS',
    'HINDZINC.NS',
    'JINDSTEL.NS',
    'JSWSTEEL.NS',
    'NATIONALUM.NS',
    'NMDC.NS',
    'SAIL.NS',
    'TATASTEEL.NS',
    'VEDL.NS',
    'BPCL.NS',
    'GAIL.NS',
    'GUJGASLTD.NS',
    'HINDPETRO.NS',
    'IGL.NS',
    'IOC.NS',
    'MGL.NS',
    'ONGC.NS',
    'PETRONET.NS',
    'RELIANCE.NS',
    'BAJAJHIND.NS',
    'DEVYANI.NS',
    'GRSE.NS ',
    'IRFC.NS',
    'NYKAA.NS',
    'POLYPLEX.NS',
    'RAJPACK.NS',
    'RENUKA.NS',
    'RVNL.NS',
    'TTKPRESTIG.NS',
    'ZOMATO.NS ',
    'ABBOTINDIA.NS',
    'ALKEM.NS',
    'APOLOHOSP.NS',
    'AUROPHARMA.NS',
    'BIOCON.NS',
    'CIPLA.NS',
    'DIVISLAB.NS',
    'DRREDDY.NS',
    'GLENMARK.NS',
    'GRANULES.NS',
    'IPCALAB.NS',
    'LALPATHLAB.NS',
    'LAURULABS.NS',
    'LUPIN.NS',
    'METROPOLIS.NS',
    'SUNPHARMA.NS',
    'SYNGENE.NS',
    'TORNPHARM.NS',
    'ZYDUSLIFE.NS',
    'IEX.NS',
    'NTPC.NS',
    'POWERGRID.NS',
    'SUZLON.NS',
    'TATAPOWER.NS',
    'DELTACORP.NS',
    'DLF.NS',
    'GODREJPROP.NS',
    'INDHOTEL.NS',
    'OBEROIRLTY.NS',
    'BHARTIARTL.NS',
    'IDEA.NS',
    'INDUSTOWER.NS',
    'TATACOMM.NS',
    'TELECOM.NS',
    'ABFRL.NS',
    'PAGEIND.NS',
    'RAYMOND.NS',
    'SRF.NS',
    'TRENT.NS',
    ]


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

if __name__ == '__main__':
    # Run stock monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_stock_indicators)
    monitor_thread.daemon = True
    monitor_thread.start()
    socketio.run(app, host='0.0.0.0', port=5001)
