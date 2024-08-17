import pandas as pd

def create_dummy_df():
    # Define the columns and their data types
    columns = {
        'tradingsymbol': 'string',
        'exchange': 'string',
        'instrument_token': 'uint32',
        'product': 'string',
        'quantity': 'int64',
        'overnight_quantity': 'int64',
        'multiplier': 'int64',
        'average_price': 'float64',
        'close_price': 'float64',
        'last_price': 'float64',
        'value': 'float64',
        'pnl': 'float64',
        'm2m': 'float64',
        'unrealised': 'float64',
        'realised': 'float64',
        'buy_quantity': 'int64',
        'buy_price': 'float64',
        'buy_value': 'float64',
        'buy_m2m': 'float64',
        'day_buy_quantity': 'int64',
        'day_buy_price': 'float64',
        'day_buy_value': 'float64',
        'sell_quantity': 'int64',
        'sell_price': 'float64',
        'sell_value': 'float64',
        'sell_m2m': 'float64',
        'day_sell_quantity': 'int64',
        'day_sell_price': 'float64',
        'day_sell_value': 'float64'
    }

    # Create a dummy DataFrame with the columns and initialize the first row with zeroes or empty strings
    dummy_data = {col: [0] if dtype.startswith('int') or dtype.startswith('float') else [''] for col, dtype in columns.items()}
    dummy_df = pd.DataFrame(dummy_data)

    # Set the DataFrame typesfor col, dtype in columns.items():
        dummy_df[col] = dummy_df[col].astype(dtype)

    return dummy_df


