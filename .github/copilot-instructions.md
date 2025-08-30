# github copilot custom project instructions for `proxywhirl`

> `proxywhirl` is an advanced rotating proxy system that collects free online proxies, efficiently and robustly validates them, caches them in a variety of formats (memory, JSON, SQLite), and offers a rotating proxy interface for seamless integration with applications. Interfaces include: Python3 package, Typer CLI, TUI, FastAPI API, and Vite Frontend. Utility logic is included to produce analytics, reports, proxy lists, and more.

## repo structure

- **[`.github/`](./.github/)**                  - GitHub workflows, issue templates, and project metadata ([devops.md](./.github/devops.md))
- **[`docs/`](./docs/)**                        - Next.js-based FumaDocs documentation site with shadcn-ui + Tailwind CSS v4 ([docs.instructions.md](./.github/docs.instructions.md))
- **[`examples/`](./examples/)**                - Sample configurations, notebooks, and usage examples
- **[`frontend/`](./frontend/)**                - Vite-powered React frontend for proxy management UI ([frontend](./.github/frontend))
- **[`lists/`](./lists/)**                      - Pre-validated proxy lists and collection data
- **[`proxywhirl/`](./proxywhirl/)**            - Core Python package with CLI, API, validator, and rotator logic ([backend.instructions.md](./.github/backend.instructions.md))
- **[`tests/`](./tests/)**                      - Comprehensive test suite with unit, integration, and E2E tests ([backend.instructions.md](./.github/backend.instructions.md))
- **[`.gitignore`](./.gitignore)**              - Git ignore patterns for Python, Node.js, and build artifacts
- **[`.python-version`](./.python-version)**    - Python version specification for pyenv/uv
- **[`LICENSE`](./LICENSE)**                    - Open source license terms
- **[`Makefile`](./Makefile)**                  - Development workflow automation and task runners ([devops.md](./.github/devops.md))
- **[`pyproject.toml`](./pyproject.toml)**      - Python project configuration with uv dependency management ([backend.instructions.md](./.github/backend.instructions.md))
- **[`README.md`](./README.md)**                - Project overview, installation, and usage documentation

---
