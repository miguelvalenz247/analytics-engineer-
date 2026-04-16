from ibkr_broker import place_order, tickle, select_account

PORTFOLIO = [
    ('NVDA',  54),
    ('MSFT',  16),
    ('AVGO',  13),
    ('AMD',   16),
    ('META',   8),
    ('AMZN',  17),
    ('GOOGL', 23),
    ('TSM',   17),
    ('ARM',   26),
    ('ORCL',  13),
]

def execute():
    print('=== Executing buy-and-hold portfolio ===')
    tickle()
    select_account()
    for symbol, shares in PORTFOLIO:
        print(f'Buying {symbol}: {shares} shares...')
        result = place_order(symbol, shares, 'BUY')
        print(f'  -> {result}')
    print('=== Done. Hold until year end. ===')

if __name__ == '__main__':
    execute()
