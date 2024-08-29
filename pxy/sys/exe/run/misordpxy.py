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
        closed_trades = []
        open_trades = []

        for symbol, trades in trade_data.items():
            ltp = positions_df.loc[positions_df['tradingsymbol'] == symbol, 'last_price'].values[0] if not positions_df.empty else None

            if trades['buy'] and trades['sell']:
                buy = trades['buy'][0]
                sell = trades['sell'][0]

                if buy['qty'] == sell['qty']:
                    pnl = (sell['price'] - buy['price']) * buy['qty']
                    pl_percent = (pnl / (buy['price'] * buy['qty'])) * 100
                    closed_trades.append({
                        'Symbol': symbol,
                        'Buy Price': buy['price'],
                        'Sell Price': sell['price'],
                        'LTP': ltp,
                        'Quantity': buy['qty'],
                        'Profit/Loss': pnl,
                        'PL%': pl_percent,
                        'Status': 'Closed'
                    })
            else:
                # If only buy order exists, calculate unrealized profit/loss
                if trades['buy']:
                    pnl = (ltp - trades['buy'][0]['price']) * trades['buy'][0]['qty'] if ltp else None
                    pl_percent = (pnl / (trades['buy'][0]['price'] * trades['buy'][0]['qty'])) * 100 if pnl else None
                    open_trades.append({
                        'Symbol': symbol,
                        'Buy Price': trades['buy'][0]['price'],
                        'Sell Price': None,
                        'LTP': ltp,
                        'Quantity': trades['buy'][0]['qty'],
                        'Profit/Loss': pnl,
                        'PL%': pl_percent,
                        'Status': 'Open'
                    })

        return pd.DataFrame(closed_trades), pd.DataFrame(open_trades)
    except Exception as e:
        print(f"An error occurred in profit calculation: {e}")
        return pd.DataFrame(), pd.DataFrame()

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
            return pd.DataFrame(), pd.DataFrame()

        # Retrieve positions using the Kite Connect API
        positions_response = broker.kite.positions().get('net', [])
        positions_df = get_positionsinfo(positions_response)

        if positions_df.empty:  # Check if positions_df is empty
            print("No positions available.")
            return pd.DataFrame(), pd.DataFrame()

        # Calculate profit or loss and split into closed and open trades
        closed_df, open_df = calculate_profit(orders_df, positions_df)

        # Print the results
        print("Closed Trades:")
        print(closed_df.to_string(index=False))
        print("\nOpen Trades:")
        print(open_df.to_string(index=False))

        # Optionally, save results to CSV files
        closed_df.to_csv('closed_trades.csv', index=False)
        open_df.to_csv('open_trades.csv', index=False)

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        logger.error(f"{str(e)} unable to process orders")
        return pd.DataFrame(), pd.DataFrame()

# Call the process_data function
process_data()


