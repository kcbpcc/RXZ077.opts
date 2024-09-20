from rich import print
import yfinance as yf
import time
import warnings

# Suppress yfinance warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Constants for time range
START_TIME = 223  # 3:45 AM UTC
END_TIME = 245    # 4:05 AM UTC

def fetch_data(symbol):
    # Fetch real-time data for the specified symbol with a 1-minute interval
    data = yf.Ticker(symbol).history(period="5d", interval="1m")
    return data

def calculate_heikin_ashi_colors(data):
    # Calculate Heikin-Ashi candles
    ha_close = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
    ha_open = (data['Open'].shift(1) + data['Close'].shift(1)) / 2

    # Calculate the colors of the last 4 closed candles (oldest to latest)
    colors = ['🟥' if ha_close.iloc[-i] < ha_open.iloc[-i] else '🟩' for i in range(1, min(6, len(ha_close) + 1))][::-1]

    # Current and previous candle colors
    current_color = 'Bear' if ha_close.iloc[-1] < ha_open.iloc[-1] else 'Bull'
    last_closed_color = 'Bear' if ha_close.iloc[-2] < ha_open.iloc[-2] else 'Bull'
    second_last_closed_color = 'Bear' if ha_close.iloc[-3] < ha_open.iloc[-3] else 'Bull'
    third_last_closed_color = 'Bear' if ha_close.iloc[-4] < ha_open.iloc[-4] else 'Bull'

    # Rich print statement for all candle colors (adjusting for length)
    onemincandlesequance = f'{"".join(colors)}'

    return onemincandlesequance, current_color, last_closed_color, second_last_closed_color, third_last_closed_color

def calculate_last_twenty_heikin_ashi_colors(symbol):
    # Check if the current time is within the specified time range (3:45 AM to 4:00 AM UTC)
    current_utc_time = time.gmtime().tm_hour * 60 + time.gmtime().tm_min

    # Fetch data if within time range or default period
    data = fetch_data(symbol)
    
    return calculate_heikin_ashi_colors(data)

def get_market_check(symbol):
    # Get the Heikin-Ashi candle colors
    onemincandlesequance, current_color, last_closed_color, second_last_closed_color, third_last_closed_color = calculate_last_twenty_heikin_ashi_colors(symbol)

    # Determine the market condition based on Heikin-Ashi colors
    if current_color == 'Bear' and last_closed_color == 'Bear':
        mktpxy = 'Bear'
    elif current_color == 'Bull' and last_closed_color == 'Bull':
        mktpxy = 'Bull'
    elif current_color == 'Bear' and last_closed_color == 'Bull' and second_last_closed_color == 'Bull' and third_last_closed_color == 'Bull':
        mktpxy = 'Sell'
    elif current_color == 'Bull' and last_closed_color == 'Bear' and second_last_closed_color == 'Bear' and third_last_closed_color == 'Bear':
        mktpxy = 'Buy'
    else:
        mktpxy = 'None'

    return onemincandlesequance, mktpxy
