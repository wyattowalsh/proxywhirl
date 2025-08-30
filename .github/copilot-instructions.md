# github copilot custom project instructions for `proxywhirl`

> `proxywhirl` is a rotating proxy system for web data extraction workflows that collects, validates, analyzes, reports, caches, and serves proxy servers via a. variety of interfaces: Python3 package, Typer CLI, Textual TUI, FastAPI API, and Vite/React Frontend. Utility logic is included to execute analytics, compile reports, aggregate proxy lists, and more. Logic implementations aim to be maximally elegant, performant, robust, flexible, clear, succinct, graceful, and developer-friendly.

---

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
