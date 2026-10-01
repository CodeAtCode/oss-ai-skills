---
name: celery
description: Use when running background tasks with Celery - worker and broker configuration (Redis, RabbitMQ), task routing by name vs queue, chains/groups/chords, retry patterns (autoretry_for, retry_backoff), acks_late semantics, failure detection, and monitoring with Flower
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - task-queue
    - async
    - distributed
    - celery
---

# Celery

Distributed task processing with focus on routing, composition, and failure handling.

## When Not to Use Celery

Before adopting Celery, check if you actually need it:

| Scenario | Better Alternative |
|----------|-------------------|
| Short-lived fan-out (5-10 parallel HTTP calls) | Simple thread pool or `asyncio.gather` |
| Single-server Django app with moderate load | Django 6.0+ built-in task queue |
| Work dominated by long IO (10+ min tasks) | Task-per-request model or job queue (dramatiq, huey) |
| Operational overhead unacceptable | django-tasks, RQ, or simple database polling |

**Check before adopting:**
- Do you need multiple workers across machines? (If no → simpler queue)
- Do you have 100+ tasks/minute sustained? (If no → overkill)
- Can you tolerate operational cost (broker + worker fleet + monitoring)? (If no → huey/dramatiq)

## Task Routing and Queue Configuration

### Routing by Task Name (Recommended)

```python
# settings.py or celery.py
CELERY_TASK_ROUTES = {
    'myapp.tasks.send_email': {'queue': 'email'},
    'myapp.tasks.process_video': {'queue': 'video'},
    'myapp.tasks.*': {'queue': 'default'},  # Catch-all
}
```

**Why routing by task name beats routing by queue name:**
- Task name is stable; queue name is an implementation detail
- You can move a task to a different queue without changing call sites
- Clearer intent: "send_email goes to email queue" vs "this call goes to high_priority"

### Precedence: Route vs Queue Argument

```python
# Task decorator sets default queue
@shared_task(queue='default')
def send_email(user_id):
    pass

# apply_async queue overrides decorator
send_email.apply_async(args=[1], queue='high_priority')  # Uses 'high_priority'

# But task_routes overrides both if configured
# CELERY_TASK_ROUTES = {'myapp.tasks.send_email': {'queue': 'critical'}}
# Result: 'critical' wins (routing function is final)
```

**Precedence order:** `task_routes` (routing function) > `apply_async(queue=...)` > decorator `@shared_task(queue=...)`

### Per-Queue Worker Startup

```bash
# High-priority queue: solo pool for immediate processing
celery -A myproject worker -Q high -P solo -n high@%h

# Low-priority queue: prefork for throughput
celery -A myproject worker -Q low -P prefork --concurrency=4 -n low@%h

# Mixed queues: one worker handles both
celery -A myproject worker -Q high,low -P prefork --concurrency=2
```

**Pool choices:**
- `solo`: Single process, no concurrency. Use for debugging or tasks that can't be parallelized.
- `prefork`: Default. Good for CPU-bound or mixed workloads.
- `eventlet`/`gevent`: High concurrency for I/O-bound tasks (100+ simultaneous).

### Critical Failure: Route to Queue with No Worker

```python
# Task routed to queue no one consumes
CELERY_TASK_ROUTES = {'myapp.tasks.cleanup': {'queue': 'cleanup'}}

# Problem: No worker started with -Q cleanup
# Result: Task sits in broker forever, silently. No error, no retry.
```

**Detection:**
```bash
# Check which queues have active workers
celery -A myproject inspect active

# Check queue depth
redis-cli LLEN celery  # For Redis broker

# Flower UI: Monitor queue lengths per queue
```

**Fix:** Start a worker for the queue OR remove the route so tasks go to a consumed queue.

## Task Composition: Chains, Groups, Chords

### When to Use Each

