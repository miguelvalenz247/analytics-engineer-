import json, os
TRACKER_FILE = '/Users/miguelvalenzuela/ibkr_trading_bot/positions.json'

def load_positions():
    if not os.path.exists(TRACKER_FILE):
        return {}
    with open(TRACKER_FILE) as f:
        return json.load(f)

def save_positions(p):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(p, f, indent=2)

def record_entry(symbol, entry_price, shares, engine='momentum'):
    p = load_positions()
    p[symbol] = {'entry_price': entry_price, 'shares': shares, 'engine': engine}
    save_positions(p)
    print(f'Recorded: {symbol} @ ${entry_price} x {shares} [{engine}]')

def remove_position(symbol):
    p = load_positions()
    if symbol in p:
        del p[symbol]
        save_positions(p)

def get_position(symbol):
    return load_positions().get(symbol)
