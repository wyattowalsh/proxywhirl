#!/bin/bash
# Quick coverage check for core library files

echo "Running coverage on core library (excluding CLI/API)..."
uv run pytest tests/unit/ tests/integration/ \
    --cov=proxywhirl \
    --cov-report=term-missing \
    --cov-report=html:logs/htmlcov \
    -q \
    2>&1 | tee /tmp/coverage_output.txt

echo ""
echo "=== COVERAGE SUMMARY ==="
grep -A 20 "^Name" /tmp/coverage_output.txt | grep -E "^(Name|proxywhirl/(strategies|rotator|models|storage|__init__|exceptions|utils)\.py|TOTAL)"

echo ""
echo "Full report: logs/htmlcov/index.html"
