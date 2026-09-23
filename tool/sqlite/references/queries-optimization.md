<!-- Loaded on demand from ../SKILL.md -->

# Advanced Queries and Optimization

## Advanced Queries

### Joins

```sql
-- Inner join
SELECT o.id, u.username, o.total, o.status
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.status = 'completed';

-- Left join
SELECT u.username, COUNT(o.id) as order_count, COALESCE(SUM(o.total), 0) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
HAVING order_count > 0;

-- Subquery
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Common Table Expression (CTE)
WITH active_users AS (
    SELECT id, username FROM users WHERE is_active = 1
)
SELECT au.username, COUNT(o.id) as orders
FROM active_users au
LEFT JOIN orders o ON au.id = o.user_id
GROUP BY au.id;
```

### Window Functions

```sql
-- Row number
SELECT name, price,
    ROW_NUMBER() OVER (ORDER BY price DESC) as rank
FROM products;

-- Partitioned aggregation
SELECT name, category, price,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) as category_rank,
    AVG(price) OVER (PARTITION BY category) as avg_category_price
FROM products;

-- Running total
SELECT id, total,
    SUM(total) OVER (ORDER BY id) as running_total
FROM orders;
```

### Upsert (INSERT OR REPLACE)

```sql
-- Insert or replace
INSERT OR REPLACE INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@new.com');

-- Insert or ignore (skip if conflict)
INSERT OR IGNORE INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com');

-- UPSERT with DO UPDATE (SQLite 3.24+)
INSERT INTO users (username, email)
VALUES ('bob', 'bob@example.com')
ON CONFLICT(username) DO UPDATE SET
    email = excluded.email;
```

## Optimization

### PRAGMA Settings

```python
conn = sqlite3.connect('app.db')

# Performance
conn.execute("PRAGMA journal_mode = WAL")         # Write-Ahead Logging
conn.execute("PRAGMA synchronous = NORMAL")        # Balance safety/speed
conn.execute("PRAGMA cache_size = -64000")          # 64MB cache
conn.execute("PRAGMA temp_store = MEMORY")          # Temp tables in memory
conn.execute("PRAGMA mmap_size = 268435456")        # 256MB memory map

# Safety
conn.execute("PRAGMA foreign_keys = ON")            # Enable FK constraints
conn.execute("PRAGMA busy_timeout = 5000")          # Wait 5s on lock
```

### Query Analysis

```sql
-- Explain query plan
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Check indexes
SELECT * FROM pragma_index_list('users');

-- Table info
PRAGMA table_info(users);
PRAGMA index_list(users);
PRAGMA index_info(idx_users_email);
```

### Statistics with ANALYZE

The query planner picks indexes based on table statistics. Without them it can
choose catastrophically bad plans — an FTS5 query on a few thousand rows can go
from 5s to 0.05s after a single `ANALYZE`.

```sql
-- Gather statistics for the query planner
ANALYZE;

-- Re-run after bulk loads, schema changes, or significant data drift
-- Inspect stored stats:
SELECT * FROM sqlite_stat1;
SELECT * FROM sqlite_stat4;  -- if SQLITE_ENABLE_STAT4
```

Without `ANALYZE`, a 4000-row FTS5 table can pick an accidentally-quadratic
plan. Run it once after load, then schedule periodically.

### Bulk Operations

```python
# Fast bulk insert
conn.execute("PRAGMA synchronous = OFF")
conn.execute("PRAGMA journal_mode = MEMORY")

conn.executemany(
    "INSERT INTO large_table (col1, col2) VALUES (?, ?)",
    data  # list of tuples
)
conn.commit()

conn.execute("PRAGMA synchronous = NORMAL")
conn.execute("PRAGMA journal_mode = WAL")
```