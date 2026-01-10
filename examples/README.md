# ProxyWhirl Examples

A curated, runnable gallery for ProxyWhirl. Everything defaults to offline-friendly mocks unless otherwise noted.

## Layout
- `python/` — numbered scripts for focused workflows:
  - `00_quickstart.py` — pool + rotator + mocked request
  - `10_rotation_strategies.py` — all strategies side-by-side
  - `20_retry_and_failover.py` — retries, circuit breakers, metrics
  - `30_health_monitoring.py` — concrete monitor subclass + eviction
  - `40_fetch_and_validate.py` — fetch/parse/validate with bundled assets
  - `50_persistence.py` — JSON + SQLite storage demos
  - `60_browser_rendering.py` — guarded Playwright example (requires `proxywhirl[js]`)
  - `70_tui_demo.py` — launches the TUI with demo proxies
  - `90_cli_walkthrough.sh` — CLI commands with safe defaults
- `notebooks/` — interactive guides:
  - `01_getting_started.ipynb` — fast onboarding
  - `09_quick_reference.ipynb` — copy/paste snippets
  - `20_end_to_end.ipynb` — full tour (API, CLI, storage)
- `assets/` — sample proxy lists (text/CSV/HTML) used by the fetch/validate examples.
- `_common.py` — small helpers shared by the scripts.

## Prereqs
```bash
uv sync --group dev --extra storage --extra js   # full toolchain
# or minimal
uv sync --group dev                              # base + tests
```
Playwright/browser rendering: `uv pip install "proxywhirl[js]" && playwright install chromium`

## Running
- Python scripts: `uv run python examples/python/00_quickstart.py`
- CLI walkthrough: `bash examples/python/90_cli_walkthrough.sh` (adjust commands as needed)
- Notebooks: open in your editor/VS Code and run cells top-to-bottom.

## Notes
- Scripts prefer mock transports and bundled assets to stay deterministic.
- Swap in real proxy sources/endpoints when you are ready for live traffic.
