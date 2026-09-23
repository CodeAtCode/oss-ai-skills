<!-- Loaded on demand from ../SKILL.md -->

# Common Patterns and Concurrency

## Common Patterns

### Connection Pool (Thread-safe)

```python
import sqlite3
import threading
from contextlib import contextmanager

class SQLitePool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self._local = threading.local()
        
    def get_connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode = WAL")
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn
    
    @contextmanager
    def cursor(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
```

### Split Tables Across Multiple Files

When tables don't need to join, put them in separate `.db` files. Each file
gets its own writer lock, so independent workloads stop contending.

```python
import sqlite3

users = sqlite3.connect("users.db")
events = sqlite3.connect("events.db")
# users.db and events.db have independent write locks,
# independent WAL files, and independent backups.
```

ATTACH can still cross-query when needed:

```sql
ATTACH 'events.db' AS events;
SELECT u.name, e.title FROM users u JOIN events.events e ON e.user_id = u.id;
```

Trade-off: no cross-database foreign keys, and transactions are not atomic
across files. Only split when the tables are genuinely independent.

### Migration Helper

```python
import sqlite3

MIGRATIONS = {
    1: """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    """,
    2: """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE INDEX idx_orders_user ON orders(user_id);
    """,
}

def run_migrations(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS _migrations (version INTEGER PRIMARY KEY)")
    
    current = conn.execute("SELECT MAX(version) FROM _migrations").fetchone()[0] or 0
    
    for version, sql in sorted(MIGRATIONS.items()):
        if version > current:
            conn.executescript(sql)
            conn.execute("INSERT INTO _migrations (version) VALUES (?)", (version,))
            conn.commit()
            print(f"Migration {version} applied")
    
    conn.close()
```

## Concurrent Access & Locking Issues

### The Problem: WAL Mode and Concurrency

WAL (Write-Ahead Logging) allows concurrent readers but **only ONE writer at a time**:

```python
# Problem: with busy_timeout=0, writers fail immediately
# SQLiteError: database is locked

# Solution: set appropriate busy_timeout
conn.execute("PRAGMA busy_timeout = 5000")  # 5 seconds retry
```

### Best Practices for Concurrent Access

```python
import sqlite3

def get_connection(db_path):
    conn = sqlite3.connect(db_path)

    # Performance
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -64000")

    # CRITICAL for concurrency
    conn.execute("PRAGMA busy_timeout = 5000")

    # Safety
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
```

### Long-Running Writes and Batch Deletes

WAL allows one writer at a time. A `DELETE FROM big_table WHERE ...` that runs
longer than `busy_timeout` blocks every other writer and can crash workers when
they hit the 5s default.

```python
# BAD: one big delete holds the write lock for seconds
conn.execute("DELETE FROM completed_tasks WHERE created_at < ?", (cutoff,))

# GOOD: delete in small batches so each transaction is sub-second
while True:
    cur = conn.execute(
        "DELETE FROM completed_tasks WHERE rowid IN ("
        "  SELECT rowid FROM completed_tasks WHERE created_at < ? LIMIT 1000"
        ")",
        (cutoff,),
    )
    conn.commit()
    if cur.rowcount == 0:
        break
```

For large maintenance, prefer scheduled maintenance windows over live batches.

### Isolation for Multiple Instances

To avoid contention in applications with multiple instances:

```python
import os

# Use XDG_DATA_HOME isolation for separate sessions
# Example: opencode run with multiple workers
os.environ['XDG_DATA_HOME'] = f'/tmp/opencode-{os.getpid()}'
# Each worker has its own DB
```