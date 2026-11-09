"""Writes PAPER_REPORT.md: everything in one readable page (works on a phone). Run after run_scheduled.py."""
import json, os, datetime as dt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from agency import gates, ticket
from agency.portfolio import load_view, combined_state, sleeve_summary
from agency.report import metrics

def inr(n, d=2): return ('-' if n < 0 else '') + 'Rs' + format(abs(n), f',.{d}f')
def sg(n): return ('+' if n >= 0 else '') + inr(n)

def tail(p, n):
    try: return open(p, encoding='utf-8').read().splitlines()[-n:]
    except Exception: return []

def live_marks(cfg, sleeves):
    """Latest intraday price per open position (proxy). Returns ({symbol: price}, extra_pnl_total). Skips stale quotes."""
    import time
    marks, extra = {}, 0.0
    try: import dashboard_server as ds
    except Exception: return marks, extra
    maxage = cfg.get('alerts', {}).get('live_max_age_minutes', 120) * 60
    for s in sleeves:
        p = s['state']['pos']
        if not p or not s['bars']: continue
        try:
            q = ds.live_quote(s['symbol'])
            if q.get('ok') and time.time() - q['asof'] < maxage:
                k = s['cfg']['contract']; mult = k['lot_size'] / k['quote_unit']
                marks[s['symbol']] = q['last']; extra += (q['last'] - s['bars'][-1]['close']) * p['side'] * mult * p['qty']
        except Exception: pass
    return marks, extra

def build():
    cfg = json.load(open('config_multi.json')); view = load_view(cfg, bars_n=400)
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    L = ['# Paper portfolio report', '', f'Updated: {now}. **PAPER TRADING with simulated fills on proxy prices. No real money, no real orders.**', '']
    if not view:
        L += ['No portfolio yet. The first run has not completed.', '', '## Last runner log lines', '```'] + tail('logs/run.log', 12) + ['```']
        open('PAPER_REPORT.md', 'w', encoding='utf-8').write('\n'.join(L)); return
    sl = view['sleeves']; comb = combined_state(cfg, sl, view['pf']['fit']); m = metrics(comb, cfg) if len(comb['curve']) > 1 else None
    eq_close = comb['curve'][-1]['equity']; marks, extra = live_marks(cfg, sl); eq = eq_close + extra; total = cfg['capital_inr']; days = len(comb['curve']) - 1
    L += [f"## Total money now: {inr(eq)}", '', f"- {'Includes live prices for open positions (proxy). Last daily close total: ' + inr(eq_close) if marks else 'Based on the last daily close (no fresh live price)'}.",
          f"- Profit / loss: **{sg(eq - total)} ({(eq - total) / total * 100:+.2f}%)** since start with {inr(total, 0)}",
          f"- Day {days} of {cfg['finish_after_trading_days']} (MCX trading days). Data through {comb['last_date']}.",
          f"- Closed trades: {len(comb['trades'])}. Costs and tax paid: {inr(comb['costs'])}. Risk vetoes/blocks: {comb['vetoes']}. Halted: {'YES' if comb['halted'] else 'no'}."]
    if m:
        net = eq - total - m['ai_cost']
        L += [f"- Liquid fund would have earned {inr(m['benchmark_gain'])} in the same time. Net after AI cost: {sg(net)} -> **{'ahead of' if net > m['benchmark_gain'] else 'behind'} the liquid fund**."]
    L += ['', '## Each asset', '', '| Asset | Money put in | Money now | Profit / loss | Closed trades | Position |', '|---|---|---|---|---|---|']
    for s in sl:
        x = sleeve_summary(cfg, s); L.append(f"| {x['symbol']}{' (paper only)' if s['paper_only'] else ''} | {inr(x['alloc'], 0)} | {inr(x['equity'])} | {sg(x['pnl'])} | {x['trades']} | {x['pos']} |")
    un = total - sum(s['alloc'] for s in sl)
    if un > 0: L.append(f"| Cash not allocated | {inr(un, 0)} | {inr(un)} | - | - | - |")
    L += ['', '## Open positions', '']
    anyp = False
    for s in sl:
        p = s['state']['pos']
        if not p or not s['bars']: continue
        k = s['cfg']['contract']; mult = k['lot_size'] / k['quote_unit']; last = marks.get(s['symbol'], s['bars'][-1]['close']); un_ = (last - p['entry']) * p['side'] * mult * p['qty']; anyp = True
        L.append(f"- {s['symbol']}: {'LONG' if p['side'] > 0 else 'SHORT'} {p['qty']} lot since {p['date']}, entry {p['entry']:.2f}, stop {p['stop']:.2f}, last {last:.2f}, open P&L {sg(un_)}")
    if not anyp: L.append('- None. Everything is in cash.')
    L += ['', '## Money by day (all assets)', '', '| Date | Total money | Change |', '|---|---|---|']
    c = comb['curve']
    for i in range(max(1, len(c) - 20), len(c)): L.append(f"| {c[i]['date']} | {inr(c[i]['equity'])} | {sg(c[i]['equity'] - c[i - 1]['equity'])} |")
    L += ['', '## All trades', '']
    if comb['trades']:
        L += ['| Asset | In | Out | Side | Entry | Exit | Net | Exit by |', '|---|---|---|---|---|---|---|---|']
        for t in reversed(comb['trades']): L.append(f"| {t['symbol']} | {t['entry_date']} | {t['exit_date']} | {'LONG' if t['side'] > 0 else 'SHORT'} | {t['entry']} | {t['exit']} | {sg(t['net'])} | {t['why']} |")
    else: L.append('No trades yet. Staying in cash is a valid result.')
    L += ['', '## Orders queued for the next open (paper)', '']
    for s in sl:
        t = ticket.build(s['state'], s['cfg'], s['bars']) if not s['paper_only'] else {'lines': ['Paper only.']}
        L.append(f"**{s['symbol']}**: " + ' '.join(x.strip() for x in t['lines'] if x.strip())[:300])
    L += ['', '## Which assets the money could fund', '']
    for r in view['pf']['fit']: L.append(f"- {r['symbol']}: " + (f"funded {inr(r['alloc'], 0)}" if r['ok'] else 'NOT funded: ' + '; '.join(r['reasons'])))
    g = gates.evaluate(comb, cfg)
    L += ['', '## Go-live gates (all must pass before any real money)', ''] + [f"- {'PASS' if r['ok'] else 'FAIL'}: {r['name']} (need {r['need']}, have {r['have']})" for r in g['rows']]
    L += ['', f"**{'Eligible for Stage 1' if g['ready'] else 'Not ready for real money'}.** Passing is necessary, not proof of an edge.", '', '## Runner log (last 10 lines)', '```'] + tail('logs/run.log', 10) + ['```']
    open('PAPER_REPORT.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    try:
        import alert
        sent = alert.check(cfg, eq, comb['halted'], f"Day {days}; closed trades {len(comb['trades'])}; open positions: " + ', '.join(f"{x['symbol']} {x['pos']}" for x in (sleeve_summary(cfg, s) for s in sl)))
        if sent: print('alerts sent:', sent)
    except Exception as e: print('alert error', repr(e))

if __name__ == '__main__':
    build()
