# ProxyWhirl Development Makefile
# Python 3.13+ library for rotating proxy management

.DEFAULT_GOAL := help
.PHONY: help setup sync-dev sync-prod dev test format lint clean docs-dev docs-build docs-deps

# Colors for pretty output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Python environment
VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv

help: ## Show this help message
	@echo "$(CYAN)ProxyWhirl Development Commands$(RESET)"
	@echo "$(YELLOW)Environment Management:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(setup|sync)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo "$(YELLOW)Development Workflow:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(dev|test|format|lint)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo "$(YELLOW)Documentation & UI:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "docs|frontend|ui" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo "$(YELLOW)Utilities:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "clean|validate" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Environment Management
setup: ## Create virtual environment and sync all dependencies
	@echo "$(CYAN)Setting up Python environment...$(RESET)"
	$(UV) venv && source $(VENV)/bin/activate
	@echo "$(CYAN)Syncing all dependencies...$(RESET)"
	$(UV) sync --all-groups
	@echo "$(GREEN)✓ Environment setup complete$(RESET)"

ci-setup: ## Setup for CI environment (includes PATH export)
	@echo "$(CYAN)Setting up CI environment...$(RESET)"
	$(UV) sync --all-groups
	@echo "$$(pwd)/.venv/bin" >> $$GITHUB_PATH
	@echo "$(GREEN)✓ CI environment setup complete$(RESET)"
	
sync-dev: ## Sync development dependencies only
	@echo "$(CYAN)Syncing development dependencies...$(RESET)"
	$(UV) sync --group dev --group test --group lint --group format
	@echo "$(GREEN)✓ Development dependencies synced$(RESET)"

sync-prod: ## Sync production dependencies only
	@echo "$(CYAN)Syncing production dependencies...$(RESET)"
	$(UV) sync
	@echo "$(GREEN)✓ Production dependencies synced$(RESET)"

# Development Workflow  
dev: docs-dev ## Start documentation development server (alias for docs-dev)

test: ## Run all tests with coverage
	@echo "$(CYAN)Running tests with pytest...$(RESET)"
	$(UV) run pytest
	@echo "$(GREEN)✓ Tests completed$(RESET)"

format: ## Format code with black and isort
	@echo "$(CYAN)Formatting code with black...$(RESET)"
	$(UV) run black proxywhirl tests
	@echo "$(CYAN)Sorting imports with isort...$(RESET)"
	$(UV) run isort proxywhirl tests
	@echo "$(GREEN)✓ Code formatting complete$(RESET)"

lint: ## Run all linters (ruff, pylint, mypy) in sequence
	@echo "$(CYAN)Running ruff linter...$(RESET)"
	$(UV) run ruff check
	@echo "$(CYAN)Running pylint...$(RESET)"
	$(UV) run pylint proxywhirl
	@echo "$(CYAN)Running mypy type checker...$(RESET)"
	$(UV) run mypy proxywhirl
	@echo "$(GREEN)✓ All linting checks passed$(RESET)"

# Quality gate that runs everything in correct order
quality: format lint test ## Run complete quality pipeline: format → lint → test
	@echo "$(GREEN)✓ Quality pipeline completed successfully$(RESET)"

# Documentation
docs-deps: ## Install documentation dependencies
	@echo "$(CYAN)Installing documentation dependencies...$(RESET)"
	cd docs && pnpm install --frozen-lockfile
	@echo "$(GREEN)✓ Documentation dependencies installed$(RESET)"

docs-dev: ## Start documentation development server
	@echo "$(CYAN)Starting documentation development server...$(RESET)"
	@echo "$(YELLOW)Server will be available at http://localhost:3000$(RESET)"
	cd docs && pnpm dev

docs-build: ## Build documentation for production
	@echo "$(CYAN)Building documentation...$(RESET)"
	cd docs && pnpm build
	@echo "$(GREEN)✓ Documentation built successfully$(RESET)"

# Frontend
frontend-deps: ## Install frontend dependencies
	@echo "$(CYAN)Installing frontend dependencies...$(RESET)"
	cd frontend && pnpm install --frozen-lockfile
	@echo "$(GREEN)✓ Frontend dependencies installed$(RESET)"

frontend-dev: ## Start frontend development server
	@echo "$(CYAN)Starting frontend development server...$(RESET)"
	@echo "$(YELLOW)Server will be available at http://localhost:5173$(RESET)"
	cd frontend && pnpm dev

frontend-build: ## Build frontend for production
	@echo "$(CYAN)Building frontend...$(RESET)"
	cd frontend && pnpm build
	@echo "$(GREEN)✓ Frontend built successfully$(RESET)"

frontend-lint: ## Lint frontend code
	@echo "$(CYAN)Linting frontend code...$(RESET)"
	cd frontend && pnpm lint
	@echo "$(GREEN)✓ Frontend linting complete$(RESET)"

# Combined targets
ui-deps: docs-deps frontend-deps ## Install all UI dependencies (docs + frontend)

ui-build: docs-build frontend-build ## Build all UIs (docs + frontend)

ui-dev: ## Start both documentation and frontend servers (requires tmux)
	@echo "$(CYAN)Starting both UI development servers...$(RESET)"
	@echo "$(YELLOW)Documentation: http://localhost:3000$(RESET)"
	@echo "$(YELLOW)Frontend: http://localhost:5173$(RESET)"
	@if command -v tmux >/dev/null 2>&1; then \
		tmux new-session -d -s proxywhirl-dev "cd docs && pnpm dev" \; \
		split-window -h "cd frontend && pnpm dev" \; \
		attach-session -t proxywhirl-dev; \
	else \
		echo "$(RED)tmux not found. Starting docs server only...$(RESET)"; \
		make docs-dev; \
	fi

# Utilities
validate-pkgmgrs: ## Validate package manager consistency (uv + pnpm)
	@echo "$(CYAN)Validating package manager consistency...$(RESET)"
	./scripts/validate-package-managers.sh
	@echo "$(GREEN)✓ Package manager validation complete$(RESET)"

clean: ## Clean up build artifacts, cache, and temporary files
	@echo "$(CYAN)Cleaning up build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf logs/.coverage
	rm -rf logs/coverage/
	rm -rf logs/*.html
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	cd docs && rm -rf .next/ && rm -rf out/
	cd frontend && rm -rf dist/ && rm -rf node_modules/.vite/
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

# Common development commands
install: setup ## Alias for setup
deps: ui-deps ## Alias for ui-deps (docs + frontend)
serve: docs-dev ## Alias for docs-dev
build: ui-build ## Alias for ui-build