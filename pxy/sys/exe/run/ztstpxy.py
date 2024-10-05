import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger
import os
import logging

logger = Logger(30, dir_path + "main.log")  # Renamed logger instance

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
        return pd.DataFrame()

try:
    sys.stdout = open('output.txt', 'w')
    broker = get_kite()
except Exception as e:
    remove_token(dir_path)
    print(traceback.format_exc())
    logger.error(f"{str(e)} unable to get holdings")
    sys.exit(1)
finally:
    if sys.stdout != sys.__stdout__:
        sys.stdout.close()
        sys.stdout = sys.__stdout__

def process_data():
    try:
        positions_response = broker.kite.positions().get('net', [])
        positions_df = get_positionsinfo(positions_response)
        if positions_df.empty:  # Check if positions_df is empty
            return pd.DataFrame()

        # Saving the positions_df to CSV
        positions_df.to_csv('pxypositions.csv', index=False)

        # Creating combined_df and adding new columns with 'pxy_' prefix only
        combined_df = pd.DataFrame()
        combined_df['pxy_key'] = positions_df['exchange'] + ":" + positions_df['tradingsymbol']
        combined_df['pxy_ltp'] = positions_df['last_price']
        combined_df['pxy_close'] = positions_df['close_price']
        combined_df['pxy_qty'] = positions_df['quantity']
        combined_df['pxy_rqty'] = positions_df['quantity'] + positions_df['day_sell_quantity']
        combined_df['pxy_avg'] = positions_df.get('average_price', 0)

        # Calculation of investment and value
        combined_df['pxy_invst'] = (combined_df['pxy_qty'] * combined_df['pxy_avg']).round(0).astype(int)
        combined_df['pxy_value'] = combined_df['pxy_qty'] * combined_df['pxy_ltp']
        combined_df['pxy_pnl'] = positions_df.get('unrealised', 0)

        # Saving the combined_df to CSV (only columns with 'pxy_' prefix)
        combined_df.to_csv('pxycombined.csv', index=False)
        return combined_df

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    process_data()
