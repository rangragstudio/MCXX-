# Paper portfolio report

Updated: 2026-11-09 04:59 UTC. **PAPER TRADING with simulated fills on proxy prices. No real money, no real orders.**

## Total money now: Rs15,000.00

- Based on the last daily close (no fresh live price).
- Profit / loss: **+Rs0.00 (+0.00%)** since start with Rs15,000
- Day 0 of 60 (MCX trading days). Data through 2026-11-08.
- Closed trades: 0. Costs and tax paid: Rs0.00. Risk vetoes/blocks: 0. Halted: no.

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

- FAIL: Paper trading days (need >= 60, have 0)
- FAIL: Closed paper trades (need >= 30, have 0)
- FAIL: Expectancy per trade after costs (need > Rs0, have Rs0)
- FAIL: Profit factor (need >= 1.3, have None)
- PASS: Max drawdown (need < 10.0% and never halted, have 0.0%)
- FAIL: Beats liquid fund after AI cost (need yes, have no)
- PASS: Auditor mismatches (need 0, have 0)

**Not ready for real money.** Passing is necessary, not proof of an edge.

## Runner log (last 10 lines)
```
2026-11-09T04:50:54 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4435}
2026-11-09T04:50:54 portfolio created: {"GOLDPETAL": 9000, "SILVER100": 0, "CRUDEOILM": 0, "BTC": 6000}
2026-11-09T04:50:58 GOLDPETAL started 2026-11-08 enabled none
2026-11-09T04:51:00 BTC started 2026-11-07 enabled ['trend_ema20_50']
2026-11-09T04:59:22 data: {"GOLDPETAL": 6574, "SILVER100": 6575, "CRUDEOILM": 6582, "BTC": 4435}
```
