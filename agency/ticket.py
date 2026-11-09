"""Order ticket for tomorrow's open. YOU place the order manually in your broker app. Nothing is sent anywhere."""
from . import indicators as ind

def build(st, cfg, bars):
    k = cfg['contract']; mult = k['lot_size'] / k['quote_unit']; sym = k['symbol']
    if not st or not bars: return {'has_order': False, 'lines': ['No state yet.'], 'text': 'No state yet.'}
    last = bars[-1]['close']; pend = st.get('pending'); pos = st.get('pos'); L = []
    if not pend:
        L.append('NO ORDER for the next open. Do nothing.')
        if pos: L.append(f"Keep your {'LONG' if pos['side'] > 0 else 'SHORT'} open. Your stop-loss stays at about Rs{pos['stop']:.0f}.")
        return {'has_order': False, 'lines': L, 'text': '\n'.join(L)}
    if pend['close'] and pos:
        L.append(f"1) CLOSE your open {'LONG (SELL' if pos['side'] > 0 else 'SHORT (BUY'} 1 lot {sym} to square off) at the market open. Cancel its stop-loss order.")
    if pend['open']:
        side, sd = pend['open']['side'], pend['open']['stop_dist']
        risk = sd * mult; margin = cfg['margin_pct'] / 100 * last * mult
        L.append(f"{'2' if pend['close'] else '1'}) {'BUY' if side > 0 else 'SELL'} 1 lot {sym} at the market open (use the contract month with more than 5 days to expiry).")
        L.append(f"   Right after it fills, place a stop-loss at fill price {'minus' if side > 0 else 'plus'} Rs{sd:.0f} (about Rs{last - side * sd:.0f} if it fills near yesterday's close Rs{last:.0f}).")
        L.append(f"   Money at risk if the stop hits: about Rs{risk:.0f} plus costs. Margin blocked: about Rs{margin:.0f}. Reason: {pend.get('reason') or '-'}")
    L += ['', 'Rules: one lot only. Never hold into expiry (Gold Petal settles by delivery; many brokers square off before it).',
          'If you skip a ticket, tell the agency by creating KILL_SWITCH.txt (the dashboard has a button) so paper and real do not drift apart.']
    return {'has_order': True, 'lines': L, 'text': '\n'.join(L)}
