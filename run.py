import argparse, json, os, sys
from agency import data as D
from agency.engine import Agency
from agency.report import markdown, metrics

def load_cfg(p): return json.load(open(p))

def make_agency_factory(state_path=None):
    def mk(cfg, enabled, enforce=True): return Agency(cfg, enabled=enabled, enforce=enforce, state_path=state_path)
    return mk

def train_and_start(cfg, bars, train_end, state_path=None, enforce=True):
    """Validate strategies on bars[:train_end+1] only, then begin paper trading from the last training bar."""
    train = bars[:train_end + 1]
    q = Agency(cfg, enabled=[], enforce=False).quant
    ev = q.validate(train, cfg, make_agency_factory())
    ag = Agency(cfg, enabled=[e['name'] for e in ev if e['enabled']], enforce=enforce, state_path=state_path)
    ag.st['evidence'] = ev
    ag.start(bars, train_end)
    return ag

def main():
    ap = argparse.ArgumentParser(description='MCX paper-trading agency')
    ap.add_argument('cmd', choices=['sample', 'backtest', 'replay', 'daily', 'report'])
    ap.add_argument('--data', default='data/sample_synthetic.csv'); ap.add_argument('--config', default='config.json')
    ap.add_argument('--days', type=int, default=15); ap.add_argument('--train-frac', type=float, default=0.5)
    ap.add_argument('--state', default='state.json'); ap.add_argument('--reset-halt', action='store_true')
    a = ap.parse_args(); cfg = load_cfg(a.config)
    if a.cmd == 'sample':
        D.write_csv(D.synthetic(), 'data/sample_synthetic.csv'); print('wrote data/sample_synthetic.csv (SYNTHETIC test data only)'); return
    if a.cmd == 'report':
        st = json.load(open(a.state)); print(markdown(st, cfg, 'Paper trading report')); return
    bars = D.load_csv(a.data)
    if a.cmd in ('backtest', 'replay'):
        n = len(bars); end = int(n * a.train_frac) - 1 if a.cmd == 'backtest' else n - a.days - 1
        ag = train_and_start(cfg, bars, end)
        for i in range(end + 1, n): ag.on_bar(bars, i)
        os.makedirs('reports', exist_ok=True)
        out = f"reports/{a.cmd}_{bars[-1]['date']}.md"; txt = markdown(ag.st, cfg, f"{a.cmd.title()} on {os.path.basename(a.data)}")
        open(out, 'w').write(txt); print(txt[:1800]); print(f"\nfull report: {out}"); return
    if a.cmd == 'daily':
        if os.path.exists(a.state):
            ag = Agency(cfg, state_path=a.state)
            if a.reset_halt: ag.st['halted'] = False; ag.st['peak'] = ag.st['curve'][-1]['equity']; ag.save()
            new = [i for i, b in enumerate(bars) if b['date'] > ag.st['last_date']]
            for i in new: ag.on_bar(bars, i)
            print(f"processed {len(new)} new bar(s); last date {ag.st['last_date']}")
        else:
            ag = train_and_start(cfg, bars, len(bars) - 1, state_path=a.state)
            print(f"started paper trading from {ag.st['last_date']}; enabled strategies: {ag.enabled or 'none (staying in cash)'}")
        m = metrics(ag.st, cfg) if len(ag.st['curve']) > 1 else None
        if ag.st['pending']: print('Order queued for next open:', ag.st['pending'])
        print(ag.st['log'][-1] if ag.st['log'] else '')
        if m: print(f"equity Rs{m['final']} | P&L Rs{m['pnl']} | trades {m['trades']} | maxDD {m['max_drawdown_pct']}% | halted {m['halted']}")
if __name__ == '__main__': main()
