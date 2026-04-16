import json, os, yfinance as yf, requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('/Users/miguelvalenzuela/ibkr_trading_bot/.env')

BASE = '/Users/miguelvalenzuela/ibkr_trading_bot'
RULES_JSON = BASE + '/current_rules.json'
HISTORY_FILE = BASE + '/rules_history.json'
COMMS_LOG = BASE + '/comms_log.json'
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

PROFILES = {
    'aggressive': {'max_position_size': 3000,'max_positions': 10,'max_daily_trades': 5,'stop_loss': -0.12,'take_profit': 0.25,'trailing_stop': -0.08,'max_portfolio_deployment': 0.90,'vix_threshold': 30,'risk_level': 'low'},
    'normal':     {'max_position_size': 2500,'max_positions': 8, 'max_daily_trades': 3,'stop_loss': -0.10,'take_profit': 0.20,'trailing_stop': -0.07,'max_portfolio_deployment': 0.80,'vix_threshold': 25,'risk_level': 'medium'},
    'defensive':  {'max_position_size': 1500,'max_positions': 5, 'max_daily_trades': 2,'stop_loss': -0.07,'take_profit': 0.15,'trailing_stop': -0.05,'max_portfolio_deployment': 0.60,'vix_threshold': 20,'risk_level': 'high'},
    'paused':     {'max_position_size': 0,   'max_positions': 0, 'max_daily_trades': 0,'stop_loss': -0.05,'take_profit': 0.10,'trailing_stop': -0.03,'max_portfolio_deployment': 0.00,'vix_threshold': 15,'risk_level': 'extreme'},
}

APPROVED_TICKERS = ['NVDA','MSFT','AVGO','PLTR','META','AMZN','GOOG','TSM','MU','AMD','NFLX','TTD','LMT','AAPL','CRM']

def load_rules():
    try:
        with open(RULES_JSON) as f: return json.load(f)
    except: return PROFILES['normal'].copy()

def log_communication(event, message, data={}):
    try:
        with open(COMMS_LOG) as f: logs = json.load(f)
    except: logs = []
    logs.append({'timestamp': datetime.now().isoformat(), 'event': event, 'message': message, 'data': data})
    with open(COMMS_LOG, 'w') as f: json.dump(logs[-100:], f, indent=2)
    print('[' + event + '] ' + message)

def save_history(old, new, reason):
    try:
        with open(HISTORY_FILE) as f: h = json.load(f)
    except: h = []
    skip = ['last_updated','update_reason','profile','approved_tickers']
    changes = {k: {'from': old.get(k), 'to': new.get(k)} for k in new if new.get(k) != old.get(k) and k not in skip}
    h.append({'timestamp': datetime.now().isoformat(), 'reason': reason, 'changes': changes})
    with open(HISTORY_FILE, 'w') as f: json.dump(h[-50:], f, indent=2)

def save_rules(rules, reason, profile):
    rules['last_updated'] = datetime.now().isoformat()
    rules['update_reason'] = reason
    rules['profile'] = profile
    rules['approved_tickers'] = APPROVED_TICKERS
    with open(RULES_JSON, 'w') as f: json.dump(rules, f, indent=2)
    write_bot_rules(rules)
    print('Rules saved: ' + profile)

