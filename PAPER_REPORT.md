# Paper portfolio report

Updated: 2026-11-26 12:04 UTC. **PAPER TRADING with simulated fills on proxy prices. No real money, no real orders.**

## Total money now: Rs15,000.00

- Based on the last daily close (no fresh live price).
- Profit / loss: **+Rs0.00 (+0.00%)** since start with Rs15,000
- Day 13 of 60 (MCX trading days). Data through 2026-11-25.
- Closed trades: 0. Costs and tax paid: Rs0.00. Risk vetoes/blocks: 0. Halted: no.
- Liquid fund would have earned Rs44.71 in the same time. Net after AI cost: +Rs0.00 -> **behind the liquid fund**.

## Each asset

| Asset | Money put in | Money now | Profit / loss | Closed trades | Position |
|---|---|---|---|---|---|
| GOLDPETAL | Rs9,000 | Rs9,000.00 | +Rs0.00 | 0 | flat |
| BTC (paper only) | Rs6,000 | Rs6,000.00 | +Rs0.00 | 0 | flat |

## Open positions

- None. Everything is in cash.

## Money by day (all assets)

| Date | Total money | Change |
|---|---|---|
| 2026-11-09 | Rs15,000.00 | +Rs0.00 |
| 2026-11-10 | Rs15,000.00 | +Rs0.00 |
| 2026-11-11 | Rs15,000.00 | +Rs0.00 |
| 2026-11-12 | Rs15,000.00 | +Rs0.00 |
| 2026-11-13 | Rs15,000.00 | +Rs0.00 |
| 2026-11-16 | Rs15,000.00 | +Rs0.00 |
| 2026-11-17 | Rs15,000.00 | +Rs0.00 |
| 2026-11-18 | Rs15,000.00 | +Rs0.00 |
| 2026-11-19 | Rs15,000.00 | +Rs0.00 |
| 2026-11-20 | Rs15,000.00 | +Rs0.00 |
| 2026-11-23 | Rs15,000.00 | +Rs0.00 |
| 2026-11-24 | Rs15,000.00 | +Rs0.00 |
| 2026-11-25 | Rs15,000.00 | +Rs0.00 |

## All trades

No trades yet. Staying in cash is a valid result.

## Orders queued for the next open (paper)

**GOLDPETAL**: NO ORDER for the next open. Do nothing.
**BTC**: Paper only.

## Which assets the money could fund

- GOLDPETAL: funded Rs9,000
- SILVER100: NOT funded: a normal stop risks Rs806, well above the Rs375 per-trade limit
- CRUDEOILM: NOT funded: margin Rs26,879 is over 50% of capital; a normal stop risks Rs6,563, well above the Rs375 per-trade limit
- BTC: funded Rs6,000

## Go-live gates (all must pass before any real money)

- FAIL: Paper trading days (need >= 60, have 13)
- FAIL: Closed paper trades (need >= 30, have 0)
- FAIL: Expectancy per trade after costs (need > Rs0, have Rs0)
- FAIL: Profit factor (need >= 1.3, have None)
- PASS: Max drawdown (need < 10.0% and never halted, have 0.0%)
- FAIL: Beats liquid fund after AI cost (need yes, have no)
- PASS: Auditor mismatches (need 0, have 0)

**Not ready for real money.** Passing is necessary, not proof of an edge.

## Runner log (last 10 lines)
```
2026-11-24T23:13:38 data: {"GOLDPETAL": 6585, "SILVER100": 6586, "CRUDEOILM": 6593, "BTC": 4451}
2026-11-24T23:13:39 GOLDPETAL: 1 new bar(s), at 2026-11-24
2026-11-25T09:00:24 data: {"GOLDPETAL": 6585, "SILVER100": 6586, "CRUDEOILM": 6593, "BTC": 4452}
2026-11-25T09:00:24 BTC: 1 new bar(s), at 2026-11-24
2026-11-25T12:21:47 data: {"GOLDPETAL": 6585, "SILVER100": 6586, "CRUDEOILM": 6593, "BTC": 4452}
2026-11-25T21:56:05 data: {"GOLDPETAL": 6585, "SILVER100": 6586, "CRUDEOILM": 6593, "BTC": 4452}
2026-11-26T08:47:17 data: {"GOLDPETAL": 6586, "SILVER100": 6587, "CRUDEOILM": 6594, "BTC": 4453}
2026-11-26T08:47:17 GOLDPETAL: 1 new bar(s), at 2026-11-25
2026-11-26T08:47:17 BTC: 1 new bar(s), at 2026-11-25
2026-11-26T12:04:13 data: {"GOLDPETAL": 6586, "SILVER100": 6587, "CRUDEOILM": 6594, "BTC": 4453}
```
