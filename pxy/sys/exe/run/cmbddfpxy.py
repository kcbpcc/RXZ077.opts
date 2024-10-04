import sys
import traceback
import pandas as pd
from login_get_kite import get_kite, remove_token
from cnstpxy import dir_path
from toolkit.logger import Logger

logger = Logger(30, dir_path + "main.log")

def get_positionsinfo(resp_list):
    """Fetch positions data and return as DataFrame."""
    try:
        if resp_list:  # Check if the response list is not empty
            return pd.DataFrame(resp_list)
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no data
    except Exception as e:
        print(f"An error occurred in positions: {e}")
        return pd.DataFrame()

def sell_and_book_profit(df, sell_price, sell_quantity):
    """Calculate and book realized profit on selling, and adjust position."""
    try:
        # Calculate realized profit for the sold quantity
        realized_profit = (sell_price - df['average_price']) * sell_quantity
        df['booked'] = df.get('booked', 0) + realized_profit  # Add to booked profit
        
        # Reduce position quantity
        df['quantity'] -= sell_quantity
        
        print(f"Booked profit from selling {sell_quantity} units: {realized_profit}")
        return df
    except Exception as e:
        print(f"An error occurred during sell process: {e}")
        traceback.print_exc()

def reset_pnl_on_new_buy(df, new_buy_quantity, new_buy_price):
    """Recalculate average price and reset PnL after new buy."""
    try:
        total_quantity = df['quantity'] + new_buy_quantity
        df['average_price'] = (
            (df['quantity'] * df['average_price'] + new_buy_quantity * new_buy_price) / total_quantity
        ).round(2)  # Recalculate average price
        
        # Update position with new quantity
        df['quantity'] = total_quantity
        df['pnl'] = 0  # Reset unrealized PnL
        
        print(f"New average price: {df['average_price']}, total quantity: {df['quantity']}")
        return df
    except Exception as e:
        print(f"An error occurred during buy process: {e}")
        traceback.print_exc()

def process_data():
    """Main logic to process positions, book profit on sell, and reset PnL on buy."""
    try:
        positions_response = broker.kite.positions().get('net', [])
        positions_df = get_positionsinfo(positions_response)
        if positions_df.empty:
            return pd.DataFrame()

        positions_df.to_csv('pxypositions.csv', index=False)

        # Adding necessary columns
        positions_df['key'] = positions_df['exchange'] + ":" + positions_df['tradingsymbol']
        positions_df['ltp'] = positions_df['last_price']
        positions_df['close'] = positions_df['close_price']
        positions_df['Invested'] = (positions_df['quantity'] * positions_df['average_price']).round(0).astype(int)
        positions_df['value'] = positions_df['quantity'] * positions_df['ltp']

        # Simulate a sale and profit booking
        positions_df = sell_and_book_profit(positions_df, sell_price=150, sell_quantity=100)

        # Simulate a new buy and reset the PnL
        positions_df = reset_pnl_on_new_buy(positions_df, new_buy_quantity=50, new_buy_price=105)

        positions_df['PL%'] = round((positions_df['pnl'] / positions_df['Invested'] * 100), 2)
        positions_df['Yvalue'] = positions_df['quantity'] * positions_df['close']
        positions_df['dPnL'] = positions_df['value'] - positions_df['Yvalue']
        
        positions_df.to_csv('pxycombined.csv', index=False)
        return positions_df
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        sys.stdout = open('output.txt', 'w')
        broker = get_kite()
        process_data()
    except Exception as e:
        remove_token(dir_path)
        print(traceback.format_exc())
        logger.error(f"{str(e)} unable to get holdings")
        sys.exit(1)
    finally:
        if sys.stdout != sys.__stdout__:
            sys.stdout.close()
            sys.stdout = sys.__stdout__

