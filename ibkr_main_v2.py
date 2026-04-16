from scanner import get_top_picks
from ibkr_broker import place_order, get_portfolio_value, get_conid
import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://localhost:5001/v1/api"
ACCOUNT_ID = "DUM174280"
TOP_N = 10

def get_current_positions():
    resp = requests.get(f"{BASE_URL}/portfolio/{ACCOUNT_ID}/positions/0", verify=False)
    data = resp.json()
    positions = {}
    for p in data:
        sym = p.get("ticker")
        qty = p.get("position", 0)
        if sym and qty != 0:
            positions[sym] = qty
    return positions

def run_cycle():
    print("=== IBKR Momentum Portfolio Cycle ===")

    portfolio_value = get_portfolio_value()
    print(f"Portfolio value: ${portfolio_value:,.2f}")

    # Get top picks
    print("Scanning for top picks...")
    picks = get_top_picks(TOP_N)
    target_symbols = [p["symbol"] for p in picks]
    print(f"Top {TOP_N} picks: {target_symbols}")

    # Get current positions
    current = get_current_positions()
    print(f"Current positions: {list(current.keys())}")

    # Sell positions not in top picks
    for sym, qty in current.items():
        if sym not in target_symbols and qty > 0:
            print(f"Exiting {sym} ({qty} shares)...")
            result = place_order(sym, qty, "SELL")
            print(f"  -> {result}")

    # Buy top picks with equal weight
    alloc = portfolio_value / TOP_N
    for pick in picks:
        sym = pick["symbol"]
        price = pick["price"]
        shares = int(alloc / price)
        if shares < 1:
            print(f"Skipping {sym} — allocation too small")
            continue
        already_own = current.get(sym, 0)
        if already_own >= shares:
            print(f"Already holding {sym} ({already_own} shares), skipping")
            continue
        buy_qty = shares - already_own
        print(f"Buying {sym}: {buy_qty} share(s) @ ${price}")
        result = place_order(sym, buy_qty, "BUY")
        print(f"  -> {result}")

    print("=== Cycle complete ===")

if __name__ == "__main__":
    run_cycle()
