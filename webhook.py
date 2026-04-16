from flask import Flask, request
from sms_bot import load_pending, clear_pending, send_sms
from ibkr_broker import place_order, tickle, select_account

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_reply():
    body = request.form.get('Body', '').strip().upper()
    print(f'Received SMS: {body}')
    pending = load_pending()
    if not pending:
        send_sms('No pending orders found.')
        return '', 204
    if body == 'YES':
        tickle()
        select_account()
        results = []
        for order in pending:
            result = place_order(order['symbol'], order['qty'], order['side'])
            results.append(f"{order['side']} {order['qty']} {order['symbol']}: done")
        clear_pending()
        send_sms('Orders executed:\n' + '\n'.join(results))
    elif body == 'NO':
        clear_pending()
        send_sms('Cancelled. No trades placed.')
    else:
        send_sms('Reply YES to execute or NO to cancel.')
    return '', 204

if __name__ == '__main__':
    app.run(port=5050, debug=False)
