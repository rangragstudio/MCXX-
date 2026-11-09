from . import indicators as ind

class Trend:
    name = 'trend_ema20_50'
    def desired(self, w):
        if len(w) < 60: return 0
        c = [b['close'] for b in w[-200:]]
        a = ind.atr(w[-100:])
        gap = (ind.ema(c, 20)[-1] - ind.ema(c, 50)[-1]) / a
        return 1 if gap > 0.3 else -1 if gap < -0.3 else 0

class Breakout:
    name = 'breakout_20d'
    def __init__(self, n=20, hold=10): self.n, self.hold = n, hold
    def desired(self, w):
        if len(w) < self.n + self.hold + 1: return 0
        for j in range(self.hold):
            idx = len(w) - 1 - j; prior = w[idx - self.n:idx]
            if w[idx]['close'] > max(b['high'] for b in prior): return 1
            if w[idx]['close'] < min(b['low'] for b in prior): return -1
        return 0

class MeanReversion:
    name = 'meanrev_rsi14'
    def __init__(self, lo=30, hi=70, look=10): self.lo, self.hi, self.look = lo, hi, look
    def desired(self, w):
        if len(w) < 40: return 0
        r = [x for x in ind.rsi([b['close'] for b in w[-100:]]) if x is not None]
        recent, cur = r[-self.look:], r[-1]
        if min(recent) < self.lo and cur < 50: return 1
        if max(recent) > self.hi and cur > 50: return -1
        return 0

def all_strategies():
    return [Trend(), Breakout(), MeanReversion()]
