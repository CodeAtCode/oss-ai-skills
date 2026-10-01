---
name: httpx
description: Use when making HTTP requests in Python with httpx - sync and async clients, connection pooling, timeouts, HTTP/2, retry patterns, transport configuration, or choosing between httpx/requests/aiohttp
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - http
    - async
    - client
    - network
---

# httpx

Modern HTTP client with sync/async APIs, HTTP/2, and production-grade features.

## Quick Start

```python
import httpx

# Always use timeouts in production
timeout = httpx.Timeout(
    connect=5.0,   # Connection establishment
    read=30.0,     # Response body read
    write=10.0,    # Request body write
    pool=5.0       # Connection pool acquisition
)

with httpx.Client(timeout=timeout) as client:
    response = client.get("https://api.example.com/data")
    print(response.status_code)
    print(response.json())
```

See [Quick Start](https://www.python-httpx.org/quickstart/) for basic request patterns.

## Production Configuration

### Timeouts (Mandatory)

The most common production failure is `httpx.get(url)` with no timeout—a hung server holds the connection forever.

```python
import httpx

# Configure once on the client, reuse across requests
timeout = httpx.Timeout(
    connect=5.0,   # Fails if TCP handshake exceeds this
    read=30.0,     # Fails if server stops sending data
    write=10.0,    # Fails if client can't send request
    pool=5.0       # Fails if no connection available in pool
)

client = httpx.Client(timeout=timeout)
```

**Timeout exception hierarchy:**

| Exception | When it fires | What it indicates |
|-----------|---------------|-------------------|
| `ConnectTimeout` | TCP handshake / TLS handshake | Server unreachable or firewall blocking |
| `ReadTimeout` | Waiting for response body | Server processing too slowly |
| `WriteTimeout` | Sending request body | Client network saturated |
| `PoolTimeout` | Waiting for connection from pool | Connection pool exhausted |

```python
from httpx import ConnectTimeout, ReadTimeout, TimeoutException

try:
    response = client.get("https://api.example.com")
except ConnectTimeout:
    # Server unreachable—retry with backoff or fail fast
    pass
except ReadTimeout:
    # Server hung—may have partial response
    pass
except TimeoutException as e:
    # Catch-all for any timeout subclass
    print(f"Timeout: {e}")
```

### Connection Pooling

**Rule: One `httpx.Client` per application/process, reused across requests.** A client per request defeats pooling and leaks connections.

```python
# Correct: Single client reused
class APIService:
    def __init__(self):
        limits = httpx.Limits(
            max_connections=50,          # Max total connections
            max_keepalive_connections=20, # Max idle connections
            keepalive_expiry=30          # Keepalive timeout (seconds)
        )
        timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
        self.client = httpx.Client(limits=limits, timeout=timeout)

    def fetch_user(self, user_id: int):
        return self.client.get(f"/users/{user_id}")

    def shutdown(self):
        self.client.close()  # Call on app shutdown hook
```

**Common pooling mistakes:**

```python
# Wrong: New client per request (leaks connections)
def handle_request():
    with httpx.Client() as client:  # Creates new connection pool
        return client.get("https://api.example.com")

# Wrong: Sync and async clients are not interchangeable
async def fetch_async():
    with httpx.Client() as client:  # Blocks event loop!
        return client.get("https://api.example.com")

# Correct: Use AsyncClient in async contexts
async def fetch_async():
    async with httpx.AsyncClient() as client:
        return await client.get("https://api.example.com")
```

### HTTP/2 Configuration

```python
# Enable HTTP/2 (requires httpx[http2])
client = httpx.Client(http2=True)

# HTTP/2 requires ALPN negotiation
# If server doesn't support it:
# - Silent fallback to HTTP/1.1 (most common)
# - RemoteProtocolError if ALPN fails explicitly
```

**When HTTP/2 is worth it:**
- ✅ Many concurrent requests to the same host (multiplexing benefit)
- ✅ Large response bodies (header compression helps)
- ❌ Small request counts (TLS handshake overhead dominates)
- ❌ Single-request scripts (no multiplexing benefit)

```python
# Check if HTTP/2 was negotiated
response = client.get("https://api.example.com")
print(response.http_version)  # "HTTP/2" or "HTTP/1.1"
```

### Retry Patterns (Idempotency Only)

**Never retry non-idempotent requests.** A retried POST can duplicate a charge, create duplicate records, or trigger side effects twice.

```python
import httpx
import time
import random

def exponential_backoff_with_jitter(attempt: int, base: float = 1.0, max_delay: float = 30.0) -> float:
    """Bounded exponential backoff with jitter."""
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.1)  # 10% jitter
    return delay + jitter

def safe_get_with_retries(client: httpx.Client, url: str, max_retries: int = 3):
    """Retry-safe GET request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = client.get(url)
            if response.status_code >= 500:
                # Server error—may be safe to retry
                time.sleep(exponential_backoff_with_jitter(attempt))
                continue
            return response
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed
            time.sleep(exponential_backoff_with_jitter(attempt))
    raise RuntimeError("Should not reach here")

# NEVER RETRY: Non-idempotent operations
def create_user(client: httpx.Client, data: dict):
    """Post is not retry-safe—do not wrap in retry logic."""
    return client.post("/users", json=data)
    # If this fails, you don't know if it succeeded or not
    # Implement idempotency keys instead of retries
```

**Transport-level retries:**

httpx doesn't include `urllib3.Retry`-style built-in retries because idempotency is context-dependent. Use transport mounts for fine-grained control:

```python
# Custom retry transport (advanced)
class RetryTransport(httpx.BaseTransport):
    def __init__(self, transport: httpx.BaseTransport, max_retries: int = 3):
        self.transport = transport
        self.max_retries = max_retries

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        # Implement retry logic here, checking request.method for idempotency
        pass

client = httpx.Client(transport=RetryTransport(httpx.HTTPTransport()))
```

## Client Selection Guide

Before choosing an HTTP client, run this check:

```python
# Decision flow:
# 1. Does the codebase need async?
#    - Yes → httpx or aiohttp
#    - No → httpx or requests
#
# 2. Does it need HTTP/2?
#    - Yes → httpx (only option with HTTP/2)
#    - No → continue
#
# 3. Is dependency count a constraint?
#    - Yes → stdlib urllib.request
#    - No → continue
#
# 4. Sync or async?
#    - Sync → requests (ubiquitous) or httpx (modern typing)
#    - Async → httpx (sync+async) or aiohttp (async-only, server-side focus)
```

| Client | Sync | Async | HTTP/2 | Dependencies | Best for |
|--------|------|-------|--------|--------------|----------|
| `requests` | ✅ | ❌ | ❌ | 1 (urllib3) | Simple sync scripts, ubiquitous ecosystem |
| `httpx` | ✅ | ✅ | ✅ | 2 (httpcore, certifi) | Modern apps needing async or HTTP/2 |
| `aiohttp` | ❌ | ✅ | ❌ | 3 (aiohttp, yarl, multidict) | Async servers (client + server in one) |
| `urllib.request` | ✅ | ❌ | ❌ | 0 (stdlib) | Zero-dependency scripts, constrained envs |

## Testing

**Why `respx` beats monkeypatching internals:** Mocking at the transport layer avoids implementation details, works with both sync and async clients, and doesn't break when httpx updates its internals.

```python
import httpx
import respx
import pytest

@respx.mock
def test_request_method_and_headers():
    """Assert on request method, URL, and headers."""
    route = respx.post("https://api.example.com/users").mock(
        return_value=httpx.Response(201, json={"id": 123})
    )

    client = httpx.Client()
    response = client.post(
        "https://api.example.com/users",
        json={"name": "Alice"},
        headers={"X-Request-ID": "abc-123"}
    )

    assert response.status_code == 201
    assert response.json() == {"id": 123}

    # Assert request was made correctly
    assert route.called
    request = route.calls[0].request
    assert request.method == b"POST"
    assert "X-Request-ID" in request.headers
```

**Testing retry behavior without wall-clock delay:**

```python
import httpx
from httpx import MockTransport

def test_retry_behavior():
    """Test retry logic by injecting a failing transport."""
    call_count = 0

    def failing_transport(request):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectTimeout("Simulated timeout", request=request)
        return httpx.Response(200, json={"success": True})

    transport = MockTransport(failing_transport)
    client = httpx.Client(transport=transport)

    # Your retry logic should handle this
    response = client.get("https://example.com")
    assert response.json() == {"success": True}
    assert call_count == 3  # Verified retry count
```

**Testing async with respx:**

```python
import pytest
import httpx
import respx

@pytest.mark.asyncio
async def test_async_client():
    @respx.mock
    async def inner():
        route = respx.get("https://api.example.com/data").mock(
            return_value=httpx.Response(200, json={"data": "test"})
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            assert response.json() == {"data": "test"}
            assert route.called

    await inner()
```

## Common Pitfalls

### Connection Leaks

```python
# Wrong: Client not closed
client = httpx.Client()
response = client.get("https://example.com")
# Connection pool never cleaned up

# Correct: Context manager or explicit close
with httpx.Client() as client:
    response = client.get("https://example.com")

# Or for long-lived clients
client = httpx.Client()
try:
    response = client.get("https://example.com")
finally:
    client.close()
```

### Mixing Sync and Async

```python
# Wrong: Sync client in async function blocks event loop
async def fetch():
    with httpx.Client() as client:  # Blocks!
        return client.get("https://example.com")

# Correct: Use AsyncClient
async def fetch():
    async with httpx.AsyncClient() as client:
        return await client.get("https://example.com")
```

### Timeout Not Set

```python
# Wrong: No timeout—server can hang forever
httpx.get("https://slow-server.com")

# Correct: Explicit timeout
httpx.get("https://slow-server.com", timeout=httpx.Timeout(connect=5.0, read=30.0))
```

## Deep Dives

Load these reference files on demand when you need deeper coverage:

- **Async patterns** — `references/async.md` — Concurrent requests, streaming uploads/downloads, event loop integration
- **Advanced features** — `references/advanced.md` — HTTP/2 deep dive, proxy configuration, event hooks, custom transports
- **Testing & framework integration** — `references/testing-integration.md` — FastAPI/Django integration, advanced respx patterns, async test fixtures

## References

- **Official Documentation**: https://www.python-httpx.org/
- **GitHub Repository**: https://github.com/encode/httpx
- **HTTP/2 Specification**: https://httpwg.org/specs/rfc9113.html
