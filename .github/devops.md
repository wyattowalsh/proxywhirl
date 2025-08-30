---
applyTo: ".github/workflows/**,.github/ISSUE_TEMPLATE/**,.github/PULL_REQUEST_TEMPLATE/**,.github/**/*.md"
---

# ProxyWhirl Deployment Instructions

Follow these instructions for advanced CI/CD, security, and zero-downtime deployment with AI assistance.

## CI/CD Pipeline Configuration

### GitHub Actions Workflow Standards
All workflows must follow these patterns for ProxyWhirl:

```yaml
# Required workflow structure
name: ProxyWhirl [Pipeline Name]

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target Environment'
        required: true
        default: 'dev'
        type: choice
        options: ['dev', 'staging', 'prod']

env:
  PYTHON_VERSION: "3.13"
  NODE_VERSION: "20"
  UV_CACHE_DIR: ~/.cache/uv
  PNPM_CACHE_DIR: ~/.pnpm-store
```

### OIDC Security Requirements (MANDATORY)
Always use OIDC for trusted publishing:

```yaml
# Required permissions for OIDC
permissions:
  id-token: write      # OIDC token generation
  contents: read       # Repository access
  attestations: write  # Provenance attestation
  security-events: write  # SARIF reporting

jobs:
  secure-publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python with OIDC
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Setup uv with caching
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      
      - name: Build with provenance
        run: uv build --wheel
      
      - name: Publish with OIDC (Trusted Publishing)
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          attestations: true  # Generate provenance attestation
```

### Advanced Caching Strategy
Implement intelligent caching for all dependencies:

```yaml
# Multi-layer caching for optimal performance
- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.cache/pip
      ${{ github.workspace }}/.venv
    key: python-${{ runner.os }}-${{ hashFiles('uv.lock', 'pyproject.toml') }}
    restore-keys: |
      python-${{ runner.os }}-

- name: Cache analysis tools
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/ruff
      ~/.cache/mypy
      ~/.cache/pylint
    key: analysis-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}

- name: Cache Node.js dependencies (docs)
  uses: actions/cache@v4
  with:
    path: |
      ~/.pnpm-store
      docs/node_modules
      docs/.next/cache
    key: node-${{ runner.os }}-${{ hashFiles('docs/pnpm-lock.yaml') }}
```

## Security Implementation Requirements

### SAST/DAST Integration (MANDATORY)
All workflows must include security scanning:

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Python Security Scanning
      run: |
        uv run bandit -r proxywhirl -f sarif -o bandit-report.sarif
        uv run safety check --json --output safety-report.json
        uv run pip-audit --format=sarif --output=pip-audit.sarif
    
    - name: Upload SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: bandit-report.sarif
    
    - name: CodeQL Analysis
      uses: github/codeql-action/analyze@v3
      with:
        languages: python
        queries: security-extended,security-and-quality
```

### Dependency Management Automation
Configure Dependabot with security-first approach:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "10:00"
    target-branch: "dev"
    groups:
      security-updates:
        applies-to: security-updates
        patterns: ["*"]
      critical-dependencies:
        patterns: ["pydantic*", "httpx*", "loguru*"]
    commit-message:
      prefix: "deps"
      include: "scope"
```

## Matrix Testing Strategy

### Cross-Platform Testing Requirements
Test across multiple environments:

```yaml
quality-matrix:
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
      python-version: ["3.13", "3.14-dev"]
      include:
        - os: ubuntu-latest
          platform: linux
          cache-prefix: linux
        - os: macos-latest
          platform: darwin
          cache-prefix: macos
        - os: windows-latest
          platform: win32
          cache-prefix: windows

  runs-on: ${{ matrix.os }}
  
  steps:
    - name: Quality Pipeline Execution
      run: |
        # Platform-specific quality checks
        if [[ "${{ matrix.platform }}" == "windows" ]]; then
          # Windows-specific testing adjustments
          export PYTEST_TIMEOUT=300
        fi
        
        # Execute comprehensive quality pipeline
        uv run pytest -n auto --cov=proxywhirl --benchmark-autosave
        uv run ruff check . --output-format=github
        uv run mypy proxywhirl --strict
```

## Performance Monitoring Integration

### Benchmark Regression Detection
Monitor performance across releases:

```yaml
performance-validation:
  runs-on: ubuntu-latest
  steps:
    - name: Benchmark Execution
      run: |
        # Run performance benchmarks
        uv run pytest tests/benchmarks/ \
          --benchmark-only \
          --benchmark-json=benchmark-results.json \
          --benchmark-autosave
    
    - name: Performance Regression Analysis
      run: |
        # Compare against baseline performance
        uv run python scripts/analyze_performance.py \
          --current=benchmark-results.json \
          --baseline=main \
          --threshold=1.2 \
          --output=performance-report.md
    
    - name: Performance Report Comment
      uses: actions/github-script@v7
      if: github.event_name == 'pull_request'
      with:
        script: |
          const fs = require('fs')
          const report = fs.readFileSync('performance-report.md', 'utf8')
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## Performance Analysis\n\n${report}`
          })
