MAX_POSITION_PCT = 0.10
MAX_DAILY_LOSS_PCT = 0.02
ALLOWED_TICKERS = ['AAPL', 'NVDA', 'JPM']

def check_signal(signal, portfolio_value):
    if signal['symbol'] not in ALLOWED_TICKERS:
        return False, 'Ticker not in allowed list'
    if signal['action'] == 'HOLD':
        return False, 'Signal is HOLD'
    max_position = portfolio_value * MAX_POSITION_PCT
    shares = int(max_position / signal['price'])
    if shares < 1:
        return False, 'Position too small'
    return True, shares

if __name__ == '__main__':
    signal = {'symbol': 'AAPL', 'price': 266.90, 'action': 'BUY'}
    approved, result = check_signal(signal, 42000)
    print('Approved:', approved)
    print('Shares or reason:', result)