def write_bot_rules(rules):
    tickers = json.dumps(rules.get('approved_tickers', APPROVED_TICKERS))
    content = 'APPROVED_TICKERS = ' + tickers + chr(10)
    content += 'MAX_POSITION_SIZE = ' + str(rules.get('max_position_size', 2500)) + chr(10)
    content += 'MAX_POSITIONS = ' + str(rules.get('max_positions', 8)) + chr(10)
    content += 'MAX_DAILY_TRADES = ' + str(rules.get('max_daily_trades', 3)) + chr(10)
    content += 'STOP_LOSS = ' + str(rules.get('stop_loss', -0.10)) + chr(10)
    content += 'TAKE_PROFIT = ' + str(rules.get('take_profit', 0.20)) + chr(10)
    content += 'TRAILING_STOP = ' + str(rules.get('trailing_stop', -0.07)) + chr(10)
    content += 'MAX_HOLD_DAYS = ' + str(rules.get('max_hold_days', 30)) + chr(10)
    content += 'MIN_STOCK_PRICE = ' + str(rules.get('min_stock_price', 10.0)) + chr(10)
    content += 'MAX_PORTFOLIO_DEPLOYMENT = ' + str(rules.get('max_portfolio_deployment', 0.80)) + chr(10)
    content += chr(10) + 'EARNINGS_BLACKOUT = []' + chr(10)
    content += 'import json, yfinance as yf' + chr(10)
    content += 'from datetime import datetime' + chr(10)
    content += 'def is_approved_ticker(s): return s in APPROVED_TICKERS' + chr(10)
    content += 'def is_weekend(): return datetime.now().weekday() >= 5' + chr(10)
    content += 'def get_trade_count():' + chr(10)
    content += '    today = datetime.now().strftime("%Y-%m-%d")' + chr(10)
    content += '    try:' + chr(10)
    content += '        with open("/Users/miguelvalenzuela/ibkr_trading_bot/daily_trades.json") as f: return json.load(f).get(today, 0)' + chr(10)
    content += '    except: return 0' + chr(10)
    content += 'def log_trade():' + chr(10)
    content += '    today = datetime.now().strftime("%Y-%m-%d")' + chr(10)
    content += '    path = "/Users/miguelvalenzuela/ibkr_trading_bot/daily_trades.json"' + chr(10)
    content += '    try:' + chr(10)
    content += '        with open(path) as f: data = json.load(f)' + chr(10)
    content += '    except: data = {}' + chr(10)
    content += '    data[today] = data.get(today, 0) + 1' + chr(10)
    content += '    with open(path, "w") as f: json.dump(data, f)' + chr(10)
    content += 'def check_vix():' + chr(10)
    content += '    try:' + chr(10)
    content += '        vix = yf.download("^VIX", period="1d", progress=False)' + chr(10)
    content += '        return float(vix["Close"].iloc[-1].squeeze()) > ' + str(rules.get('vix_threshold', 25)) + chr(10)
    content += '    except: return False' + chr(10)
    content += 'def requires_approval(symbol, amount, action):' + chr(10)
    content += '    r = []' + chr(10)
    content += '    if amount > MAX_POSITION_SIZE: r.append("Order over limit")' + chr(10)
    content += '    if action == "SELL": r.append("Full position sell")' + chr(10)
    content += '    return r' + chr(10)
    content += 'def run_all_checks(symbol, amount, price, action):' + chr(10)
    content += '    if symbol not in APPROVED_TICKERS: return False, [symbol + " not approved"]' + chr(10)
    content += '    if price < MIN_STOCK_PRICE: return False, ["Price too low"]' + chr(10)
    content += '    if amount > MAX_POSITION_SIZE: return False, ["Amount exceeds max"]' + chr(10)
    content += '    if get_trade_count() >= MAX_DAILY_TRADES: return False, ["Daily limit reached"]' + chr(10)
    content += '    if datetime.now().weekday() >= 5: return False, ["Weekend"]' + chr(10)
    content += '    if check_vix(): return False, ["VIX too high"]' + chr(10)
    content += '    return True, requires_approval(symbol, amount, action)' + chr(10)
    with open(BASE + '/bot_rules.py', 'w') as f: f.write(content)
    log_communication('RULES_WRITTEN', 'bot_rules.py updated')

def get_market_data():
    try:
        vix = yf.download('^VIX', period='5d', progress=False)
        vix_val = float(vix['Close'].iloc[-1].squeeze())
        vix_chg = float(vix['Close'].pct_change().iloc[-1].squeeze()) * 100
        sp500 = yf.download('^GSPC', period='5d', progress=False)
        sp_chg = float(sp500['Close'].pct_change().iloc[-1].squeeze()) * 100
        return {'vix': round(vix_val,2), 'vix_change': round(vix_chg,2), 'sp500_change': round(sp_chg,2)}
    except Exception as e:
        log_communication('ERROR', 'Market data failed: ' + str(e))
        return {'vix': 20, 'vix_change': 0, 'sp500_change': 0}

