import requests
import json
from broker import session, BASE_URL

def search_contract(symbol):
    response = session.get(f"{BASE_URL}/iserver/secdef/search?symbol={symbol}")
    return response.json()

def get_price(conid):
    response = session.get(f"{BASE_URL}/iserver/marketdata/snapshot?conids={conid}&fields=31,84,86")
    return response.json()

if __name__ == "__main__":
    result = search_contract("AAPL")
    print(json.dumps(result, indent=2))
