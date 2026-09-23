---
name: sqlite
description: Use when working with SQLite in Python - schema design, transactions, FTS5 full-text search, JSON columns, PRAGMA tuning, backups and corruption recovery, or multi-instance concurrency
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - sqlite
    - database
    - sql
    - embedded
    - python
    - db-api
---

# SQLite

SQLite - self-contained, serverless, zero-configuration SQL database engine.

## Overview

SQLite is an embedded relational database. The entire database is stored in a single cross-platform disk file. No server process needed.

- **Serverless** - No separate server process
- **Zero config** - No installation or setup
- **Single file** - Entire database in one `.db` file
- **ACID** - Full transactional support
- **Cross-platform** - Works everywhere

> See [Slicker.me SQLite Features](https://slicker.me/sqlite/features.htm) for a comprehensive feature overview.

---

## Python Integration

### Basic Usage

```python
import sqlite3

# Connect (creates file if not exists)
conn = sqlite3.connect('myapp.db')

# Use as context manager (auto-commits)
with sqlite3.connect('myapp.db') as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
    conn.commit()

# In-memory database
conn = sqlite3.connect(':memory:')
```

### Row Factory

```python
# Access columns by name
conn = sqlite3.connect('myapp.db')
conn.row_factory = sqlite3.Row

cursor = conn.execute("SELECT * FROM users")
for row in cursor:
    print(row['name'], row['email'])

# Or use dict factory
def dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

conn.row_factory = dict_factory
```

### CRUD Operations

```python
import sqlite3

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row

# Create
conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        in_stock INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert
conn.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
             ("Widget", 9.99, "gadgets"))

# Bulk insert
products = [("A", 1.0, "cat1"), ("B", 2.0, "cat2"), ("C", 3.0, "cat1")]
conn.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", products)
conn.commit()

# Read
cursor = conn.execute("SELECT * FROM products WHERE price > ?", (2.0,))
for row in cursor:
    print(dict(row))

# Update
conn.execute("UPDATE products SET price = ? WHERE name = ?", (12.99, "Widget"))
conn.commit()

# Delete
conn.execute("DELETE FROM products WHERE id = ?", (1,))
conn.commit()

conn.close()
```

---

## Schema Design

### Data Types

SQLite uses dynamic typing with storage classes:
- **NULL** - Null value
- **INTEGER** - Signed integer (1-8 bytes)
- **REAL** - Floating point (8-byte IEEE)
- **TEXT** - UTF-8, UTF-16BE, or UTF-16LE string
- **BLOB** - Binary data

### Table Creation

```sql
-- Basic table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- With foreign key
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Enable foreign keys (required in SQLite)
PRAGMA foreign_keys = ON;

-- Index
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);

-- Unique constraint
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Composite index
CREATE INDEX idx_products_cat_price ON products(category, price);
```

### Alter Table

```sql
-- SQLite supports limited ALTER TABLE
ALTER TABLE users ADD COLUMN avatar TEXT;
ALTER TABLE users RENAME COLUMN username TO handle;
ALTER TABLE users RENAME TO accounts;

-- For complex changes, recreate:
BEGIN TRANSACTION;
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
INSERT INTO users_new SELECT id, name, email FROM users;
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
COMMIT;
```

---

## Transactions

```python
# Manual transaction
conn = sqlite3.connect('app.db')
conn.execute("PRAGMA foreign_keys = ON")

try:
    conn.execute("BEGIN")
    conn.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (1, 99.99))
    conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (1,))
    conn.commit()
except Exception as e:
    conn.rollback()
    raise

# Context manager (auto-commit or rollback)
with conn:
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
    # Auto-commits on success, auto-rollback on exception
```

---

## Full-Text Search (FTS5)

```sql
-- Create FTS table
CREATE VIRTUAL TABLE articles_fts USING fts5(title, body, content='articles', content_rowid='id');

-- Populate
INSERT INTO articles_fts (rowid, title, body) SELECT id, title, body FROM articles;

-- Search
SELECT * FROM articles_fts WHERE articles_fts MATCH 'sqlite AND python';
SELECT * FROM articles_fts WHERE articles_fts MATCH 'sqlite OR database';
SELECT * FROM articles_fts WHERE articles_fts MATCH '"full text search"';

-- Ranked results
SELECT rank, * FROM articles_fts WHERE articles_fts MATCH 'sqlite' ORDER BY rank;

-- Keep FTS in sync with triggers
CREATE TRIGGER articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts (rowid, title, body) VALUES (new.id, new.title, new.body);
END;

CREATE TRIGGER articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts (articles_fts, rowid, title, body) VALUES ('delete', old.id, old.title, old.body);
END;
```

---

## JSON Support

```sql
-- Store JSON in TEXT column
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    data TEXT
);

-- Extract values
SELECT json_extract(data, '$.name') FROM events;
SELECT json_extract(data, '$.tags[0]') FROM events;

-- Insert JSON
INSERT INTO events (data) VALUES (json('{"name": "click", "tags": ["ui", "btn"]}'));

-- JSON functions
SELECT json_type(data) FROM events;          -- 'object'
SELECT json_array_length(data, '$.tags') FROM events;  -- 2
SELECT json_insert(data, '$.count', 1) FROM events;
SELECT json_set(data, '$.count', 42) FROM events;
```

---

## CLI Commands

```bash
# Open database
sqlite3 myapp.db

# Execute SQL
sqlite3 myapp.db "SELECT * FROM users;"

# Import CSV
sqlite3 myapp.db -csv -header "SELECT * FROM users;" > output.csv

# Export schema
sqlite3 myapp.db ".schema"

# Dump database
sqlite3 myapp.db ".dump" > backup.sql

# Restore from dump
sqlite3 new.db < backup.sql

# List tables
sqlite3 myapp.db ".tables"

# Describe table
sqlite3 myapp.db ".schema users"
```

## Best Practices

### Essential PRAGMA Settings

```python
import sqlite3

conn = sqlite3.connect('app.db')

# Performance
conn.execute("PRAGMA journal_mode = WAL")      # Write-Ahead Logging
conn.execute("PRAGMA synchronous = NORMAL")    # Balance safety/speed
conn.execute("PRAGMA cache_size = -64000")      # 64MB cache
conn.execute("PRAGMA temp_store = MEMORY")     # Temp tables in memory
conn.execute("PRAGMA mmap_size = 268435456")    # 256MB memory map

# Safety
conn.execute("PRAGMA foreign_keys = ON")       # Enforce FK constraints
conn.execute("PRAGMA busy_timeout = 5000")      # Wait 5s on lock

# Always enable WAL mode for concurrent access
# Benefits: better concurrency, atomic writes, faster reads
```

### Connection Management

```python
# Use context manager (auto-commits/rollbacks)
with sqlite3.connect('app.db') as conn:
    conn.execute("INSERT INTO users VALUES (?, ?)", (name, email))
    # Auto-commits, auto-closes

# Row factory for column access
conn.row_factory = sqlite3.Row  # Access by name: row['column']

# Never leave connections open
# For web apps: create per-request, close after response
```

### Performance Tips

```python
# Use executemany for bulk inserts
data = [(f"user{i}", f"email{i}@test.com") for i in range(1000)]
conn.executemany("INSERT INTO users (name, email) VALUES (?, ?)", data)

# Disable sync for bulk loads
conn.execute("PRAGMA synchronous = OFF")
# ... bulk insert ...
conn.execute("PRAGMA synchronous = NORMAL")

# Create indexes after data load (faster)
# CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);

# Use EXPLAIN QUERY PLAN to analyze queries
```

### Thread Safety

```python
# Each thread needs its own connection
# ❌ BAD: Shared connection
# conn = sqlite3.connect('app.db')  # Don't share across threads

# ✅ GOOD: Thread-local connections
import threading
thread_local = threading.local()

def get_db():
    if not hasattr(thread_local, 'conn'):
        thread_local.conn = sqlite3.connect('app.db')
    return thread_local.conn
```

### Key Patterns

```python
# Use parameterized queries (prevent SQL injection)
# ✅ GOOD
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ BAD - vulnerable to SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Use INTEGER PRIMARY KEY for auto-increment
# Don't use TEXT PRIMARY KEY (slower)

# Add indexes on foreign keys and WHERE columns
# CREATE INDEX idx_orders_user ON orders(user_id);
```

### Do:

- Enable WAL mode for concurrent access
- Always use parameterized queries
- Set busy_timeout for handling locks
- Use context managers for connections

### Don't:

- Use strings for PRIMARY KEY when INTEGER suffices
- Run ANALYZE after every write (do it periodically)
- Use database file on network drives (slow)
- Forget to enable foreign keys (they're off by default)

---

## References

- **SQLite Docs**: https://www.sqlite.org/docs.html
- **SQLite Python**: https://docs.python.org/3/library/sqlite3.html
- **SQL As Understood By SQLite**: https://www.sqlite.org/lang.html
- **SQLite WAL**: https://www.sqlite.org/wal.html
- **SQLite Limits**: https://www.sqlite.org/limits.html
- **Corruption FAQ**: https://www.sqlite.org/lockingv3.html
- **OpenCode Issue #21215**: concurrent sessions crash with SQLITE_BUSY
- **OpenCode Issue #21790**: sessions lost due to failed migration
- **jvns.ca – Learning about running SQLite**: https://jvns.ca/blog/2026/07/17/learning-about-running-sqlite/

---

## Deep Dives

Load these reference files on demand for specialized topics:

- **[Advanced Queries & Optimization](references/queries-optimization.md)** — Joins, window functions, upsert, PRAGMA tuning, query analysis, ANALYZE, bulk operations
- **[Backups & Recovery](references/backups-recovery.md)** — Online backup, VACUUM INTO, Litestream, corruption recovery, large database maintenance
- **[Patterns & Concurrency](references/patterns-concurrency.md)** — Connection pooling, split tables, migration helpers, WAL locking, batch deletes, multi-instance isolation