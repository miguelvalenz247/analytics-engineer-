from flask import Flask
import json
from datetime import datetime

app = Flask(__name__)
BASE = '/Users/miguelvalenzuela/ibkr_trading_bot'

def load(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

@app.route('/')
def dashboard():
    rules = load(BASE + '/current_rules.json', {})
    comms = load(BASE + '/comms_log.json', [])
    history = load(BASE + '/rules_history.json', [])
    positions = load(BASE + '/positions.json', {})
    risk = rules.get('risk_level', 'medium')
    profile = rules.get('profile', 'normal')
    rcolors = {'low':'#00ff88','medium':'#ffaa00','high':'#ff4444','extreme':'#ff0000'}
    pcolors = {'aggressive':'#00ff88','normal':'#ffaa00','defensive':'#ff8800','paused':'#ff0000'}
    rc = rcolors.get(risk, '#ffaa00')
    pc = pcolors.get(profile, '#ffaa00')
    sl = str(round(rules.get('stop_loss',-0.10)*100,1))
    tp = str(round(rules.get('take_profit',0.20)*100,1))
    ts = str(round(rules.get('trailing_stop',-0.07)*100,1))
    dep = str(round(rules.get('max_portfolio_deployment',0.80)*100))
    tickers = ''.join(['<span style=background:#1a1a1a;color:#00ff88;padding:2px 8px;margin:2px;border-radius:4px;display:inline-block>' + t + '</span>' for t in rules.get('approved_tickers',[])])
    comms_html = ''.join(['<div style=font-size:11px;padding:4px 0;border-bottom:1px solid #1a1a1a;color:#888><span style=color:#00ff88>' + c.get('event','') + '</span> ' + c.get('message','') + ' <span style=color:#444>' + c.get('timestamp','')[:19] + '</span></div>' for c in reversed(comms[-10:])])
    hist_html = ''
    for h in reversed(history[-5:]):
        hist_html += '<div style=padding:8px 0;border-bottom:1px solid #1a1a1a>'
        hist_html += '<div style=color:#ffaa00;font-size:12px>' + h.get('reason','') + '</div>'
        hist_html += '<div style=color:#444;font-size:11px>' + h.get('timestamp','')[:19] + '</div>'
        for k,v in h.get('changes',{}).items():
            hist_html += '<div style=color:#ffaa00;font-size:11px;margin-left:8px>' + k + ': ' + str(v.get('from')) + ' to ' + str(v.get('to')) + '</div>'
        hist_html += '</div>'
    if not hist_html: hist_html = '<div style=color:#444;padding:12px>No rule changes yet</div>'
    now = datetime.now().strftime('%A %B %d %Y %I:%M %p')
    page = '<html><head><title>AI Bot Dashboard</title>'
    page += '<meta http-equiv=refresh content=30>'
    page += '<style>body{background:#0a0a0a;color:#fff;font-family:monospace;padding:20px} .card{background:#111;border:1px solid #1a1a1a;border-radius:8px;padding:16px;margin:8px 0} .row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1a1a1a;font-size:13px} h2{color:#666;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px} .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px} .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px}</style>'
    page += '</head><body>'
    page += '<h1 style=color:#00ff88;margin-bottom:4px>AI Trading Bot Dashboard</h1>'
    page += '<p style=color:#555>' + now + ' | Auto-refreshes every 30s</p>'
    page += '<div class=grid3 style=margin-top:12px>'
    page += '<div class=card><h2>Risk Level</h2><div style=font-size:28px;font-weight:bold;color:' + rc + '>' + risk.upper() + '</div><div style=color:#555;font-size:12px>' + rules.get('update_reason','No assessment') + '</div></div>'
    page += '<div class=card><h2>Profile</h2><div style=font-size:28px;font-weight:bold;color:' + pc + '>' + profile.upper() + '</div><div style=color:#555;font-size:12px>Updated: ' + rules.get('last_updated','Never')[:19] + '</div></div>'
    page += '<div class=card><h2>Positions</h2><div style=font-size:28px;font-weight:bold;color:#00ff88>' + str(len(positions)) + '</div><div style=color:#555;font-size:12px>Active holdings tracked</div></div>'
    page += '</div><div class=grid>'
    page += '<div class=card><h2>Trading Rules</h2>'
    page += '<div class=row><span>Max Position</span><span style=color:#00ff88>$' + str(rules.get('max_position_size',2500)) + '</span></div>'
    page += '<div class=row><span>Max Positions</span><span style=color:#00ff88>' + str(rules.get('max_positions',8)) + '</span></div>'
    page += '<div class=row><span>Max Daily Trades</span><span style=color:#00ff88>' + str(rules.get('max_daily_trades',3)) + '</span></div>'
    page += '<div class=row><span>Stop Loss</span><span style=color:#ff4444>' + sl + '%</span></div>'
    page += '<div class=row><span>Take Profit</span><span style=color:#00ff88>' + tp + '%</span></div>'
    page += '<div class=row><span>Trailing Stop</span><span style=color:#ffaa00>' + ts + '%</span></div>'
    page += '<div class=row><span>Max Deployed</span><span style=color:#00ff88>' + dep + '%</span></div>'
    page += '<div class=row><span>VIX Threshold</span><span style=color:#ffaa00>' + str(rules.get('vix_threshold',25)) + '</span></div>'
    page += '</div>'
    page += '<div class=card><h2>Approved Tickers</h2>' + tickers + '</div>'
    page += '</div><div class=grid style=margin-top:12px>'
    page += '<div class=card><h2>Communication Log</h2>' + comms_html + '</div>'
    page += '<div class=card><h2>Rule Change History</h2>' + hist_html + '</div>'
    page += '</div></body></html>'
    return page

@app.route('/api/status')
def api_status():
    from flask import jsonify
    return jsonify({'rules': load(BASE+'/current_rules.json',{}),'comms': load(BASE+'/comms_log.json',[])[-5:],'positions': load(BASE+'/positions.json',{})})

if __name__ == '__main__':
    print('Dashboard: http://localhost:5051')
    app.run(port=5051, debug=False)
