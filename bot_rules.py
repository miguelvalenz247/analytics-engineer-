APPROVED_TICKERS = ["NVDA","MSFT","AVGO","PLTR","META","AMZN","GOOG","TSM","MU","AMD","NFLX","TTD","LMT","AAPL","CRM"]
MAX_POSITION_SIZE = 2500
MAX_POSITIONS = 8
MAX_DAILY_TRADES = 3
MAX_PORTFOLIO_DEPLOYMENT = 0.80
MIN_STOCK_PRICE = 10.00
STOP_LOSS = -0.10
TAKE_PROFIT = 0.20
TRAILING_STOP = -0.07
MAX_HOLD_DAYS = 30
EARNINGS_BLACKOUT = []

import json, yfinance as yf
from datetime import datetime

def is_approved_ticker(s): return s in APPROVED_TICKERS
def is_weekend(): return datetime.now().weekday() >= 5

def is_blackout_time():
    now = datetime.now()
    if is_weekend(): return True
    open_end = now.replace(hour=10, minute=0, second=0)
    close_start = now.replace(hour=15, minute=30, second=0)
    return now < open_end or now > close_start

def check_vix():
    try:
        vix = yf.download("^VIX", period="1d", progress=False)
        val = float(vix["Close"].iloc[-1].squeeze())
        return val > 25
    except: return False

def get_trade_count():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open("/Users/miguelvalenzuela/ibkr_trading_bot/daily_trades.json") as f:
            return json.load(f).get(today, 0)
    except: return 0

def log_trade():
    today = datetime.now().strftime("%Y-%m-%d")
    path = "/Users/miguelvalenzuela/ibkr_trading_bot/daily_trades.json"
    try:
        with open(path) as f: data = json.load(f)
    except: data = {}
    data[today] = data.get(today, 0) + 1
    with open(path, "w") as f: json.dump(data, f)

def requires_approval(symbol, amount, action):
    reasons = []
    if amount > 1000: reasons.append("Order over $1000")
    if action == "SELL": reasons.append("Full position sell")
    if symbol in EARNINGS_BLACKOUT: reasons.append(f"{symbol} earnings this week")
    if get_trade_count() >= 2: reasons.append(f"Already {get_trade_count()} trades today")
    return reasons

def run_all_checks(symbol, amount, price, action):
    if not is_approved_ticker(symbol): return False, [f"{symbol} not approved"]
    if price < MIN_STOCK_PRICE: return False, ["Price too low"]
    if amount > MAX_POSITION_SIZE: return False, ["Amount exceeds max"]
    if get_trade_count() >= MAX_DAILY_TRADES: return False, ["Daily limit reached"]
    if is_blackout_time(): return False, ["Blackout period"]
    if symbol in EARNINGS_BLACKOUT: return False, [f"{symbol} earnings blackout"]
    if check_vix(): return False, ["VIX too high"]
    return True, requires_approval(symbol, amount, action)