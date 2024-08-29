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
        if resp_list:  # Check if the response list is not empty
            df = pd.DataFrame(resp_list)
            df['source'] = 'positions'
        else:
            df = pd.DataFrame()  # Return an empty DataFrame if no data
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
        overnight_trades = []
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
                # Create dummy orders for overnight positions
                if trades['buy']:
                    buy = trades['buy'][0]
                    overnight_trades.append({
                        'Symbol': symbol,
                        'Buy Price': buy['price'],
                        'Sell Price': None,
                        'LTP': ltp,
                        'Quantity': buy['qty'],
                        'Profit/Loss': (ltp - buy['price']) * buy['qty'] if ltp else None,
                        'PL%': ((ltp - buy['price']) / buy['price']) * 100 if ltp else None,
                        'Status': 'Overnight'
                    })

        # Adding dummy trades to positions_df for further calculations
        overnight_df = pd.DataFrame(overnight_trades)
        all_trades_df = pd.concat([orders_df, overnight_df], ignore_index=True)

        # Process open trades again to separate them from the dummy overnight trades
        for symbol, trades in trade_data.items():
            ltp = positions_df.loc[positions_df['tradingsymbol'] == symbol, 'last_price'].values[0] if not positions_df.empty else None

            if trades['buy'] and not trades['sell']:
                # If only buy order exists, calculate unrealized profit/loss
                buy = trades['buy'][0]
                pnl = (ltp - buy['price']) * buy['qty'] if ltp else None
                pl_percent = (pnl / (buy['price'] * buy['qty'])) * 100 if pnl else None
                open_trades.append({
                    'Symbol': symbol,
                    'Buy Price': buy['price'],
                    'Sell Price': None,
                    'LTP': ltp,
                    'Quantity': buy['qty'],
                    'Profit/Loss': pnl,
                    'PL%': pl_percent,
                    'Status': 'Open'
                })

        closed_df = pd.DataFrame(closed_trades)
        open_df = pd.DataFrame(open_trades)
        return closed_df, open_df, all_trades_df
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
        orders_response = broker.kite.orders().get('orders', [])
        orders_df = pd.DataFrame(orders_response)
        positions_response = broker.kite.positions().get('net', [])
        positions_df = get_positionsinfo(positions_response)

        # Calculate profit and create DataFrames
        closed_df, open_df, all_trades_df = calculate_profit(orders_df, positions_df)

        # Print DataFrames
        print("Closed Orders:")
        print(closed_df)
        print("\nOpen Orders:")
        print(open_df)
        print("\nAll Trades (Including Overnight):")
        print(all_trades_df)

        return closed_df, open_df, all_trades_df

    except Exception as e:
        print(f"An error occurred in processing data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Run the data processing function
process_data()

