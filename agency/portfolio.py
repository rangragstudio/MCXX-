"""Multi-asset paper portfolio: one sleeve (Agency) per instrument, a shared Rs capital, portfolio-level halt."""
import copy, json, os
from . import indicators as ind
from .engine import Agency
from .report import metrics

def sleeve_cfg(cfg, inst, alloc):
    c = copy.deepcopy(cfg); total = cfg['capital_inr']; r = cfg['risk']
    c['contract'] = {'symbol': inst['symbol'], 'lot_size': inst['lot_size'], 'quote_unit': inst['quote_unit']}
    c['capital_inr'] = alloc; c['margin_pct'] = inst['margin_pct']; c['slippage_per_unit'] = inst['slippage_per_unit']
    c['costs'] = inst.get('costs', cfg['costs']); c['long_only'] = inst.get('long_only', False); c['gain_tax_pct'] = inst.get('gain_tax_pct', 0)
    cap = lambda pct: pct / 100 * total / alloc * 100
    c['risk'] = {'max_risk_per_trade_pct': cap(r['max_risk_per_trade_pct']), 'max_margin_use_pct': 80,
                 'daily_loss_limit_pct': cap(r['daily_loss_limit_pct']), 'weekly_loss_limit_pct': cap(r['weekly_loss_limit_pct']),
                 'drawdown_halt_pct': 100}
    c.pop('instruments', None)
    return c

def fit_report(cfg, bars_by_sym):
    """Which instruments can this capital actually fund under the risk rules? Honest screen, then weights -> rupees."""
    total = cfg['capital_inr']; cap = cfg['risk']['max_risk_per_trade_pct'] / 100 * total; rows = []
    for inst in cfg['instruments']:
        b = bars_by_sym.get(inst['symbol'])
        row = {'symbol': inst['symbol'], 'name': inst['name'], 'paper_only': inst.get('paper_only', False), 'weight': inst['weight']}
        if not b or len(b) < 120: row.update(ok=False, reasons=['no data'], lot_value=None, margin=None, stop_risk=None); rows.append(row); continue
        mult = inst['lot_size'] / inst['quote_unit']; price = b[-1]['close']; a = ind.atr(b[-100:])
        value = price * mult; margin = inst['margin_pct'] / 100 * value; stop = cfg['stop_atr_mult'] * a * mult
        why = []
        if margin > cfg['risk']['max_margin_use_pct'] / 100 * total: why.append(f"margin Rs{margin:,.0f} is over {cfg['risk']['max_margin_use_pct']}% of capital")
        if stop > 1.3 * cap: why.append(f"a normal stop risks Rs{stop:,.0f}, well above the Rs{cap:,.0f} per-trade limit")
        row.update(ok=not why, reasons=why, lot_value=round(value), margin=round(margin), stop_risk=round(stop)); rows.append(row)
    live = [r for r in rows if r['ok']]
    while live:
        w = sum(r['weight'] for r in live); drop = False
        for r in list(live):
            r['alloc'] = round(total * r['weight'] / w)
            if r['alloc'] < r['margin'] / 0.8:
                r['ok'] = False; r['reasons'].append(f"sleeve Rs{r['alloc']:,} too small for its margin"); live.remove(r); drop = True
        if not drop: break
    for r in rows: r.setdefault('alloc', 0)
    for r in rows:
        if not r['ok']: r['alloc'] = 0
    return rows

def combined_curve(sleeves, total, unalloc):
    dates = sorted({c['date'] for s in sleeves for c in s['state']['curve']}); out = []
    for d in dates:
        e = unalloc
        for s in sleeves:
            last = None
            for c in s['state']['curve']:
                if c['date'] <= d: last = c['equity']
                else: break
            e += last if last is not None else s['state']['initial']
        out.append({'date': d, 'equity': round(e, 2)})
    return out

def combined_state(cfg, sleeves, fit):
    total = cfg['capital_inr']; unalloc = total - sum(s['alloc'] for s in sleeves)
    curve = combined_curve(sleeves, total, unalloc); trades = []; log = []; ev = []
    for s in sleeves:
        st = s['state']
        trades += [dict(t, symbol=s['symbol']) for t in st['trades']]
        ev += [dict(e, symbol=s['symbol']) for e in st['evidence']]
        log += [f"[{s['symbol']}] {l}" for l in st['log'][-40:]]
    trades.sort(key=lambda t: t['exit_date'])
    clock = next((s for s in sleeves if s['symbol'] == cfg.get('clock_symbol')), sleeves[0] if sleeves else None)
    if clock:
        keep = {c['date'] for c in clock['state']['curve']}; curve = [c for c in curve if c['date'] in keep] or curve
    peak = max([c['equity'] for c in curve] + [total])
    return {'initial': total, 'curve': curve, 'trades': trades, 'costs': sum(s['state']['costs'] for s in sleeves),
            'vetoes': sum(s['state']['vetoes'] for s in sleeves), 'halted': any(s['state']['halted'] for s in sleeves),
            'audit': [a for s in sleeves for a in s['state']['audit']], 'evidence': ev, 'enabled': [e['name'] for e in ev if e['enabled']],
            'log': log, 'pos': None, 'pending': None, 'peak': peak, 'last_date': curve[-1]['date'] if curve else None, 'realized': 0, 'fit': fit}

def sleeve_summary(cfg, s):
    st = s['state']; m = metrics(st, s['cfg']) if len(st['curve']) > 1 else None
    pos = st['pos']; eq = st['curve'][-1]['equity'] if st['curve'] else s['alloc']
    return {'symbol': s['symbol'], 'alloc': s['alloc'], 'equity': eq, 'pnl': round(eq - s['alloc'], 2), 'trades': len(st['trades']),
            'pos': ('LONG' if pos['side'] > 0 else 'SHORT') if pos else 'flat', 'enabled': st['enabled'], 'halted': st['halted']}

def _read_bars(path, n=None):
    import csv
    out = []
    try:
        with open(path, newline='', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                out.append({'date': r['date'], 'open': float(r['open']), 'high': float(r['high']), 'low': float(r['low']), 'close': float(r['close'])})
    except Exception: return []
    return out[-n:] if n else out

def load_view(cfg, root='.', bars_n=130):
    """Reads portfolio.json + state_<SYM>.json + data/<SYM>.csv. Used by the dashboard."""
    pj = os.path.join(root, 'portfolio.json')
    if not os.path.exists(pj): return None
    pf = json.load(open(pj)); sleeves = []
    for inst in cfg['instruments']:
        sym = inst['symbol']; alloc = pf['alloc'].get(sym, 0); sp = os.path.join(root, f'state_{sym}.json')
        if alloc <= 0 or not os.path.exists(sp): continue
        scfg = sleeve_cfg(cfg, inst, alloc)
        sleeves.append({'symbol': sym, 'name': inst['name'], 'alloc': alloc, 'cfg': scfg, 'state': json.load(open(sp)),
                        'paper_only': inst.get('paper_only', False), 'bars': _read_bars(os.path.join(root, 'data', f'{sym}.csv'), bars_n), 'inst': inst})
    return {'pf': pf, 'sleeves': sleeves}
