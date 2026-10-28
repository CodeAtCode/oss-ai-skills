> Loaded on demand from SKILL.md when the agent needs DRF-to-django-ninja migration patterns.

## DRF to Django Ninja Migration

**What has no clean equivalent:** browsable API, `get_serializer_class()` polymorphism, complex nested serializers with dynamic depth.

**Mapping table:**

| DRF pattern | Django Ninja equivalent |
|-------------|------------------------|
| `ModelSerializer` | `ModelSchema` (generated from model) |
| `ViewSet` | `Router` + `api.get`/`api.post` decorators |
| `perform_create()` | resolver body (function body) |
| `APIView` class | function-based handler |
| `IsAuthenticated` | operation-level auth callback (`auth=`) |
| `PageNumberPagination` | `paginate(PageNumberPagination)` decorator |

**Before (DRF):**

```python
# serializers.py
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'body']

# views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

**After (Django Ninja):**

```python
# schemas.py
class PostSchema(ModelSchema):
    class Config:
        model = Post
        model_fields = ['id', 'title', 'body']

# api.py
@api.get("/posts", response=List[PostSchema], auth=IsAuthenticated())
def list_posts(request):
    return Post.objects.all()

@api.post("/posts", response=PostSchema, auth=IsAuthenticated())
def create_post(request, payload: PostCreateSchema):
    return Post.objects.create(author=request.user, **payload.dict())
```
