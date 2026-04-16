import yfinance as yf
import pandas as pd
from universe import get_sp500_tickers

def score_momentum(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True, progress=False)
        if df is None or len(df) < 30:
            return None
        close = df["Close"].squeeze()
        roc20 = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma30 = close.rolling(30).mean().iloc[-1]
        trend = 1 if ma10 > ma30 else -1
        score = roc20 * trend
        return {"symbol": ticker, "score": round(float(score), 4), "price": round(float(close.iloc[-1]), 2)}
    except Exception as e:
        return None

def get_top_picks(n=10):
    tickers = get_sp500_tickers()
    results = []
    for t in tickers:
        s = score_momentum(t)
        if s:
            results.append(s)
    df = pd.DataFrame(results).sort_values("score", ascending=False)
    return df.head(n).to_dict(orient="records")

if __name__ == "__main__":
    print("Scanning universe...")
    picks = get_top_picks(10)
    for p in picks:
        print(p)
