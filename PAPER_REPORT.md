# Paper portfolio report

Updated: 2026-11-13 23:48 UTC. **PAPER TRADING with simulated fills on proxy prices. No real money, no real orders.**

## Total money now: Rs15,000.00

- Based on the last daily close (no fresh live price).
- Profit / loss: **+Rs0.00 (+0.00%)** since start with Rs15,000
- Day 5 of 60 (MCX trading days). Data through 2026-11-13.
- Closed trades: 0. Costs and tax paid: Rs0.00. Risk vetoes/blocks: 0. Halted: no.
- Liquid fund would have earned Rs13.15 in the same time. Net after AI cost: +Rs0.00 -> **behind the liquid fund**.

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

- FAIL: Paper trading days (need >= 60, have 5)
- FAIL: Closed paper trades (need >= 30, have 0)
- FAIL: Expectancy per trade after costs (need > Rs0, have Rs0)
- FAIL: Profit factor (need >= 1.3, have None)
- PASS: Max drawdown (need < 10.0% and never halted, have 0.0%)
- FAIL: Beats liquid fund after AI cost (need yes, have no)
- PASS: Auditor mismatches (need 0, have 0)

**Not ready for real money.** Passing is necessary, not proof of an edge.

## Runner log (last 10 lines)
```
2026-11-12T07:35:20 BTC: 1 new bar(s), at 2026-11-11
2026-11-12T10:47:55 data: {"GOLDPETAL": 6576, "SILVER100": 6577, "CRUDEOILM": 6584, "BTC": 4439}
2026-11-12T18:45:16 data: {"GOLDPETAL": 6576, "SILVER100": 6577, "CRUDEOILM": 6584, "BTC": 4439}
2026-11-13T07:05:49 data: {"GOLDPETAL": 6577, "SILVER100": 6578, "CRUDEOILM": 6585, "BTC": 4439}
2026-11-13T07:05:49 GOLDPETAL: 1 new bar(s), at 2026-11-12
2026-11-13T10:43:46 data: {"GOLDPETAL": 6577, "SILVER100": 6578, "CRUDEOILM": 6585, "BTC": 4440}
2026-11-13T10:43:46 BTC: 1 new bar(s), at 2026-11-12
2026-11-13T18:27:11 data: {"GOLDPETAL": 6577, "SILVER100": 6578, "CRUDEOILM": 6585, "BTC": 4440}
2026-11-13T23:48:42 data: {"GOLDPETAL": 6578, "SILVER100": 6579, "CRUDEOILM": 6586, "BTC": 4440}
2026-11-13T23:48:42 GOLDPETAL: 1 new bar(s), at 2026-11-13
```
