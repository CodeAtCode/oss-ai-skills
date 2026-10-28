---
name: django
description: Use when building Django applications - security hardening, authentication and permissions, ORM optimization, PostgreSQL features, Django 6.0, migrations, testing, and ecosystem libraries
metadata:
  author: mte90
  version: 3.0.0
  tags:
    - python
    - django
    - security
    - orm
    - postgresql
    - admin
    - authentication
    - sessions
---

> **Objective:** Use this skill to reduce N+1 query incidents, SQL-injection exposure, migration-drift breakages, permission-bypass incidents by enforcing ORM loading discipline, parameterized-query rules, migration-contract checks, permission-decorator patterns below.

# Django

Comprehensive guide to Django covering security, ORM, PostgreSQL, GeoDjango, Django 6.0 essentials, admin extensions, and ecosystem tools.

## Overview

Django provides a batteries-included web framework with robust features out of the box:
- **Security** - CSRF protection, authentication, sessions, password hashing, security middleware
- **ORM** - Powerful database abstraction with query optimization
- **PostgreSQL** - Full-text search, array fields, JSONB, range fields
- **GeoDjango** - Geographic database operations with GPS extraction
- **Django 6.0** - Middleware changes, built-in tasks framework, CSP, GeneratedField
- **Admin Extensions** - Operational dashboards and monitoring tools

## Specialized Skills

For deeper coverage of specific domains, see these dedicated skills:

- ↳ **[django-admin](frameworks/django-admin/SKILL.md)** — Admin save_formset/get_search_results/db_index patterns
- ↳ **[django-transaction](frameworks/django-transaction/SKILL.md)** — atomic/select_for_update/on_commit/upserts

---

## Deep Dives

Load these reference files on demand for detailed coverage:

- ↳ **[security.md](references/security.md)** — CSRF protection, sessions, security middleware, field-level encryption
- ↳ **[authentication-permissions.md](references/authentication-permissions.md)** — Authentication views, custom backends, password management, login templates, Django permissions
- ↳ **[orm-performance.md](references/orm-performance.md)** — ORM optimization, caching, response time, materialized views
- ↳ **[postgresql.md](references/postgresql.md)** — pgvector, GeneratedField, GeoDjango, PostgreSQL features
- ↳ **[django6-modern.md](references/django6-modern.md)** — Django Tasks framework, 6.0 essentials, multi-DB routing, model fields, app naming
- ↳ **[testing-migrations.md](references/testing-migrations.md)** — Testing optimization, migrations, signals, StreamingHttpResponse
- ↳ **[external-api.md](references/external-api.md)** — Operational dashboards, external API integration
- ↳ **[ecosystem.md](references/ecosystem.md)** — Django ecosystem libraries

## Best Practices (Do X Because Y)

1. **Always use `{% csrf_token %}` in POST forms** because missing tokens allow malicious sites to submit forms on behalf of authenticated users (CSRF attacks)
2. **Enable HTTPS with SECURE_SSL_REDIRECT = True** because unencrypted connections expose session cookies and user data to network eavesdroppers
3. **Enable HSTS with SECURE_HSTS_SECONDS** because browsers that once visited over HTTPS should never fall back to HTTP (prevents downgrade attacks)
4. **Set SESSION_COOKIE_SECURE = True** because cookies sent over HTTP can be intercepted and reused by attackers
5. **Use @login_required or PermissionRequiredMixin** because unprotected views expose sensitive data to unauthenticated users
6. **Validate file uploads with ALLOWED_EXTENSIONS** because malicious file uploads can execute server-side code (RCE)
7. **Never interpolate user input into raw SQL - use ORM or %s formatting** because string interpolation enables SQL injection attacks
8. **Use select_related for FK relationships** because accessing FK without it fires N+1 queries (one per row in templates)
9. **Use prefetch_related for M2M/reverse FK** because JOINs without prefetching duplicate objects and explode memory usage
10. **Audit dead references after field renames** because admin list_display, forms, and serializers silently break with old field names

---

## References

