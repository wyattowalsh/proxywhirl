# R-008: RV-010 Module-Complexity Backlog (Read-Only, No Code Change)

Large-module complexity candidates identified for future refactoring (out of scope for this
remediation per Part 6 approval gates — backlog only):

| Module | Approx. LOC | Notes |
| ------ | ----------- | ----- |
| `proxywhirl/cli.py` | large, many Typer subcommands | Candidate: split subcommands into `cli/` package (`pool.py`, `config.py`, `fetch.py`, etc.) |
| `proxywhirl/strategies.py` | ~1900+ lines, 9 strategy classes | Candidate: one module per strategy under `strategies/` package, keep `StrategyRegistry` + protocol in `__init__.py` |
| `proxywhirl/fetchers.py` | ~1990 lines, parsers + fetcher + validator | Candidate: split into `fetchers/parsers.py`, `fetchers/validator.py`, `fetchers/fetcher.py` |
| `proxywhirl/storage.py` | ~1740+ lines, `FileStorage` + `SQLiteStorage` | Candidate: split into `storage/file.py`, `storage/sqlite.py`, shared helpers in `storage/_common.py` |

## Recommendation

Track as a backlog item (RV-010: `backlog`). Any split must preserve the public `__init__.py` export
surface (`proxywhirl/__init__.py`) unchanged and requires human sign-off per `AGENTS.md` "Ask First:
Public API changes" — do not attempt module splits opportunistically inside this remediation pass.
