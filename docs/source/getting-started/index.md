---
title: Getting Started
---

ProxyWhirl supports Python 3.9+ with rich extras for validation, storage, and browser rendering. Follow these steps to install dependencies, verify the quickstart, and ship production-ready rotation in minutes.

# Getting Started

## 1. Install with uv

```bash
uv sync --group dev
uv run python -c "import proxywhirl; print(proxywhirl.__version__)"
```

```{note}
The project constitution requires `uv run` for every Python command to guarantee reproducible environments.
```

## 2. Run the smoke suite

```bash
uv run pytest
uv run mypy --strict proxywhirl
uv run ruff check proxywhirl
```

These checks mirror the CI template in :doc:`guides/automation` so local changes remain merge-ready.

## 3. Validate the quickstart script

```bash
uv run python validate_quickstart.py
```

The helper script exercises every quickstart snippet and fails fast if packaging, imports, or API signatures drift.

## 4. Explore next steps

- :doc:`rotation-strategies` — choose and compose rotation strategies.
- :doc:`../reference/rest-api` — operate ProxyWhirl over REST.
- :doc:`../guides/automation` — add docs and strategy validation to CI.

```{toctree}
:maxdepth: 2
:hidden:

rotation-strategies
```
