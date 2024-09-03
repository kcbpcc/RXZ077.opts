import yfinance as yf
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def get_7_day_sma(symbol):
    data = yf.Ticker(symbol).history(period="1mo", interval="1d")  # Fetch 1 month of data
    sma_7 = data['Close'].rolling(window=7).mean().iloc[-1]  # Calculate the 7-day SMA
    return sma_7

def round_to_nearest_500(price):
    return round(price / 500) * 500

def round_to_nearest_1000(price):
    return round(price / 1000) * 1000

def get_prices():
    BCE_Strike = round_to_nearest_1000(get_7_day_sma('^NSEBANK'))
    CE_Strike = round_to_nearest_500(get_7_day_sma('^NSEI'))
    PE_Strike = round_to_nearest_500(get_7_day_sma('^NSEI'))
    BPE_Strike = round_to_nearest_1000(get_7_day_sma('^NSEBANK'))
                                    
    return BCE_Strike, CE_Strike, PE_Strike, BPE_Strike




