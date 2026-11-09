"""Local live dashboard for the multi-asset paper portfolio. 127.0.0.1 only (this PC).
Start: python dashboard_server.py   then open http://127.0.0.1:8765   (demo layout: /?demo=1)"""
import csv, json, os, subprocess, sys, time, datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT); sys.path.insert(0, ROOT)
PORT = 8765; proc = None; _live = {}

def read_json(p, default=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return default

def tail(p, n=15):
    try: return open(p, encoding='utf-8').read().splitlines()[-n:]
    except Exception: return []

def portfolio_payload(cfg, view, mode):
    from agency import gates, ticket
    from agency.portfolio import combined_state, sleeve_summary
    from agency.report import metrics
    sleeves = []
    for s in view['sleeves']:
        t = {'has_order': False, 'lines': ['PAPER ONLY (research). No real order, ever.']} if s['paper_only'] else ticket.build(s['state'], s['cfg'], s['bars'])
        sleeves.append({'symbol': s['symbol'], 'name': s['name'], 'alloc': s['alloc'], 'paper_only': s['paper_only'], 'state': s['state'],
                        'config': s['cfg'], 'bars': s['bars'], 'ticket': t, 'yahoo': s['inst']['yahoo']})
    comb = combined_state(cfg, view['sleeves'], view['pf']['fit'])
    eq = comb['curve'][-1]['equity'] if comb['curve'] else cfg['capital_inr']
    m = metrics(comb, cfg) if len(comb['curve']) > 1 else None
    return {'multi': True, 'mode': mode, 'sleeves': sleeves, 'gates': gates.evaluate(comb, cfg),
            'portfolio': {'capital': cfg['capital_inr'], 'equity': eq, 'curve': comb['curve'], 'trades': comb['trades'], 'fit': view['pf']['fit'],
                          'summary': [sleeve_summary(cfg, s) for s in view['sleeves']], 'metrics': m, 'halted': view['pf'].get('halted', False)}}

def real_state():
    from agency import portfolio
    cfg = read_json('config_multi.json', {}); base = {'now': dt.datetime.now().isoformat(timespec='seconds'), 'config': cfg,
        'done': os.path.exists('DONE.txt'), 'runlog': tail('logs/run.log'), 'running': bool(proc and proc.poll() is None), 'kill': os.path.exists('KILL_SWITCH.txt')}
    view = portfolio.load_view(cfg)
    if not view: return {**base, 'multi': True, 'mode': 'live', 'waiting': True}
    return {**base, **portfolio_payload(cfg, view, 'live')}

def demo_state():
    """Synthetic demo (gold + bitcoin sleeves, strategies forced on) just to preview the layout."""
    import copy, random
    from agency import data as D
    from agency.engine import Agency
    from agency.portfolio import sleeve_cfg, fit_report
    cfg = copy.deepcopy(read_json('config_multi.json')); cfg['risk']['max_risk_per_trade_pct'] = 5.0
    gold = D.synthetic(420, seed=2, start=15300.0); end = 300
    r = random.Random(8); p = 7e6; d = dt.date.fromisoformat(gold[0]['date']); btc = []
    while len(btc) < 600:
        o = p * (1 + r.gauss(0, .002)); c = o * (1 + r.gauss(0.0004, .018)); btc.append({'date': d.isoformat(), 'open': round(o), 'high': round(max(o, c) * 1.008), 'low': round(min(o, c) * .992), 'close': round(c)})
        p = c; d += dt.timedelta(days=1)
    bars = {'GOLDPETAL': gold, 'SILVER100': D.synthetic(420, seed=6, start=2346.0), 'CRUDEOILM': D.synthetic(420, seed=7, start=9079.0), 'BTC': btc}
    fit = fit_report(cfg, {k: v[:end + 1] for k, v in bars.items()}); alloc = {'GOLDPETAL': 9000, 'BTC': 6000}
    for r_ in fit: r_['alloc'] = alloc.get(r_['symbol'], 0); r_['ok'] = r_['alloc'] > 0 or r_['ok']
    names = ['trend_ema20_50', 'breakout_20d', 'meanrev_rsi14']; sleeves = []
    for inst in cfg['instruments']:
        sym = inst['symbol']
        if sym not in alloc: continue
        sc = sleeve_cfg(cfg, inst, alloc[sym]); ag = Agency(sc, enabled=names, enforce=True)
        b = bars[sym]; start = end if sym != 'BTC' else next(i for i, x in enumerate(b) if x['date'] == gold[end]['date'])
        ag.st['evidence'] = [{'name': n, 'trades': 12, 'exp_in_sample': 20.0, 'exp_out_of_sample': 5.0, 'enabled': True} for n in names]
        ag.start(b, start)
        for i in range(start + 1, len(b)):
            if b[i]['date'] <= gold[end + 15]['date']: ag.on_bar(b, i)
        sleeves.append({'symbol': sym, 'name': inst['name'], 'alloc': alloc[sym], 'cfg': sc, 'state': ag.st, 'paper_only': inst.get('paper_only', False),
                        'bars': [x for x in b if x['date'] <= gold[end + 15]['date']][-130:], 'inst': inst})
    view = {'pf': {'fit': fit, 'alloc': alloc, 'halted': False}, 'sleeves': sleeves}
    return {'now': dt.datetime.now().isoformat(timespec='seconds'), 'config': cfg, 'done': False, 'runlog': ['DEMO DATA: synthetic prices, strategies forced on'],
            'running': False, 'kill': False, **portfolio_payload(cfg, view, 'demo')}

def build_live(px, fx, scale, factor, use_fx):
    import pandas as pd
    def idx(df):
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        df = df.copy(); i = pd.to_datetime(df.index)
        i = i.tz_localize('UTC') if i.tz is None else i.tz_convert('UTC')
        df.index = i; return df[~df.index.duplicated()].sort_index()
    g, f = idx(px), idx(fx)
    fxc = f['Close'].reindex(g.index, method='ffill').bfill(); t, p = [], []
    for ts, c, r in zip(g.index, g['Close'], fxc):
        if c == c and r == r: t.append(int(ts.timestamp())); p.append(round(float(c) * (float(r) if use_fx else 1.0) * scale * factor, 2))
    if len(p) < 2: raise RuntimeError('no intraday points')
    return {'ok': True, 't': t[-400:], 'p': p[-400:], 'last': p[-1], 'first': p[0], 'asof': t[-1], 'scale': scale}

def live_quote(sym):
    c = _live.get(sym)
    if c and time.time() - c[0] < 15: return c[1]
    try:
        import yfinance as yf
        import fetch_data
        cfg = read_json('config_multi.json', {}); inst = next(i for i in cfg['instruments'] if i['symbol'] == sym)
        g = yf.Ticker(inst['yahoo']).history(period='1d', interval='1m', auto_adjust=False)
        f = yf.Ticker('INR=X').history(period='1d', interval='5m', auto_adjust=False)
        if len(g) < 2 or len(f) < 1:
            g = yf.Ticker(inst['yahoo']).history(period='5d', interval='5m', auto_adjust=False); f = yf.Ticker('INR=X').history(period='5d', interval='15m', auto_adjust=False)
        data = build_live(g, f, fetch_data.load_scales().get(sym, 1.0), inst['usd_factor'], inst['use_fx'])
    except Exception as e: data = {'ok': False, 'error': repr(e)[:200]}
    _live[sym] = (time.time(), data); return data

def demo_live(price):
    now = int(time.time()); p = price; t, v = [], []
    for k in range(240, 0, -1):
        import random
        p *= 1 + random.Random(now // 60 - k).gauss(0, 0.0004); t.append(now - k * 60); v.append(round(p, 2))
    return {'ok': True, 't': t, 'p': v, 'last': v[-1], 'first': v[0], 'asof': t[-1], 'scale': None, 'demo': True}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype):
        b = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == '/api/state':
            try: data = demo_state() if 'demo' in q else real_state()
            except Exception as e: data = {'mode': 'error', 'error': repr(e)}
            return self.send(200, json.dumps(data), 'application/json')
        if u.path == '/api/live':
            sym = (q.get('sym') or ['GOLDPETAL'])[0]
            data = demo_live(float((q.get('price') or ['15300'])[0])) if 'demo' in q else live_quote(sym)
            return self.send(200, json.dumps(data), 'application/json')
        if u.path in ('/', '/index.html'): return self.send(200, open('dashboard/index.html', 'rb').read(), 'text/html; charset=utf-8')
        self.send(404, 'not found', 'text/plain')
    def do_POST(self):
        global proc
        if self.path == '/api/run':
            if proc and proc.poll() is None: return self.send(200, json.dumps({'status': 'busy'}), 'application/json')
            proc = subprocess.Popen([sys.executable, 'run_scheduled.py'], cwd=ROOT)
            return self.send(200, json.dumps({'status': 'started'}), 'application/json')
        if self.path == '/api/kill':
            if os.path.exists('KILL_SWITCH.txt'): os.remove('KILL_SWITCH.txt'); st = 'off'
            else: open('KILL_SWITCH.txt', 'w').write('created from dashboard'); st = 'on'
            return self.send(200, json.dumps({'status': st}), 'application/json')
        self.send(404, 'not found', 'text/plain')

if __name__ == '__main__':
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    print(f'Dashboard: http://127.0.0.1:{PORT}   (demo: /?demo=1)   Ctrl+C to stop')
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
