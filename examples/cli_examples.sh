#!/bin/bash
# ProxyWhirl CLI Examples
# This script demonstrates various CLI commands and features

set -e  # Exit on error

echo "================================"
echo "ProxyWhirl CLI Examples"
echo "================================"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to print section headers
print_section() {
    echo
    echo -e "${BLUE}## $1${NC}"
    echo
}

# Helper function to print commands
print_command() {
    echo -e "${YELLOW}$ $1${NC}"
}

# ===========================
# 1. Configuration Management
# ===========================

print_section "1. Configuration Management"

print_command "proxywhirl config init"
echo "# Initialize a new config file in current directory"
# proxywhirl --no-lock config init

print_command "proxywhirl config show"
echo "# Display all configuration settings"
proxywhirl --no-lock config show

print_command "proxywhirl config get rotation_strategy"
echo "# Get a specific config value"
proxywhirl --no-lock config get rotation_strategy

print_command "proxywhirl config set max_retries 5"
echo "# Update a config value"
# proxywhirl --no-lock config set max_retries 5

# ===========================
# 2. Pool Management
# ===========================

print_section "2. Pool Management"

print_command "proxywhirl pool list"
echo "# List all proxies in the pool"
proxywhirl --no-lock pool list

print_command "proxywhirl pool add http://proxy1.example.com:8080"
echo "# Add a proxy to the pool"
# proxywhirl --no-lock pool add http://proxy1.example.com:8080

print_command "proxywhirl pool add http://proxy2.example.com:8080 -u myuser -p mypass"
echo "# Add a proxy with authentication"
# proxywhirl --no-lock pool add http://proxy2.example.com:8080 -u myuser -p mypass

print_command "proxywhirl pool test http://proxy1.example.com:8080"
echo "# Test a specific proxy"
# proxywhirl --no-lock pool test http://proxy1.example.com:8080

print_command "proxywhirl pool remove http://proxy1.example.com:8080"
echo "# Remove a proxy from the pool"
# proxywhirl --no-lock pool remove http://proxy1.example.com:8080

# ===========================
# 3. Making HTTP Requests
# ===========================

print_section "3. Making HTTP Requests"

print_command "proxywhirl request https://httpbin.org/get"
echo "# Make a simple GET request"
proxywhirl --no-lock request https://httpbin.org/get

print_command "proxywhirl --format json request https://httpbin.org/get"
echo "# Get JSON output"
proxywhirl --no-lock --format json request https://httpbin.org/get

print_command "proxywhirl request --method POST --data '{\"key\":\"value\"}' https://httpbin.org/post"
echo "# Make a POST request with JSON data"
proxywhirl --no-lock request --method POST --data '{"key":"value"}' https://httpbin.org/post

print_command "proxywhirl request --header 'Authorization: Bearer token' https://httpbin.org/headers"
echo "# Add custom headers"
proxywhirl --no-lock request --header "Authorization: Bearer token123" https://httpbin.org/headers

print_command "proxywhirl request --retries 5 https://httpbin.org/status/503"
echo "# Retry failed requests"
proxywhirl --no-lock request --retries 3 https://httpbin.org/status/200

print_command "proxywhirl request --proxy http://myproxy.com:8080 https://httpbin.org/ip"
echo "# Override proxy for a single request"
# proxywhirl --no-lock request --proxy http://myproxy.com:8080 https://httpbin.org/ip

# ===========================
# 4. Health Monitoring
# ===========================

print_section "4. Health Monitoring"

print_command "proxywhirl health"
echo "# Check health of all proxies once"
proxywhirl --no-lock health

print_command "proxywhirl health --continuous --interval 60"
echo "# Monitor proxy health continuously (every 60 seconds)"
echo "# Press Ctrl+C to stop"
# proxywhirl --no-lock health --continuous --interval 60

print_command "proxywhirl --format json health"
echo "# Get health status as JSON"
# proxywhirl --no-lock --format json health

# ===========================
# 5. Output Formats
# ===========================

print_section "5. Output Formats"

print_command "proxywhirl --format text pool list"
echo "# Human-readable output with colors (default)"
# proxywhirl --no-lock --format text pool list

print_command "proxywhirl --format json pool list"
echo "# JSON output for scripting"
# proxywhirl --no-lock --format json pool list

print_command "proxywhirl --format csv pool list"
echo "# CSV output for spreadsheets"
# proxywhirl --no-lock --format csv pool list

# ===========================
# 6. Verbose Mode
# ===========================

print_section "6. Verbose Mode"

print_command "proxywhirl --verbose request https://httpbin.org/get"
echo "# Enable verbose logging"
proxywhirl --no-lock --verbose request https://httpbin.org/get

# ===========================
# 7. Advanced Usage
# ===========================

print_section "7. Advanced Usage"

print_command "proxywhirl --config /path/to/config.toml pool list"
echo "# Use a specific config file"
# proxywhirl --config /path/to/config.toml pool list

print_command "proxywhirl --no-lock pool list"
echo "# Disable file locking (use with caution)"
proxywhirl --no-lock pool list

print_command "proxywhirl request https://httpbin.org/get | jq '.body'"
echo "# Pipe output to other tools (with JSON format)"
proxywhirl --no-lock --format json request https://httpbin.org/get | head -20

# ===========================
# 8. Help & Documentation
# ===========================

print_section "8. Help & Documentation"

print_command "proxywhirl --help"
echo "# Show main help"
proxywhirl --help

print_command "proxywhirl request --help"
echo "# Show help for specific command"
proxywhirl request --help

print_command "proxywhirl pool --help"
proxywhirl pool --help

print_command "proxywhirl config --help"
proxywhirl config --help

print_command "proxywhirl health --help"
proxywhirl health --help

echo
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Examples completed!${NC}"
echo -e "${GREEN}================================${NC}"
