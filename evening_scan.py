from scanner import get_top_picks
from ibkr_broker import tickle, select_account, get_portfolio_value
from position_tracker import load_positions
from sms_bot import send_sms, save_pending
import requests, urllib3, yfinance as yf
urllib3.disable_warnings()

BASE_URL = 'https://localhost:5001/v1/api'
ACCOUNT_ID = 'DUM174280'
PORTFOLIO_SIZE = 43000
TOP_N = 8

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

def run():
    print('=== Evening Portfolio Scan ===')
    tickle()
    select_account()

    portfolio_value = get_portfolio_value()
    picks = get_top_picks(TOP_N)
    target = [p['symbol'] for p in picks]
    current = get_ibkr_positions()
    tracked = load_positions()

    lines = [f'Evening Report - Portfolio: ${portfolio_value:,.0f}']
    lines.append('')
    lines.append('CURRENT POSITIONS:')

    proposed = []
    total_pnl = 0

    for sym, data in tracked.items():
        entry = data['entry_price']
        shares = data['shares']
        try:
            price = get_current_price(sym)
            pnl = (price - entry) / entry
            pnl_dollars = (price - entry) * shares
            total_pnl += pnl_dollars
            status = 'HOLD'
            if pnl >= 0.20:
                status = 'SELL - Take profit'
                proposed.append({'symbol': sym, 'qty': shares, 'side': 'SELL'})
            elif pnl <= -0.15:
                status = 'SELL - Stop loss'
                proposed.append({'symbol': sym, 'qty': shares, 'side': 'SELL'})
            elif sym not in target:
                status = 'SELL - Out of top picks'
                proposed.append({'symbol': sym, 'qty': shares, 'side': 'SELL'})
            lines.append(f'{sym}: ${price:.2f} | {pnl*100:+.1f}% | {status}')
        except:
            lines.append(f'{sym}: price unavailable')

    lines.append('')
    lines.append(f'Total PnL: ${total_pnl:+,.0f}')
    lines.append('')
    lines.append("TOMORROW'S BUYS:")

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
        lines.append('No changes needed.')
    else:
        lines.append('')
        lines.append('Reply YES to execute at open or NO to skip.')
        save_pending(proposed)

    send_sms('\n'.join(lines))
    print('Evening report sent.')

if __name__ == '__main__':
    run()
