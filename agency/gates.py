"""Go-live gates. All must pass before any real money. Necessary, not sufficient: passing does not prove an edge."""
from .report import metrics

def evaluate(st, cfg):
    g = cfg.get('gates', {'min_trading_days': 60, 'min_trades': 30, 'min_profit_factor': 1.3})
    if not st or not st.get('curve'): return {'rows': [], 'ready': False, 'days': 0}
    m = metrics(st, cfg); halt = cfg['risk']['drawdown_halt_pct']
    rows = [
        ('Paper trading days', f">= {g['min_trading_days']}", f"{m['trading_days']}", m['trading_days'] >= g['min_trading_days']),
        ('Closed paper trades', f">= {g['min_trades']}", f"{m['trades']}", m['trades'] >= g['min_trades']),
        ('Expectancy per trade after costs', '> Rs0', f"Rs{m['expectancy']}", m['trades'] > 0 and m['expectancy'] > 0),
        ('Profit factor', f">= {g['min_profit_factor']}", f"{m['profit_factor']}", (m['profit_factor'] or 0) >= g['min_profit_factor']),
        ('Max drawdown', f"< {halt}% and never halted", f"{m['max_drawdown_pct']}%{' (HALTED)' if m['halted'] else ''}", m['max_drawdown_pct'] < halt and not m['halted']),
        ('Beats liquid fund after AI cost', 'yes', 'yes' if m['beats_benchmark'] else 'no', m['beats_benchmark']),
        ('Auditor mismatches', '0', f"{m['audit_issues']}", m['audit_issues'] == 0),
    ]
    out = [{'name': n, 'need': need, 'have': have, 'ok': bool(ok)} for n, need, have, ok in rows]
    return {'rows': out, 'ready': all(r['ok'] for r in out), 'days': m['trading_days']}
