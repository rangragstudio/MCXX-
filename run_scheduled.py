"""Run daily by the scheduler: download data, advance every paper sleeve, write tickets and checkpoint reports."""
import json, os, subprocess, datetime as dt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from agency import data as D, gates, ticket
from agency.engine import Agency
from agency.portfolio import fit_report, sleeve_cfg, combined_state, sleeve_summary
from agency.report import markdown, metrics
from run import train_and_start
import fetch_data

def log(msg):
    os.makedirs('logs', exist_ok=True)
    open('logs/run.log', 'a').write(f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}\n")

def load_bars(cfg):
    out = {}
    for i in cfg['instruments']:
        p = os.path.join('data', i['symbol'] + '.csv')
        if os.path.exists(p):
            try: out[i['symbol']] = D.load_csv(p)
            except Exception as e: log(f"{i['symbol']}: bad data file ({e})")
    return out

def main(download=True):
    cfg = json.load(open(os.environ.get('MCX_CONFIG', 'config_multi.json'))); target = cfg['finish_after_trading_days']; clock = cfg['clock_symbol']
    if os.path.exists('DONE.txt'): log('already finished'); return
    if download:
        res = fetch_data.update_all(cfg); log('data: ' + json.dumps(res))
        if not isinstance(res.get(clock), int): log('clock instrument data missing; will retry next run'); return
    bars = load_bars(cfg)
    if clock not in bars: log('no data for clock instrument'); return
    if os.path.exists('portfolio.json'): pf = json.load(open('portfolio.json'))
    else:
        fit = fit_report(cfg, bars); pf = {'fit': fit, 'alloc': {r['symbol']: r['alloc'] for r in fit}, 'halted': False, 'created': dt.date.today().isoformat()}
        json.dump(pf, open('portfolio.json', 'w'), indent=1); log('portfolio created: ' + json.dumps(pf['alloc']))
    kill = os.path.exists('KILL_SWITCH.txt'); sleeves = []; clock_last = None
    order = sorted([i for i in cfg['instruments'] if pf['alloc'].get(i['symbol'], 0) > 0 and i['symbol'] in bars], key=lambda i: i['symbol'] != clock)
    for inst in order:
        sym = inst['symbol']; alloc = pf['alloc'][sym]; scfg = sleeve_cfg(cfg, inst, alloc); path = f'state_{sym}.json'; b = bars[sym]
        if not os.path.exists(path): ag = train_and_start(scfg, b, len(b) - 1, state_path=path); log(f"{sym} started {ag.st['last_date']} enabled {ag.enabled or 'none'}")
        else:
            ag = Agency(scfg, state_path=path)
            if (kill or pf['halted']) and not ag.st['halted']: ag.st['halted'] = True; ag.st['log'].append('HALTED by kill switch or portfolio drawdown limit.')
            n = 0
            for i, bar in enumerate(b):
                if bar['date'] <= ag.st['last_date']: continue
                ok = (len(ag.st['curve']) - 1 < target) if sym == clock else (clock_last is not None and bar['date'] <= clock_last)
                if ok: ag.on_bar(b, i); n += 1
            if n: log(f"{sym}: {n} new bar(s), at {ag.st['last_date']}")
        if sym == clock: clock_last = ag.st['last_date']
        sleeves.append({'symbol': sym, 'alloc': alloc, 'cfg': scfg, 'state': ag.st, 'inst': inst, 'ag': ag, 'bars': b})
    comb = combined_state(cfg, sleeves, pf['fit']); days = len(comb['curve']) - 1
    dd = (comb['peak'] - comb['curve'][-1]['equity']) / comb['peak'] * 100 if comb['curve'] else 0
    if dd >= cfg['risk']['drawdown_halt_pct'] and not pf['halted']:
        pf['halted'] = True; json.dump(pf, open('portfolio.json', 'w'), indent=1); log(f'PORTFOLIO HALT: drawdown {dd:.1f}%')
        for s in sleeves: s['ag'].st['halted'] = True; s['ag'].save()
    L = [f"# Order tickets for the next open (data up to {comb['last_date']})", '', 'PAPER SYSTEM. Act on these only in the real-money stage. One ticket per instrument.', '']
    for s in sleeves:
        L.append(f"## {s['inst']['name']}")
        if s['inst'].get('paper_only'): L += ['PAPER ONLY (research). No real order, ever.', '']; continue
        L += [ticket.build(s['state'], s['cfg'], s['bars'])['text'], '']
    open('ORDER_TICKET.md', 'w', encoding='utf-8').write('\n'.join(L))
    for cp in cfg['checkpoints']:
        fn = f'RESULT_AFTER_{cp}_DAYS.md'
        if days >= cp and not os.path.exists(fn):
            gt = gates.evaluate(comb, cfg); body = markdown(comb, cfg, f'Portfolio result after {cp} trading days')
            body += "\n\n## What each instrument is doing\n\n| Asset | Allocated | Equity | P&L | Trades | Position |\n|---|---|---|---|---|---|\n"
            for s in sleeves:
                x = sleeve_summary(cfg, s); body += f"| {x['symbol']} | Rs{x['alloc']:,} | Rs{x['equity']:,.2f} | Rs{x['pnl']:,.2f} | {x['trades']} | {x['pos']} |\n"
            body += "\n## Which instruments could be funded (fit screen)\n\n"
            for r in pf['fit']: body += f"- {r['symbol']}: {'FUNDED Rs' + format(r['alloc'], ',') if r['ok'] else 'NOT FUNDED: ' + '; '.join(r['reasons'])}\n"
            body += "\n## Go-live gates (all must pass before real money)\n\n" + "\n".join(f"- {'PASS' if r['ok'] else 'FAIL'}: {r['name']}: need {r['need']}, have {r['have']}" for r in gt['rows'])
            body += f"\n\n**{'All gates passed. Eligible for Stage 1 (one lot, manual orders, MCX instruments only).' if gt['ready'] else 'NOT ready for real money.'}**\n"
            open(fn, 'w', encoding='utf-8').write(body); log(f'checkpoint {cp} written')
            if os.name == 'nt':
                try: os.startfile(fn)
                except Exception: pass
    if days >= target:
        open('DONE.txt', 'w').write('finished ' + dt.datetime.now().isoformat()); log('FINISHED')
        if os.name == 'nt':
            for t in ('MCXAgency',):
                try: subprocess.run(['schtasks', '/Delete', '/TN', t, '/F'], capture_output=True)
                except Exception: pass

if __name__ == '__main__':
    try: main()
    except Exception as e: log('ERROR: ' + repr(e))
