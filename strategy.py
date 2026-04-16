import yfinance as yf
import pandas as pd

TICKERS = ['AAPL', 'NVDA', 'JPM']

def get_signal(symbol):
    df = yf.download(symbol, period='60d', interval='1d', auto_adjust=True, progress=False)
    df['ma_10'] = df['Close'].rolling(10).mean()
    df['ma_30'] = df['Close'].rolling(30).mean()
    latest = df.iloc[-1]
    price = float(latest['Close'].iloc[0])
    ma10 = float(latest['ma_10'].iloc[0])
    ma30 = float(latest['ma_30'].iloc[0])
    if ma10 > ma30:
        action = 'BUY'
    elif ma10 < ma30:
        action = 'SELL'
    else:
        action = 'HOLD'
    return {'symbol': symbol, 'price': price, 'ma_10': ma10, 'ma_30': ma30, 'action': action}

if __name__ == '__main__':
    for t in TICKERS:
        print(get_signal(t))
