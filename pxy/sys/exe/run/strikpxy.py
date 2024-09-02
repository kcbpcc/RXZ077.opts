import yfinance as yf
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def get_7_day_sma(symbol):
    data = yf.Ticker(symbol).history(period="1mo", interval="1d")  # Fetch 1 month of data
    sma_7 = data['Close'].rolling(window=7).mean().iloc[-1]  # Calculate the 7-day SMA
    return sma_7

def get_current_price(symbol):
    data = yf.Ticker(symbol).history(period="1d", interval="1m")  # Fetch only one day of data
    current_price = data['Close'].iloc[-1]  # Get the last available price
    return current_price

def round_to_nearest_500(price):
    return round(price / 500) * 500

def round_to_nearest_1000(price):
    return round(price / 1000) * 1000

def get_prices():
    # Get current prices and SMA values
    current_price_nsei = get_current_price('^NSEI')
    current_price_nsebank = get_current_price('^NSEBANK')
    sma_7_nsei = get_7_day_sma('^NSEI')
    sma_7_nsebank = get_7_day_sma('^NSEBANK')
    
    if current_price_nsei > sma_7_nsei:
        BCE_Strike = round_to_nearest_1000(sma_7_nsebank)
        CE_Strike = round_to_nearest_500(sma_7_nsei)
        PE_Strike = round_to_nearest_500(current_price_nsei)
        BPE_Strike = round_to_nearest_1000(current_price_nsebank)
    elif current_price_nsei < sma_7_nsei:
        BCE_Strike = round_to_nearest_1000(current_price_nsebank)
        CE_Strike = round_to_nearest_500(current_price_nsei)
        PE_Strike = round_to_nearest_500(sma_7_nsei)
        BPE_Strike = round_to_nearest_1000(sma_7_nsebank)
                                    
    return BCE_Strike, CE_Strike, PE_Strike, BPE_Strike




