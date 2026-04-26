#!/bin/bash
set -euo pipefail

# ProxyWhirl Health Check Script

API_URL="${PROXYWHIRL_API_URL:-http://localhost:8000}"
TIMEOUT=5

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_endpoint() {
    local endpoint="$1"
    local expected_status="${2:-200}"
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" -m "$TIMEOUT" "$API_URL$endpoint" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $endpoint ($response)"
        return 0
    else
        echo -e "${RED}✗${NC} $endpoint (expected $expected_status, got $response)"
        return 1
    fi
}

main() {
    echo "Health Check: $API_URL"
    echo ""
    
    local failed=0
    
    check_endpoint "/api/v1/health" "200" || ((failed++))
    check_endpoint "/api/v1/proxy" "200" || ((failed++))
    check_endpoint "/api/v1/health/metrics" "200" || ((failed++))
    
    echo ""
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}All health checks passed${NC}"
        exit 0
    else
        echo -e "${RED}$failed health checks failed${NC}"
        exit 1
    fi
}

main
