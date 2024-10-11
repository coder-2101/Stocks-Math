import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

def get_bollinger_percentage(stock_symbol):
    try:
        # Fetch stock data with a 1-hour interval
        stock_data_1h = yf.download(stock_symbol, period="6mo", interval="1h")

        if stock_data_1h.empty:
            print(f"Error: No data fetched for {stock_symbol}")
            return None

        # Resample to 2-hour intervals
        stock_data = stock_data_1h.resample('2H').agg({
            'Open': 'first',  # Take the first value for the open price
            'High': 'max',    # Take the maximum value for the high price
            'Low': 'min',     # Take the minimum value for the low price
            'Close': 'last',  # Take the last value for the close price
            'Volume': 'sum'   # Sum the volume traded in the 2-hour interval
        }).dropna()

        if stock_data.empty:
            print(f"Error: No data after resampling for {stock_symbol}")
            return None

        # Calculate the typical price (Open + High + Low + Close) / 4
        stock_data['OHLC4'] = (stock_data['Open'] + stock_data['High'] + stock_data['Low'] + stock_data['Close']) / 4

        # Calculate Variable Monthly Average (assuming it's an Exponential Moving Average here)
        # Adjust as per your definition of variable monthly average
        stock_data['VMA'] = stock_data['OHLC4'].ewm(span=20, adjust=False).mean()

        # Calculate Bollinger Bands using pandas_ta
        bbands = ta.bbands(stock_data['OHLC4'], length=20, std=2)

        # Merge Bollinger Bands with stock data
        stock_data = stock_data.join(bbands)

        # Calculate Bollinger %b
        stock_data['%b'] = ((stock_data['OHLC4'] - stock_data['BBL_20_2.0']) /
                            (stock_data['BBU_20_2.0'] - stock_data['BBL_20_2.0'])) * 100

        return stock_data['%b'].iloc[-1]  # Return the most recent Bollinger %b
    except Exception as e:
        print(f"An error occurred for {stock_symbol}: {e}")
        return None

def check_bollinger_percentage(stock_symbol):
    bollinger_percentage = get_bollinger_percentage(stock_symbol)

    if bollinger_percentage is not None:
        print(f"Current Bollinger %b for {stock_symbol}: {bollinger_percentage:.2f}%")
        if bollinger_percentage < 0:
            print(f"ALERT: Bollinger %b for {stock_symbol} has dropped below 0%!")
        elif bollinger_percentage < 5:  # Adjust the threshold as needed
            print(f"ALERT: Bollinger %b for {stock_symbol} is approaching 0%!")

# List of stock symbols
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

# Check Bollinger Percentage in a loop (e.g., every day)
while True:
    for symbol in stock_symbols:
        check_bollinger_percentage(symbol)
    # Wait for 24 hours before checking again
    time.sleep(24 * 60 * 60)