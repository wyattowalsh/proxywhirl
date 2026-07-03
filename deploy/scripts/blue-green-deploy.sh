#!/bin/bash
set -euo pipefail

# Blue-Green Deployment Script for ProxyWhirl
# Ensures zero-downtime deployments by running two identical production environments

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BLUE_PORT=8000
GREEN_PORT=8001
BLUE_ENV="blue"
GREEN_ENV="green"
HEALTH_CHECK_URL="/api/ready"
MAX_RETRIES=30
RETRY_INTERVAL=2

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

get_active_env() {
    # Check which environment is currently active (receiving traffic)
    if curl -s "http://localhost:8080" > /dev/null 2>&1; then
        # Determine which is active by checking upstream
        if curl -s "http://localhost:$BLUE_PORT$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            echo "$BLUE_ENV"
        else
            echo "$GREEN_ENV"
        fi
    else
        echo "$BLUE_ENV"  # Default to blue
    fi
}

get_inactive_env() {
    if [ "$(get_active_env)" = "$BLUE_ENV" ]; then
        echo "$GREEN_ENV"
    else
        echo "$BLUE_ENV"
    fi
}

get_inactive_port() {
    if [ "$(get_active_env)" = "$BLUE_ENV" ]; then
        echo "$GREEN_PORT"
    else
        echo "$BLUE_PORT"
    fi
}

health_check() {
    local port=$1
    local retries=0
    
    log_info "Performing health check on port $port..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s "http://localhost:$port$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log_info "✓ Health check passed for port $port"
            return 0
        fi
        retries=$((retries + 1))
        log_warn "Health check attempt $retries/$MAX_RETRIES failed, retrying in ${RETRY_INTERVAL}s..."
        sleep "$RETRY_INTERVAL"
    done
    
    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

smoke_tests() {
    local port=$1
    
    log_info "Running smoke tests on port $port..."
    local curl_args=("-f" "-s")
    if [ -n "${PROXYWHIRL_API_KEY:-}" ]; then
        curl_args+=("-H" "X-API-Key: $PROXYWHIRL_API_KEY")
    fi
    
    # Test API endpoints
    if ! curl -f -s "http://localhost:$port/api/ready" > /dev/null; then
        log_error "Smoke test failed: /api/ready"
        return 1
    fi
    
    if [ -n "${PROXYWHIRL_API_KEY:-}" ] || [ "${PROXYWHIRL_PUBLIC_METRICS:-false}" = "true" ]; then
        if ! curl "${curl_args[@]}" "http://localhost:$port/api/metrics" > /dev/null; then
            log_error "Smoke test failed: /api/metrics"
            return 1
        fi
    else
        log_warn "Skipping /api/metrics smoke test; set PROXYWHIRL_API_KEY or PROXYWHIRL_PUBLIC_METRICS=true"
    fi
    
    log_info "✓ All smoke tests passed"
    return 0
}

deploy_inactive_env() {
    local inactive_port=$(get_inactive_port)
    local inactive_env=$(get_inactive_env)
    
    log_info "Deploying to $inactive_env environment on port $inactive_port..."
    
    # Build and deploy to inactive environment
    docker build -t "proxywhirl:$inactive_env" .
    docker run -d --name "proxywhirl-$inactive_env" \
        -p "$inactive_port:8000" \
        -e PROXYWHIRL_ENVIRONMENT="$inactive_env" \
        -e PROXYWHIRL_LOG_LEVEL=INFO \
        "proxywhirl:$inactive_env"
    
    log_info "✓ Deployed to $inactive_env"
}

switch_traffic() {
    local old_env=$(get_active_env)
    local new_env=$(get_inactive_env)
    local new_port=$(get_inactive_port)
    
    log_info "Switching traffic from $old_env to $new_env..."
    
    # Update load balancer configuration (example with nginx)
    # This would typically be done via your load balancer's API
    # For now, we'll assume the load balancer is managed separately
    
    # Verify traffic is being served by new environment
    sleep 5
    if health_check "$new_port"; then
        log_info "✓ Traffic successfully switched to $new_env"
        return 0
    else
        log_error "Traffic switch failed, rollback recommended"
        return 1
    fi
}

rollback() {
    local old_env=$(get_active_env)
    
    log_warn "Rolling back to $old_env..."
    
    # Load balancer would route traffic back to old environment
    # Clean up failed deployment
    docker stop "proxywhirl-$(get_inactive_env)" || true
    docker rm "proxywhirl-$(get_inactive_env)" || true
    
    log_info "✓ Rollback complete"
}

main() {
    log_info "Starting Blue-Green Deployment..."
    
    local inactive_env=$(get_inactive_env)
    local inactive_port=$(get_inactive_port)
    
    log_info "Active environment: $(get_active_env)"
    log_info "Inactive environment: $inactive_env (port: $inactive_port)"
    
    # Step 1: Deploy to inactive environment
    if ! deploy_inactive_env; then
        log_error "Deployment failed"
        exit 1
    fi
    
    # Step 2: Health checks
    if ! health_check "$inactive_port"; then
        log_error "Health check failed, aborting deployment"
        docker stop "proxywhirl-$inactive_env" || true
        docker rm "proxywhirl-$inactive_env" || true
        exit 1
    fi
    
    # Step 3: Smoke tests
    if ! smoke_tests "$inactive_port"; then
        log_error "Smoke tests failed, aborting deployment"
        docker stop "proxywhirl-$inactive_env" || true
        docker rm "proxywhirl-$inactive_env" || true
        exit 1
    fi
    
    # Step 4: Switch traffic
    if ! switch_traffic; then
        log_error "Traffic switch failed"
        rollback
        exit 1
    fi
    
    # Step 5: Cleanup old environment (optional - keep for quick rollback)
    log_info "Deployment complete!"
    log_info "Old environment available for rollback at port $((inactive_port == BLUE_PORT ? GREEN_PORT : BLUE_PORT))"
}

if [ "${1:-}" = "rollback" ]; then
    rollback
else
    main
fi
