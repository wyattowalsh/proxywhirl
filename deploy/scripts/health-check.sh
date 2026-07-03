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

    local curl_args=("-s" "-o" "/dev/null" "-w" "%{http_code}" "-m" "$TIMEOUT")
    if [ -n "${PROXYWHIRL_API_KEY:-}" ]; then
        curl_args+=("-H" "X-API-Key: $PROXYWHIRL_API_KEY")
    fi

    local response
    response=$(curl "${curl_args[@]}" "$API_URL$endpoint" || echo "000")
    
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
    
    check_endpoint "/api/ready" "200" || ((failed++))
    if [ -n "${PROXYWHIRL_API_KEY:-}" ] || [ "${PROXYWHIRL_PUBLIC_METRICS:-false}" = "true" ]; then
        check_endpoint "/api/metrics" "200" || ((failed++))
    else
        echo -e "${YELLOW}!${NC} /api/metrics skipped (set PROXYWHIRL_API_KEY or PROXYWHIRL_PUBLIC_METRICS=true)"
    fi
    
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
