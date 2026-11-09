# MCX multi-asset paper portfolio (gold, silver, crude, Bitcoin), hands-off

PAPER TRADING ONLY. No orders, no broker connection, no credentials.

## Setup (Windows, once)
1. Install Python 3.10+ from python.org (tick "Add python.exe to PATH").
2. Unzip this folder somewhere permanent (for example C:\mcx_agency) and double-click `setup_windows.bat`.
3. When asked, type today's MCX Gold Petal price per gram (from your broker app).
That's all. A Windows scheduled task named MCXAgency then runs every day at 8:00 AM (and catches up if the PC was off).
After 15 trading days it writes `RESULT_AFTER_15_DAYS.md`, opens it, and removes its own schedule.

Live dashboard: http://127.0.0.1:8765 (starts at login; or double-click `open_dashboard.bat`). Preview the layout any time with http://127.0.0.1:8765/?demo=1. Progress log: `logs\run.log`. To cancel: `stop_and_remove.bat`.
Mac/Linux: run `python3 run_scheduled.py` daily from cron, e.g. `30 8 * * * cd /path/mcx_agency && python3 run_scheduled.py`.

## Important: the data is a PROXY
Yahoo Finance has no MCX prices. The agency uses COMEX gold futures x USD/INR / 31.1035, scaled to match the MCX price you typed.
Real MCX Gold Petal differs (import duty, premium, monthly contracts, different trading hours), so results show how the process behaves, not what MCX would have paid.
To use real MCX data instead, replace data\goldpetal.csv (date,open,high,low,close) and skip fetching.

## The agents
Researcher, Quant (strategy must be profitable after costs both in-sample and out-of-sample to vote), CIO, Risk Guardian (veto, loss limits, 10% drawdown halt), Cost Analyst, Paper Broker, Auditor, Survival Officer. See agency/agents.py.

## Honest limits
- Uses all available history (roughly 25 years). It cannot have "40 years of experience".
- With several strategies tested on noisy data, one can qualify by luck. Fifteen trading days cannot prove an edge.
- 1 lot of Gold Petal needs about 6% of Rs4,500 at risk, so config.json allows 7% per trade. config_strict.json (0.5%) vetoes everything.
- Needs the PC on and online around 8:00 AM IST. Missed runs catch up the next time it is on.
- The Windows setup and scheduled task were not tested on a real PC by me. If setup prints an error, send me the message.

## Dashboard notes
- It reads state.json and data\goldpetal.csv from this folder and refreshes every 5 seconds. The agency itself only advances once a day (daily bars), so numbers change when the 8:00 AM run finishes. "Update now" runs it immediately.
- It listens on 127.0.0.1 only, so only this PC can open it.
- The page layout was tested with a simulated browser (no errors, all panels fill). I could not view it in a real browser, so tell me if anything looks wrong.

## Live market on the dashboard
The top card shows a ticking gold price (rupees per gram), the intraday chart, session change, and your paper position's live P&L and distance to the stop. It refreshes every 15 seconds.
- Source: Yahoo Finance COMEX gold x USD/INR, scaled to MCX by the price you typed at setup. It can lag a few minutes and is not MCX tick data. It goes stale when COMEX is closed (weekends, the daily break).
- It is display only. The agency still decides once a day from daily bars.
- For real MCX ticks you would need a broker data API (Zerodha Kite Connect, Upstox, Dhan or Angel One). That needs your own API keys kept on your PC, and I have not built or tested those adapters.

## Going live later
See LIVE_PLAN.md. config.json now mirrors the real plan (Rs15,000, 1 lot, 2.5% risk per trade). config_small_4500.json is the old Rs4,500 version.
New in this version: go-live gates and a daily order ticket (dashboard + ORDER_TICKET.md), a KILL SWITCH button (creates KILL_SWITCH.txt), a day-15 checkpoint and a day-60 review. The scheduler now runs 60 trading days, not 15.

## Multi-asset version (current)
config_multi.json holds Rs15,000 and four candidate instruments: Gold Petal, Silver 100, Crude Oil Mini, Bitcoin (paper only).
On the first run a fit screen decides which ones the money can actually fund under the risk rules: a lot's margin must be under 50% of capital and a normal stop must not be far above the per-trade limit (2.5% = Rs375). Weights then split the money. Unfunded assets are listed with the reason on the dashboard and in the result files.
Each funded asset runs as its own sleeve (state_<ASSET>.json) with the same agents. A portfolio drawdown of 10% halts every sleeve.
Bitcoin is long-only, paper-only forever, with fees and the 30% gain tax charged as costs. It never gets a real-order ticket.
The dashboard shows total money, profit and loss, every trade across assets, and a tab per asset.
The older single-gold tools (run.py backtest/replay/daily with config.json) still work.
Sleeve sizes are fixed at the first run. Delete portfolio.json and state_*.json (only while flat) to re-run the fit screen.
Bitcoin's fixed lot (0.0005 BTC) can grow too big for its sleeve if the price rises a lot; the Risk Guardian then vetoes entries.

## Cloud mode (no PC needed)
Upload mcx_bundle.py and .github/workflows/paper.yml to a GitHub repository. GitHub runs the agency every morning (06:00 India time), commits the state, and writes PAPER_REPORT.md. Known MCX prices in config_multi.json ("calibration") scale the proxy prices automatically; edit them there if you want fresher anchors.
If Yahoo Finance blocks GitHub's servers, the runner log (logs/run.log) says so and the next run retries.
