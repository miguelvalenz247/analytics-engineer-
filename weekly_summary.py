from ibkr_broker import tickle, select_account, get_portfolio_value
from position_tracker import load_positions
from sms_bot import send_sms
from datetime import datetime
STARTING_VALUE = 25800
def run():
    tickle()
    select_account()
    pv = get_portfolio_value()
    ret = pv - STARTING_VALUE
    pct = (ret / STARTING_VALUE) * 100
    pos = load_positions()
    lines = [
        "Good morning Miguel! Weekly Summary",
        "Date: " + datetime.now().strftime("%A %b %d"),
        "---",
        "Portfolio: $" + f"{pv:,.0f}",
        "Return: $" + f"{ret:+,.0f} ({pct:+.1f}%)",
        "Positions: " + str(len(pos)),
        "---", "Holdings:"
    ]
    for sym, data in pos.items():
        lines.append("  " + sym + ": " + str(data["shares"]) + " shares")
    lines.append("---")
    lines.append("No action needed. Reply REVIEW for history.")
    send_sms(chr(10).join(lines))
    print("Weekly summary sent.")
if __name__ == "__main__":
    run()