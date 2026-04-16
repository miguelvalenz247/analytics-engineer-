from strategy import get_signal
from risk import check_signal
from ibkr_broker import place_order, get_portfolio_value

TICKERS = ["AAPL", "NVDA", "JPM"]

def run_cycle():
    print("=== Starting IBKR trading cycle ===")

    portfolio_value = get_portfolio_value()
    print(f"Portfolio value: ${portfolio_value:,.2f}")

    for ticker in TICKERS:
        print(f"[{ticker}]")
        signal = get_signal(ticker)
        action = signal["action"]
        price  = signal["price"]
        ma10   = signal["ma_10"]
        ma30   = signal["ma_30"]
        print(f"  Price: ${price:.2f} | MA10: {ma10:.2f} | MA30: {ma30:.2f} | Signal: {action}")
        if action == "HOLD":
            print("  -> Skipping (HOLD)")
            continue
        approved, result = check_signal(signal, portfolio_value)
        if not approved:
            print(f"  -> Blocked by risk manager: {result}")
            continue
        shares = result
        side = "BUY" if action == "BUY" else "SELL"
        print(f"  -> Placing {side} order: {shares} share(s)...")
        order = place_order(ticker, shares, side)
        print(f"  -> Response: {order}")

    print("=== Cycle complete ===")

if __name__ == "__main__":
    run_cycle()
