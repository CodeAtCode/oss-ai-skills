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
| [Firefox Extension](extend/firefox-extension/SKILL.md) | Use when developing Firefox WebExtensions - Manifest V2/V3 configuration, WebExtension APIs, content security policy, web-ext CLI, cross-browser support with the polyfill, AMO submission, or debugging extensions | 807 | firefox, webextension, browser-extension, mozilla, amo, manifest-v3 |
| [GIMP Plugin](extend/gimp-plugin/SKILL.md) | Use when developing GIMP 3.0+ plugins in Python 3 - procedure registration, image and layer operations, GEGL operations, PDB calls, dialogs and progress bars, file export, or batch processing plugins | 1,169 | python, gimp, image-processing, graphics, plugin, gegl |
| [Kate Plugin](extend/kate-plugin/SKILL.md) | Use when developing C++ plugins for Kate - KTextEditor Framework, CMake/ECM, Qt threading, KDE plugin architecture | 498 | kate, kde, text-editor, plugin, c++, qt, kde-frameworks |
| [KDE Plasmoid](extend/kde-plasmoid/SKILL.md) | Use when building KDE Plasma 6 widgets with a Python backend - plasmoid structure, metadata.json, QML UI, configuration system, plasmapkg2 packaging, KDE Store submission, or plasmoid testing and debugging | 1,170 | kde, plasma, plasmoid, widget, qml, qt, desktop |
| [mGBA Scripting](extend/mgba/SKILL.md) | Use when scripting mGBA emulator automation in Lua - console API, ROM and save state operations, frame callbacks, input handling, memory reading for cheats and RAM watches, sockets, or TAS and speedrunner tooling | 1,001 | lua, emulator, gba, gameboy-advance, scripting, memory-hacking |
| [OpenCode Plugin](extend/opencode/SKILL.md) | Use when developing plugins, tools, and extensions for the OpenCode agent - plugin contract and crash-prevention rules, ctx and event APIs, subagent lifecycle, MCP integration, SDK usage, REST API, testing, or publishing to npm | 1,177 | opencode, plugin, ai-agent, mcp, tool-development |
| [OpenRCT2 Plugin](extend/openrct2/SKILL.md) | Use when developing OpenRCT2 plugins in TypeScript - plugin registration and game actions, window and widget UI, event hooks, park, map, ride and entity access, network API, storage, or ES5 runtime constraints | 1,032 | openrct2, plugin, javascript, typescript, game-modding, rollercoaster-tycoon |
| [Playwright Visual Regression](frameworks/playwright-visual-regression/SKILL.md) | Use when setting up visual regression testing with Playwright - toHaveScreenshot baselines, masking dynamic content, handling animations, full-page and element screenshots, cross-browser runs, CI integration, VUDA MCP tooling, or debugging flaky visual diffs | 1,058 | playwright, visual-regression, screenshot, testing, e2e, vuda, vrt |
| [Thunderbird Extension](extend/thunderbird-extension/SKILL.md) | Use when developing Thunderbird MailExtensions - Manifest V2/V3 configuration, messenger.* APIs for accounts, messages, folders and compose, UI actions, message display scripts, Experiment APIs, ATN submission, or migration from legacy extensions | 1,077 | thunderbird, mailextension, email-extension, mozilla, atn, messenger-api |
| [Vagrant](extend/vagrant/SKILL.md) | Use when managing Vagrant VM environments - Vagrantfile configuration, providers like VirtualBox and libvirt, provisioners (shell, Ansible, Chef, Puppet, Docker), multi-machine setups, networking, synced folders, custom boxes, plugins, or triggers | 1,110 | vagrant, virtualization, devops, virtualbox, infrastructure |
| [Zed Editor](extend/zed-editor/SKILL.md) | Use when developing Zed editor extensions in Rust - extension.toml manifest, LSP server integration, tree-sitter grammars and query files, MCP servers, slash commands, DAP debuggers, themes, snippets, or publishing to the Zed marketplace | 1,125 | zed, editor, extension, rust, wasm, tree-sitter, lsp, plugin |

