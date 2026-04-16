from dotenv import load_dotenv
from strategy import get_signal
from risk import check_signal
from alpaca_broker import place_order, get_account

load_dotenv()

TICKERS = ["AAPL", "NVDA", "JPM"]

def run_cycle():
    print("=== Starting trading cycle ===\n")

    account = get_account()
    portfolio_value = float(account.portfolio_value)
    print(f"Portfolio value: ${portfolio_value:,.2f}\n")

    for ticker in TICKERS:
        print(f"[{ticker}]")

        signal = get_signal(ticker)
        action = signal['action']
        price  = signal['price']
        ma10   = signal['ma_10']
        ma30   = signal['ma_30']
        print(f"  Price: ${price:.2f} | MA10: {ma10:.2f} | MA30: {ma30:.2f} | Signal: {action}")

        if action == "HOLD":
            print("  → Skipping (HOLD)\n")
            continue

        approved, result = check_signal(signal, portfolio_value)
        if not approved:
            print(f"  → Blocked by risk manager: {result}\n")
            continue

        shares = result
        side = "buy" if action == "BUY" else "sell"

        print(f"  → Placing {side.upper()} order: {shares} share(s)...")
        order = place_order(ticker, shares, side)
        print(f"  → Order ID: {order.id} | Status: {order.status}\n")

    print("=== Cycle complete ===")

if __name__ == "__main__":
    run_cycle()
