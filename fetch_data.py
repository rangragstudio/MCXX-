"""Downloads futures/crypto prices and USD/INR from Yahoo Finance and converts them to MCX-style rupee prices.
THESE ARE PROXIES, not MCX prices. A per-instrument scale (from --calibrate) matches each one to the MCX level you type."""
import json, os, sys, time, datetime as dt
from agency import data as D
SCALE_FILE = os.path.join('data', 'proxy_scale.json')

def complete_cutoff(now_utc, kind='mcx'):
    if kind == 'crypto': return now_utc.date() - dt.timedelta(days=1)
    from zoneinfo import ZoneInfo
    et = now_utc.astimezone(ZoneInfo('America/New_York'))
    return et.date() if (et.hour, et.minute) >= (17, 30) else et.date() - dt.timedelta(days=1)

def _clean(df):
    import pandas as pd
    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
    idx = pd.to_datetime(df.index)
    if idx.tz is not None: idx = idx.tz_localize(None)
    df = df.copy(); df.index = idx.normalize()
    return df[~df.index.duplicated(keep='last')].sort_index()

def build_rows(px, fx, factor, scale, use_fx, cutoff):
    g, f = _clean(px), _clean(fx)
    fxc = f['Close'].reindex(g.index, method='ffill').bfill()
    rows = []
    for d, r in g.iterrows():
        if d.date() > cutoff: continue
        rate = fxc.loc[d] if use_fx else 1.0
        vals = [r['Open'], r['High'], r['Low'], r['Close'], rate]
        if any(v != v for v in vals): continue
        k = rate * scale * factor
        rows.append({'date': d.strftime('%Y-%m-%d'), 'open': round(r['Open'] * k, 2), 'high': round(r['High'] * k, 2),
                     'low': round(r['Low'] * k, 2), 'close': round(r['Close'] * k, 2)})
    return rows

def _dl(ticker):
    import yfinance as yf
    for _ in range(3):
        try:
            df = yf.download(ticker, period='max', interval='1d', auto_adjust=False, progress=False)
            if len(df) > 200: return df
        except Exception: pass
        time.sleep(4)
    raise RuntimeError(f'could not download {ticker}')

def load_scales():
    if not os.path.exists(SCALE_FILE): return {}
    d = json.load(open(SCALE_FILE))
    if 'scale' in d: return {'GOLDPETAL': d['scale']}
    return {k: v['scale'] for k, v in d.items() if isinstance(v, dict) and 'scale' in v}

def auto_calibrate(cfg, fx):
    """If a symbol has no saved scale, derive it from a known MCX price on a known date (config 'calibration')."""
    d = json.load(open(SCALE_FILE)) if os.path.exists(SCALE_FILE) else {}
    if 'scale' in d: d = {'GOLDPETAL': d}
    now = dt.datetime.now(dt.timezone.utc); changed = False
    for cal in cfg.get('calibration', []):
        if cal['symbol'] in d: continue
        inst = next((i for i in cfg['instruments'] if i['symbol'] == cal['symbol']), None)
        if not inst: continue
        try:
            rows = build_rows(_dl(inst['yahoo']), fx, inst['usd_factor'], 1.0, inst['use_fx'], complete_cutoff(now, inst.get('kind', 'mcx')))
            ref = [r for r in rows if r['date'] <= cal['date']][-1]
            d[cal['symbol']] = {'scale': cal['mcx_price'] / ref['close'], 'mcx_price': cal['mcx_price'], 'date': ref['date'], 'auto': True}; changed = True
        except Exception: pass
    if changed:
        os.makedirs('data', exist_ok=True); json.dump(d, open(SCALE_FILE, 'w'))

def update_all(cfg, outdir='data'):
    """Returns {symbol: n_rows or error string}."""
    now = dt.datetime.now(dt.timezone.utc); scales = load_scales(); res = {}
    try: fx = _dl('INR=X')
    except Exception as e: return {i['symbol']: 'fx download failed: ' + repr(e) for i in cfg['instruments']}
    os.makedirs(outdir, exist_ok=True)
    auto_calibrate(cfg, fx); scales = load_scales()
    for inst in cfg['instruments']:
        try:
            rows = build_rows(_dl(inst['yahoo']), fx, inst['usd_factor'], scales.get(inst['symbol'], 1.0), inst['use_fx'], complete_cutoff(now, inst.get('kind', 'mcx')))
            if len(rows) < 120: raise RuntimeError('too few rows')
            D.write_csv(rows, os.path.join(outdir, inst['symbol'] + '.csv')); res[inst['symbol']] = len(rows)
        except Exception as e: res[inst['symbol']] = repr(e)[:120]
    return res

def calibrate(cfg, symbol, mcx_price):
    inst = next(i for i in cfg['instruments'] if i['symbol'] == symbol)
    rows = build_rows(_dl(inst['yahoo']), _dl('INR=X'), inst['usd_factor'], 1.0, inst['use_fx'], complete_cutoff(dt.datetime.now(dt.timezone.utc), inst.get('kind', 'mcx')))
    scale = float(mcx_price) / rows[-1]['close']
    os.makedirs('data', exist_ok=True)
    d = json.load(open(SCALE_FILE)) if os.path.exists(SCALE_FILE) else {}
    if 'scale' in d: d = {'GOLDPETAL': d}
    d[symbol] = {'scale': scale, 'mcx_price': float(mcx_price), 'date': rows[-1]['date']}
    json.dump(d, open(SCALE_FILE, 'w'))
    print(f"{symbol}: scale {scale:.4f} (MCX Rs{mcx_price} vs proxy Rs{rows[-1]['close']:.2f} on {rows[-1]['date']})")

if __name__ == '__main__':
    cfg = json.load(open(os.environ.get('MCX_CONFIG', 'config_multi.json')))
    if len(sys.argv) > 3 and sys.argv[1] == '--calibrate': calibrate(cfg, sys.argv[2], sys.argv[3])
    else: print(update_all(cfg))