def get_news_risk():
    if not NEWS_API_KEY: return 'neutral', []
    crisis = ['war','invasion','nuclear','crash','recession','collapse','sanctions','iran','attack','default']
    positive = ['ceasefire','deal','growth','recovery','rally','record','peace']
    try:
        resp = requests.get('https://newsapi.org/v2/everything', params={'q': 'stock market OR economy','language': 'en','pageSize': 20,'sortBy': 'publishedAt','apiKey': NEWS_API_KEY}, timeout=10)
        headlines = [a['title'].lower() for a in resp.json().get('articles', [])]
        crisis_hits = sum(1 for h in headlines for k in crisis if k in h)
        positive_hits = sum(1 for h in headlines for k in positive if k in h)
        if crisis_hits >= 5: return 'crisis', []
        if crisis_hits >= 3: return 'negative', []
        if positive_hits >= 3: return 'positive', []
        return 'neutral', []
    except: return 'neutral', []

def determine_profile(vix, vix_chg, sp_chg, sentiment):
    if vix > 35 or sentiment == 'crisis': return 'paused', 'EXTREME RISK: VIX=' + str(vix)
    if vix > 25 or sentiment == 'negative' or sp_chg < -2: return 'defensive', 'HIGH RISK: VIX=' + str(vix) + ' SP=' + str(sp_chg) + '%'
    if vix < 15 and sentiment in ['positive','neutral'] and sp_chg > 0: return 'aggressive', 'LOW RISK: VIX=' + str(vix) + ' SP=' + str(sp_chg) + '%'
    return 'normal', 'MEDIUM RISK: VIX=' + str(vix) + ' SP=' + str(sp_chg) + '%'

def is_major_change(old, new_profile):
    if new_profile == 'paused': return True
    if old.get('profile','normal') in ['aggressive','normal'] and new_profile == 'defensive': return True
    if abs(PROFILES[new_profile]['stop_loss'] - old.get('stop_loss',-0.10)) > 0.03: return True
    return False

def run_risk_assessment():
    print('=== AI Risk Manager ===')
    log_communication('START', 'Risk assessment started')
    md = get_market_data()
    log_communication('MARKET_DATA', 'VIX=' + str(md['vix']) + ' SP=' + str(md['sp500_change']) + '%', md)
    sentiment, _ = get_news_risk()
    log_communication('NEWS', 'Sentiment=' + sentiment)
    profile, reason = determine_profile(md['vix'], md['vix_change'], md['sp500_change'], sentiment)
    log_communication('PROFILE', 'Selected=' + profile + ' Reason=' + reason)
    old = load_rules()
    if old.get('profile','normal') == profile:
        log_communication('NO_CHANGE', 'Profile unchanged: ' + profile)
        print('No change needed - staying on ' + profile + ' profile')
        return
    new = PROFILES[profile].copy()
    new['approved_tickers'] = old.get('approved_tickers', APPROVED_TICKERS)
    if is_major_change(old, profile):
        log_communication('MAJOR', 'SMS required: ' + old.get('profile','normal') + ' -> ' + profile)
        from sms_bot import send_sms, save_pending
        msg = 'RISK ALERT: ' + old.get('profile','normal').upper() + ' -> ' + profile.upper()
        msg += chr(10) + 'Reason: ' + reason
        msg += chr(10) + 'Reply YES to apply or NO to keep current rules.'
        save_pending([{'type': 'rule_update', 'new_rules': new, 'profile': profile, 'reason': reason}])
        send_sms(msg)
        print('SMS sent for approval')
    else:
        save_history(old, new, reason)
        save_rules(new, reason, profile)
        log_communication('AUTO_APPLIED', 'Auto-updated to ' + profile + ': ' + reason)

if __name__ == '__main__':
    run_risk_assessment()
