# Contributing to Edge Simulator

Thanks for considering a contribution!

## Getting started

```bash
git clone https://github.com/pnkwars/edge-simulator
cd edge-simulator
python3 app.py        # web UI
python3 gamble.py     # CLI
```

No build step — the web UI is static HTML + Tailwind/Chart.js CDN; Python is stdlib only.

## Guidelines

- Keep changes small and focused; one concern per PR.
- For UI changes, include a screenshot or short recording.
- Validate inputs — keep error messages clear and inline (red border + hint).
- Charts should remain responsive; test at 375px and 1280px.

## Pull requests

1. Fork, branch from `main` (`feat/...` or `fix/...`).
2. Commit with conventional messages (`feat:`, `fix:`, `docs:`, etc.).
3. Open a PR with context, reproduction steps, and before/after if visual.

## Reporting issues

Use the **Issues** tab templates (Bug report / Feature request). Include steps to reproduce, expected vs actual, and browser/Python version.
