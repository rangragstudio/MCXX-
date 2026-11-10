# Paper portfolio report

Updated: 2026-11-10 18:31 UTC. **PAPER TRADING with simulated fills on proxy prices. No real money, no real orders.**

## Total money now: Rs15,000.00

- Based on the last daily close (no fresh live price).
- Profit / loss: **+Rs0.00 (+0.00%)** since start with Rs15,000
- Day 1 of 60 (MCX trading days). Data through 2026-11-09.
- Closed trades: 0. Costs and tax paid: Rs0.00. Risk vetoes/blocks: 0. Halted: no.
- Liquid fund would have earned Rs2.63 in the same time. Net after AI cost: +Rs0.00 -> **behind the liquid fund**.

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

- FAIL: Paper trading days (need >= 60, have 1)
- FAIL: Closed paper trades (need >= 30, have 0)
- FAIL: Expectancy per trade after costs (need > Rs0, have Rs0)
- FAIL: Profit factor (need >= 1.3, have None)
- PASS: Max drawdown (need < 10.0% and never halted, have 0.0%)
- FAIL: Beats liquid fund after AI cost (need yes, have no)
- PASS: Auditor mismatches (need 0, have 0)

**Not ready for real money.** Passing is necessary, not proof of an edge.

## Runner log (last 10 lines)
```
2026-11-09T04:51:00 BTC started 2026-11-07 enabled ['trend_ema20_50']
2026-11-09T04:59:22 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4435}
2026-11-09T13:47:10 data: {"GOLDPETAL": 6573, "SILVER100": 6574, "CRUDEOILM": 6581, "BTC": 4436}
2026-11-09T13:47:10 BTC: 1 new bar(s), at 2026-11-08
2026-11-09T23:19:47 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4436}
2026-11-09T23:19:47 GOLDPETAL: 1 new bar(s), at 2026-11-09
2026-11-10T07:39:37 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4437}
2026-11-10T07:39:37 BTC: 1 new bar(s), at 2026-11-09
2026-11-10T10:53:09 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4437}
2026-11-10T18:31:45 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4437}
```
