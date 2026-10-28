---
name: django-ninja
description: Use when building Django REST APIs with django-ninja - Pydantic schemas, routers, CRUD endpoints, authentication, pagination, file uploads, async views, OpenAPI docs, or migrating from DRF
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - django
    - rest-api
    - pydantic
    - openapi
    - type-safe
---

> **Objective:** Use this skill to reduce schema-validation bypass, N+1-in-serializer incidents, auth-decorator misapplication, and OpenAPI-drift bugs by enforcing Pydantic-boundary discipline, queryset-loading rules, and router-auth patterns below.

# Django Ninja

Build fast, type-safe REST APIs with Django and Pydantic v2.

## Overview

Django Ninja provides automatic request validation, response serialization, and generates OpenAPI documentation.

**Versions**: django-ninja 1.6.x + Django 6.0 compatible. Requires Pydantic v2.

## Installation

```bash
pip install django-ninja
```

### Django Integration

**Do** add `ninja` to `INSTALLED_APPS` because the framework needs its middleware and URL helpers:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'ninja',
]
```

### Basic Setup

**Do** create a `NinjaAPI` instance and expose it via Django URLs:

```python
# api.py
from ninja import NinjaAPI

api = NinjaAPI()

@api.get("/hello")
def hello(request):
    return {"message": "Hello World"}

# urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

## Deep Dives

See these reference files for detailed patterns:

- **references/drf-migration.md** — DRF-to-django-ninja migration patterns
- **references/schema-reference.md** — Pydantic schema definitions, ModelSchema configuration, nested schemas
- **references/router-endpoints.md** — HTTP methods, path/query parameters, request body, form data
- **references/auth-pagination-errors.md** — Authentication methods, pagination strategies, error handling
- **references/crud-patterns.md** — CRUD operations, bulk operations, relationship handling
- **references/files-async-openapi.md** — File uploads, async support, OpenAPI customization
- **references/django-integration.md** — Django ORM integration, middleware, signals, production practices
- **references/testing-troubleshooting.md** — Testing with pytest, auth testing, common issues

## Runtime Behavior

### Validation Timing

**Do** rely on validation happening before the resolver executes because failed input never reaches your business logic:

```python
# This never runs if payload fails validation
@api.post("/posts", response=PostSchema)
def create_post(request, payload: PostCreateSchema):
    # payload is guaranteed valid here
    return Post.objects.create(**payload.dict())
```

### The `response=` Parameter

**Do** always specify `response=` because it affects both runtime serialization AND OpenAPI schema generation:

```python
# Without response= — OpenAPI shows 200 with empty schema
@api.get("/health")
def health(request):
    return {"status": "ok"}  # Works, but docs are incomplete

# With response= — OpenAPI documents the actual response
@api.get("/health", response=dict)
def health(request):
    return {"status": "ok"}  # Docs show {"status": "string"}
```

**Failure mode:** omitting `response=` on endpoints that return data causes generated clients to have no type information.

### `dict`/`list` Annotations Bypass Validation

**Do** use `Schema` classes instead of bare `dict`/`list` because raw types bypass Pydantic validation:

```python
# Bypasses Pydantic validation — raw dict passthrough
@api.post("/raw", response=dict)
def raw_handler(request, payload: dict):
    return payload  # No validation, no type safety

# Use Schema for validation
@api.post("/typed", response=PostSchema)
def typed_handler(request, payload: PostCreateSchema):
    return Post.objects.create(**payload.dict())  # Validated
```

### `operation_id` Contract

**Do** set stable `operation_id` values because code generation tools use them and changing them breaks existing clients:

```python
# Stable operation IDs for client generation
@api.get("/posts/{id}", operation_id="get_post")
def get_post(request, id: int):
    ...

# Bad: changing this breaks existing generated clients
@api.get("/posts/{id}", operation_id="fetch_post")  # Breaking change!
```

## Testing

### TestClient from django-ninja

**Do** use `TestClient` for unit testing because it doesn't require a running server:

```python
from ninja.testing import TestClient
from .api import api  # Your NinjaAPI instance

client = TestClient(api)

def test_list_posts():
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Post"

def test_create_post():
    payload = {"title": "New Post", "body": "Content here"}
    response = client.post("/posts", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_validation_error():
    payload = {"title": ""}  # Missing required field
    response = client.post("/posts", json=payload)
    assert response.status_code == 422  # Validation error
```

### Testing Auth Callbacks

**Do** test auth callbacks directly because they can fail independently of endpoints:

```python
from ninja.security import HttpBearer

class CustomAuth(HttpBearer):
    def __call__(self, request, token: str):
        if not is_valid_token(token):
            raise PermissionError("Invalid token")
        request.user = get_user_by_token(token)
        return request.user

# Test the auth callback directly
def test_custom_auth_invalid():
    auth = CustomAuth()
    try:
        auth(None, "invalid_token")
        assert False, "Should have raised"
    except PermissionError:
        pass  # Expected

# Test endpoint with auth
@api.get("/protected", auth=CustomAuth())
def protected(request):
    return {"user": request.user.username}

def test_protected_endpoint():
    response = client.get("/protected")
    assert response.status_code == 401  # No auth header
    
    response = client.get("/protected", headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
```

### Separating Resolver Logic from HTTP

**Do** extract business logic into pure functions because it makes testing easier without Django:

```python
# business_logic.py — pure functions, no HTTP dependencies
def create_post_data(title: str, body: str, author_id: int) -> dict:
    """Pure function — easy to test without Django."""
    return {
        "title": title.strip(),
        "body": body.strip(),
        "author_id": author_id,
    }

# api.py — thin HTTP layer
class PostCreateSchema(Schema):
    title: str
    body: str

@api.post("/posts", response=PostSchema)
def create_post(request, payload: PostCreateSchema):
    data = create_post_data(payload.title, payload.body, request.user.id)
    return Post.objects.create(**data)
```

## Ecosystem Libraries

### django-ninja-extra
**PyPI**: `django-ninja-extra` | **URL**: https://github.com/eadwinCode/django-ninja-extra

**Use** when you need class-based controllers (`@api_controller`) or DRF-style permission classes. **Tradeoff:** adds complexity; prefer function-based handlers for simple APIs.

### django-ninja-jwt
**PyPI**: `django-ninja-jwt` | **URL**: https://github.com/eadwinCode/django-ninja-jwt

**Use** for JWT authentication (obtain/refresh/verify tokens). **Tradeoff:** pulls in `django-ninja-extra` as a dependency. For custom token logic, write your own `HttpBearer` subclass instead.

### django-ninja-aio-crud
**PyPI**: `django-ninja-aio-crud` | **URL**: https://github.com/caspel26/django-ninja-aio-crud

**Use** for auto-generated async CRUD endpoints with built-in filtering/pagination. **Tradeoff:** opinionated structure; harder to customize than hand-written handlers.

### django-contract-tester
**PyPI**: `django-contract-tester` | **URL**: https://github.com/maticardenas/django-contract-tester

**Use** to validate test requests/responses against OpenAPI schemas. **Tradeoff:** only needed for strict contract testing; regular pytest assertions work for most cases.

## References

- **Official Documentation**: https://django-ninja.dev/
- **GitHub Repository**: https://github.com/vitalik/django-ninja
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **OpenAPI Specification**: https://swagger.io/specification/
- **Django Documentation**: https://docs.djangoproject.com/