| Pattern | Use Case | Requires Backend |
|---------|----------|------------------|
| `chain` | Sequential steps (A → B → C) | No (but needed for `.get()`) |
| `group` | Parallel independent tasks | No (but needed for results) |
| `chord` | Parallel + callback (wait for all, then run) | **Yes** (stores intermediate results) |

### Chains (Sequential)

```python
from celery import chain

# Correct: Results flow through
workflow = chain(
    validate_user.s(user_id),
    process_data.s(),
    send_notification.s()
)
result = workflow.apply_async()
# Each task's output becomes next task's input

# Error handling: link error callback
from celery import group

error_handler = handle_error.s()
workflow = (
    chain(validate.s(), process.s()) |
    save_result.s()
)
workflow.apply_async(link_error=error_handler)
```

### Groups (Parallel)

```python
from celery import group

# Correct: Independent parallel tasks
job = group(
    fetch_data.s(source_id)
    for source_id in [1, 2, 3, 4, 5]
)
result = job.apply_async()
all_results = result.get()  # [res1, res2, res3, res4, res5]

# Wrong: Passing unbounded group into chord (deadlock risk)
# See chord section below
```

### Chords (Parallel + Callback)

```python
from celery import chord, group

# Correct form: Bounded group as chord header
result = chord(
    group(
        process_item.s(item_id)
        for item_id in item_ids[:100]  # Bounded list
    ),
    summarize_results.s()  # Callback receives [res1, res2, ...]
).apply_async()

# Incorrect form that hangs: Unbounded generator
# DO NOT DO THIS:
# result = chord(
#     group(process_item.s(item_id) for item_id in infinite_generator()),
#     callback.s()
# )
# Why: Chord waits for ALL header tasks to complete. Generator never ends.

# Also incorrect: Group with dynamic size > worker capacity
# If you have 4 workers but group(1000 tasks), some tasks wait.
# Chord callback never fires until all 1000 complete.
# Solution: Use chunks or multiple chords
```

**Chord backend requirement:**
```python
# settings.py
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Required for chords

# Without backend, chord callback never fires
# Error: Chord 'xxx' raised: 'NoneType' object is not subscriptable
```

## Retry and Failure Handling

### Auto-Retry Configuration

```python
@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError, ExternalAPIError),
    retry_backoff=True,          # Exponential backoff (1s, 2s, 4s, 8s...)
    retry_backoff_max=600,       # Cap at 10 minutes
    retry_jitter=True,           # Add randomness to prevent thundering herd
    max_retries=3,
)
def fetch_external_data(self, url):
    """Auto-retry on transient failures."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

**Retry parameters explained:**
- `autoretry_for`: Tuple of exception classes that trigger auto-retry
- `retry_backoff=True`: Delays grow exponentially (default: 1s to 60s)
- `retry_backoff_max`: Maximum delay between retries
- `retry_jitter=True`: Add ±25% randomness to each delay
- `max_retries`: Total retry attempts (excluding first execution)

### Manual Retry

```python
@shared_task(bind=True, max_retries=5)
def process_with_manual_retry(self, record_id):
    try:
        record = Record.objects.get(id=record_id)
        return record.process()
    except Record.DoesNotExist:
        # Don't retry: data missing permanently
        logger.error(f"Record {record_id} not found")
        return None
    except DatabaseError as exc:
        # Retry with custom countdown
        countdown = min(60 * (2 ** self.request.retries), 300)
        raise self.retry(exc=exc, countdown=countdown)
    except Exception as exc:
        # Unexpected error: re-raise without retry
        logger.exception("Unexpected error")
        raise
```

### What NOT to Retry

```python
# Non-idempotent side effects: Don't retry
@shared_task(bind=True, max_retries=3)
def charge_credit_card(self, payment_id):
    """WRONG: Charging card multiple times on retry."""
    payment = Payment.objects.get(id=payment_id)
    stripe.Charge.create(amount=payment.amount, card=payment.card_id)
    # If worker crashes after charge but before DB update, retry charges again

