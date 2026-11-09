"""Opens a GitHub issue that @mentions the repo owner, which the GitHub app turns into a phone notification."""
import json, os, urllib.request, datetime as dt

def _issue(title, body):
    tok, repo = os.environ.get('GITHUB_TOKEN'), os.environ.get('GITHUB_REPOSITORY')
    if not tok or not repo: return False
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/issues', data=json.dumps({'title': title, 'body': body}).encode(), method='POST',
        headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'paper-bot'})
    try: urllib.request.urlopen(req, timeout=20); return True
    except Exception: return False

def check(cfg, equity, halted, summary):
    """Alert on each new profit step reached today, and once when the risk halt triggers. Paper money only."""
    step = cfg.get('alerts', {}).get('profit_step_inr', 150); total = cfg['capital_inr']; profit = equity - total
    ist = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)).date().isoformat()
    st = json.load(open('alert_state.json')) if os.path.exists('alert_state.json') else {}
    if st.get('date') != ist: st = {'date': ist, 'max_level': 0, 'halt_sent': st.get('halt_sent', False)}
    owner = '@' + os.environ.get('GITHUB_REPOSITORY_OWNER', 'rangragstudio'); sent = []
    level = int(profit // step) if profit > 0 else 0
    if level > st['max_level']:
        if _issue(f'Paper profit +Rs{profit:,.0f} ({profit / total * 100:+.2f}%)', f'{owner} PAPER portfolio is up Rs{profit:,.2f} (total Rs{equity:,.2f}).\n\n{summary}\n\nSee PAPER_REPORT.md. Paper money only.'):
            sent.append('profit')
        st['max_level'] = level
    if halted and not st.get('halt_sent'):
        if _issue('Paper portfolio HALTED by Risk Guardian', f'{owner} The 10% portfolio drawdown limit was hit. All assets are halted.\n\n{summary}'): sent.append('halt')
        st['halt_sent'] = True
    if not halted: st['halt_sent'] = False
    json.dump(st, open('alert_state.json', 'w')); return sent
