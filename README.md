# OSS AI Skills Collection
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

A comprehensive collection of AI assistant skills (SKILL.md files) following the [skillreg.dev](https://skillreg.dev/docs/skill-md-reference) specification, designed to help to use and extend open-source projects (for plugins).
*Note: we test the majority of them and improving based on asking to the agents to extend the skills based on their experience.*

## What is this?

This repository provides reusable skill definitions that can be loaded into AI coding assistants. Each skill encapsulates domain knowledge, best practices, and workflows for specific tasks in open-source development.

## Available Skills

### Extend

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [Firefox Extension](extend/firefox-extension/SKILL.md) | Build WebExtensions for Firefox - MV2/MV3, APIs, web-ext, AMO publishing | 796 | firefox, webextension, browser-extension, mozilla, amo, manifest-v3 |
| [GIMP Plugin](extend/gimp-plugin/SKILL.md) | GIMP 3.0+ plugins with Python 3 - GEGL operations, image manipulation, UI dialogs | 1,156 | python, gimp, image-processing, graphics, plugin, gegl |
| [Kate Plugin](extend/kate-plugin/SKILL.md) | Develop C++ plugins for Kate - KTextEditor, CMake/ECM, QThread agent architecture, IThreadStorage, QTest | 498 | kate, kde, text-editor, plugin, c++, qt, kde-frameworks |
| [KDE Plasmoid](extend/kde-plasmoid/SKILL.md) | Build Plasma 6 widgets - Python backend, QML UI, deployment, KDE Store publishing, troubleshooting | 1,168 | kde, plasma, plasmoid, widget, qml, qt, desktop |
| [mGBA Scripting](extend/mgba/SKILL.md) | Lua scripting for mGBA emulator - game automation, memory hacking, cheats, callbacks | ~800 | lua, emulator, gba, gameboy-advance, scripting, memory-hacking |
| [OpenCode Plugin](extend/opencode/SKILL.md) | Develop plugins for OpenCode AI agent - v1.18+ Plugin Contract, crash-prevention rules, MCP, tools, SDK, HTTP REST API, subagent lifecycle, event handler patterns | 1,166 | opencode, plugin, ai-agent, mcp, tool-development |
| [OpenRCT2 Plugin](extend/openrct2/SKILL.md) | JavaScript/TypeScript plugins for OpenRCT2 - game actions, UI windows, hooks, multiplayer | 877 | openrct2, plugin, javascript, typescript, game-modding, rollercoaster-tycoon |
| [Playwright Visual Regression](frameworks/playwright-visual-regression/SKILL.md) | Visual regression testing with Playwright - toHaveScreenshot(), Python/TS, VUDA MCP, masking, thresholds, CI/CD | 1,056 | playwright, visual-regression, screenshot, testing, e2e, vuda, vrt |
| [Thunderbird Extension](extend/thunderbird-extension/SKILL.md) | Build MailExtensions for Thunderbird - messenger.* APIs, compose, ATN | 1,067 | thunderbird, mailextension, email-extension, mozilla, atn, messenger-api |
| [Vagrant](extend/vagrant/SKILL.md) | Development environments - providers, provisioners, multi-machine, plugins, troubleshooting | 1,097 | vagrant, virtualization, devops, virtualbox, infrastructure |
| [Zed Editor](extend/zed-editor/SKILL.md) | Zed extensions - Rust/Wasm plugins, LSP, Tree-sitter, themes, MCP, slash commands, known issues, references | 1,135 | zed, editor, extension, rust, wasm, tree-sitter, lsp, plugin |

### Frameworks

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [aiohttp](frameworks/aiohttp/SKILL.md) | Async HTTP server/client - WebSocket, SSE, middleware, JWT auth, logging, error handling, pytest-aiohttp testing | 1,540 | python, http, async, server, websocket, sse |
| [android-apk-patch](frameworks/android-apk-patch/SKILL.md) | Modify, repackage, test Android APKs - split APK handling, GApps workarounds, signing, Frida instrumentation, redroid/Waydroid testing | 1,565 | android, apk, patching, smali, signing, split-apk, gapps, frida, redroid, waydroid |
| [BPCore Engine](frameworks/bpcore-engine/SKILL.md) | Lua game framework for GBA - API reference, sprites, entities, collision, audio, save/load SRAM, multiplayer protocol | 873 | lua, gba, game-engine, gameboy-advance |
| [Celery](frameworks/celery/SKILL.md) | Distributed task queue - Redis/RabbitMQ brokers, periodic tasks, Django integration | 1,250 | python, task-queue, async, distributed, celery |
| [Django](frameworks/django/SKILL.md) | Security, ORM, PostgreSQL, GeoDjango, Django 6.0 essentials, admin extensions, middleware, authentication, sessions, ecosystem tools | 1,727 | python, django, web-framework, async, hub |
| [Django Bolt](frameworks/django-bolt/SKILL.md) | Rust-powered high-performance API framework - 60k+ RPS, decorator routing, built-in auth, async ORM | 2,567 | python, django, bolt, api, rust, performance, async |
| [Django Celery](frameworks/django-celery/SKILL.md) | Django Celery integration - distributed tasks, django-celery-beat scheduling, monitoring | ~700 | python, django, celery, task-queue, periodic-tasks, django-celery-beat |
| [Django HTMX](frameworks/django-htmx/SKILL.md) | Build modern dynamic web apps with Django and htmx - partial rendering, HTMX-specific responses, querystring tag, CSP nonce support, Django 6.0 compatible | 487 | django, htmx, python, web, frontend, partial-rendering |
| [Django Ninja](frameworks/django-ninja/SKILL.md) | Fast REST APIs with Pydantic v2 - schemas, authentication, pagination, context support, OpenAPI docs, Django 6.0 compatible | 1,884 | python, django, rest-api, pydantic, openapi, type-safe |
| [Django Storages](frameworks/django-storages/SKILL.md) | Django cloud storage - S3, Azure, Google Cloud, boto3, STORAGES dict, AWS_S3_TRANSFER_CONFIG, Django 6.0 compatible | 741 | python, django, storage, s3, azure, gcs, cloud |
| [Django Unfold](frameworks/django-unfold/SKILL.md) | Modern Django admin theme - @display decorator, charts, CSP nonce, customization, actions, filters, Django 6.0 compatible | 670 | python, django, admin, unfold, theme, dashboard |
| [django-allauth](frameworks/django-allauth/SKILL.md) | django-allauth 65.x - local accounts, OAuth, email verification, MFA, OIDC provider (allauth.idp.oidc), Django 6.0 compatible | 605 | python, django, authentication, oauth, mfa, allauth, oidc |
| [django-filter](frameworks/django-filter/SKILL.md) | Django filtering library 25.x - querysets, DRF integration, custom filters, FilterSet, explicit fields=__all__, Django 6.0 compatible | 518 | django, django-filter, filtering, django-rest-framework, queryset |
| [httpx](frameworks/httpx/SKILL.md) | Modern async HTTP client - sync/async API, HTTP/2, connection pooling, retries, v0.28.1 stable (v1.0 in development) | 905 | python, http, async, client, network |
| [LlamaIndex](frameworks/llama-index/SKILL.md) | LLM applications 0.14 - RAG, retrievers, agents, vector stores, Workflow engine, streaming, evaluation | 1,223 | python, llm, rag, llamaindex, ai, vector-store, agents, workflow |
| [Pydantic](frameworks/pydantic/SKILL.md) | Data validation - TypeAdapter, RootModel, discriminated unions, error handling, serialization, settings, FastAPI | 1,499 | python, validation, pydantic, serialization, settings |
| [pygame](frameworks/pygame/SKILL.md) | Python 2D game development - sprites, surfaces, events, sound, fonts, game loops, collision | 549 | python, game-development, 2d-games, pygame, graphics |
| [PyQt](frameworks/pyqt/SKILL.md) | Desktop applications - PyQt5/PyQt6/PySide6, widgets, signals, layouts, threading, testing | 1,937 | python, qt, pyqt, pyside, gui, desktop, hub |
|   ↳ [pyqt-core](frameworks/pyqt/core/SKILL.md) | QtCore fundamentals - signals, slots, properties, timers, settings, file I/O | 487 | python, qt, pyqt, core, signals |
|   ↳ [pyqt-dialogs](frameworks/pyqt/dialogs/SKILL.md) | Dialogs - QFileDialog, QMessageBox, custom dialogs, Qt 6 | 518 | python, qt, pyqt, dialogs, ui |
|   ↳ [pyqt-multimedia](frameworks/pyqt/multimedia/SKILL.md) | Audio/video playback, camera access, media recording, error handling, codec support | 1,773 | python, qt, pyqt, multimedia, audio, video |
|   ↳ [pyqt-styling](frameworks/pyqt/styling/SKILL.md) | QSS styling - selectors, properties, dark theme | 668 | python, qt, pyqt, styling, qss, css |
|   ↳ [pyqt-testing](frameworks/pyqt/testing/SKILL.md) | Testing - pytest-qt, qtbot, waitSignal, fixtures | 444 | python, qt, pyqt, testing, pytest |
|   ↳ [pyqt-threading](frameworks/pyqt/threading/SKILL.md) | Threading - QThread, QThreadPool, QRunnable, moveToThread, thread safety, lifecycle, pitfalls | 931 | python, qt, pyqt, threading, concurrency |
|   ↳ [pyqt-widgets](frameworks/pyqt/widgets/SKILL.md) | QtWidgets - buttons, inputs, containers, item views, layouts | 610 | python, qt, pyqt, widgets, gui |
| [pytest](frameworks/pytest/SKILL.md) | Python testing 9.0 - fixtures, parametrization, asyncio, Django, pathlib.Path hooks, CI strict mode, mocking, coverage, parallel | 1,610 | python, testing, tdd, fixtures, unit-test |
| [Qt C++](frameworks/qt-cpp/SKILL.md) | Cross-platform desktop apps - signals/slots, QML, threading, CMake, deployment | 1,204 | qt, c++, gui, desktop, qt6, cmake, cross-platform, qml |
| [ratatui](frameworks/ratatui/SKILL.md) | Rust TUI framework - widgets, layouts, design principles, accessibility, MVU architecture, ecosystem, tui-logger, recipes | 2,598 | rust, tui, terminal, cli, user-interface, ecosystem |
| [SQLAlchemy](frameworks/sqlalchemy/SKILL.md) | Python SQL toolkit/ORM - queries, CTEs, window functions, async, Alembic, migration testing, PostgreSQL optimization, non-integer PKs | 1,619 | python, orm, database, sql, alembic, async |
| [Tailwind CSS](frameworks/tailwind/SKILL.md) | Utility-first CSS framework v4 - CSS-first config, @theme directive, Oxide engine, Lightning CSS, v3 migration | 812 | css, frontend, responsive, design-system, utility-first |
| [TurboDRF](frameworks/turbodrf/SKILL.md) | Django REST mixin - TurboDRFMixin, auto CRUD, role-based permissions, tenancy, security gates | 713 | python, django, rest-api, turbodrf, permissions |

### Tool

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [ast-grep](tool/ast-grep/SKILL.md) | AST-based code search and rewriting - structural patterns, linting, refactoring, multi-language | 531 | ast-grep, code-search, linting, refactoring, cli, ast |
| [Docker](tool/docker/SKILL.md) | Containers - Dockerfile, docker-compose, BuildKit, multi-stage builds, production, CI/CD, security | 432 | docker, docker-compose, containerization, deployment, ci-cd |
| [Redis](tool/redis/SKILL.md) | In-memory database (redis-py 8.0) - RESP3 protocol, async API, Redis Stack (Search/JSON/TimeSeries), caching, pub/sub, sessions, rate limiting | 509 | redis, database, caching, pub-sub, sessions, rate-limiting, resp3, async |
| [SQLite](tool/sqlite/SKILL.md) | Embedded database - SQL queries, schema design, Python integration, FTS5, ANALYZE, Litestream/restic backups, concurrent access | 922 | sqlite, database, sql, embedded, python |
| [Waydroid](tool/waydroid/SKILL.md) | Android on Linux - container-based Android with Wayland, GPU acceleration, GAPPS | ~657 | waydroid, android, container, linux, wayland, gapps |

### Languages

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [Rust Common Pitfalls](languages/rust-common-pitfalls/SKILL.md) | Rust pitfalls - compiler errors, struct constructors, test organization, module splitting, thiserror error design, panic elimination | 1,208 | rust, pitfalls, best-practices, common-errors, testing |

## Skill Format

Each skill follows the [skillreg.dev specification](https://skillreg.dev/docs/skill-md-reference):

```yaml
---
name: skill-name
description: Short description of the skill
metadata:
  author: Author Name
  version: 1.0.0
  tags:
    - tag1
    - tag2
---

# Skill Title

[Markdown content with guidelines, examples, references...]
```

## How to Use

1. **Browse available skills** in the `contribute/`, `extend/`, or `frameworks/` directories
2. **Copy the SKILL.md** to your project or load it into your AI assistant
3. **Reference the skill** when asking for help with that domain
4. **Customize** as needed for your specific project
