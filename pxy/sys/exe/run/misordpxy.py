import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger
import os
import logging

logger = Logger(30, dir_path + "main.log")  # Renamed logger instance

def get_ordersinfo(orders):
    try:
        if orders:  # Check if the orders list is not empty
            df = pd.DataFrame(orders)
            df = df[df['status'] == 'COMPLETE']  # Filter only completed orders
            df = df[['order_timestamp', 'transaction_type', 'tradingsymbol', 'product', 'quantity', 'average_price', 'status']]
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no data
    except Exception as e:
        print(f"An error occurred in fetching orders: {e}")
        return pd.DataFrame()

def get_positionsinfo(positions):
    try:
        if positions:  # Check if the positions list is not empty
            df = pd.DataFrame(positions)
            df = df[['tradingsymbol', 'last_price']]  # Extract only relevant columns
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no data
    except Exception as e:
        print(f"An error occurred in fetching positions: {e}")
        return pd.DataFrame()

def calculate_profit(orders_df, positions_df):
    try:
        # Create a dictionary to hold buy/sell orders
        trade_data = {}

        for index, row in orders_df.iterrows():
            symbol = row['tradingsymbol']
            qty = row['quantity']
            price = row['average_price']
            order_type = row['transaction_type']

            if symbol not in trade_data:
                trade_data[symbol] = {'buy': [], 'sell': []}

            trade_data[symbol][order_type.lower()].append({'price': price, 'qty': qty})

        # Now calculate PnL
        result = []

        for symbol, trades in trade_data.items():
            ltp = positions_df.loc[positions_df['tradingsymbol'] == symbol, 'last_price'].values[0]

            if trades['buy'] and trades['sell']:
                buy = trades['buy'][0]
                sell = trades['sell'][0]

                if buy['qty'] == sell['qty']:
                    pnl = (sell['price'] - buy['price']) * buy['qty']
                    result.append({
                        'Symbol': symbol,
                        'Buy Price': buy['price'],
                        'Sell Price': sell['price'],
                        'LTP': ltp,
                        'Quantity': buy['qty'],
                        'Profit/Loss': pnl,
                        'Status': 'Closed'
                    })
                else:
                    # Handle mismatched quantities if required
                    pass
            else:
                # If only buy order exists, calculate unrealized profit/loss
                if trades['buy']:
                    pnl = (ltp - trades['buy'][0]['price']) * trades['buy'][0]['qty']
                else:
                    pnl = None
                result.append({
                    'Symbol': symbol,
                    'Buy Price': trades['buy'][0]['price'] if trades['buy'] else None,
                    'Sell Price': trades['sell'][0]['price'] if trades['sell'] else None,
                    'LTP': ltp,
                    'Quantity': trades['buy'][0]['qty'] if trades['buy'] else trades['sell'][0]['qty'],
                    'Profit/Loss': pnl,
                    'Status': 'Open'
                })

        return pd.DataFrame(result)
    except Exception as e:
        print(f"An error occurred in profit calculation: {e}")
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
        # Retrieve orders using the Kite Connect API
        orders_response = broker.kite.orders()
        orders_df = get_ordersinfo(orders_response)

        if orders_df.empty:  # Check if orders_df is empty
            print("No completed orders available.")
            return pd.DataFrame()

        # Retrieve positions using the Kite Connect API
        positions_response = broker.kite.positions().get('net', [])
        positions_df = get_positionsinfo(positions_response)

        if positions_df.empty:  # Check if positions_df is empty
            print("No positions available.")
            return pd.DataFrame()

        # Calculate profit or loss using positions' last prices
        profit_df = calculate_profit(orders_df, positions_df)

        # Print the result
        print(profit_df)

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        logger.error(f"{str(e)} unable to process orders")
        return pd.DataFrame()

# Call the process_data function
process_data()
