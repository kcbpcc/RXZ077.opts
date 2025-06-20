import os
import sys
import time
import subprocess
import importlib
import warnings
from rich.console import Console
from clorpxy import RED, GREEN, SILVER, UNDERLINE, RESET, BRIGHT_YELLOW, BRIGHT_RED, BRIGHT_GREEN, BOLD, GREY

console = Console()

def get_user_input(prompt, default='s'):
    user_input = input(prompt).strip()
    if user_input == '':
        return default
    return user_input

def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            print(f"Import error: {e}")
        except Exception as ex:
            print(f"An error occurred: {ex}")
    return wrapper

# Prompt for user input
run_type = get_user_input("How do you want to run 🗺️⁀જ✈︎ short/long:")

# Run cpritepxy.pyc
subprocess.run(['python3', 'cpritepxy.pyc'])
subprocess.run(['python3', 'worldpxy.pyc'])

while True:
    @handle_exceptions
    def reload_sleeppxy():
        try:
            import sleeppxy
            importlib.reload(sleeppxy)
            from sleeppxy import progress_bar
            return progress_bar
        except ModuleNotFoundError as e:
            print(f"Module 'sleeppxy' not found: {e}")
        except AttributeError as e:
            print(f"Function 'progress_bar' not found in 'sleeppxy': {e}")
            
    @handle_exceptions
    def reload_cyclepxy():
        try:
            import cyclepxy
            importlib.reload(cyclepxy)
            from cyclepxy import cycle
            return cycle
        except ModuleNotFoundError as e:
            print(f"Module 'cyclepxy' not found: {e}")
        except AttributeError as e:
            print(f"Function 'cycle' not found in 'cyclepxy': {e}")

    # Reload modules and functions
    progress_bar = reload_sleeppxy()
    cycle = reload_cyclepxy()

    @handle_exceptions
    def reload_mktpxy():
        importlib.reload(sys.modules['mktpxy'])
        from mktpxy import get_market_check  # Re-import the function
        return get_market_check(symbol) 

    @handle_exceptions
    def cycle_handler():
        from cyclepxy import cycle
        importlib.reload(sys.modules['cyclepxy'])  # Reload module after import
        return cycle()

    @handle_exceptions
    def peak_time_handler():
        from utcpxy import peak_time
        importlib.reload(sys.modules['utcpxy'])  # Reload module after import
        return peak_time()

    @handle_exceptions
    def predict_market_sentiment_handler():
        from predictpxy import predict_market_sentiment
        importlib.reload(sys.modules['predictpxy'])  # Reload module after import
        return predict_market_sentiment()

    @handle_exceptions
    def get_market_check_handler(symbol):
        from mktpxy import get_market_check
        importlib.reload(sys.modules['mktpxy'])  # Reload module after import
        return get_market_check(symbol)

    @handle_exceptions
    def get_nse_action_handler():
        from nftpxy import get_nse_action
        importlib.reload(sys.modules['nftpxy'])  # Reload module after import
        return get_nse_action()

    @handle_exceptions
    def get_bnk_action_handler():
        from bftpxy import get_bnk_action
        importlib.reload(sys.modules['bftpxy'])  # Reload module after import
        return get_bnk_action()

    @handle_exceptions
    def calculate_macd_signal_handler(symbol):
        from macdpxy import calculate_macd_signal
        return calculate_macd_signal(symbol)

    @handle_exceptions
    def check_index_status_handler(symbol):
        from smapxy import check_index_status
        return check_index_status(symbol)
    try:
        peak = peak_time_handler()
        if os.name == 'nt':
            os.system('cls')
        else:
            if peak == 'NONPEAK':
                os.system('clear -x')
    except Exception as e:
        print(f"Error handling peak time: {e}")
    try:
        mktpredict = predict_market_sentiment_handler()
    except Exception as e:
        print(f"Error handling market sentiment prediction: {e}")
        mktpredict = None
    try:
        onemincandlesequance, mktpxy = get_market_check_handler('^NSEI')
    except Exception as e:
        print(f"Error handling market check for ^NSEI: {e}")
        onemincandlesequance, mktpxy = "none", "none"
    try:
        bnkonemincandlesequance, bmktpxy = get_market_check_handler('^NSEBANK')
    except Exception as e:
        print(f"Error handling market check for ^NSEBANK: {e}")
        bnkonemincandlesequance, bmktpxy = "none", "none"
    try:
        ha_nse_action, nse_power, Day_Change, Open_Change = get_nse_action_handler()
    except Exception as e:
        print(f"Error handling NSE action: {e}")
        ha_nse_action, nse_power, Day_Change, Open_Change = 0.5, 0.5, 0.5, 0.5
    try:
        ha_bnk_action, bnk_power, bDay_Change, bOpen_Change = get_bnk_action_handler()
    except Exception as e:
        print(f"Error handling NSE action: {e}")
        ha_bnk_action, bnk_power, bDay_Change, bOpen_Change = 0.5, 0.5, 0.5, 0.5
    try:
        macd = calculate_macd_signal_handler("^NSEI")
    except Exception as e:
        print(f"Error handling MACD signal calculation: {e}")
        macd = None
    try:
        nsma = check_index_status_handler('^NSEI')
        bsma = check_index_status_handler('^NSEBANK')
    except Exception as e:
        print(f"Error handling index status: {e}")
        nsma, bsma = None, None
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################     ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    print((BRIGHT_GREEN + "🏛 PXY® PreciseXceleratedYield Pvt Ltd™ 🏛".center(42) if ha_nse_action == 'Bullish' else BRIGHT_RED + "🏛 PXY® PreciseXceleratedYield Pvt Ltd™ 🏛".center(42) if ha_nse_action == 'Bearish' else "🏛 PXY® PreciseXceleratedYield Pvt Ltd™ 🏛".center(42)) + RESET)    
    print("*" * 42)
    subprocess.run(['python3', 'tistpxy.pyc']) 
    subprocess.run(['python3', 'cntrloptpxy.pyc'] if run_type == 'l' else ['python3', 'cntrloptpxy.pyc', '-short'])
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################     ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    if bmktpxy in ['Buy', 'Sell']:
        importlib.reload(sys.modules.get('mktpxy', None))
        print("━" * 42)
        #subprocess.run(['python3', 'buyboptpxy.pyc']) if peak != 'PEAKSTART' else None
    else:
        print("━" * 42)
        print(f"{GREY}🚫 Not Buying BANKS opts, as it is {(GREEN if bmktpxy == 'Bull' else RED)}{bmktpxy}{GREY} ✋{RESET}")
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################     ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    if mktpxy in ['Buy', 'Sell']:
        importlib.reload(sys.modules.get('mktpxy', None))
        print("━" * 42)
        #subprocess.run(['python3', 'buynoptpxy.pyc']) if peak != 'PEAKSTART' else None
    else:
        print("━" * 42)
        print(f"{GREY}🚫 Not Buying NIFTY opts, as it is {(GREEN if mktpxy == 'Bull' else RED)}{mktpxy}{GREY} ✋{RESET}")
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################     ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    subprocess.run(['python3', 'worldpxy.pyc']) if run_type == 'l' else None
    #subprocess.run(['python3', 'mngoptpxy.pyc']) #if (bnk_power > 0.85 or bnk_power < 0.15 or nse_power > 0.85 or nse_power < 0.15) else None
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################     ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    if run_type == 'l':
        subprocess.run(['python3', 'niftychartpxy.pyc'])
        subprocess.run(['python3', 'daypxy.pyc'])
        subprocess.run(['python3', 'cndlpxy.pyc'])
        if 'nsma' in locals(): 
            color = BRIGHT_GREEN if nsma == "up" else BRIGHT_RED if nsma == "down" else BRIGHT_YELLOW
            print(color + "ﮩ٨ﮩ٨ـﮩ٨ﮩ٨ـﮩ٨ـﮩﮩ٨ﮩ٨NIFTY٨ﮩ٨ـﮩ٨ـﮩﮩ٨ﮩ٨ـﮩ٨ﮩ٨ـﮩ" + RESET)
        subprocess.run(['python3', 'bniftychartpxy.pyc'])
        subprocess.run(['python3', 'bdaypxy.pyc'])
        subprocess.run(['python3', 'bcndlpxy.pyc'])
        if 'bsma' in locals():
            color = BRIGHT_GREEN if bsma == "up" else BRIGHT_RED if bsma == "down" else BRIGHT_YELLOW
            print(color + "ﮩ٨ﮩ٨ـﮩ٨ﮩ٨ـﮩ٨ـﮩﮩ٨BANKNIFTY٨ﮩ٨ـﮩ٨ـﮩﮩ٨ﮩ٨ـﮩ٨ﮩ٨" + RESET)
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################    ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
    #subprocess.run(['python3', 'misordpxy.pyc'])
    subprocess.run(['python3', 'plpxy.pyc']) if peak == "PEAKEND" else None
    print("━" * 42)
    if run_type == 's':
        subprocess.run(['python3', 'cntrloptprntpxy.pyc', 's'])
    elif run_type == 'l':
        subprocess.run(['python3', 'cntrloptprntpxy.pyc', 'l'])
    print("━" * 42)
    subprocess.run(['python3', 'selfpxy.pyc'])
    progress_bar(cycle, (mktpxy if peak in ["PEAKSART", "PEAKEND", "NONPEAK"] else None))
############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################    ############################################"PXY® PreciseXceleratedYield Pvt Ltd™############################################ 
