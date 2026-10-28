> Loaded on demand from SKILL.md when the agent needs router HTTP methods, path/query parameters, and request body patterns.

## Router & API

### HTTP Methods

```python
from ninja import NinjaAPI
from .schemas import UserIn, UserOut, PostSchema

api = NinjaAPI()

# GET - Retrieve resources
@api.get("/users", response=List[UserOut])
def list_users(request):
    return User.objects.all()

@api.get("/users/{user_id}", response=UserOut)
def get_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user

# POST - Create resources
@api.post("/users", response=UserOut)
def create_user(request, payload: UserIn):
    user = User.objects.create_user(**payload.dict())
    return user

# PUT - Full update
@api.put("/users/{user_id}", response=UserOut)
def update_user(request, user_id: int, payload: UserUpdate):
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return user

# PATCH - Partial update
@api.patch("/users/{user_id}", response=UserOut)
def partial_update_user(request, user_id: int, payload: UserUpdate):
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return user

# DELETE
@api.delete("/users/{user_id}")
def delete_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"success": True}
```

### Path Parameters

```python
from ninja import Path

@api.get("/posts/{post_id}/comments/{comment_id}")
def get_comment(request, post_id: int, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    return {"comment": comment.content}

# UUID path parameters
import uuid

@api.get("/orders/{order_id}")
def get_order(request, order_id: uuid.UUID):
    return get_object_or_404(Order, id=order_id)
```

### Query Parameters

```python
from ninja import Query, Schema
from typing import Optional, List
from datetime import date

class FilterParams(Schema):
    search: Optional[str] = None
    status: Optional[str] = None
    ordering: Optional[str] = "-created_at"
    page: int = 1
    page_size: int = 20

@api.get("/posts", response=List[PostSchema])
def list_posts(request, filters: FilterParams = Query(...)):
    posts = Post.objects.all()
    
    if filters.search:
        posts = posts.filter(Q(title__icontains=filters.search))
    if filters.status:
        posts = posts.filter(status=filters.status)
    
    posts = posts.order_by(filters.ordering)
    return posts[(filters.page - 1) * filters.page_size:filters.page * filters.page_size]
```

### Request Body

```python
from ninja import Body, Schema
from typing import List

class PostCreate(Schema):
    title: str
    body: str
    category_ids: List[int]
    tags: List[str] = []

@api.post("/posts", response=PostSchema)
def create_post(request, payload: PostCreate):
    post = Post.objects.create(title=payload.title, body=payload.body, author=request.user)
    if payload.category_ids:
        post.categories.set(payload.category_ids)
    return post

# Multiple body parameters
@api.post("/posts/{post_id}/comments")
def add_comment(request, post_id: int, content: str = Body(...), author_name: str = Body(...)):
    return Comment.objects.create(post_id=post_id, content=content, author_name=author_name)
```

### Form Data

```python
from ninja import Form, Schema, File
from django.core.files.uploadedfile import UploadedFile

class ContactForm(Schema):
    name: str
    email: str
    message: str

@api.post("/contact")
def contact_form(request, data: ContactForm = Form(...)):
    send_contact_email(data.name, data.email, data.message)
    return {"status": "sent"}

@api.post("/upload")
def upload_file(request, file: UploadedFile = File(...), description: str = Form(...)):
    pass
```