# Correct: Make idempotent
@shared_task(bind=True, max_retries=3)
def charge_credit_card_idempotent(self, payment_id):
    payment = Payment.objects.select_for_update().get(id=payment_id)
    
    if payment.status == 'charged':
        return {'status': 'already_charged'}
    
    with transaction.atomic():
        payment.refresh_from_db()
        if payment.status == 'charged':
            return {'status': 'already_charged'}
        
        stripe.Charge.create(amount=payment.amount, card=payment.card_id)
        payment.status = 'charged'
        payment.save()
    
    return {'status': 'charged'}
```

### acks_late and task_reject_on_worker_lost

```python
# settings.py
CELERY_ACKS_LATE = True  # Acknowledge task AFTER execution completes

CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Reject unacked tasks when worker dies
```

**Semantics and trade-offs:**

| Setting | Behavior | Trade-off |
|---------|----------|-----------|
| `acks_late=False` (default) | Ack immediately on receipt | Worker crash = task lost (no retry) |
| `acks_late=True` | Ack after task completes | Worker crash = task requeued (may run twice) |
| `reject_on_worker_lost=True` | Reject unacked tasks on worker death | Same as acks_late but explicit |

**At-least-once delivery means idempotency is your responsibility:**
```python
# With acks_late=True, this task may run twice:
@shared_task(acks_late=True)
def send_welcome_email(user_id):
    # WRONG: Sends duplicate email
    User.objects.get(id=user_id).send_email()
    
# Correct: Idempotent
@shared_task(acks_late=True)
def send_welcome_email_idempotent(user_id):
    user = User.objects.get(id=user_id)
    if user.welcome_email_sent:
        return {'status': 'already_sent'}
    
    with transaction.atomic():
        user.refresh_from_db()
        if user.welcome_email_sent:
            return {'status': 'already_sent'}
        user.send_email()
        user.welcome_email_sent = True
        user.save()
```

## Common Issues (Symptom-First)

### Symptom: Tasks Never Execute (Stuck in PENDING)

**How to confirm:**
```bash
# 1. Check worker is running and consuming correct queue
celery -A myproject inspect active

# 2. Check queue routing
python -c "from myproject.celery import app; print(app.conf.task_routes)"

# 3. Check broker queue depth
redis-cli LLEN celery  # Should decrease as tasks execute

# 4. Verify task name matches
celery -A myproject inspect registered  # Task must appear here
```

**Fix:**
- Queue misrouting: Add route or start worker with `-Q <queue_name>`
- Missing `default_queue`: Set `CELERY_TASK_DEFAULT_QUEUE = 'default'`
- Task not registered: Check `autodiscover_tasks()` is called

### Symptom: Tasks Silently Lost (No Error, No Execution)

**How to confirm:**
```bash
# 1. Check broker/result backend mismatch
# If broker=redis://localhost:6379/0 but result_backend=redis://localhost:6379/1
# Results go to different Redis instance

# 2. Check worker logs for "Task xxx raised" without traceback
# Worker may have crashed before ack

# 3. Verify task version probe
celery -A myproject inspect registered  # Compare task versions across workers
```

**Fix:**
- Ensure `broker_url` and `result_backend` point to same broker instance
- Set `CELERY_TASK_ALWAYS_EAGER = False` (debug mode default)
- Check firewall/network between workers and broker

### Symptom: Stale Workers Running Old Code

**How to confirm:**
```python
# In task, probe version
@shared_task
def version_probe():
    import myapp.tasks
    return myapp.tasks.__version__  # Or check git commit hash

# Compare across workers
celery -A myproject inspect active
```

**Fix:**
- Restart workers after code deploy: `systemctl restart celery`
- Use `--max-tasks-per-child=1000` to force periodic restarts
- Deploy with zero-downtime: start new workers, drain old workers

### Symptom: Worker Killed Mid-Task (Data Corruption)

**How to confirm:**
```bash
# Check for OOM killer in system logs
dmesg | grep -i "out of memory"
grep "Out of memory" /var/log/syslog

