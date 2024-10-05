import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger

# Logger setup
logger = Logger(30, dir_path + "main.log")  # Renamed logger instance

# Function to handle the conversion of positions response
def get_positionsinfo(resp_list):
    try:
        if resp_list:  # Check if the response list is not empty
            df = pd.DataFrame(resp_list)
            df['source'] = 'positions'
        else:
            df = pd.DataFrame()  # Return an empty DataFrame if no data
        return df
    except Exception as e:
        print(f"An error occurred in positions: {e}")
        logger.error(f"Error processing positions: {str(e)}")
        return pd.DataFrame()

try:
    # Get the KiteConnect instance
    broker = get_kite()

    # Retrieve positions data from KiteConnect
    positions = broker.kite.positions()

    # Display the raw positions data as returned by KiteConnect
    print("Raw Positions Data:")
    print(positions)

    # Extract net positions from the response
    net_positions = positions.get('net', [])

    # Print each position's details as shown in the KiteConnect positions screen
    print("\nFormatted Positions Data:")
    for position in net_positions:
        print(f"Symbol: {position['tradingsymbol']}, Qty: {position['quantity']}, "
              f"PnL: {position['pnl']}, Buy Price: {position['buy_price']}, Last Price: {position['last_price']}")

except Exception as e:
    # If any error occurs, handle the exception, remove token, and log the error
    remove_token(dir_path)
    print(traceback.format_exc())
    logger.error(f"{str(e)} unable to get positions")
    sys.exit(1)

