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
            print("No positions available.")
            return pd.DataFrame()

        positions_df.to_csv('pxypositions.csv', index=False)
        combined_df = positions_df.reset_index(drop=True)
        combined_df['key'] = combined_df['exchange'] + ":" + combined_df['tradingsymbol']
        combined_df['ltp'] = combined_df['last_price']
        combined_df['close'] = combined_df['close_price']
        combined_df['qty'] = combined_df['quantity']
        combined_df['pnl'] = combined_df.get('pnl', 0).astype(int)
        combined_df['avg'] = combined_df.get('average_price', 0)
        combined_df['Invested'] = (combined_df['qty'] * combined_df['avg']).round(0).astype(int)
        combined_df['value'] = combined_df['qty'] * combined_df['ltp']
        combined_df['PnL'] = (combined_df['value'] - combined_df['Invested']).astype(int)
        combined_df['PL%'] = ((combined_df['PnL'] / combined_df['Invested']) * 100).round(2)
        combined_df['Yvalue'] = combined_df['qty'] * combined_df['close']
        combined_df['dPnL'] = combined_df['value'] - combined_df['Yvalue']
        combined_df.to_csv('pxycombined.csv', index=False)
        return combined_df

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    process_data()
