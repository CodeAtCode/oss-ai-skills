> Loaded on demand from SKILL.md when the agent needs Pydantic schema definitions and ModelSchema configuration.

## Schema Definitions

### Pydantic v2 Context Support (Django 6.0+)

```python
class Payload(Schema):
    id: int
    request_path: str
    
    @staticmethod
    def resolve_request_path(data, context):
        return context["request"].get_full_path()
```

### Basic Schema

```python
from ninja import Schema
from datetime import datetime
from typing import Optional, List

class UserIn(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime

class UserUpdate(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
```

### ModelSchema (from Django Models)

```python
from ninja import ModelSchema
from .models import User, Post

class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PostSchema(ModelSchema):
    author: UserSchema  # Nested schema
    
    class Config:
        model = Post
        model_fields = ['id', 'title', 'slug', 'body', 'publish', 'status']

class PostCreateSchema(ModelSchema):
    class Config:
        model = Post
        model_fields = ['title', 'body', 'status']
        model_fields_optional = ['status']  # Optional fields

class PostUpdateSchema(ModelSchema):
    class Config:
        model = Post
        model_fields = ['title', 'body', 'status']
        model_fields_optional = '__all__'  # All fields optional
```

### Nested Schemas

```python
from typing import List

class CommentSchema(Schema):
    id: int
    content: str

class PostDetailSchema(Schema):
    id: int
    title: str
    author: UserSchema
    comments: List[CommentSchema]
```

### Pydantic-in-Django specifics

For full validator/type reference, see https://docs.pydantic.dev/. Focus on these Django-specific patterns:

```python
from ninja import Schema, ModelSchema
from pydantic import ConfigDict, field_validator
from typing import Optional, Partial

# DjangoGetter for lazy model field access (avoids N+1)
class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'email']

# ConfigDict(extra="forbid") for strict input validation
class CreatePostSchema(Schema):
    title: str
    body: str
    
    model_config = ConfigDict(extra="forbid")  # reject unknown fields

# Partial[ModelSchema] for PATCH requests
class UpdatePostSchema(Schema):
    title: Optional[str] = None
    body: Optional[str] = None

# Handling deferred/annotated values
class PostWithAnnotations(Schema):
    # Works with annotated/deferred model fields
    comment_count: int
    
    @staticmethod
    def resolve_comment_count(data, context):
        # Access request context for custom resolution
        return data.get("_comment_count", 0)
```

**Key points:**
- `ConfigDict(from_attributes=True)` required when reading from Django model instances (auto-set by `ModelSchema`)
- `extra="forbid"` prevents silent data loss on unknown input fields
- Use `Partial[]` or optional fields with defaults for PATCH operations