# Check worker process exit codes
journalctl -u celery | grep "killed"
```

**Fix:**
- Set `acks_late=True` + idempotent tasks (task re-runs on crash)
- Increase worker memory limits
- Use `CELERY_WORKER_MAX_MEMORY_PER_CHILD = 400000` (KB)

### Symptom: Time-Limit Exceptions

```python
# Hard time limit: Worker kills task immediately
@shared_task(time_limit=300)  # 5 minutes hard limit
def long_task():
    pass

# Soft time limit: Task receives SoftTimeLimitExceeded exception
@shared_task(soft_time_limit=240)  # 4 minutes soft limit
def graceful_task():
    try:
        return do_work()
    except SoftTimeLimitExceeded:
        # Cleanup before forced termination
        cleanup()
        raise
```

**Detection:**
```bash
# Check worker logs for "Task raised SoftTimeLimitExceeded"
grep "SoftTimeLimitExceeded" /var/log/celery/worker.log
```

### Symptom: Results Never Appear

**How to confirm:**
```python
# 1. Check result backend is configured
print(app.conf.result_backend)  # Must not be None

# 2. Check backend matches between sender and receiver
# If task sent with backend=redis://... but result.get() uses different backend

# 3. Check result expiration
print(app.conf.result_expires)  # Default 1 day
```

**Fix:**
- Set `CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'`
- Don't set `ignore_result=True` unless you don't need results
- Increase `result_expires` for long-running workflows

### Symptom: Duplicate Task Execution

**How to confirm:**
```bash
# Check acks_late setting
celery -A myproject inspect config | grep ACKS_LATE

# Check for worker restarts during task execution
journalctl -u celery | grep -E "(restarting|killed|OOM)"
```

**Fix:**
- Make tasks idempotent (see retry section)
- Use database unique constraints
- Implement deduplication tokens

## Best Practices

### Idempotent Tasks

```python
@shared_task(bind=True)
def process_payment(self, payment_id):
    """Idempotent: Safe to run multiple times."""
    payment = Payment.objects.select_for_update().get(id=payment_id)
    
    if payment.status == 'completed':
        return {'status': 'already_processed'}
    
    with transaction.atomic():
        payment.refresh_from_db()
        if payment.status == 'completed':
            return {'status': 'already_processed'}
        
        result = payment.charge()
        payment.status = 'completed'
        payment.save()
    
    return result
```

### Task Granularity

```python
# Bad: Monolithic task
@shared_task
def process_order_bad(order_id):
    order = Order.objects.get(id=order_id)
    order.validate()
    order.charge()
    order.ship()

# Good: Composable tasks
@shared_task
def validate_order(order_id):
    Order.objects.get(id=order_id).validate()
    charge_order.delay(order_id)

@shared_task
def charge_order(order_id):
    order = Order.objects.get(id=order_id)
    order.charge()
    ship_order.delay(order_id)
```

## Deep Dives

Load these on demand for detailed reference:

- **Calling Workflows** (`references/calling-workflows.md`) — `apply_async` options, signatures, chains, groups, chords, chunks, and task states
- **Periodic Tasks & Routing** (`references/beat-routing.md`) — Celery Beat scheduling, crontab syntax, django-celery-beat, queue routing
- **Error Handling & Monitoring** (`references/errors-monitoring.md`) — Retries, error callbacks, DLQ, Flower, CLI monitoring, Prometheus
- **Testing & Performance** (`references/testing-performance.md`) — pytest testing, worker configuration, task optimization, memory management

## References

- **Official Documentation**: https://docs.celeryq.dev/
- **GitHub Repository**: https://github.com/celery/celery
- **Flower Monitoring**: https://github.com/mher/flower
