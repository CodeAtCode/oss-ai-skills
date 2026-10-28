---
name: kde-plasmoid
description: Use when building KDE Plasma 6 widgets with a Python backend - plasmoid structure, metadata.json, QML UI, configuration system, plasmapkg2 packaging, KDE Store submission, or plasmoid testing and debugging
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - kde
    - plasma
    - plasmoid
    - widget
    - qml
    - qt
    - desktop
---

> **Objective:** Use this skill to reduce plasmoid-load failures, metadata-schema rejections, QML-binding-loop freezes, and packaging errors by enforcing metadata-discipline, QML-lifecycle rules, and plasmapkg2-verification patterns below.

# KDE Plasmoid Development with Python

Build Plasma 6 widgets with Python backend + QML UI.

**Important**: Native Python Plasmoids (PyKDE4/PyKDE5) are deprecated in Plasma 6. Use QML UI + Python backend via QObject.

See `references/plasmoid-structure.md` for complete structure, metadata.json schema, and dependency listings.

## Python Backend Rules

**Do subclass QObject** because QML requires QObject-derived types for property/signal exposure.

**Do emit signals after property changes** because QML bindings only update on signal emission:
```python
dataUpdated = Signal()

@Property(str, notify=dataUpdated)
def data(self):
    return self._data

@data.setter
def data(self, value):
    if self._data != value:
        self._data = value
        self.dataUpdated.emit()  # ← Required for QML update
```

**Do use @Slot for QML-callable methods** because unmarked methods may fail cross-language calls.

**Do initialize all properties in __init__** because QML accesses properties before any other initialization.

See `references/python-backend.md` for PySide6/PyQt6 registration syntax and signal/slot patterns.

## QML UI Rules

**Do use Kirigami units for all sizing** because hardcoded values break HiDPI scaling:
```qml
// ✅ GOOD
width: Kirigami.Units.gridUnit * 10
spacing: Kirigami.Units.smallSpacing

// ❌ BAD - Won't scale on HiDPI
width: 320
```

**Do provide fallback values for configuration** because missing config keys return undefined:
```qml
text: plasmoid.configuration.customLabel || "Default"
```

**Do use `Plasmoid.fullRepresentation` for expanded view** because Plasma routes expanded clicks there.

**Do use `Plasmoid.compactRepresentation` for panel mode** because panel widgets need compact UI.

**Do use Plasma 6 imports (no version for plasmoid/core)** because versioned imports break on Plasma 6:
```qml
import org.kde.plasma.plasmoid           // ✅ No version
import org.kde.plasma.components 3.0     // ✅ Components need version
import org.kde.plasma.core 2.0           // ✅ Core needs version
import org.kde.kirigami 2.0              // ✅ Kirigami needs version
```

See `references/qml-ui.md` for complete main.qml template and representation patterns.

## Best Practices

**Do use signal-based updates** because polling wastes CPU cycles:
```python
class Backend(QObject):
    dataChanged = Signal()
    
    def updateData(self):
        self._data = compute()
        self.dataChanged.emit()  # ← Notify QML only when changed
```

**Do use lazy initialization for expensive data** because repeated computation freezes the UI:
```python
@Slot(result=str)
def expensiveData(self):
    if not hasattr(self, '_cached'):
        self._cached = self._computeExpensive()
    return self._cached
```

**Do use QTimer for periodic updates** because manual loops block the event loop:
```python
self._timer = QTimer()
self._timer.timeout.connect(self.refresh)
self._timer.start(60000)  # 60 seconds
```

**Do avoid blocking the main thread** because QML waits for slot completion:
```python
# ❌ BAD - Blocks UI for 5 seconds
@Slot(result=str)
def slowOperation(self):
    time.sleep(5)  # Freezes widget!
```

**Do avoid implicit QML bindings on heavy properties** because binding loops freeze the widget:
```qml
// ❌ BAD - Re-evaluates on every frame
width: computeExpensiveWidth()  // Called constantly!

// ✅ GOOD - Evaluates once, updates on signal
width: backend.calculatedWidth
```

## Deep Dives

Refer to these on-demand reference files for detailed topics:

- **Configuration System** — `references/configuration.md`: metadata.json schema, KCFG main.xml, config.qml, configGeneral.qml, property aliases with cfg_ prefix
- **Packaging & Publishing** — `references/packaging-publishing.md`: plasmapkg2 CLI, .plasmoid package creation, local/system deployment, KDE Store submission workflow
- **Testing & Debugging** — `references/testing-debugging.md`: plasmoidtest tool, exit codes, troubleshooting guide, unit/integration tests, debug logging

## References

- [Plasma Widget Tutorial](https://develop.kde.org/docs/plasma/widget/)
- [Porting to KF6](https://develop.kde.org/docs/plasma/widget/porting_kf6/)
- [Python + Kirigami](https://develop.kde.org/docs/getting-started/python/)
- [QML API Reference](https://develop.kde.org/docs/plasma/widget/plasma-qml-api/)
- [KDE Store](https://store.kde.org/)
- [Kirigami Documentation](https://develop.kde.org/docs/kirigami/)
- [plasmapkg2 Tool](https://apps.kde.org/plasmapkg2/)
