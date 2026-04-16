import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://localhost:5001/v1/api"
ACCOUNT_ID = "DUM174280"

def tickle():
    requests.post(f"{BASE_URL}/tickle", verify=False)

def select_account():
    requests.post(f"{BASE_URL}/iserver/account", json={"acctId": ACCOUNT_ID}, verify=False)

def get_account():
    resp = requests.get(f"{BASE_URL}/portfolio/{ACCOUNT_ID}/summary", verify=False)
    return resp.json()

def get_portfolio_value():
    data = get_account()
    return float(data["netliquidation"]["amount"])

def get_conid(symbol):
    resp = requests.get(f"{BASE_URL}/trsrv/stocks", params={"symbols": symbol}, verify=False)
    data = resp.json()
    for item in data.get(symbol, []):
        for contract in item.get("contracts", []):
            if contract.get("exchange") in ("NASDAQ", "NYSE"):
                return contract["conid"]
    return None

def place_order(symbol, qty, side):
    conid = get_conid(symbol)
    if not conid:
        return {"error": f"Could not find conid for {symbol}"}
    order = {
        "orders": [{
            "conid": conid,
            "orderType": "MKT",
            "side": side.upper(),
            "quantity": qty,
            "tif": "DAY"
        }]
    }
    resp = requests.post(
        f"{BASE_URL}/iserver/account/{ACCOUNT_ID}/orders",
        json=order,
        verify=False
    )
    result = resp.json()
    for _ in range(5):
        if not isinstance(result, list):
            break
        if result and "order_id" in result[0]:
            break
        reply_id = result[0].get("id") if result else None
        if not reply_id:
            break
        confirm = requests.post(
            f"{BASE_URL}/iserver/reply/{reply_id}",
            json={"confirmed": True},
            verify=False
        )
        result = confirm.json()
    return result

if __name__ == "__main__":
    tickle()
    select_account()
    print("Portfolio value:", get_portfolio_value())
    print("AAPL conid:", get_conid("AAPL"))