### Frameworks

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [aiohttp](frameworks/aiohttp/SKILL.md) | Use when building Python async HTTP services or clients with aiohttp - web server routing, middleware, WebSocket, SSE, streaming, client sessions, pytest-aiohttp testing, or troubleshooting SSL and timeout issues | 1,346 | python, http, async, server, websocket, sse |
| [android-apk-patch](frameworks/android-apk-patch/SKILL.md) | Use when modifying Android APKs - decompiling and recompiling with apktool, editing smali or resources, handling split APKs, APK signing v1/v2/v3 and key rotation, resolving AAPT2 and dependency errors, patching GApps-dependent apps, or testing modified APKs on emulators, Redroid, or Waydroid | 1,573 | android, apk, patching, smali, signing, split-apk, gapps, frida, redroid, waydroid |
| [BPCore Engine](frameworks/bpcore-engine/SKILL.md) | Use when building GBA games with the BPCore Lua engine - entity, sprite and tilemap functions, SRAM save and load, link cable multiplayer protocol, camera and scrolling, or optimization patterns | 881 | lua, gba, game-engine, gameboy-advance |
| [Celery](frameworks/celery/SKILL.md) | Use when running background tasks with Celery - worker and broker configuration (Redis, RabbitMQ, SQS), task definitions, chains and chords, Celery Beat periodic tasks, routing, retries, Flower monitoring, or testing tasks with pytest | 1,288 | python, task-queue, async, distributed, celery |
| [Django](frameworks/django/SKILL.md) | Use when building Django applications - security hardening, authentication and permissions, ORM optimization, PostgreSQL features, Django 6.0, migrations, testing, and ecosystem libraries | 2,604 | python, django, web-framework, async, hub |
|   ↳ [django-admin](frameworks/django-admin/SKILL.md) | Use when customizing Django Admin - save_formset, get_search_results, formsets, queryset optimization, db_index, custom URLs | 582 | python, django, admin, orm, optimization |
|   ↳ [django-transaction](frameworks/django-transaction/SKILL.md) | Use when handling Django transactions and concurrency - atomic, select_for_update, on_commit, upserts, M2M ordering | 496 | python, django, transactions, concurrency, orm |
| [Django Bolt](frameworks/django-bolt/SKILL.md) | Use when building high-performance APIs with django-bolt - routing, JWT auth, msgspec serializers, WebSockets, SSE streaming, file uploads, ORM patterns, runbolt deployment, or migrating from DRF | 2,211 | python, django, bolt, api, rust, performance, async |
| [Django Celery](frameworks/django-celery/SKILL.md) | Use when integrating Celery with Django - task definition and calling, django-celery-beat scheduling, worker deployment, Flower monitoring, testing tasks, batch processing, or choosing between cron and beat | 682 | python, django, celery, task-queue, periodic-tasks, django-celery-beat |
| [Django HTMX](frameworks/django-htmx/SKILL.md) | Use when building dynamic Django web apps with htmx - partial rendering, HTMX responses, querystring tag, CSP | 487 | django, htmx, python, web, frontend, partial-rendering |
| [Django Ninja](frameworks/django-ninja/SKILL.md) | Use when building Django REST APIs with django-ninja - Pydantic schemas, routers, CRUD endpoints, authentication, pagination, file uploads, async views, OpenAPI docs, or migrating from DRF | 1,995 | python, django, rest-api, pydantic, openapi, type-safe |
| [Django Storages](frameworks/django-storages/SKILL.md) | Use when configuring django-storages for cloud file storage - STORAGES setting, Amazon S3, Google Cloud Storage and Azure backends, signed URLs, CDN and caching, multipart uploads, or storage testing | 729 | python, django, storage, s3, azure, gcs, cloud |
| [Django TDD](frameworks/django-tdd/SKILL.md) | Use when testing Django applications with pytest - TDD workflow, pytest-django setup, factory_boy and model-bakery fixtures, DRF API testing, mocking and patching, integration tests, or coverage | 860 | python, django, testing, pytest, tdd |
| [Django Unfold](frameworks/django-unfold/SKILL.md) | Use when theming the Django admin with django-unfold - settings and sidebar configuration, custom admin site, components and @display decorator, filters, actions, tabs, dark mode and styling, or Django 6.x compatibility | 803 | python, django, admin, unfold, theme, dashboard |
| [django-allauth](frameworks/django-allauth/SKILL.md) | Use when implementing Django authentication - local accounts, OAuth, email verification, MFA, OIDC, django-organizations | 603 | python, django, authentication, oauth, mfa, allauth, oidc |
| [django-filter](frameworks/django-filter/SKILL.md) | Use when filtering Django querysets - FilterSet, custom filters, Django REST Framework integration, explicit fields | 518 | django, django-filter, filtering, django-rest-framework, queryset |
| [httpx](frameworks/httpx/SKILL.md) | Use when making HTTP requests in Python with httpx - sync and async clients, streaming, HTTP/2, connection pooling, retries, proxies, SSL verification, respx testing, or FastAPI and Django integration | 906 | python, http, async, client, network |
| [LlamaIndex](frameworks/llama-index/SKILL.md) | Use when building RAG or LLM applications with LlamaIndex - data loaders, node parsing, vector stores, retrievers and rerankers, query engines, agents and workflows, streaming, or evaluation | 1,231 | python, llm, rag, llamaindex, ai, vector-database, openai, agents |
| [Pydantic](frameworks/pydantic/SKILL.md) | Use when validating and serializing Python data with Pydantic v2 - models, field and model validators, constrained and special types, TypeAdapter, discriminated unions, BaseSettings, or FastAPI integration | 1,389 | python, validation, pydantic, serialization, settings |
| [pygame](frameworks/pygame/SKILL.md) | Use when building 2D games in Python with pygame - game loop and delta time, sprites and groups, collision detection, drawing and surfaces, events and input, sound and fonts, camera, or performance optimization | 749 | python, game-development, 2d-games, pygame, graphics |
| [PyQt](frameworks/pyqt/SKILL.md) | Hub skill for PyQt/PySide - overview, comparison, project structure. Use when building cross-platform Qt desktop apps | 416 | python, qt, pyqt, pyside, gui, desktop, hub |
|   ↳ [pyqt-core](frameworks/pyqt/core/SKILL.md) | Use when working with PyQt/PySide6 QtCore - signals, slots, properties, timers, settings, file I/O | 487 | python, qt, pyqt, core, signals |
|   ↳ [pyqt-dialogs](frameworks/pyqt/dialogs/SKILL.md) | Use when implementing PyQt/PySide6 dialogs - standard dialogs (QFileDialog, QMessageBox, QInputDialog, QColorDialog, QFontDialog), custom QDialog patterns, modal vs modeless dialogs, input validation, Qt 6 dialog APIs | 518 | python, qt, pyqt, dialogs, ui |
|   ↳ [pyqt-multimedia](frameworks/pyqt/multimedia/SKILL.md) | Use when adding multimedia to PyQt/PySide6 apps - audio and video playback with QMediaPlayer, camera capture with QCamera and QMediaCaptureSession, audio/video recording with QMediaRecorder, GStreamer backend setup, or codec and platform compatibility issues | 1,071 | python, qt, pyqt, multimedia, audio, video |
|   ↳ [pyqt-styling](frameworks/pyqt/styling/SKILL.md) | Use when styling PyQt/PySide6 widgets with QSS - selectors and pseudo-states, stylesheet application, common style properties, widget-specific styling, or building a dark theme | 673 | python, qt, pyqt, styling, qss, css, themes |
|   ↳ [pyqt-testing](frameworks/pyqt/testing/SKILL.md) | Use when testing PyQt/PySide6 applications with pytest-qt - qtbot fixture, signal/wait patterns, mouse/keyboard simulation, dialog testing, model/view testing, threaded code testing, or manual debugging techniques | 464 | python, qt, pyqt, testing, pytest |
|   ↳ [pyqt-threading](frameworks/pyqt/threading/SKILL.md) | Use when handling PyQt/PySide6 threading - QThread patterns, QThreadPool/QRunnable, thread safety rules, moveToThread, Qt Concurrent, QTimer, testing threaded code, lifecycle management | 1,418 | python, qt, pyqt, threading, concurrency |
|   ↳ [pyqt-widgets](frameworks/pyqt/widgets/SKILL.md) | Use when building PyQt/PySide6 UIs with QtWidgets - display, input and container widgets, buttons, item views like QListWidget and QTableWidget, layout management, or event handling (mouse/keyboard events, event filters, shortcuts) | 756 | python, qt, pyqt, widgets, gui |
| [pytest](frameworks/pytest/SKILL.md) | Use when writing Python tests with pytest - fixtures, parametrization, markers, conftest layout, pytest-asyncio, pytest-django, coverage with pytest-cov, mocking with pytest-mock, parallel runs with xdist, or CI integration | 1,527 | python, testing, tdd, fixtures, unit-test |
| [Qt C++](frameworks/qt-cpp/SKILL.md) | Use when developing desktop applications with Qt in C++ - CMake setup, signals and slots, QThread and QtConcurrent, QML integration, model/view programming, Qt5 to Qt6 migration, or windeployqt/macdeployqt/linuxdeployqt deployment | 1,214 | qt, c++, gui, desktop, qt6, cmake, cross-platform, qml |
| [ratatui](frameworks/ratatui/SKILL.md) | Use when building terminal user interfaces in Rust with the ratatui crate - layout system, widget usage, input/event handling, app state architecture, TUI testing, or migrating between ratatui 0.29 and 0.30 | 1,829 | rust, tui, terminal, cli, user-interface, ecosystem |
| [SQLAlchemy](frameworks/sqlalchemy/SKILL.md) | Use when working with SQLAlchemy 2.0 in Python - declarative models and relationships, queries and sessions, async engines with FastAPI, Alembic migrations, bulk operations, PostgreSQL query optimization, or debugging detached instances and N+1 queries | 1,434 | python, orm, database, sql, alembic, async |
| [Tailwind CSS](frameworks/tailwind/SKILL.md) | Use when styling with Tailwind CSS v4 - @theme directive and design tokens, custom utilities and variants, dark mode, the Oxide engine, arbitrary values, framework integration, or migrating from v3 | 814 | css, frontend, responsive, design-system, utility-first |
| [TurboDRF](frameworks/turbodrf/SKILL.md) | Use when building Django REST APIs with TurboDRF - model Meta configuration, role-based and field-level permissions, multi-tenant predicates, router wiring, management commands, settings, or troubleshooting | 791 | python, django, rest-api, turbodrf, permissions |

