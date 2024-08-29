import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger
import os
import logging

# Setup logging
logger = Logger(30, dir_path + "main.log")

def get_positionsinfo(resp_list):
    try:
        if isinstance(resp_list, list):  # Check if the response is a list
            df = pd.DataFrame(resp_list)
            df['source'] = 'positions'
        else:
            df = pd.DataFrame()  # Return an empty DataFrame if the response is not a list
        return df
    except Exception as e:
        print(f"An error occurred in positions: {e}")
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

        # Create lists for different trade types
        closed_trades = []
        open_trades = []
        overnight_trades = []

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
                        'Quantity': buy['qty'],
                        'Profit/Loss': f'₹{pnl:.2f}',
                        'PL%': f'{pl_percent:.2f}%',
                        'Status': 'Closed'
                    })
            else:
                # Create dummy orders for overnight positions
                if trades['buy']:
                    buy = trades['buy'][0]
                    overnight_trades.append({
                        'Symbol': symbol,
                        'Buy Price': buy['price'],
                        'Sell Price': '--',
                        'Quantity': buy['qty'],
                        'Profit/Loss': f'₹{(ltp - buy['price']) * buy['qty']:.2f}' if ltp else '--',
                        'PL%': '--',
                        'Status': 'Open'
                    })

        # Create DataFrames for different trade types
        closed_df = pd.DataFrame(closed_trades)
        open_df = pd.DataFrame(open_trades)
        overnight_df = pd.DataFrame(overnight_trades)

        return closed_df[['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%','Status']], \
               open_df[['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%','Status']], \
               overnight_df[['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%','Status']]

    except Exception as e:
        print(f"An error occurred in profit calculation: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def process_data():
    try:
        # Initialize Kite connection
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

        # Retrieve orders and positions
        orders_response = broker.kite.orders()
        positions_response = broker.kite.positions().get('net', [])

        # Check the type of response
        if isinstance(orders_response, dict):
            orders_response = orders_response.get('orders', [])
        if isinstance(positions_response, dict):
            positions_response = positions_response.get('net', [])

        # Convert responses to DataFrames
        orders_df = pd.DataFrame(orders_response)
        positions_df = get_positionsinfo(positions_response)

        # Print DataFrames for debugging
        print("Orders DataFrame:")
        print(orders_df.head())
        print("\nPositions DataFrame:")
        print(positions_df.head())

        # Calculate profit and create DataFrames
        closed_df, open_df, overnight_df = calculate_profit(orders_df, positions_df)

        # Print DataFrames
        print("Closed Orders:")
        print(closed_df)
        print("\nOpen Orders:")
        print(open_df)
        print("\nOvernight Positions:")
        print(overnight_df)

        return closed_df, open_df, overnight_df

    except Exception as e:
        print(f"An error occurred in processing data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Run the data processing function
process_data()
