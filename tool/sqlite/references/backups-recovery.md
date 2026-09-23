<!-- Loaded on demand from ../SKILL.md -->

# Backups, Recovery, and Large Database Maintenance

## Backups

### Online Backup (Python API)

```python
import sqlite3

def backup_database(src_path, dst_path):
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    src.backup(dst)
    dst.close()
    src.close()
```

### VACUUM INTO (snapshot without holding a long lock)

`VACUUM INTO` produces a clean, defragmented copy in one statement. Pair with
`gzip` and an off-site uploader (restic, rsync, S3 CLI) for nightly snapshots.

```bash
sqlite3 /data/app.db "VACUUM INTO '/tmp/app.sqlite'"
gzip /tmp/app.sqlite
restic -r s3://bucket/backup backup /tmp/app.sqlite.gz
restic -r s3://bucket/backup forget -l 1 -H 6 -d 2 -w 2 -m 2 -y 2
restic -r s3://bucket/backup prune
```

`VACUUM INTO` reads the whole database, so on large DBs it can exceed memory
or time budgets under a busy writer — batch outside peak traffic.

### Litestream (streaming replication)

[Litestream](https://litestream.io/) continuously streams the WAL to S3-compatible
storage, giving near-zero-RPO recovery without full-database snapshots.

```yaml
# litestream.yml
dbs:
  - path: /data/app.db
    replicas:
      - url: s3://bucket/app
        retention: 400h
```

```bash
litestream replicate -config litestream.yml
# Restore:
# litestream restore -o /data/app.db s3://bucket/app
```

Prefer Litestream over scheduled `VACUUM INTO` when the database changes often —
incremental WAL shipping avoids the OOM risk of snapshotting a large DB.

### Verify backups

A backup that was never restored is a myth. Test restore on a throwaway instance
and `PRAGMA integrity_check;` before trusting it.

## Database Corruption Recovery

### Signs of Corruption

```
SQLiteError: database disk image is malformed
SQLiteError: file is not a database
SQLITE_CANTOPEN: unable to open database file
```

### Recovery Procedure

```bash
# 1. Make backup
cp corrupted.db corrupted.db.bak

# 2. Validate the database
sqlite3 corrupted.db "PRAGMA integrity_check;"
# Output: ok (if all good) or list of errors

# 3. Try to recover data
sqlite3 corrupted.db ".recover" | sqlite3 new.db

# 4. If it doesn't work, dump and rebuild
sqlite3 corrupted.db ".dump" 2>/dev/null | sqlite3 rebuilt.db
```

### Corruption Prevention

```python
# 1. Always use WAL mode (not DELETE) for consistency
conn.execute("PRAGMA journal_mode = WAL")

# 2. Clean close - don't kill process
# Use context manager
with sqlite3.connect('app.db') as conn:
    # work
# Auto-close guaranteed

# 3. Regular backups
def backup_db(src, dst):
    src_conn = sqlite3.connect(src)
    dst_conn = sqlite3.connect(dst)
    src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
```

## Large Database Maintenance

### Size Monitoring

```python
import os

def get_db_size(db_path):
    """Returns size in MB"""
    return os.path.getsize(db_path) / (1024 * 1024)

# Example: real OpenCode database
# Size: 1214 MB
# Sessions: 1542
# Messages: 61873
# Parts: 253442

db_size = get_db_size('app.db')
print(f"Database size: {db_size:.1f} MB")

if db_size > 1000:
    print("WARNING: Database > 1GB, consider maintenance")
```

### Periodic Maintenance

```python
def maintain_database(conn):
    """Call periodically or after many writes"""

    # VACUUM: rebuild and compact the database
    # Reduces size, rebuilds indexes
    conn.execute("VACUUM")

    # ANALYZE: update statistics for query planner
    # Useful after many INSERT/UPDATE/DELETE
    conn.execute("ANALYZE")

    # Check integrity
    result = conn.execute("PRAGMA integrity_check").fetchone()
    if result[0] != 'ok':
        print(f"WARNING: {result[0]}")

# Schedule: weekly or after N write operations
# NOTE: VACUUM doesn't work in transaction
```

### Statistics Queries

```sql
-- Basic statistics
SELECT 'Sessions:' as label, COUNT(*) FROM session;
SELECT 'Messages:' as label, COUNT(*) FROM message;
SELECT 'Parts:' as label, COUNT(*) FROM part;

-- Old sessions (>30 days)
SELECT COUNT(*) FROM session
WHERE time_updated < (strftime('%s', 'now') - 30*86400)*1000;

-- Orphan records (without relationships)
SELECT COUNT(*) FROM message m
LEFT JOIN session s ON m.session_id = s.id
WHERE s.id IS NULL;

SELECT COUNT(*) FROM part p
LEFT JOIN message m ON p.message_id = m.id
WHERE m.id IS NULL;

-- Todo by status
SELECT status, COUNT(*) FROM todo GROUP BY status;
```