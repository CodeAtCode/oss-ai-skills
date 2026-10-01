---
name: aiohttp
description: Use when building Python async HTTP services or clients with aiohttp - web server routing, middleware, WebSocket, SSE, streaming, client sessions, pytest-aiohttp testing, or troubleshooting SSL and timeout issues
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - http
    - async
    - server
    - websocket
    - sse
---

# aiohttp

Asynchronous HTTP client/server framework for Python.

## When to Use aiohttp

**Choose aiohttp when:**
- Building async Python HTTP servers with fine-grained control over routing and middleware
- Need both client and server in one framework with WebSocket/SSE support
- Streaming responses or large file uploads/downloads are required

**Consider alternatives:**
- **fastapi** — When you want automatic OpenAPI docs, Pydantic validation built-in, and simpler syntax
- **httpx** — When you need a modern async HTTP client with HTTP/2 support (better than aiohttp's)
- **Flask/FastAPI + httpx** — For sync codebases (aiohttp is purely async)

## Quick Start: Minimal Server

```python
from aiohttp import web

async def health_check(request):
    return web.json_response({"status": "ok"})

async def create_user(request):
    data = await request.json()
    # Validate with Pydantic or manual checks
    return web.json_response({"id": 1, "username": data["username"]}, status=201)

app = web.Application()
app.router.add_get('/health', health_check)
app.router.add_post('/users', create_user)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
```

## Server-Side Patterns

### Application Setup with Startup/Cleanup Hooks

Use `app.on_startup` and `app.on_cleanup` for resource lifecycle:

```python
from aiohttp import web
import asyncpg

async def init_db(app):
    """Create database connection pool."""
    app['db_pool'] = await asyncpg.create_pool(
        host='localhost',
        port=5432,
        database='app_db'
    )

async def close_db(app):
    """Close database connection pool."""
    await app['db_pool'].close()

app = web.Application()
app.on_startup.append(init_db)
app.on_cleanup.append(close_db)
app.router.add_get('/users', list_users)
```

### Modern Lifespan Context (v3.9+)

For cleaner startup/shutdown with context manager semantics:

```python
from aiohttp import web

async def lifespan_ctx(app):
    """Lifespan context manager for resource management."""
    # Startup
    app['db_pool'] = await create_db_pool()
    app['cache'] = await create_cache()
    
    yield  # App runs here
    
    # Cleanup
    await app['cache'].close()
    await app['db_pool'].close()

app = web.Application()
app.router.add_get('/data', data_handler)
# Run with: web.run_app(app, lifespan=lifespan_ctx)
```

### Middleware Patterns

Middleware wraps request handling for cross-cutting concerns:

```python
from aiohttp import web
import time
import logging

logger = logging.getLogger(__name__)

@web.middleware
async def timing_middleware(request, handler):
    """Track request duration."""
    start = time.perf_counter()
    try:
        response = await handler(request)
        duration = time.perf_counter() - start
        logger.info(f"{request.method} {request.path} {response.status} ({duration:.3f}s)")
        return response
    except Exception as e:
        duration = time.perf_counter() - start
        logger.error(f"{request.method} {request.path} failed after {duration:.3f}s: {e}")
        raise

@web.middleware
async def auth_middleware(request, handler):
    """Authentication middleware."""
    public_paths = ['/health', '/public/']
    if any(request.path.startswith(p) for p in public_paths):
        return await handler(request)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not await validate_token(auth_header):
        return web.json_response(
            {"error": "Unauthorized"},
            status=401,
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    # Attach user info to request
    request['user'] = await decode_token(auth_header)
    return await handler(request)

# Combine middleware (applied left-to-right)
app = web.Application(middlewares=[timing_middleware, auth_middleware])
```

### Response Choices

| Response Type | Use Case | Example |
|---------------|----------|---------|
| `web.Response(text=...)` | Plain text, HTML | `web.Response(text="OK", content_type="text/html")` |
| `web.json_response(...)` | JSON bodies (auto-serializes) | `web.json_response({"key": "value"}, status=201)` |
| `web.StreamResponse()` | Streaming large responses | See streaming section below |
| `web.FileResponse()` | File downloads | `web.FileResponse('data.zip')` |
| `web.HTTPFound()` | Redirects | `web.HTTPFound('/new-location')` |
| HTTP exception classes | Error responses | `web.HTTPBadRequest()`, `web.HTTPNotFound()` |

Manual status setting:
```python
# Explicit status codes
return web.json_response({"error": "not found"}, status=404)
return web.Response(text="Created", status=201)

# HTTP exception classes (automatic status)
raise web.HTTPBadRequest(reason="Invalid input")
return web.HTTPUnauthorized(headers={'WWW-Authenticate': 'Bearer'})
```

### Streaming Responses

For large files or real-time data:

```python
from aiohttp import web
import asyncio

async def stream_data(request):
    """Server-Sent Events style streaming."""
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
    await response.prepare(request)
    
    try:
        for i in range(10):
            data = f"data: {{'count': {i}}}\n\n"
            await response.write(data.encode())
            await response.drain()
            await asyncio.sleep(1)
    finally:
        await response.write_eof()
    
    return response

async def stream_file(request):
    """Stream large file in chunks."""
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Length'] = str(file_size)
    await response.prepare(request)
    
    async with aiofiles.open('large_file.bin', 'rb') as f:
        while chunk := await f.read(8192):
            await response.write(chunk)
    
    return response
```

## Client-Side Patterns

### Basic Client Usage

```python
import aiohttp
import asyncio

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            response.raise_for_status()
            return await response.json()

asyncio.run(fetch_data())
```

### Connection Pooling Configuration

```python
import aiohttp

# Default connector (often insufficient for production)
# session = aiohttp.ClientSession()  # ❌ BAD: Uses defaults

# Production-ready connector
connector = aiohttp.TCPConnector(
    limit=100,              # Total connection pool size (default: 100)
    limit_per_host=30,      # Max connections per host (default: 30)
    ttl_dns_cache=300,      # DNS cache TTL in seconds
    ssl=True,               # Verify SSL certificates
    enable_cleanup_closed=True,  # Clean closed connections
)

timeout = aiohttp.ClientTimeout(
    total=30,       # Total request timeout (connect + transfer)
    connect=5,      # Connection establishment timeout
    sock_connect=5, # Socket connection timeout
    sock_read=10,   # Read timeout (per read operation)
)

session = aiohttp.ClientSession(
    connector=connector,
    timeout=timeout,
    headers={'User-Agent': 'my-app/1.0'}
)
```

### Session Lifecycle

```python
# ✅ GOOD: Reuse session across requests
async def process_multiple_urls(urls):
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=100)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def fetch_url(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

# ❌ BAD: Creating session per request (causes socket exhaustion)
async def bad_pattern(urls):
    results = []
    for url in urls:
        async with aiohttp.ClientSession() as session:  # New session each time
            async with session.get(url) as response:
                results.append(await response.json())
        # Session closed immediately after each request
    return results
```

## Anti-Patterns and Failure Modes

### Socket Exhaustion from Session Per Request

**Symptom:** `OSError: [Errno 24] Too many open files` or connection timeouts under load

**Cause:** Creating `ClientSession()` inside request handlers or loops without reuse. Each session maintains its own connection pool and file descriptors.

**Fix:**
```python
# ❌ ANTI-PATTERN: Session created per request
async def handler(request):
    session = aiohttp.ClientSession()  # New session every request
    async with session.get(url) as resp:
        return web.json_response(await resp.json())

# ✅ FIX: Session stored in app, reused across requests
async def init_app():
    app = web.Application()
    app['session'] = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=100)
    )
    return app

async def cleanup_app(app):
    await app['session'].close()

app = await init_app()
app.on_cleanup.append(cleanup_app)

async def handler(request):
    session = request.app['session']
    async with session.get(url) as resp:
        return web.json_response(await resp.json())
```

### No Total Timeout: Hung Server Holds Connections

**Symptom:** Connections accumulate, eventually hitting `limit` in TCPConnector, new requests hang

**Cause:** Missing `ClientTimeout` means no total timeout. A slow or hung server can hold connections indefinitely.

**Fix:**
```python
# ❌ ANTI-PATTERN: No timeout specified
session = aiohttp.ClientSession()
async with session.get('https://slow-api.com/data') as resp:
    # If server hangs, this waits forever
    data = await resp.json()

# ✅ FIX: Always set timeouts
timeout = aiohttp.ClientTimeout(
    total=30,       # Max total time for entire request
    connect=5,      # Max time to establish connection
    sock_read=10    # Max time between read operations
)
session = aiohttp.ClientSession(timeout=timeout)
```

### Missing Read/Connect Timeouts

**Symptom:** Connection established but data never arrives; or DNS resolution hangs

**Cause:** Only setting `total` timeout isn't enough. `sock_read` and `connect` catch specific failure modes.

**Fix:**
```python
# ❌ ANTI-PATTERN: Only total timeout
timeout = aiohttp.ClientTimeout(total=60)

# ✅ FIX: Granular timeouts
timeout = aiohttp.ClientTimeout(
    total=60,       # Overall request timeout
    connect=5,      # Fail fast if can't connect
    sock_connect=5, # Socket connection timeout
    sock_read=30    # Read timeout (prevents stuck on slow responses)
)
```

### Reusing Session Across Event Loops

**Symptom:** `RuntimeError: Cannot call nested app.handler()` or `RuntimeError: Session is closed`

**Cause:** `ClientSession` is bound to the event loop it was created on. Reusing it after `asyncio.run()` restarts the loop.

**Fix:**
```python
# ❌ ANTI-PATTERN: Global session
session = aiohttp.ClientSession()  # Created at module load

async def main():
    asyncio.run(fetch_data())  # New event loop
    # session is bound to old loop!

# ✅ FIX: Create session within event loop context
async def main():
    async with aiohttp.ClientSession() as session:
        await fetch_data(session)

asyncio.run(main())
```

### Not Releasing Response Resources

**Symptom:** Memory growth, connection pool depletion over time

**Cause:** Not using `async with` or not calling `response.release()` leaves connections in limbo.

**Fix:**
```python
# ❌ ANTI-PATTERN: Not consuming response
async with session.get(url) as response:
    # Forgot to read/release
    pass
# Response may not be fully released

# ✅ FIX: Always consume or explicitly release
async with session.get(url) as response:
    data = await response.read()  # Consume fully
# OR
async with session.get(url) as response:
    if response.status != 200:
        response.release()  # Explicit release for early exit
        raise Exception(f"Unexpected status: {response.status}")
```

## Client/Server Selection Guidance

### When to Tune TCPConnector

**Plain `ClientSession` is fine when:**
- Making occasional requests (< 10/second)
- Single host API calls
- Development/testing

**Tune `TCPConnector` when:**
- High throughput (> 100 req/s) → increase `limit` and `limit_per_host`
- Calling many different hosts → increase `limit`, keep `limit_per_host` moderate
- Connection errors under load → enable `enable_cleanup_closed=True`
- DNS lookups are slow → set `ttl_dns_cache=300` or higher

```python
# High-throughput single API
connector = aiohttp.TCPConnector(
    limit=500,
    limit_per_host=100,
    ttl_dns_cache=300
)

# Many different hosts (aggregator pattern)
connector = aiohttp.TCPConnector(
    limit=1000,
    limit_per_host=10,  # Don't overwhelm any single host
    ttl_dns_cache=600
)
```

### When aiohttp is Wrong

**Use httpx instead when:**
- Need HTTP/2 support (aiohttp's is experimental)
- Want sync API alongside async (httpx provides both)
- Using libraries that don't play well with aiohttp's connector

**Use sync HTTP client (requests) when:**
- Codebase is synchronous
- Integration with sync frameworks (Flask without ASGI, Django sync views)
- HTTP/2 not required and simplicity preferred

## Testing

See `references/testing.md` for pytest-aiohttp fixtures, test client usage, and lifespan testing patterns.

## Deep Dives

Load these reference files on demand for specific topics:

- **Middleware & Auth** — `references/middleware.md`: Global error handlers, logging, CORS, rate limiting, JWT/basic auth patterns (when implementing cross-cutting concerns)
- **Client & Performance** — `references/client.md`: WebSocket client, streaming uploads, compression, keepalive tuning (when optimizing client performance)
- **Testing & Lifespan** — `references/testing.md`: Application signals, lifespan context, test client, pytest-aiohttp fixtures (when writing tests)
- **Troubleshooting** — `references/troubleshooting.md`: Connection refused, timeouts, SSL errors, memory leaks (when debugging issues)

**Official Documentation**: https://docs.aiohttp.org/
**GitHub Repository**: https://github.com/aio-libs/aiohttp
**pytest-aiohttp**: https://pytest-aiohttp.readthedocs.io/
