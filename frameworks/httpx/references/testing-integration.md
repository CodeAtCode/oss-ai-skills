# Testing & Framework Integration

This file is loaded on demand from ../SKILL.md.

## respx Deep Dive

```python
import httpx
import respx
import pytest

@respx.mock
def test_assert_request_properties():
    """Assert method, URL, headers, and body."""
    route = respx.post("https://api.example.com/users").mock(
        return_value=httpx.Response(201, json={"id": 123})
    )

    client = httpx.Client()
    response = client.post(
        "https://api.example.com/users",
        json={"name": "Alice"},
        headers={"X-Request-ID": "abc-123"}
    )

    assert route.called
    request = route.calls[0].request
    
    # Assert request properties
    assert request.method == b"POST"
    assert request.headers.get(b"x-request-id") == b"abc-123"
    
    # Assert request body
    import json
    body = json.loads(request.content)
    assert body == {"name": "Alice"}
```

**Pattern matching:**

```python
import respx
import httpx

@respx.mock
def test_query_param_matching():
    """Match on query parameters."""
    route = respx.get("https://api.example.com/search").params(
        q="python", page=1
    ).mock(return_value=httpx.Response(200))
    
    response = httpx.get("https://api.example.com/search", params={"q": "python", "page": 1})
    assert route.called
```

**Side effects for stateful testing:**

```python
import respx
import httpx

@respx.mock
def test_sequential_responses():
    """Different responses for same endpoint."""
    call_count = 0
    
    def side_effect(request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(503)  # First call fails
        return httpx.Response(200, json={"data": "success"})
    
    route = respx.get("https://api.example.com/data").mock(side_effect=side_effect)
    
    # First call fails
    response1 = httpx.get("https://api.example.com/data")
    assert response1.status_code == 503
    
    # Second call succeeds
    response2 = httpx.get("https://api.example.com/data")
    assert response2.status_code == 200
```

## FastAPI Integration

```python
from fastapi import FastAPI, Depends
import httpx

app = FastAPI()

# Dependency injection for httpx client
def get_http_client() -> httpx.Client:
    with httpx.Client(timeout=30.0) as client:
        yield client

@app.get("/users/{user_id}")
def get_user(user_id: int, client: httpx.Client = Depends(get_http_client)):
    response = client.get(f"https://api.example.com/users/{user_id}")
    return response.json()
```

**Testing FastAPI with httpx:**

```python
from fastapi.testclient import TestClient
import httpx
import respx

def test_fastapi_endpoint(respx_mock):
    """Test FastAPI endpoint that calls external API."""
    # Mock external API call
    respx_mock.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
    )
    
    from main import app
    client = TestClient(app)
    
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice"}
```

## Django Integration

```python
from django.http import JsonResponse
import httpx

def external_api_view(request):
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            "https://api.example.com/data",
            headers={"Authorization": f"Bearer {request.user.token}"}
        )
        response.raise_for_status()
        return JsonResponse(response.json())
```

**Async Django views:**

```python
from django.http import JsonResponse
import httpx
import asyncio

async def async_external_api_view(request):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://api.example.com/data")
        response.raise_for_status()
        return JsonResponse(response.json())
```

## Testing Retry Logic

```python
import httpx
from httpx import MockTransport
import time

def test_retry_with_mock_transport():
    """Test retry behavior without actual network delays."""
    call_count = 0
    
    def flaky_transport(request):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectTimeout("Simulated timeout", request=request)
        return httpx.Response(200, json={"success": True})
    
    transport = MockTransport(flaky_transport)
    client = httpx.Client(transport=transport)
    
    # Your retry logic
    try:
        response = client.get("https://example.com")
        assert response.json() == {"success": True}
        assert call_count == 3  # Verified retry count
    except httpx.ConnectTimeout:
        pytest.fail("Retry logic should have handled this")
```
