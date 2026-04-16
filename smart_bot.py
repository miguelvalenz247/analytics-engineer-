from scanner import get_top_picks
from ibkr_broker import tickle, select_account
from position_tracker import load_positions
from sms_bot import send_sms, save_pending
import requests, urllib3
urllib3.disable_warnings()

BASE_URL = 'https://localhost:5001/v1/api'
ACCOUNT_ID = 'DUM174280'
PORTFOLIO_SIZE = 43000
TOP_N = 8

def get_ibkr_positions():
    resp = requests.get(f'{BASE_URL}/portfolio/{ACCOUNT_ID}/positions/0', verify=False)
    positions = {}
    for p in resp.json():
        sym = p.get('ticker')
        qty = p.get('position', 0)
        if sym and qty != 0:
            positions[sym] = qty
    return positions

def run():
    print('=== Smart Bot Morning Scan ===')
    tickle()
    select_account()
    picks = get_top_picks(TOP_N)
    target = [p['symbol'] for p in picks]
    current = get_ibkr_positions()
    tracked = load_positions()
    proposed = []
    lines = ['Good morning Miguel! Trade proposals:']

    for sym, data in tracked.items():
        entry = data['entry_price']
        shares = data['shares']
        match = next((p for p in picks if p['symbol'] == sym), None)
        if match:
            pnl = (match['price'] - entry) / entry
            if pnl >= 0.20:
                proposed.append({'symbol': sym, 'qty': shares, 'side': 'SELL'})
                lines.append(f'SELL {sym}: +{pnl*100:.1f}% take profit')
            elif pnl <= -0.15:
                proposed.append({'symbol': sym, 'qty': shares, 'side': 'SELL'})
                lines.append(f'SELL {sym}: {pnl*100:.1f}% stop loss')
        if sym not in target:
            qty = current.get(sym, 0)
            if qty > 0:
                proposed.append({'symbol': sym, 'qty': qty, 'side': 'SELL'})
                lines.append(f'SELL {sym}: out of top {TOP_N}')

    alloc = PORTFOLIO_SIZE / TOP_N
    for pick in picks:
        sym = pick['symbol']
        price = pick['price']
        shares = int(alloc / price)
        already = current.get(sym, 0)
        if shares > 0 and already < shares:
            buy_qty = shares - already
            proposed.append({'symbol': sym, 'qty': buy_qty, 'side': 'BUY'})
            lines.append(f'BUY {sym}: {buy_qty} shares @ ${price}')

    if not proposed:
        send_sms('Good morning Miguel! No trades today. Portfolio looks good.')
        return

    save_pending(proposed)
    lines.append('')
    lines.append('Reply YES to execute or NO to skip.')
    send_sms('\n'.join(lines))
    print('SMS sent.')

if __name__ == '__main__':
    run()
