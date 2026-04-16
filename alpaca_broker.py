import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL")

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def get_account():
    return api.get_account()

def place_order(symbol, qty, side):
    return api.submit_order(symbol=symbol, qty=qty, side=side, type='market', time_in_force='day')

if __name__ == '__main__':
    account = get_account()
    print('Cash:', account.cash)
    print('Portfolio value:', account.portfolio_value)
