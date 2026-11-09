import json, os
from . import indicators as ind
from .agents import (CostAnalyst, ResearchAnalyst, QuantScientist, RiskGuardian, PaperBroker, CIO, Auditor)
from .strategies import all_strategies

def fresh_state(cfg):
    c = cfg['capital_inr']
    return {'initial': c, 'pos': None, 'pending': None, 'peak': c, 'realized': 0.0, 'costs': 0.0, 'trades': [],
            'curve': [], 'last_date': None, 'halted': False, 'vetoes': 0, 'enabled': [], 'evidence': [], 'log': [], 'audit': []}

class Agency:
    def __init__(s, cfg, enabled=None, enforce=True, state_path=None):
        s.cfg, s.path = cfg, state_path
        s.st = None
        if state_path and os.path.exists(state_path):
            s.st = json.load(open(state_path))
        else:
            s.st = fresh_state(cfg)
        if enabled is not None: s.st['enabled'] = enabled
        s.costs = CostAnalyst(cfg); s.research = ResearchAnalyst(); s.quant = QuantScientist(all_strategies())
        s.strats = s.quant.strategies
        s.risk = RiskGuardian(cfg, enforce); s.broker = PaperBroker(cfg, s.st, s.costs, s.risk)
        s.cio = CIO(cfg); s.auditor = Auditor()

    @property
    def enabled(s): return s.st['enabled']

    def window(s, bars, i): return bars[max(0, i - 250):i + 1]

    def start(s, bars, i):
        """Begin paper trading from bar i (history up to and including i is treated as already seen)."""
        bar = bars[i]; s.st['last_date'] = bar['date']
        s.st['curve'].append({'date': bar['date'], 'equity': round(s.broker.equity(bar['close']), 2)})
        s.decide(bars, i); s.save()

    def on_bar(s, bars, i):
        bar = bars[i]
        if s.st['last_date'] and bar['date'] <= s.st['last_date']: return  # idempotent: no double processing
        s.broker.fill_pending(bar); s.broker.check_stop(bar)
        eq = s.broker.equity(bar['close'])
        s.st['curve'].append({'date': bar['date'], 'equity': round(eq, 2)})
        s.st['peak'] = max(s.st['peak'], eq)
        if not s.st['halted'] and s.risk.halt(s.st['peak'], eq):
            s.st['halted'] = True; s.st['log'].append(f"{bar['date']} RISK GUARDIAN halted trading: drawdown limit reached. Review required.")
        s.st['last_date'] = bar['date']
        rec = s.auditor.reconcile(s.st, bar['close'], s.broker)
        if not rec['ok']: s.st['audit'].append({'date': bar['date'], **rec})
        s.decide(bars, i); s.save()

    def decide(s, bars, i):
        w = s.window(bars, i); bar = bars[i]; d = bar['date']
        a = ind.atr(w[-100:])
        if a is None or len(w) < 60: return
        regime = s.research.regime(w); eq = s.broker.equity(bar['close'])
        votes = s.quant.votes(w, s.enabled); cur = s.st['pos']['side'] if s.st['pos'] else 0
        want = s.cio.decide(votes, cur)
        if s.cfg.get('long_only') and want < 0: want = 0
        s.st['log'].append(f"{d} RESEARCH {regime} | QUANT {votes or 'no enabled strategies'} | CIO wants {want:+d} (now {cur:+d})")
        blocked = 'HALTED' if s.st['halted'] else s.risk.entries_blocked(s.st['curve'], s.st['initial'])
        if blocked and want != 0 and want != cur:
            s.st['log'].append(f"{d} RISK GUARDIAN blocked new entry: {blocked}"); s.st['vetoes'] += 0 if s.st['halted'] else 1; want = 0 if cur == 0 or want == -cur else cur
        if s.st['halted']: want = 0
        if want == cur: s.st['pending'] = None; return
        pend = {'close': cur != 0, 'open': None, 'reason': ','.join(n for n, v in votes if v == want)}
        if want != 0:
            stop_dist = s.cfg['stop_atr_mult'] * a
            veto = s.risk.veto(bar['close'], stop_dist, eq)
            if veto:
                s.st['vetoes'] += 1; s.st['log'].append(f"{d} RISK GUARDIAN VETO entry: {veto}")
            else:
                pend['open'] = {'side': want, 'stop_dist': stop_dist}
        s.st['pending'] = pend if (pend['close'] or pend['open']) else None
        if s.st['pending']: s.st['log'].append(f"{d} ORDER queued for next open: close={pend['close']} open={pend['open'] and pend['open']['side']}")

    def save(s):
        if s.path:
            tmp = s.path + '.tmp'; json.dump(s.st, open(tmp, 'w'), indent=1); os.replace(tmp, s.path)
