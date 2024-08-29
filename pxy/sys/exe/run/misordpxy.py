import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger

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
        trade_data = {}

        for index, row in orders_df.iterrows():
            symbol = row['tradingsymbol']
            qty = row['quantity']
            price = row['average_price']
            order_type = row['transaction_type']

            if symbol not in trade_data:
                trade_data[symbol] = {'buy': [], 'sell': []}

            trade_data[symbol][order_type.lower()].append({'price': price, 'qty': qty})

        closed_trades = []
        open_trades = []
        overnight_open_trades = []
        overnight_closed_trades = []

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
                if trades['buy']:
                    buy = trades['buy'][0]
                    profit_loss = f'₹{(ltp - buy["price"]) * buy["qty"]:.2f}' if ltp else '--'
                    if ltp:
                        overnight_open_trades.append({
                            'Symbol': symbol,
                            'Buy Price': buy['price'],
                            'Sell Price': '--',
                            'Quantity': buy['qty'],
                            'Profit/Loss': profit_loss,
                            'PL%': '--',
                            'Status': 'Open'
                        })
                    else:
                        overnight_closed_trades.append({
                            'Symbol': symbol,
                            'Buy Price': buy['price'],
                            'Sell Price': '--',
                            'Quantity': buy['qty'],
                            'Profit/Loss': '--',
                            'PL%': '--',
                            'Status': 'Overnight'
                        })

        closed_df = pd.DataFrame(closed_trades, columns=['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%', 'Status'])
        open_df = pd.DataFrame(open_trades, columns=['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%', 'Status'])
        overnight_open_df = pd.DataFrame(overnight_open_trades, columns=['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%', 'Status'])
        overnight_closed_df = pd.DataFrame(overnight_closed_trades, columns=['Symbol', 'Buy Price', 'Sell Price', 'Quantity', 'Profit/Loss', 'PL%', 'Status'])

        return closed_df, open_df, overnight_open_df, overnight_closed_df

    except Exception as e:
        print(f"An error occurred in profit calculation: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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

        # Convert responses to DataFrames
        orders_df = pd.DataFrame(orders_response)
        positions_df = get_positionsinfo(positions_response)

        # If orders_df is empty, initialize it and add overnight positions
        if orders_df.empty:
            orders_df = pd.DataFrame(columns=['tradingsymbol', 'quantity', 'average_price', 'transaction_type'])

        # Update average_price in orders_df with values from positions_df
        for index, row in positions_df.iterrows():
            symbol = row['tradingsymbol']
            avg_price = row['average_price'] if 'average_price' in row and row['average_price'] > 0 else 0
            if symbol in orders_df['tradingsymbol'].values:
                orders_df.loc[orders_df['tradingsymbol'] == symbol, 'average_price'] = avg_price

        # Add overnight positions to orders_df
        overnight_positions_df = pd.DataFrame(columns=['tradingsymbol', 'quantity', 'average_price', 'transaction_type'])

        for index, row in positions_df.iterrows():
            symbol = row['tradingsymbol']
            qty = row['overnight_quantity']
            if qty > 0:
                avg_price = row['average_price'] if 'average_price' in row and row['average_price'] > 0 else 0
                if symbol not in orders_df['tradingsymbol'].values:
                    overnight_positions_df = pd.concat([overnight_positions_df, pd.DataFrame([{
                        'tradingsymbol': symbol,
                        'quantity': qty,
                        'average_price': avg_price,
                        'transaction_type': 'BUY'
                    }])], ignore_index=True)
                else:
                    # Update existing entry if already present
                    orders_df.loc[orders_df['tradingsymbol'] == symbol, 'quantity'] += qty

        # Combine existing orders_df with new overnight positions
        orders_df = pd.concat([orders_df, overnight_positions_df], ignore_index=True)

        # Print DataFrames for debugging
        print("Orders DataFrame:")
        print(orders_df.head())
        print("\nPositions DataFrame:")
        print(positions_df.head())

        # Calculate profit and create DataFrames
        closed_df, open_df, overnight_open_df, overnight_closed_df = calculate_profit(orders_df, positions_df)

        # Print DataFrames
        print("Closed Orders:")
        print(closed_df)
        print("\nOpen Orders:")
        print(open_df)
        print("\nOvernight Open Positions:")
        print(overnight_open_df)
        print("\nOvernight Closed Positions:")
        print(overnight_closed_df)

        return closed_df, open_df, overnight_open_df, overnight_closed_df

    except Exception as e:
        print(f"An error occurred in processing data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Run the data processing function
process_data()

