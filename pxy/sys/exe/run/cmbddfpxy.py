import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger
import os
import logging

logging = Logger(30, dir_path + "main.log")

def get_holdingsinfo(resp_list):
    try:
        if resp_list:  # Check if the response list is not empty
            df = pd.DataFrame(resp_list)
            df['source'] = 'holdings'
        else:
            df = pd.DataFrame()  # Return an empty DataFrame if no data
        return df
    except Exception as e:
        print(f"An error occurred in holdings: {e}")
        return pd.DataFrame()

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
    logging.error(f"{str(e)} unable to get holdings")
    sys.exit(1)
finally:
    if sys.stdout != sys.__stdout__:
        sys.stdout.close()
        sys.stdout = sys.__stdout__

def process_data():
    try:
        holdings_response = broker.kite.holdings()
        positions_response = broker.kite.positions().get('net', [])
        
        holdings_df = get_holdingsinfo(holdings_response)
        positions_df = get_positionsinfo(positions_response)

        holdings_df.to_csv('pxyholdings.csv', index=False)
        positions_df.to_csv('pxypositions.csv', index=False)

        if holdings_df.empty and positions_df.empty:
            print("Both holdings and positions are empty 🗑🗑.")
            return None

        if not holdings_df.empty:
            holdings_df['key'] = holdings_df['exchange'] + ":" + holdings_df['tradingsymbol']
        else:
            holdings_df['key'] = None
        
        if not positions_df.empty:
            positions_df['key'] = positions_df['exchange'] + ":" + positions_df['tradingsymbol']
        else:
            positions_df['key'] = None

        combined_df = pd.concat([holdings_df, positions_df], ignore_index=True)

        if combined_df.empty:
            print("Combined DataFrame is empty.")
            return combined_df

        lst = combined_df['key'].dropna().tolist()
        if not lst:
            print("No valid keys found to fetch OHLC data.")
            return combined_df


        combined_df['ltp'] = combined_df['last_price']
        combined_df['close'] = combined_df['close_price']
        combined_df['qty'] = combined_df.apply(lambda row: int(row.get('quantity', 0) + row.get('t1_quantity', 0)) if row['source'] == 'holdings' else int(row.get('quantity', 0)), axis=1)
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
