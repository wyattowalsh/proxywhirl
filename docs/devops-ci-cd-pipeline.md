# CI/CD Pipeline Architecture

## GitHub Actions Workflow

```yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make lint
      - run: make format-check

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make test
      - uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make build
      - run: docker push proxywhirl:${{ github.sha }}
```

## Pipeline Stages

1. **Lint & Format** (parallel, 2 min)
2. **Unit Tests** (5 min)
3. **Integration Tests** (10 min)
4. **Build Docker Image** (5 min)
5. **Push to Registry** (2 min)
6. **Deploy to Staging** (5 min)
7. **Smoke Tests** (2 min)
8. **Deploy to Production** (blue-green, 10 min)

## Deployment Strategy

- **Staging**: Auto-deploy on main branch merge
- **Production**: Manual approval required
- **Rollback**: One-click via GitHub Actions dispatch

## Metrics

- Pipeline duration: < 30 min
- Success rate: > 99%
- Deployment frequency: > 2x daily
- MTTR (mean time to recovery): < 5 min
