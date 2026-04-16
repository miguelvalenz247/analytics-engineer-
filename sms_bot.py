import os, json
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv('/Users/miguelvalenzuela/ibkr_trading_bot/.env')

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_NUMBER = os.getenv('TWILIO_FROM')
MY_PHONE = os.getenv('MY_PHONE')
PENDING_FILE = '/Users/miguelvalenzuela/ibkr_trading_bot/pending_orders.json'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(message):
    client.messages.create(body=message, from_=FROM_NUMBER, to=MY_PHONE)
    print(f'SMS sent: {message[:60]}')

def save_pending(orders):
    with open(PENDING_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

def load_pending():
    try:
        with open(PENDING_FILE) as f:
            return json.load(f)
    except:
        return []

def clear_pending():
    save_pending([])
