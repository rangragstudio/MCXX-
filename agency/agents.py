"""The agency. Each class is one role with one job. All trading here is PAPER (simulated)."""
from . import indicators as ind


class CostAnalyst:
    """Regulatory & Tax Analyst (costs side): charges per order leg. Rates are config, verify with your broker."""
    def __init__(s, cfg):
        s.c = cfg['costs']; k = cfg['contract']; s.mult = k['lot_size'] / k['quote_unit']
    def leg(s, price, qty, is_sell):
        v = price * s.mult * qty; c = s.c
        brk = min(c['brokerage_flat'], v * c['brokerage_pct'] / 100)
        txn = v * c['txn_pct'] / 100; sebi = v * c['sebi_per_crore'] / 1e7
        gst = (brk + txn + sebi) * c['gst_pct'] / 100
        ctt = v * c['ctt_pct_sell'] / 100 if is_sell else 0.0
        stamp = 0.0 if is_sell else v * c['stamp_pct_buy'] / 100
        return brk + txn + sebi + gst + ctt + stamp


class ResearchAnalyst:
    """Global Market Researcher: describes the regime. Informational; goes into the audit log."""
    def regime(s, w):
        if len(w) < 60: return 'warmup'
        c = [b['close'] for b in w[-200:]]; a = ind.atr(w[-100:])
        gap = (ind.ema(c, 20)[-1] - ind.ema(c, 50)[-1]) / a
        vol = a / c[-1] * 100
        trend = 'uptrend' if gap > 0.3 else 'downtrend' if gap < -0.3 else 'range'
        return f"{trend}, ATR {a:.1f} ({vol:.2f}% of price)"


class QuantScientist:
    """Quantitative Scientist: only strategies with positive after-cost expectancy in-sample AND out-of-sample get a vote."""
    def __init__(s, strategies): s.strategies = strategies
    def validate(s, bars, cfg, make_agency):
        v = cfg['validation']; cut = int(len(bars) * v['in_sample_frac']); cut_date = bars[cut]['date']
        big = dict(cfg); big['capital_inr'] = 1_000_000
        evidence = []
        for st in s.strategies:
            ag = make_agency(big, [st.name], enforce=False)
            ag.strats = [st]
            ag.start(bars, 0)
            for i in range(1, len(bars)): ag.on_bar(bars, i)
            tr = ag.st['trades']
            ins = [t['net'] for t in tr if t['entry_date'] < cut_date]
            oos = [t['net'] for t in tr if t['entry_date'] >= cut_date]
            e_is = sum(ins) / len(ins) if ins else 0.0; e_oos = sum(oos) / len(oos) if oos else 0.0
            ok = len(tr) >= v['min_trades'] and e_is > 0 and e_oos > 0
            evidence.append({'name': st.name, 'trades': len(tr), 'exp_in_sample': round(e_is, 2),
                             'exp_out_of_sample': round(e_oos, 2), 'enabled': ok})
        return evidence
    def votes(s, w, enabled):
        return [(st.name, st.desired(w)) for st in s.strategies if st.name in enabled]


class RiskGuardian:
    """Risk Guardian: independent veto. Also owns the loss limits and the drawdown halt."""
    def __init__(s, cfg, enforce=True):
        s.r = cfg['risk']; s.enforce = enforce; k = cfg['contract']
        s.mult = k['lot_size'] / k['quote_unit']; s.margin_pct = cfg['margin_pct']
    def veto(s, price, stop_dist, equity, qty=1):
        if not s.enforce: return None
        risk = stop_dist * s.mult * qty
        if risk > s.r['max_risk_per_trade_pct'] / 100 * equity:
            return f"risk at stop Rs{risk:.0f} > limit Rs{s.r['max_risk_per_trade_pct'] / 100 * equity:.0f}"
        margin = s.margin_pct / 100 * price * s.mult * qty
        if margin > s.r['max_margin_use_pct'] / 100 * equity:
            return f"margin Rs{margin:.0f} > {s.r['max_margin_use_pct']}% of equity"
        return None
    def entries_blocked(s, curve, initial):
        if not s.enforce or not curve: return None
        eq = [c['equity'] for c in curve[-6:]]; prev = eq[-2] if len(eq) > 1 else initial
        if (eq[-1] - prev) / prev * 100 <= -s.r['daily_loss_limit_pct']: return 'daily loss limit'
        base = eq[-6] if len(eq) > 5 else initial
        if (eq[-1] - base) / base * 100 <= -s.r['weekly_loss_limit_pct']: return 'weekly loss limit'
        return None
    def halt(s, peak, equity):
        return s.enforce and (peak - equity) / peak * 100 >= s.r['drawdown_halt_pct']