```

## AI-Enhanced Deployment Validation

### MCP Tool Integration for Infrastructure
Use MCP tools for deployment validation:

```bash
# Infrastructure validation pipeline
mcp_package_versi_check_github_actions([
  {"name": "actions/checkout", "version": "v4"},
  {"name": "astral-sh/setup-uv", "version": "v4"},
  {"name": "actions/setup-node", "version": "v4"}
])

# Security best practices research
mcp_brave_search_brave_web_search("GitHub OIDC trusted publishing 2025")
mcp_docfork_get-library-docs("actions/runner", "security hardening")

# Deployment validation
mcp_sequential_th2_sequentialthinking_tools("validate deployment security")
```

### Automated Health Checks
Implement comprehensive health monitoring:

```yaml
health-validation:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Post-Deploy Health Checks
      run: |
        # Validate PyPI package availability
        timeout 300 pip install proxywhirl==${{ github.ref_name }}
        
        # Test package functionality
        python -c "
        import proxywhirl
        pw = proxywhirl.ProxyWhirl()
        print(f'ProxyWhirl v{proxywhirl.__version__} loaded successfully')
        "
        
        # Validate documentation site
        curl -f -s -o /dev/null https://proxywhirl.dev/health || exit 1
    
    - name: Smoke Test Execution
      run: |
        # Execute critical path testing
        uv run python -m proxywhirl --help
        uv run python -c "
        import asyncio
        from proxywhirl import ProxyWhirl
        
        async def smoke_test():
            pw = ProxyWhirl()
            assert hasattr(pw, 'load_proxies')
            print('✅ Smoke test passed')
        
        asyncio.run(smoke_test())
        "
```

## Release Management Instructions

### Semantic Versioning Automation
Automate version management:

```yaml
release-automation:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Generate Release Notes
      id: release-notes
      run: |
        # Auto-generate release notes from conventional commits
        npx conventional-changelog-cli -p angular -i CHANGELOG.md -s
        
        # Extract version from pyproject.toml
        VERSION=$(uv run python -c "
        import toml
        print(toml.load('pyproject.toml')['project']['version'])
        ")
        echo "version=$VERSION" >> $GITHUB_OUTPUT
    
    - name: Create GitHub Release
      uses: actions/create-release@v1
      with:
        tag_name: v${{ steps.release-notes.outputs.version }}
        release_name: ProxyWhirl v${{ steps.release-notes.outputs.version }}
        body_path: CHANGELOG.md
        draft: false
        prerelease: false
```

## Zero-Downtime Deployment Strategy

### Blue-Green Deployment Implementation
Implement seamless deployments:

```yaml
blue-green-deployment:
  runs-on: ubuntu-latest
  environment: production
  steps:
    - name: Deploy to Staging (Green)
      run: |
        # Deploy to staging environment first
        echo "Deploying to staging environment"
        # Staging deployment logic
    
    - name: Health Check Staging
      run: |
        # Comprehensive health validation
        curl -f https://staging.proxywhirl.dev/health
        # Load testing with minimal traffic
    
    - name: Traffic Switch (Blue → Green)
      if: success()
      run: |
        # Gradual traffic switching
        echo "Switching traffic to new deployment"
        # Traffic routing logic
    
    - name: Rollback on Failure
      if: failure()
      run: |
        # Automatic rollback mechanism
        echo "Rolling back to previous stable version"
        # Rollback logic
```

## Anti-Patterns (FORBIDDEN)

### Security Violations
- **FORBIDDEN**: Hardcoded secrets or API keys in workflows
- **FORBIDDEN**: Bypassing OIDC for PyPI publishing
- **FORBIDDEN**: Missing provenance attestation
- **FORBIDDEN**: Workflows without proper permissions configuration
- **FORBIDDEN**: Direct production deployment without staging validation

### Performance Violations
- **FORBIDDEN**: Missing caching strategies for dependencies
- **FORBIDDEN**: Serial execution where parallel is possible
- **FORBIDDEN**: Ignoring benchmark regression thresholds
- **FORBIDDEN**: Missing timeout configurations for long-running jobs

### Quality Violations
- **FORBIDDEN**: Deploying without comprehensive test execution
- **FORBIDDEN**: Bypassing security scanning (SAST/DAST)
- **FORBIDDEN**: Missing matrix testing across platforms
- **FORBIDDEN**: Workflows without proper error handling and rollback

### Monitoring Violations
- **FORBIDDEN**: Deployments without health checks
- **FORBIDDEN**: Missing performance monitoring and alerting
- **FORBIDDEN**: No automated rollback mechanisms
- **FORBIDDEN**: Insufficient logging and observability

Follow these instructions consistently for secure, performant, and reliable ProxyWhirl deployments with comprehensive AI-assisted validation.
