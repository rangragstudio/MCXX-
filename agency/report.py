import datetime as dt

def metrics(st, cfg):
    tr = st['trades']; curve = st['curve']; eqs = [c['equity'] for c in curve]
    wins = [t['net'] for t in tr if t['net'] > 0]; losses = [t['net'] for t in tr if t['net'] <= 0]
    peak, mdd = eqs[0], 0.0
    for e in eqs:
        peak = max(peak, e); mdd = max(mdd, (peak - e) / peak * 100)
    d0, d1 = dt.date.fromisoformat(curve[0]['date']), dt.date.fromisoformat(curve[-1]['date'])
    days = max((d1 - d0).days, 1); init = st['initial']; final = eqs[-1]
    bench = init * cfg['benchmark_liquid_fund_yield_pct'] / 100 * days / 365
    ai = cfg['ai_cost_inr_per_month'] * days / 30
    return {'start': curve[0]['date'], 'end': curve[-1]['date'], 'days': days, 'trading_days': len(curve) - 1,
            'initial': init, 'final': round(final, 2), 'pnl': round(final - init, 2), 'return_pct': round((final - init) / init * 100, 2),
            'trades': len(tr), 'win_rate_pct': round(len(wins) / len(tr) * 100, 1) if tr else 0,
            'expectancy': round(sum(t['net'] for t in tr) / len(tr), 2) if tr else 0,
            'profit_factor': round(sum(wins) / abs(sum(losses)), 2) if losses and sum(losses) != 0 else None,
            'costs_total': round(st['costs'], 2), 'max_drawdown_pct': round(mdd, 2), 'vetoes': st['vetoes'],
            'benchmark_gain': round(bench, 2), 'ai_cost': round(ai, 2), 'net_after_ai': round(final - init - ai, 2),
            'beats_benchmark': (final - init - ai) > bench, 'halted': st['halted'], 'audit_issues': len(st['audit'])}

def markdown(st, cfg, title):
    m = metrics(st, cfg); L = [f"# {title}", "", "**PAPER TRADING. Simulated fills at the next open with slippage. Not verified live performance.**", ""]
    L += [f"Period: {m['start']} to {m['end']} ({m['trading_days']} trading days)", "",
          f"- Start capital: Rs{m['initial']:,.0f}  |  End equity: Rs{m['final']:,.2f}  |  P&L: Rs{m['pnl']:,.2f} ({m['return_pct']}%)",
          f"- Trades: {m['trades']}  |  Win rate: {m['win_rate_pct']}%  |  Expectancy per trade: Rs{m['expectancy']}  |  Profit factor: {m['profit_factor']}",
          f"- Costs paid: Rs{m['costs_total']}  |  Max drawdown: {m['max_drawdown_pct']}%  |  Risk vetoes/blocks: {m['vetoes']}",
          f"- Liquid-fund benchmark for the same period: Rs{m['benchmark_gain']}  |  AI cost: Rs{m['ai_cost']}",
          f"- **Net after AI cost: Rs{m['net_after_ai']}  ->  {'BEATS' if m['beats_benchmark'] else 'DOES NOT BEAT'} the liquid fund**",
          f"- Halted by Risk Guardian: {m['halted']}  |  Auditor mismatches: {m['audit_issues']}", ""]
    L += ["## Strategy evidence (qualification before trading)", "", "| Strategy | Trades | Expectancy in-sample | Expectancy out-of-sample | Enabled |", "|---|---|---|---|---|"]
    for e in st['evidence']:
        L.append(f"| {e.get('symbol', '')} {e['name']} | {e['trades']} | {e['exp_in_sample']} | {e['exp_out_of_sample']} | {'yes' if e['enabled'] else 'no'} |")
    if not st['enabled']: L += ["", "No strategy qualified, so the agency stayed in cash. That is a valid result."]
    L += ["", "## Trades", "", "| Asset | Entry | Exit | Side | Entry px | Exit px | Net Rs | Why exit |", "|---|---|---|---|---|---|---|---|"]
    for t in st['trades']:
        L.append(f"| {t.get('symbol', '')} | {t['entry_date']} | {t['exit_date']} | {'L' if t['side'] == 1 else 'S'} | {t['entry']} | {t['exit']} | {t['net']} | {t['why']} |")
    L += ["", "## Agent log (last 40 lines)", "", "```"] + st['log'][-40:] + ["```"]
    return "\n".join(L)
