def ema(vals, n):
    k = 2.0 / (n + 1); out = []; e = None
    for v in vals:
        e = v if e is None else v * k + e * (1 - k)
        out.append(e)
    return out

def atr(bars, n=14):
    trs = []; prev = None
    for b in bars:
        tr = b['high'] - b['low'] if prev is None else max(b['high'] - b['low'], abs(b['high'] - prev), abs(b['low'] - prev))
        trs.append(tr); prev = b['close']
    if len(trs) < n:
        return None
    a = sum(trs[:n]) / n
    for t in trs[n:]:
        a = (a * (n - 1) + t) / n
    return a

def rsi(closes, n=14):
    if len(closes) <= n:
        return [None] * len(closes)
    out = [None] * n
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, n + 1)]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, n + 1)]
    ag, al = sum(gains) / n, sum(losses) / n
    out.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
        out.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    return out
