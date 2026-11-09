# Path from paper to real money (Rs15,000 to Rs20,000)

This is a process, not a promise. Most retail commodity traders lose money. You can lose all of what you put in.

## Stage 0: paper, same size as the real plan (now)
config.json is set to Rs15,000 with the same rules you would trade live: 1 lot, 2.5% max risk per trade, 3% daily and 6% weekly loss limits, 10% drawdown halt.
The scheduler runs the agency daily. Day 15 gives a first checkpoint (RESULT_AFTER_15_DAYS.md). Day 60 gives the real review (RESULT_AFTER_60_DAYS.md) with the go-live gates.
Gates (dashboard shows them live): 60+ trading days, 30+ closed trades, positive expectancy after costs, profit factor 1.3+, drawdown under 10% and never halted, beats the liquid fund, books reconcile.
Fifteen days alone cannot pass them, on purpose.

## Stage 1: real money, tiny and manual (only if every gate passes)
- Use Rs15,000, not Rs20,000. One lot only.
- Every day the dashboard shows an ORDER TICKET. You place the order and the stop-loss yourself in your broker app. Nothing is automated, so SEBI's static-IP algo rules do not apply to you.
- Record your real fill prices next to the paper ones. If real results trail paper by more than the slippage assumed, stop and tell me.
- Hard stop for you: if real equity falls 10% (about Rs1,500), stop for at least a week and review. The dashboard has a KILL SWITCH.
- Run at least 30 real trades before considering anything bigger.

## Stage 2: scale up, only after Stage 1 matches paper
Rs20,000 or a second lot only if real results over 30+ trades are in line with paper after costs.

## Stage 3: optional automation
Automated orders need a broker API with a fixed static IP address (SEBI framework, effective 1 April 2026), 2FA, and your own API keys. A normal home internet connection usually will not qualify. I have not built or tested any broker order adapter, and I will not ship one untested for real money. If you want it, pick the broker and we test it with a single lot first.

## What the numbers look like at this size (estimates)
- Margin for one Gold Petal lot: roughly Rs1,400 to Rs2,000 (about 9-13% of Rs15,000).
- A normal stop (1.5 x daily range) is about Rs275 per lot: about 1.8% of Rs15,000, 1.4% of Rs20,000.
- Costs per round trip: roughly Rs13 plus about Rs4 slippage.
- The 10% halt line is about Rs1,500: five full stops in a row.
- Rollover: Gold Petal expires monthly and settles by delivery. The paper test uses one continuous price series and ignores rollover costs and gaps, so real results will be a little worse.