class PaperBroker:
    """Execution (paper only): fills at next open with slippage, stops use the day's high/low, margin is checked."""
    def __init__(s, cfg, st, costs, risk):
        s.cfg, s.st, s.costs, s.risk = cfg, st, costs, risk
        k = cfg['contract']; s.mult = k['lot_size'] / k['quote_unit']; s.slip = cfg['slippage_per_unit']
    def equity(s, price):
        p = s.st['pos']; un = (price - p['entry']) * p['side'] * s.mult * p['qty'] if p else 0.0
        return s.st['initial'] + s.st['realized'] - s.st['costs'] + un
    def open(s, side, stop_dist, px, date, why):
        fill = px + side * s.slip; qty = 1
        margin = s.cfg['margin_pct'] / 100 * fill * s.mult * qty
        cash = s.st['initial'] + s.st['realized'] - s.st['costs']
        if cash < margin:
            s.st['log'].append(f"{date} BROKER rejected entry: cash Rs{cash:.0f} < margin Rs{margin:.0f}"); return
        c = s.costs.leg(fill, qty, is_sell=(side == -1)); s.st['costs'] += c
        s.st['pos'] = {'side': side, 'entry': fill, 'stop': fill - side * stop_dist, 'qty': qty,
                       'date': date, 'entry_cost': c, 'why': why}
        s.st['log'].append(f"{date} BROKER opened {'LONG' if side == 1 else 'SHORT'} @ {fill:.2f}, stop {s.st['pos']['stop']:.2f}")
    def close(s, fill, date, why):
        p = s.st['pos']; gross = (fill - p['entry']) * p['side'] * s.mult * p['qty']
        c = s.costs.leg(fill, p['qty'], is_sell=(p['side'] == 1)); s.st['costs'] += c; s.st['realized'] += gross
        tax = max(0.0, gross) * s.cfg.get('gain_tax_pct', 0) / 100; s.st['costs'] += tax; c += tax
        net = gross - p['entry_cost'] - c
        s.st['trades'].append({'entry_date': p['date'], 'exit_date': date, 'side': p['side'], 'entry': round(p['entry'], 2),
                               'exit': round(fill, 2), 'gross': round(gross, 2), 'costs': round(p['entry_cost'] + c, 2),
                               'net': round(net, 2), 'why': why})
        s.st['log'].append(f"{date} BROKER closed @ {fill:.2f} ({why}), net Rs{net:.2f}")
        s.st['pos'] = None
    def fill_pending(s, bar):
        p = s.st['pending']
        if not p: return
        if p['close'] and s.st['pos']:
            pos = s.st['pos']; s.close(bar['open'] - pos['side'] * s.slip, bar['date'], 'signal')
        if p['open'] and not s.st['pos']:
            s.open(p['open']['side'], p['open']['stop_dist'], bar['open'], bar['date'], p['reason'])
        s.st['pending'] = None
    def check_stop(s, bar):
        p = s.st['pos']
        if not p: return
        if p['side'] == 1 and bar['low'] <= p['stop']:
            s.close(min(p['stop'], bar['open']) - s.slip, bar['date'], 'stop')
        elif p['side'] == -1 and bar['high'] >= p['stop']:
            s.close(max(p['stop'], bar['open']) + s.slip, bar['date'], 'stop')


class CIO:
    """Chief Investment Officer: turns the evidence-qualified votes into one decision. Staying in cash is a valid decision."""
    def __init__(s, cfg): s.min_agree = cfg['min_agree']; s.stop_mult = cfg['stop_atr_mult']
    def decide(s, votes, cur):
        total = sum(v for _, v in votes)
        return 1 if total >= s.min_agree else -1 if total <= -s.min_agree else 0


class Auditor:
    """Independent Auditor: recomputes equity from the trade list and compares with the books."""
    def reconcile(s, st, price, broker):
        realized = sum(t['gross'] for t in st['trades']); costs_closed = sum(t['costs'] for t in st['trades'])
        open_cost = st['pos']['entry_cost'] if st['pos'] else 0.0
        diff_real = abs(realized - st['realized']); diff_cost = abs(costs_closed + open_cost - st['costs'])
        return {'ok': diff_real < 0.5 and diff_cost < 0.5, 'realized_diff': round(diff_real, 3), 'cost_diff': round(diff_cost, 3)}


class SurvivalOfficer:
    """Financial Survival Officer: net result after AI/infrastructure cost, and the benchmark to beat."""
    def report(s, cfg, st, days):
        gain = st['curve_last'] - st['initial'] if 'curve_last' in st else 0.0
        bench = st['initial'] * cfg['benchmark_liquid_fund_yield_pct'] / 100 * days / 365
        ai = cfg['ai_cost_inr_per_month'] * days / 30
        return {'net_pnl': gain, 'benchmark_gain': bench, 'ai_cost': ai, 'net_after_ai': gain - ai, 'beats_benchmark': gain - ai > bench}
