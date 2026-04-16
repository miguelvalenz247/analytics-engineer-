import requests
import json

BASE_URL = "https://localhost:5001/v1/api"
session = requests.Session()
session.verify = False

def get_auth_status():
    response = session.get(f"{BASE_URL}/iserver/auth/status")
    return response.json()

def get_accounts():
    response = session.get(f"{BASE_URL}/portfolio/accounts")
    return response.json()

if __name__ == "__main__":
    print(json.dumps(get_auth_status(), indent=2))
    print(json.dumps(get_accounts(), indent=2))

def place_order(conid, side, quantity):
    url = f'{BASE_URL}/iserver/account/DUM174280/orders'
    order = {'orders': [{'conid': conid, 'orderType': 'MKT', 'side': side.upper(), 'quantity': quantity, 'tif': 'DAY'}]}
    response = session.post(url, json=order)
    return response.json()
