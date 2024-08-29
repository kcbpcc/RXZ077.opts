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

def calculate_profit(df):
    try:
        # Create a dictionary to hold buy/sell orders
        trade_data = {}

        for index, row in df.iterrows():
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
            if trades['buy'] and trades['sell']:
                buy = trades['buy'][0]
                sell = trades['sell'][0]
                
                if buy['qty'] == sell['qty']:
                    pnl = (sell['price'] - buy['price']) * buy['qty']
                    result.append({
                        'Symbol': symbol,
                        'Buy Price': buy['price'],
                        'Sell Price': sell['price'],
                        'Quantity': buy['qty'],
                        'Profit/Loss': pnl,
                        'Status': 'Closed'
                    })
                else:
                    # Handle mismatched quantities if required
                    pass
            else:
                result.append({
                    'Symbol': symbol,
                    'Buy Price': trades['buy'][0]['price'] if trades['buy'] else None,
                    'Sell Price': trades['sell'][0]['price'] if trades['sell'] else None,
                    'Quantity': trades['buy'][0]['qty'] if trades['buy'] else trades['sell'][0]['qty'],
                    'Profit/Loss': None,
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

        # Calculate profit or loss
        profit_df = calculate_profit(orders_df)

        # Print the result
        print(profit_df)

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        logger.error(f"{str(e)} unable to process orders")
        return pd.DataFrame()

# Call the process_data function
process_data()
