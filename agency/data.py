import csv, math, random, datetime as dt

def load_csv(path):
    """CSV columns (any case): date, open, high, low, close. Price in rupees per quote unit."""
    rows = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (r.fieldnames or [])}
        for need in ('date', 'open', 'high', 'low', 'close'):
            if need not in cols:
                raise ValueError(f"CSV needs a '{need}' column; found {list(cols)}")
        for row in r:
            try:
                d = row[cols['date']].strip()[:10]
                rows[d] = {'date': d, **{k: float(row[cols[k]].replace(',', '')) for k in ('open', 'high', 'low', 'close')}}
            except (ValueError, AttributeError):
                continue
    bars = [rows[d] for d in sorted(rows)]
    if len(bars) < 120:
        raise ValueError(f"Need at least 120 daily bars, found {len(bars)}")
    return bars

def synthetic(n=1500, seed=7, start=5000.0):
    """SYNTHETIC random-walk data with drifting regimes. For testing the engine ONLY. Not evidence of anything."""
    rnd = random.Random(seed); p = start; d = dt.date(2020, 1, 1); out = []; drift = 0.0003
    while len(out) < n:
        d += dt.timedelta(days=1)
        if d.weekday() >= 5:
            continue
        if rnd.random() < 0.02:
            drift = rnd.choice([-0.0006, 0.0, 0.0004, 0.0008])
        o = p * (1 + rnd.gauss(0, 0.002))
        c = o * (1 + drift + rnd.gauss(0, 0.009))
        hi = max(o, c) * (1 + abs(rnd.gauss(0, 0.004))); lo = min(o, c) * (1 - abs(rnd.gauss(0, 0.004)))
        out.append({'date': d.isoformat(), 'open': round(o, 2), 'high': round(hi, 2), 'low': round(lo, 2), 'close': round(c, 2)})
        p = c
    return out

def write_csv(bars, path):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['date', 'open', 'high', 'low', 'close'])
        for b in bars:
            w.writerow([b['date'], b['open'], b['high'], b['low'], b['close']])
