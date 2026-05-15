# Validation Matrix

| Surface | Command | Expected Result |
| --- | --- | --- |
| OpenSpec | `npx -y @fission-ai/openspec@latest validate --all --json` | Change artifacts validate before implementation proceeds. |
| Lint | `uv run ruff check .` | Python source and tests pass lint. |
| Format | `uv run ruff format --check .` | Python source and tests are formatted. |
| Types | `uv run ty check proxywhirl/` | Package type checks under configured rules. |
| Focused tests | `uv run pytest tests/unit/test_api.py tests/unit/test_api_auth.py tests/unit/test_cli.py tests/unit/test_sqlite_storage.py tests/unit/test_sources.py tests/unit/test_strategy_registry.py -q` | Changed API, auth, CLI, storage, sources, and strategy contracts pass. |
| Full tests | `uv run pytest -m "not slow" --cov=proxywhirl --cov-report=xml --cov-report=term-missing --cov-report=json -q` | Non-slow suite passes with coverage reports. |
| Sources | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5` | Every enabled source validates successfully. |
| Docs | `cd docs && uv run --extra docs sphinx-build -M html source build -W --keep-going` | Sphinx build completes without warnings. |
| Packaging | `uv run python -m build` | Source and wheel distributions build. |
| Workflows | `actionlint .github/workflows/*.yml` | Remaining workflows are syntactically valid. |

## Blockers

- External source volatility can fail the source gate; fix by repairing or
  disabling the specific source with rationale.
- Missing local `actionlint` blocks workflow linting locally; CI still owns the
  check if the binary is unavailable.
