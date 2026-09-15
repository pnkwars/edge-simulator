# Edge Simulator

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%E2%80%9312-blue?style=flat-square" alt="Python 3.9-3.12">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
  <img src="https://img.shields.io/badge/chart.js-4.x-ff6384?style=flat-square" alt="Chart.js">
  <img src="https://img.shields.io/badge/tailwind-via%20CDN-38bdf8?style=flat-square" alt="Tailwind">
  <img src="https://img.shields.io/badge/local--first-no%20tracking-10ff7a?style=flat-square" alt="Local-first">
</p>

<p align="center"><i>Bet sizing you can actually trust — before you put money down.</i></p>

<p align="center">
  <b>Kelly Criterion</b> · <b>Monte Carlo</b> · <b>Parlay Builder</b> · <b>Risk &amp; Ruin</b><br>
  <sub>All in one page. No signup. No backend. Your numbers never leave the browser.</sub>
</p>

---

<p align="center">
  <img src="https://via.placeholder.com/960x480/0c1623/10ff7a?text=Edge+Simulator+%E2%80%94+Kelly+%7C+Monte+Carlo+%7C+Parlay+%7C+Risk" alt="Edge Simulator dashboard preview" width="960">
  <br><sub><i>Modern dashboard (Tailwind + Chart.js) — also available as a green-on-black CRT mode.</i></sub>
</p>

### Why this exists

Most bettors guess their stake. Edge Simulator does the opposite — you tell it what you think your edge is, and it shows what that edge is actually worth, how much it swings, and when it breaks.

If the answer is "don't bet," it says so plainly.

### What you get

| Area | What it shows | Why it matters |
|------|---------------|----------------|
| **Kelly** | Optimal `f*`, half / third / quarter Kelly, growth per bet, stake on your bankroll | Kelly maximizes growth, but full Kelly is rough. Half Kelly keeps ~75% of the growth with roughly half the pain. |
| **Monte Carlo** | 5,000+ simulated bankrolls, P5 / median / P95, profit rate, ruin % | Averages lie. The spread tells you if your P5 is near zero — which means you're betting too big. |
| **Lab** | 5 fractions head-to-head (0.25× → 1.5×) | Best median ≠ best risk. Watch how ruin spikes past 1×. |
| **Parlay** | Add legs, see combined `p` and `dec`, then compare parlay Kelly vs best single | Parlays look juicy until you multiply the variance. Usually singles are safer — the table proves it. |
| **Risk** | Streak odds, drawdown at your bet %, gambler's ruin | Small edges drown in streaks. This tab keeps you honest. |

Odds work however you keep them: `2.50` or `+150` / `-110` or `5/2`. Probability as `55%` or `0.55`.

---

### Get running in 30 seconds

```bash
git clone https://github.com/pnkwars/edge-simulator
cd edge-simulator

# Web UI — opens http://localhost:8765
python3 app.py
# → modern dashboard at /
# → CRT theme at /retro.html

# Or skip the browser entirely
python3 gamble.py                  # interactive terminal
python3 gamble.py kelly 55% 2.0    # one-liner
python3 gamble.py sim 1000 55% 2.0 0.05 500 5000
python3 gamble.py parlay 60%@1.91 55%@2.10 70%@1.50
```

No install step. `app.py` and `gamble.py` are standard library only — the web UI pulls Tailwind and Chart.js from a CDN.

> **Shortcuts:** press `1` Kelly, `2` Monte Carlo, `3` Lab, `4` Parlay, `5` Risk. Inputs auto-save to `localStorage` so you don't lose your numbers.

---

### How it thinks

**Kelly:** `f* = (b·p − q) / b` where `b = dec − 1` and `q = 1 − p`. The app also shows expected log-growth `g = p·ln(1+fb) + q·ln(1−f)` so you can see why half Kelly is often the sane default.

**Monte Carlo:** replays your bet `M` times across `N` worlds, sizing each bet as `f × bankroll`. No curve fitting — just your inputs, replayed.

**Parlay:** assumes independent legs: `p = ∏pᵢ` and `dec = ∏decᵢ`. That independence is a big assumption — the app says so up front and shows each leg's single Kelly next to the combined one.

**Risk:** straightforward streak math (`qⁿ`, `pⁿ`) plus drawdown from a fixed fraction and a quick gambler's ruin approximation for even-money stakes.

None of this is financial advice. It's a way to make your assumptions visible before you bet.

---

### Project layout

```
app.py              tiny static server on :8765 (no framework, no-store cache)
gamble.py           same math in a terminal UI — ANSI colors, sparklines, no deps
index.html          modern dashboard — Tailwind + Chart.js, fully responsive
retro.html          same app, green phosphor CRT skin
requirements.txt    only gunicorn (for hosting); the app itself needs nothing
```

### Stack

- **Frontend:** HTML + Tailwind CSS (CDN) + Chart.js 4.x — cards, hover tooltips, responsive charts that reflow at 375px and 1280px.
- **Backend:** there isn't one. `http.server` serves static files locally. That's the point.

### Deploying

Local use needs nothing. On Render / Railway / Fly.io, `requirements.txt` already includes `gunicorn`. If your host expects a WSGI entrypoint, add a small wrapper or run `python app.py` as the start command — `app.py` is `http.server`, not WSGI, so `gunicorn app:app` alone won't work (the comment in `requirements.txt` explains this).

### A quick note

If you came from "Gamble Terminal" — same project, new name. Everything else is backwards compatible; CLI flags and input formats didn't change.

---

### Contributing

Found a bug or have an idea? Open an issue — there are templates for bug reports and feature requests under `.github/ISSUE_TEMPLATE/`. Small, focused PRs are easiest to review. See [CONTRIBUTING.md](CONTRIBUTING.md) for the short workflow.

### Security

Please don't file public issues for security problems — see [SECURITY.md](SECURITY.md).

### License

MIT. Use it, fork it, ship it — just keep the notice. See [LICENSE](LICENSE).
