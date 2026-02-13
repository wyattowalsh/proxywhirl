---
title: Deployment Security & Reverse Proxy Configuration
---

# Deployment Security & Reverse Proxy Configuration

Complete guide for securely deploying ProxyWhirl in production with trusted reverse proxy configurations.

```{contents}
:local:
:depth: 2
```

## Overview

When deploying ProxyWhirl behind a reverse proxy in production, the rate limiting and client identification features depend on accurately determining the real client IP address. This is the critical security boundary that prevents attackers from spoofing their IP to bypass rate limits.

**Recommended Architecture:**

```
Internet
    ↓
[Reverse Proxy: Nginx/Caddy/HAProxy/Cloud LB]  ← Clears untrusted headers
    ↓ (X-Real-IP or X-Forwarded-For set here)
[ProxyWhirl API Server]  ← Reads trusted headers
    ↓
[Proxy Pool Management]
```

## X-Forwarded-For Security

### The Attack

The `X-Forwarded-For` HTTP header is designed to pass the real client IP through proxy chains. However, since HTTP headers can be set by any client, an attacker can forge this header to bypass security controls:

**Attack Scenario:**

1. **Attacker sends request with forged header:**
   ```
   GET /api/v1/request HTTP/1.1
   Host: api.example.com
   X-Forwarded-For: 192.0.2.1, 198.51.100.2
   ```

2. **Untrusted reverse proxy appends attacker's IP:**
   ```
   X-Forwarded-For: 192.0.2.1, 198.51.100.2, 203.0.113.50
   ```

3. **If ProxyWhirl reads leftmost IP (192.0.2.1), rate limiting is bypassed:**
   - Attacker can exhaust rate limits under spoofed IPs
   - 1000 requests/min limit becomes 1000 per unique forged IP
   - Legitimate rate limiting is rendered ineffective

### The Defense

**Key Principle:** Your reverse proxy must be configured to **clear or overwrite** any client-provided `X-Forwarded-For` header and set it to the real connecting IP address.

**Three Critical Requirements:**

1. **Clear untrusted headers** from incoming requests
2. **Set correct forwarding headers** with the real client IP
3. **ProxyWhirl trusts only the configured header** (e.g., `X-Real-IP` or the rightmost IP in `X-Forwarded-For`)

## Reverse Proxy Configurations

### Nginx

**Secure Configuration (Single Proxy):**

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://proxywhirl:8000;
        proxy_set_header Host $host;

        # Critical: Use $remote_addr (cannot be spoofed by clients)
        proxy_set_header X-Real-IP $remote_addr;

        # Set clean X-Forwarded-For from real client IP only
        proxy_set_header X-Forwarded-For $remote_addr;

        # Preserve other forwarding context
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # Connection handling
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }
}
```

**Secure Configuration (Multi-Proxy Chain with ngx_realip Module):**

When ProxyWhirl sits behind multiple proxies (e.g., CDN → nginx → app), use the `ngx_realip` module:

```nginx
# Load the realip module (may be compiled in or as a dynamic module)
# If dynamic: load_module modules/ngx_http_realip_module.so;

