# Advanced Features

This file is loaded on demand from ../SKILL.md.

## HTTP/2 Deep Dive

```python
import httpx

# Enable HTTP/2 (requires httpx[http2])
client = httpx.Client(http2=True)

# Verify HTTP/2 negotiation
response = client.get("https://example.com")
print(response.http_version)  # "HTTP/2" or "HTTP/1.1"
```

**ALPN negotiation behavior:**

| Server Support | Result |
|----------------|--------|
| HTTP/2 + HTTP/1.1 | Auto-negotiates HTTP/2 (silent fallback to 1.1 if negotiation fails) |
| HTTP/1.1 only | Silent fallback to HTTP/1.1 |
| ALPN misconfigured | `RemoteProtocolError` if TLS handshake fails |

```python
from httpx import RemoteProtocolError

try:
    client = httpx.Client(http2=True)
    response = client.get("https://misconfigured-server.com")
except RemoteProtocolError as e:
    # Server advertised HTTP/2 but failed negotiation
    print(f"ALPN negotiation failed: {e}")
```

**When HTTP/2 provides no benefit:**

- Single request per connection (no multiplexing)
- Small payloads (TLS overhead dominates)
- Server doesn't support HTTP/2 (falls back to 1.1)

## Connection Pool Tuning

```python
import httpx

# Production-ready limits
limits = httpx.Limits(
    max_connections=100,           # Max total connections across all hosts
    max_keepalive_connections=50,  # Max idle connections kept alive
    keepalive_expiry=60            # How long to keep idle connections (seconds)
)

client = httpx.Client(limits=limits)
```

**Pool exhaustion troubleshooting:**

```python
# Symptom: PoolTimeout exceptions under load
# Cause: max_connections too low for concurrent request volume

# Diagnostic: Check active connection count
import httpx

class MonitoringTransport(httpx.HTTPTransport):
    def handle_request(self, request):
        # Your monitoring logic here
        return super().handle_request(request)

# Solution: Increase limits or optimize connection reuse
limits = httpx.Limits(
    max_connections=200,
    max_keepalive_connections=100,
    keepalive_expiry=120
)
```

## Proxy Configuration

```python
import httpx

# HTTP proxy
client = httpx.Client(proxies={"http://": "http://proxy.example.com:8080"})

# HTTPS proxy
client = httpx.Client(proxies={"https://": "http://proxy.example.com:8080"})

# SOCKS proxy (requires httpx[socks])
client = httpx.Client(proxies={"http://": "socks5://user:pass@proxy:1080"})

# Per-host routing
client = httpx.Client(
    proxies={
        "http://api.internal.com": "http://internal-proxy:8080",
        "http://": "http://default-proxy:8080"  # Default route
    }
)
```

## Event Hooks

```python
import httpx
import logging

def log_request(request: httpx.Request):
    logging.info(f"→ {request.method} {request.url}")

def log_response(response: httpx.Response):
    logging.info(f"← {response.status_code} ({response.elapsed.total_seconds():.2f}s)")

client = httpx.Client(
    event_hooks={
        "request": [log_request],
        "response": [log_response],
    }
)
```

## Custom Transports

```python
import httpx

class CustomTransport(httpx.BaseTransport):
    """Example: Add custom headers to all requests."""
    
    def __init__(self, transport: httpx.BaseTransport, api_key: str):
        self.transport = transport
        self.api_key = api_key

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        request.headers["X-API-Key"] = self.api_key
        return self.transport.handle_request(request)

transport = CustomTransport(httpx.HTTPTransport(), api_key="secret")
client = httpx.Client(transport=transport)
```
