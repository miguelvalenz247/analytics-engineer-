from scanner import get_top_picks
from mean_reversion import get_mean_reversion_picks
from ibkr_broker import place_order, tickle, select_account
from position_tracker import record_entry, load_positions, remove_position
import yfinance as yf
import requests, urllib3, json
from datetime import datetime
urllib3.disable_warnings()

BASE_URL = 'https://localhost:5001/v1/api'
ACCOUNT_ID = 'DUM174280'
MOMENTUM_ALLOC = 25000
REVERSION_ALLOC = 18000
MOMENTUM_N = 6
REVERSION_N = 4
MOMENTUM_TP = 0.20
REVERSION_TP = 0.12
STOP_LOSS = -0.15
REBALANCE_FILE = '/Users/miguelvalenzuela/ibkr_trading_bot/last_rebalance.json'

def get_current_price(symbol):
    df = yf.download(symbol, period='1d', interval='1m', auto_adjust=True, progress=False)
    return float(df['Close'].squeeze().iloc[-1])

def get_ibkr_positions():
    resp = requests.get(f'{BASE_URL}/portfolio/{ACCOUNT_ID}/positions/0', verify=False)
    positions = {}
    for p in resp.json():
        sym = p.get('ticker')
        qty = p.get('position', 0)
        if sym and qty != 0:
            positions[sym] = qty
    return positions

def should_rebalance():
    try:
        with open(REBALANCE_FILE) as f:
            last = datetime.fromisoformat(json.load(f)['last'])
        return (datetime.now() - last).days >= 7
    except:
        return True

def mark_rebalanced():
    with open(REBALANCE_FILE, 'w') as f:
        json.dump({'last': datetime.now().isoformat()}, f)

def manage_exits(engine):
    tp = MOMENTUM_TP if engine == 'momentum' else REVERSION_TP
    exited = []
    for symbol, data in list(load_positions().items()):
        if data.get('engine') != engine:
            continue
        try:
            price = get_current_price(symbol)
        except:
            continue
        pnl = (price - data['entry_price']) / data['entry_price']
        print(f'  [{symbol}] Entry: ${data["entry_price"]:.2f} Now: ${price:.2f} PnL: {pnl*100:.1f}%')
        if pnl >= tp:
            print(f'    -> TAKE PROFIT +{pnl*100:.1f}%')
            place_order(symbol, data['shares'], 'SELL')
            remove_position(symbol)
            exited.append((symbol, data['shares'] * price))
        elif pnl <= STOP_LOSS:
            print(f'    -> STOP LOSS {pnl*100:.1f}%')
            place_order(symbol, data['shares'], 'SELL')
            remove_position(symbol)
            exited.append((symbol, data['shares'] * price))
        else:
            print(f'    -> Holding')
    return exited

def run_momentum():
    print('\n--- MOMENTUM ENGINE ---')
    exited = manage_exits('momentum')
    held = [s for s, d in load_positions().items() if d.get('engine') == 'momentum']

    if exited:
        picks = get_top_picks(MOMENTUM_N + len(exited))
        for sym, proceeds in exited:
            for pick in picks:
                if pick['symbol'] not in held:
                    shares = int(proceeds / pick['price'])
                    if shares < 1:
                        continue
                    print(f'Rotating into {pick["symbol"]}: {shares} shares')
                    place_order(pick['symbol'], shares, 'BUY')
                    record_entry(pick['symbol'], pick['price'], shares, 'momentum')
                    held.append(pick['symbol'])
                    break

    if not should_rebalance():
        print('Weekly rebalance not due yet.')
        return

    print('Weekly rebalance running...')
    picks = get_top_picks(MOMENTUM_N)
    target = [p['symbol'] for p in picks]
    ibkr = get_ibkr_positions()

    for sym in list(held):
        if sym not in target:
            qty = ibkr.get(sym, 0)
            if qty > 0:
                print(f'Rotating out: {sym}')
                place_order(sym, qty, 'SELL')
                remove_position(sym)

    alloc = MOMENTUM_ALLOC / MOMENTUM_N
    for pick in picks:
        sym = pick['symbol']
        shares = int(alloc / pick['price'])
        if shares < 1:
            continue
        already = ibkr.get(sym, 0)
        if already >= shares:
            print(f'Already holding {sym}')
            continue
        print(f'Buying {sym}: {shares - already} shares @ ${pick["price"]}')
        place_order(sym, shares - already, 'BUY')
        record_entry(sym, pick['price'], shares - already, 'momentum')

    mark_rebalanced()

def run_reversion():
    print('\n--- MEAN REVERSION ENGINE ---')
    manage_exits('reversion')
    picks = get_mean_reversion_picks(REVERSION_N)
    if not picks:
        print('No reversion setups today.')
        return
    held = [s for s, d in load_positions().items() if d.get('engine') == 'reversion']
    alloc = REVERSION_ALLOC / REVERSION_N
    for pick in picks:
        sym = pick['symbol']
        if sym in held:
            print(f'Already holding reversion: {sym}')
            continue
        shares = int(alloc / pick['price'])
        if shares < 1:
            continue
        print(f'Buying dip in {sym}: {shares} shares @ ${pick["price"]} ({pick["drop_5d"]}% drop)')
        place_order(sym, shares, 'BUY')
        record_entry(sym, pick['price'], shares, 'reversion')

def run_dual_engine():
    print('=== DUAL ENGINE CYCLE ===')
    print(f'Momentum: ${MOMENTUM_ALLOC:,} | Reversion: ${REVERSION_ALLOC:,}')
    tickle()
    select_account()
    run_momentum()
    run_reversion()
    print('\n=== Cycle complete ===')

if __name__ == '__main__':
    run_dual_engine()
