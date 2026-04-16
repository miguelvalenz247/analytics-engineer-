def get_sp500_tickers():
    return [
        "NVDA","MSFT","AAPL","AMZN","META","GOOGL","TSLA","AVGO","JPM","LLY",
        "V","UNH","XOM","MA","JNJ","PG","HD","COST","ABBV","MRK",
        "NFLX","CRM","BAC","CVX","AMD","PEP","KO","TMO","ACN","MCD",
        "WMT","CSCO","ABT","DHR","NKE","TXN","NEE","ORCL","PM","UPS",
        "MS","GS","BLK","SCHW","AXP","SPGI","RTX","CAT","DE","HON"
    ]

if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print(f"Universe size: {len(tickers)}")
    print("Tickers:", tickers)
