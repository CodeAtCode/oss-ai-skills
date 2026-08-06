---
name: redis
description: "Redis v8.0 - in-memory database, caching, pub/sub, sessions, rate limiting, data structures with RESP3 default and asyncio module"
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - redis
    - database
    - caching
    - pub-sub
    - sessions
    - rate-limiting
    - data-structures
    - nosql
    - resp3
    - asyncio
---

# Redis (redis-py v8.0)

Redis - in-memory data structure store, used as database, cache, and message broker.

**redis-py v8.0 changes:**
- Python 3.10+ required
- RESP3 is the default protocol (was RESP2 in 7.x)
- Async API: `redis.asyncio` module (not `.asyncio` property)

## Installation

```bash
pip install redis
```

## Basic Usage

### Synchronous Client

```python
import redis

# Default protocol is now RESP3
r = redis.Redis(host='localhost', port=6379, db=0)

# Basic commands
r.set('foo', 'bar')
value = r.get('foo')  # b'bar'

# Close connection
r.close()
```

### RESP2 vs RESP3

```python
# RESP3 (default in v8.0)
r = redis.Redis(protocol=3)

# Opt back into RESP2
r = redis.Redis(protocol=2)
```

### Async Client

```python
import redis.asyncio as redis

async def example():
    # Default protocol is RESP3
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    await r.set('foo', 'bar')
    value = await r.get('foo')  # b'bar'
    
    # Close connection
    await r.aclose()
```

**Migration from v7.x:**
```python
# OLD (v7.x and earlier)
from redis import Redis
r = Redis()
client = r.asyncio  # Property

# NEW (v8.0+)
import redis.asyncio as redis
r = redis.Redis()
```

## Connection Pool

```python
# Create a connection pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)

# Use pool with client
r = redis.Redis(connection_pool=pool)
```

### Connection Pool with Password

```python
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    password='your_password',
    max_connections=100,
)
r = redis.Redis(connection_pool=pool)
```

## Core Commands

### Strings

```python
# Set
r.set('key', 'value')
r.set('key', 'value', ex=300)  # Expiration in seconds
r.setnx('key', 'value')  # Set if not exists
r.mset({'key1': 'value1', 'key2': 'value2'})

# Get
value = r.get('key')
values = r.mget(['key1', 'key2'])

# Delete
r.delete('key')
r.delete('key1', 'key2', 'key3')

# Exists
exists = r.exists('key')

# TTL
ttl = r.ttl('key')  # Time to live in seconds
r.expire('key', 300)  # Set expiration
```

### Hashes

```python
# Set hash field
r.hset('user:1', 'name', 'Alex')
r.hset('user:1', mapping={'name': 'Alex', 'email': 'alex@example.com'})

# Get hash field
name = r.hget('user:1', 'name')
user = r.hgetall('user:1')  # All fields

# Check field exists
exists = r.hexists('user:1', 'name')

# Get all fields
fields = r.hkeys('user:1')
values = r.hvals('user:1')

# Delete field
r.hdel('user:1', 'name')
```

### Lists

```python
# Push to list
r.lpush('mylist', 'item1', 'item2')
r.rpush('mylist', 'item3')

# Pop from list
item = r.lpop('mylist')
item = r.rpop('mylist')

# Get range
items = r.lrange('mylist', 0, -1)

# List length
length = r.llen('mylist')
```

### Sets

```python
# Add to set
r.sadd('myset', 'item1', 'item2', 'item3')

# Check membership
exists = r.sismember('myset', 'item1')

# Get all members
members = r.smembers('myset')

# Remove from set
r.srem('myset', 'item1')

# Set operations
r.sunion('set1', 'set2')
r.sinter('set1', 'set2')
```

### Sorted Sets

```python
# Add to sorted set
r.zadd('scores', {'player1': 100, 'player2': 200})

# Get range by score
top_players = r.zrange('scores', 0, -1, withscores=True)

# Get range by rank
top_players = r.zrevrange('scores', 0, 9)  # Top 10

# Remove from sorted set
r.zrem('scores', 'player1')

# Score of member
score = r.zscore('scores', 'player1')
```

## Redis Stack Modules

### Redis Search

```python
# Create index
r.ft().create_index((
    TextField('name'),
    NumericField('age'),
    TagField('tags'),
))

# Search
results = r.ft().search('@name:alex @age:[20 30]')

# Drop index
r.ft().dropindex()
```

### Redis JSON

