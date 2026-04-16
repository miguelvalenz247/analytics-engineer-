import yfinance as yf
from universe import get_sp500_tickers

def get_mean_reversion_picks(n=5):
    tickers = get_sp500_tickers()
    candidates = []
    for symbol in tickers:
        try:
            df = yf.download(symbol, period='3mo', interval='1d', auto_adjust=True, progress=False)
            if len(df) < 30:
                continue
            close = df['Close'].squeeze()
            ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else close.rolling(30).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            price = float(close.iloc[-1])
            drop_5d = (price - float(close.iloc[-5])) / float(close.iloc[-5])
            if ma20 > ma50 and -0.15 <= drop_5d <= -0.08:
                candidates.append({'symbol': symbol, 'price': round(price, 2), 'drop_5d': round(drop_5d * 100, 2)})
        except:
            continue
    candidates.sort(key=lambda x: x['drop_5d'])
    return candidates[:n]

if __name__ == '__main__':
    print('Scanning for mean reversion setups...')
    picks = get_mean_reversion_picks()
    print(picks if picks else 'No setups found today.')