server {
    listen 80;
    server_name api.example.com;

    # Configure which upstream proxies are trusted
    set_real_ip_from 10.0.0.0/8;      # Trust internal network
    set_real_ip_from 172.16.0.0/12;   # Docker subnet
    set_real_ip_from 203.0.113.0/24;  # Your CDN IP range

    real_ip_header X-Forwarded-For;
    real_ip_recursive on;

    location / {
        proxy_pass http://proxywhirl:8000;
        proxy_set_header Host $host;

        # After real_ip processing, $remote_addr is the true client IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Key Points:**
- `$remote_addr` is the connecting client's IP (cannot be spoofed)
- `set_real_ip_from` whitelists trusted upstream proxies
- `real_ip_recursive on` processes the entire X-Forwarded-For chain
- Only trust proxies **within your control**

### Caddy

**Secure Configuration:**

```text
api.example.com {
    reverse_proxy localhost:8000 {
        # Replace X-Forwarded-For with real client IP
        # (Caddy removes untrusted headers by default)
        header_up -X-Forwarded-For
        header_up X-Forwarded-For {http.request.remote.host}

        # Set X-Real-IP to the actual client IP
        header_up X-Real-IP {http.request.remote.host}

        # Preserve protocol and host information
        header_up X-Forwarded-Proto {http.request.proto}
        header_up X-Forwarded-Host {http.request.host}
        header_up X-Forwarded-Port {http.request.port}
    }
}
```

**Advantages:**
- Caddy automatically removes untrusted X-Forwarded-For headers from clients
- Simple, secure-by-default configuration
- Excellent choice for production without extensive tuning

### HAProxy

**Secure Configuration:**

```text
global
    log stdout local0
    maxconn 4096

defaults
    log global
    mode http
    timeout connect 5s
    timeout client 50s
    timeout server 50s

frontend api_frontend
    bind 0.0.0.0:80
    default_backend api_backend

    # Security: Normalize headers to prevent spoofing
    # Extract real client IP from connection
    http-request set-header X-Real-IP %[src]

    # For X-Forwarded-For chains, only keep the real client IP
    http-request set-header X-Forwarded-For %[src]
    http-request set-header X-Forwarded-Proto %[req.hdr(X-Forwarded-Proto)]

    # Additional security headers
    http-request set-header X-Forwarded-Host %[req.hdr(Host)]

backend api_backend
    balance roundrobin

    # Configure ProxyWhirl server
    server api1 localhost:8000 check

    # Preserve client IP in backend communication
    option forwardfor

    # Additional security response headers
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains"
    http-response set-header X-Content-Type-Options "nosniff"
```

**Key Points:**
- `%[src]` is HAProxy's source IP (cannot be spoofed)
- `http-request set-header` is evaluated per request (before any client manipulation)
- `option forwardfor` adds/updates X-Forwarded-For with the real client IP

### Traefik

**Secure Configuration (docker-compose):**

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:latest
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    networks:
      - proxywhirl-net

  proxywhirl:
    image: proxywhirl-api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.proxywhirl.rule=Host(`api.example.com`)"
      - "traefik.http.routers.proxywhirl.entrypoints=web"
      - "traefik.http.services.proxywhirl.loadbalancer.server.port=8000"

      # Security: Forward real client IP
      - "traefik.http.middlewares.client-ip.headers.customrequestheaders.X-Real-IP={{ .ClientIP }}"
      - "traefik.http.middlewares.client-ip.headers.customrequestheaders.X-Forwarded-For={{ .ClientIP }}"
      - "traefik.http.routers.proxywhirl.middlewares=client-ip"

    environment:
      PROXYWHIRL_STORAGE_PATH: /data/proxies.db
    volumes:
      - proxywhirl-data:/data
    networks:
      - proxywhirl-net

networks:
  proxywhirl-net:
    driver: bridge

volumes:
  proxywhirl-data:
```

**Alternative (File-based Configuration):**

```yaml
# traefik-config.yml
http:
  middlewares:
    client-ip:
      headers:
        customRequestHeaders:
          X-Real-IP: "{{ .ClientIP }}"
          X-Forwarded-For: "{{ .ClientIP }}"

  routers:
    proxywhirl:
      rule: "Host(`api.example.com`)"
      service: proxywhirl-api
      middlewares:
        - client-ip

  services:
    proxywhirl-api:
      loadBalancer:
        servers:
          - url: "http://localhost:8000"
```

### AWS Application Load Balancer

**Secure Configuration (Terraform):**

```hcl
resource "aws_lb_target_group" "proxywhirl" {
  name     = "proxywhirl-api"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  # Essential: Preserve client IP in ALB
  stickiness {
    enabled = false
  }

  # Health check configuration
  health_check {
    path              = "/api/v1/health"
    port              = "8000"
    protocol          = "HTTP"
    healthy_threshold = 2
    unhealthy_threshold = 2
    timeout           = 5
    interval          = 30
    matcher           = "200"
  }

  tags = {
    Name = "proxywhirl-api"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.proxywhirl.arn
  }
}

# Security Group: Restrict to ALB traffic
resource "aws_security_group" "proxywhirl" {
  name_prefix = "proxywhirl-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "From ALB only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "proxywhirl-sg"
  }
}
```

**ALB Sets These Headers:**

```
X-Forwarded-For: <client-ip>
X-Forwarded-Proto: https
X-Forwarded-Port: 443
X-Amzn-Trace-Id: <aws-trace-id>
```

**Security Notes:**
- ALB is managed by AWS and automatically clears untrusted headers
- Enable "Preserve client IP" in target group attributes
- Trust ALB's IP range (use security groups)
- ProxyWhirl should read `X-Forwarded-For` (rightmost IP is client)

### Google Cloud Load Balancer

**Secure Configuration (gcloud):**

```bash
# Create backend service
gcloud compute backend-services create proxywhirl-backend \
  --protocol=HTTP \
  --health-checks=proxywhirl-health-check \
  --global \
  --session-affinity=NONE

# Add instance group to backend
gcloud compute backend-services add-backend proxywhirl-backend \
  --instance-group=proxywhirl-ig \
  --instance-group-zone=us-central1-a \
  --global

# Create URL map
gcloud compute url-maps create proxywhirl-lb \
  --default-service=proxywhirl-backend

# Create HTTP proxy
gcloud compute target-http-proxies create proxywhirl-proxy \
  --url-map=proxywhirl-lb

# Create forwarding rule
gcloud compute forwarding-rules create proxywhirl-forwarding \
  --global \
  --target-http-proxy=proxywhirl-proxy \
  --address=proxywhirl-ip \
  --port-range=80
```

**GCP Load Balancer Sets:**
```
X-Forwarded-For: <client-ip>
X-Forwarded-Proto: https
```

**Security Notes:**
- GCP Load Balancer automatically manages header security
- Use Cloud Armor to enforce additional IP restrictions
- Restrict backend access to LB IP range only

## ProxyWhirl Configuration

:::{seealso}
For the complete list of environment variables and configuration options, see {doc}`/reference/configuration`. For the REST API endpoint documentation, see {doc}`/reference/rest-api`.
:::

### Reading Client IP from Headers

ProxyWhirl automatically reads the client IP from trusted headers for rate limiting:

**Priority Order (first found is used):**

1. `X-Real-IP` header (recommended for reverse proxies)
2. Rightmost IP in `X-Forwarded-For` header
3. Direct connection IP (fallback)

**Environment Variables:**

```bash
# Specify which header to trust for client IP
# Options: "X-Real-IP", "X-Forwarded-For" (rightmost), or "remote-addr"
export PROXYWHIRL_CLIENT_IP_HEADER="X-Real-IP"

# Define trusted upstream proxy IP ranges (CIDR notation)
# ProxyWhirl will only trust headers from these IPs
export PROXYWHIRL_TRUSTED_PROXIES="10.0.0.0/8,172.16.0.0/12,203.0.113.50/32"

# Rate limiting per IP
export PROXYWHIRL_RATE_LIMIT_DEFAULT=100  # requests/minute
export PROXYWHIRL_RATE_LIMIT_REQUEST=50   # requests/minute for /api/v1/request
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - secure-net

  proxywhirl:
    image: proxywhirl-api:latest
    environment:
      PROXYWHIRL_STRATEGY: "round-robin"
      PROXYWHIRL_TIMEOUT: 30
      PROXYWHIRL_STORAGE_PATH: /data/proxies.db
      PROXYWHIRL_CLIENT_IP_HEADER: "X-Real-IP"
      PROXYWHIRL_TRUSTED_PROXIES: "10.0.0.0/8"
      PROXYWHIRL_RATE_LIMIT_DEFAULT: 100
      PROXYWHIRL_RATE_LIMIT_REQUEST: 50
    volumes:
      - proxywhirl-data:/data
    networks:
      - secure-net
    expose:
      - 8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  secure-net:
    driver: bridge

volumes:
  proxywhirl-data:
```

:::{warning}
For credential encryption at the cache layer, see {doc}`caching` which covers Fernet encryption, key rotation, and `SecretStr` usage. All proxy credentials should be encrypted at rest.
:::

## Security Checklist

**Before Production Deployment:**

- [ ] **Reverse proxy installed** between internet and ProxyWhirl
- [ ] **Untrusted X-Forwarded-For headers cleared** by reverse proxy
- [ ] **X-Real-IP or X-Forwarded-For set** by reverse proxy with real client IP
- [ ] **ProxyWhirl configured** to read correct header (X-Real-IP preferred)
- [ ] **Trusted proxy IP ranges configured** in ProxyWhirl
- [ ] **Rate limiting tested** with spoofed headers (verified to fail)
- [ ] **Access logs reviewed** to verify correct client IP attribution
- [ ] **Direct internet access blocked** (no exposure on :8000 from outside)
- [ ] **Security group/firewall rules** restrict to reverse proxy only
- [ ] **HTTPS/TLS enabled** on reverse proxy (use Let's Encrypt or managed service)
- [ ] **API key authentication enabled** if sensitive operations are exposed
- [ ] **CORS origins restricted** to known domains
- [ ] **Regular security updates** applied (nginx, HAProxy, ProxyWhirl)

## Troubleshooting

### Rate Limiting Not Working

**Symptom:** Requests with different `X-Forwarded-For` values bypass rate limit

**Solution:**
1. Verify reverse proxy is clearing client-provided `X-Forwarded-For`
2. Check ProxyWhirl logs for detected client IP:
   ```bash
   # Enable debug logging
   export LOGLEVEL=DEBUG
   ```
3. Test with direct request (no reverse proxy):
   ```bash
   curl http://localhost:8000/api/v1/proxies \
     -H "X-Forwarded-For: 1.2.3.4"
   # Should rate limit based on real connection IP, not header value
   ```

### Metrics Showing Wrong Client IPs

**Symptom:** Metrics endpoint shows incorrect client IP distribution

**Solution:**
1. Verify `PROXYWHIRL_CLIENT_IP_HEADER` environment variable
2. Check reverse proxy is setting the header correctly:
   ```bash
   curl -v http://localhost/api/v1/metrics
   # Look at response headers from reverse proxy
   ```
3. Review reverse proxy logs for X-Real-IP values being set

### Connection Refused Behind Reverse Proxy

**Symptom:** HTTP 502 Bad Gateway

**Solution:**
1. Verify ProxyWhirl is running:
   ```bash
   docker logs proxywhirl-container
   ```
2. Test direct connection:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
3. Check reverse proxy network connectivity
4. Review reverse proxy logs for backend errors

### SSL Certificate Errors

**Symptom:** HTTPS requests return certificate warnings

**Solution:**
1. Obtain valid certificate (Let's Encrypt recommended)
2. Configure reverse proxy with certificate
3. Set `X-Forwarded-Proto: https` in reverse proxy configuration
4. ProxyWhirl will correctly generate links with `https://`

## References

### Security Standards

- **[RFC 7239 - Forwarded HTTP Extension](https://datatracker.ietf.org/doc/html/rfc7239)** - Standard for HTTP forwarding headers
- **[MDN X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For)** - X-Forwarded-For header documentation
- **[OWASP HTTP Response Splitting](https://owasp.org/www-community/attacks/HTTP_Response_Splitting)** - Header injection attacks
- **[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)** - HTTP request validation best practices

### Reverse Proxy Documentation

- **[Nginx Proxy Module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)** - Official proxy configuration
- **[Nginx Real IP Module](https://nginx.org/en/docs/http/ngx_http_realip_module.html)** - Real IP extraction
- **[Caddy Reverse Proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)** - Caddy proxy documentation
- **[HAProxy Documentation](https://docs.haproxy.org/)** - HAProxy documentation
- **[Traefik Middleware](https://doc.traefik.io/traefik/middlewares/http/overview/)** - Traefik middleware reference

### Cloud Documentation

- **[AWS ALB Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)** - AWS Application Load Balancer
- **[GCP Load Balancing](https://cloud.google.com/load-balancing/docs)** - Google Cloud Load Balancer
- **[Azure Application Gateway](https://docs.microsoft.com/en-us/azure/application-gateway/)** - Azure gateway documentation

### ProxyWhirl Documentation

::::{grid} 2
:gutter: 3

:::{grid-item-card} REST API Reference
:link: /reference/rest-api
:link-type: doc

Full REST API documentation including rate limiting endpoints and authentication.
:::

:::{grid-item-card} Rate Limiting API
:link: /reference/rate-limiting-api
:link-type: doc

Detailed rate limiting configuration and token bucket algorithm reference.
:::

:::{grid-item-card} Configuration Reference
:link: /reference/configuration
:link-type: doc

All environment variables, TOML keys, and configuration options.
:::

:::{grid-item-card} Caching Subsystem
:link: /guides/caching
:link-type: doc

Credential encryption, key rotation, and secure cache storage.
:::

:::{grid-item-card} CLI Reference
:link: /guides/cli-reference
:link-type: doc

CLI commands for health monitoring, proxy management, and configuration.
:::

:::{grid-item-card} Automation Guide
:link: /guides/automation
:link-type: doc

CI/CD workflows for automated proxy refresh and source validation.
:::
::::