```python
from redis.commands.json.path import Path

# Set JSON document
r.json().set('/user:1', Path.root_path(), {
    'name': 'Alex',
    'age': 30,
    'tags': ['developer', 'python'],
})

# Get JSON document
user = r.json().get('/user:1')

# Get specific field
name = r.json().get('/user:1', Path('$.name'))

# Merge update
r.json().merge('/user:1', Path.root_path(), {'age': 31})

# Delete field
r.json().del_('/user:1', Path('$.age'))
```

### Redis TimeSeries

```python
# Create time series
r.ts().create('sensor:1')

# Add data point
r.ts().add('sensor:1', '*', 25.3)  # Current timestamp
r.ts().add('sensor:1', 1234567890, 25.5)  # Specific timestamp

# Get range
data = r.ts().range('sensor:1', 0, '*')

# Add with aggregation
r.ts().add('sensor:1', '*', 25.3)
aggregated = r.ts().range('sensor:1', 0, '*', agg_type='avg', bucket_size=60000)
```

## Pipelines

```python
# Basic pipeline
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.get('key1')
results = pipe.execute()  # [True, True, b'value1']

# Watch for transactions
pipe = r.pipeline(True)
pipe.watch('mykey')
val = pipe.get('mykey')
pipe.multi()
pipe.set('mykey', val + 1)
pipe.execute()
```

## Django Integration

### django-redis (still works with v8.0)

```bash
pip install django-redis
```

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
                'protocol': 3,  # RESP3
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'myapp',
        'VERSION': 1,
    }
}
```

```python
from django.core.cache import cache

# Set with expiration
cache.set('key', 'value', timeout=300)

# Get
value = cache.get('key', 'default_value')

# Delete
cache.delete('key')
cache.delete_pattern('user_*')
```

### Celery Broker

```python
# settings.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Django Channels

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

## Redis CLI

```bash
# Connect
redis-cli

# Check keys
KEYS *

# Delete by pattern (use with caution)
SCAN 0 MATCH user:* COUNT 1000 | xargs redis-cli DEL

# Clear current database
FLUSHDB

# Monitor commands
MONITOR
```

## Best Practices

### Connection Management

```python
from redis import ConnectionPool

# Reuse connection pool globally
pool = ConnectionPool.from_url('redis://localhost:6379/0', max_connections=50)

def get_redis():
    return redis.Redis(connection_pool=pool)
```

### Key Design

```python
# Use namespaced keys
KEY_PREFIX = 'myapp'
VERSION = 1
# Keys become: myapp:v1:user:123

# Add TTL to all keys
cache.set('temp_token', token, timeout=300)  # 5 min

# Use consistent naming
cache.set('user:profile:123', data)
cache.set('user:session:123', data)
```

### Performance

```python
# Batch operations
r.mset({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'})

# Use pipeline for multiple ops
pipe = r.pipeline()
pipe.set('a', 1)
pipe.set('b', 2)
pipe.execute()  # Atomic, single round-trip

# Use SCAN instead of KEYS * in production
cursor = 0
while True:
    cursor, keys = r.scan(cursor, match='user:*', count=100)
    # Process keys
    if cursor == 0:
        break
```

### Error Handling

```python
from redis.exceptions import ConnectionError, TimeoutError

try:
    value = r.get('key')
except ConnectionError:
    # Fallback to DB or default
    value = get_from_db()
except TimeoutError:
    # Handle timeout
    value = get_cached_default()
```

### Do:

- Always set TTL (expire keys)
- Use key prefixes for namespacing
- Reuse connections (use connection pool)
- Use pipeline for batch operations
- Use SCAN instead of KEYS * in production

### Don't:

- Use KEYS * in production (blocks Redis)
- Store large values (>1MB consider compression)
- Use Redis as primary data store (it's a cache)
- Forget connection timeout settings
- Create new connection per request

## Migration from v7.x

### Breaking Changes

1. **Python 3.10+ required**
   - Drop support for Python 3.9 and earlier

2. **RESP3 is default**
   ```python
   # v7.x defaulted to RESP2
   # v8.0 defaults to RESP3
   r = redis.Redis()  # Now RESP3
   r = redis.Redis(protocol=2)  # Opt into RESP2
   ```

3. **Async import path changed**
   ```python
   # v7.x
   from redis import Redis
   client = Redis().asyncio
   
   # v8.0
   import redis.asyncio as redis
   client = redis.Redis()
   ```

## References

- [redis-py Official Documentation](https://redis.readthedocs.io/)
- [redis-py v8.0 Release Notes](https://github.com/redis/redis-py/releases)
- [Redis Stack Documentation](https://redis.io/docs/stack/)
- [RESP3 Protocol Specification](https://github.com/antirez/redis-doc/blob/master/RESP3.md)