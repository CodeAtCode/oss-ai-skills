---
name: qt-cpp
description: Use when developing desktop applications with Qt in C++ - CMake setup, signals and slots, QThread and QtConcurrent, QML integration, model/view programming, Qt5 to Qt6 migration, or windeployqt/macdeployqt/linuxdeployqt deployment
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - qt
    - c++
    - gui
    - desktop
    - qt6
    - cmake
    - cross-platform
    - qml
    - threading
---

> **Objective:** Use this skill to reduce segfaults from raw pointers, signal/slot connection failures, memory leaks from parentless QObjects, and thread-assertion violations by enforcing ownership rules, connection patterns, and RAII discipline below.

# Qt C++ Development

Complete reference for building cross-platform desktop applications with Qt framework in C++.

## Overview

Qt is a powerful C++ framework for cross-platform application development. It provides rich GUI capabilities, networking, database access, and more.

## Qt Versions

### Qt5 vs Qt6

| Feature | Qt5 | Qt6 |
|---------|-----|-----|
| C++ Standard | C++11 | C++17 minimum |
| Graphics | OpenGL | Vulkan/Metal/DirectX |
| High-DPI | Manual | Enabled by default |
| QString | UTF-16 | UTF-8 by default |
| Status | Maintenance | Active development |

**Use Qt 6 for:** New projects, modern C++17/20 features, better graphics performance

**Use Qt 5 for:** Legacy codebases, Qt 5-only modules, platform constraints

## Installation

See [official installation guide](https://www.qt.io/download) or your platform's package manager.

### Quick Setup

- **Qt Online Installer**: Recommended for Windows/macOS
- **Package managers**: `brew install qt@6` (macOS), `apt install qt6-base-dev` (Ubuntu)

## Deep Dives

Load these reference files for detailed guidance:

- **Signals and Slots** — `references/signals-slots.md` — Connection syntax, lambda patterns, connection types, signal forwarding
- **Model/View Programming** — `references/model-view.md` — QAbstractListModel, QML integration
- **Qt 6 Features** — `references/qt6-features.md` — UTF-8 changes, graphics stack, properties
- **CMake Build System** — `references/cmake.md` — CMake configuration, find_package, installation rules
- **Threading** — `references/threading.md` — QThread, QThreadPool, QtConcurrent, moveToThread patterns
- **QML Integration** — `references/qml-integration.md` — Exposing C++ to QML, Q_PROPERTY, Q_INVOKABLE
- **Deployment & Issues** — `references/deployment-issues.md` — windeployqt, macdeployqt, linuxdeployqt, common problems
- **Quick Reference** — `references/quick-reference.md` — Common headers, CMake components, module lookup

## Signals and Slots

See `references/signals-slots.md` for connection syntax, lambda patterns, connection types, and signal forwarding.

## Model/View Programming

See `references/model-view.md` for QAbstractListModel implementation and QML ListView integration.

## Qt 6 Specific Features

See `references/qt6-features.md` for QString UTF-8 changes, graphics stack, and property syntax.

## Best Practices

**Do X because Y prevents Z** patterns:

1. **Use parent pointers for all QObjects** because orphaned objects leak memory when the event loop exits
2. **Prefer modern signal-slot syntax** (`&Sender::signal`) because the old `SIGNAL()/SLOT()` macros bypass compile-time checking and cause runtime connection failures
3. **Call `deleteLater()` instead of `delete`** because immediate deletion can crash if the object is still processing an event
4. **Enable `AUTOMOC`, `AUTOUIC`, `AUTORCC`** in CMake because missing MOC generation causes "undefined reference to vtable" errors
5. **Use `Q_PROPERTY` for QML-exposed data** because QML bindings require property notifications to update the UI
6. **Move long-running work to worker threads** because blocking the main thread freezes the UI and triggers watchdog timeouts
7. **Use `moveToThread()` for worker objects** because it ensures signals/slots queue correctly across thread boundaries
8. **Test deployment on each target platform early** because windeployqt/macdeployqt issues often require platform-specific fixes
9. **Validate all user input at boundaries** because Qt's string handling (especially UTF-8 in Qt6) can expose encoding bugs

## Resources

- **Official Documentation:** https://doc.qt.io/qt-6/
- **Qt Wiki:** https://wiki.qt.io/
- **Qt Forum:** https://forum.qt.io/
- **Examples:** https://doc.qt.io/qt-6/examples-and-tutorials.html
- **Qt Creator:** https://www.qt.io/product/development-tools
- **Qt Project Hosting:** https://codereview.qt-project.org/

