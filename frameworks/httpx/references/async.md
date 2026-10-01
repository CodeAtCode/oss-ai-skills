# Async Patterns

This file is loaded on demand from ../SKILL.md.

## AsyncClient Setup

```python
import asyncio
import httpx

# Basic async client
async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        return response.text

asyncio.run(fetch())

# With default configuration
client = httpx.AsyncClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=httpx.Timeout(connect=5.0, read=30.0)
)
```

## Concurrent Requests

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[httpx.Response]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        return await asyncio.gather(*tasks)

async def main():
    urls = [
        "https://api.example.com/users/1",
        "https://api.example.com/users/2",
        "https://api.example.com/users/3",
    ]
    responses = await fetch_all(urls)
    for response in responses:
        print(response.json())

asyncio.run(main())
```

**With connection limits:**

```python
async def fetch_with_limits(urls: list[str]):
    limits = httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30
    )
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [client.get(url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Streaming

```python
import asyncio
import httpx

async def stream_download(url: str, destination: str):
    """Stream a large file to disk."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            with open(destination, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)

asyncio.run(stream_download("https://example.com/large-file", "download.zip"))
```

**Async streaming upload:**

```python
async def stream_upload(url: str, source: str):
    """Stream a large file as request body."""
    async with httpx.AsyncClient() as client:
        async def generate():
            with open(source, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk
        
        response = await client.post(url, content=generate())
        print(response.status_code)

asyncio.run(stream_upload("https://api.example.com/upload", "large-file.bin"))
```

## Event Loop Integration

```python
import asyncio
import httpx

# Run httpx in existing event loop
async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        return response.text

# Correct: Use asyncio.run() for top-level entry
result = asyncio.run(main())

# Wrong: Don't create new event loop inside running loop
# asyncio.new_event_loop()  # This will fail if already running
```