### Tool

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [ast-grep](tool/ast-grep/SKILL.md) | Use when doing structural code search and rewriting - ast-grep linting, refactoring, multi-language patterns | 531 | ast-grep, code-search, linting, refactoring, cli, ast |
| [Docker](tool/docker/SKILL.md) | Use when working with Docker containers - Dockerfile, docker-compose, BuildKit, multi-stage builds, production, CI/CD | 432 | docker, docker-compose, containerization, deployment, ci-cd |
| [Redis](tool/redis/SKILL.md) | Use when working with Redis - in-memory database, caching, pub/sub, sessions, rate limiting, RESP3, asyncio, Redis Stack | 509 | redis, database, caching, pub-sub, sessions, rate-limiting, resp3, async |
| [SQLite](tool/sqlite/SKILL.md) | Use when working with SQLite in Python - schema design, transactions, FTS5 full-text search, JSON columns, PRAGMA tuning, backups and corruption recovery, or multi-instance concurrency | 925 | sqlite, database, sql, embedded, python |
| [Waydroid](tool/waydroid/SKILL.md) | Use when setting up or troubleshooting Waydroid on Linux - installation and initialization, waydroid CLI, GPU and networking setup, GApps and Play certification, ADB integration, file sharing, or desktop environment integration | 539 | waydroid, android, container, linux, wayland, gapps |

### Languages

| Skill | Description | Lines | Tags |
|-------|-------------|-------|------|
| [Rust Common Pitfalls](languages/rust-common-pitfalls/SKILL.md) | Use when fixing Rust compiler errors and pitfalls - E0382/E0502/E0716 borrow-checker and move errors, test organization, coverage enforcement, thiserror design, panic elimination, or module splitting | 1,432 | rust, pitfalls, best-practices, common-errors, testing |

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
