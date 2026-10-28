---
name: pyqt-core
description: Use when working with PyQt/PySide6 QtCore - signals, slots, properties, timers, settings, file I/O
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - qt
    - pyqt
    - pyside
    - core
    - signals
    - slots
---

> **Objective:** Use this skill to reduce missed signal/slot connections, wrong connection-type crashes, QSettings scope mismatches, and timer leak incidents by enforcing connection-type rules for cross-thread communication, queue-aware patterns for worker threads, scope discipline for QSettings groups/arrays, and timer lifecycle checks with parent ownership.

# PyQt Core - QtCore Module

QtCore provides core non-GUI functionality: signals/slots, timers, settings, and file I/O.

## Critical Rules (Do X Because Y)

### 1. Use QueuedConnection for Cross-Thread Signals

**Do** use `Qt.QueuedConnection` when emitting signals from worker threads to UI slots because direct connections execute in the emitter's thread, causing crashes when slots access thread-unsafe UI objects.

```python
from PySide6.QtCore import Qt, QObject, Signal, QThread

class Worker(QThread):
    dataReady = Signal(dict)  # Declared in worker thread
    
    def run(self):
        data = self.expensiveOperation()
        self.dataReady.emit(data, Qt.QueuedConnection)  # Queue to UI thread

class MainWindow(QWidget):
    def setupWorker(self):
        self.worker = Worker()
        self.worker.dataReady.connect(self.handleData, Qt.QueuedConnection)
        self.worker.start()
```

**Failure mode:** Segmentation fault or Qt runtime error "QMetaObject::invokeMethod: Unable to unmarshal value" when DirectConnection crosses thread boundary.

### 2. Block Signals During Batch Updates

**Do** call `blockSignals(True)` before batch updates because each signal emission triggers connected slots, causing redundant processing and performance degradation.

```python
def populateTable(self, items):
    self.table.blockSignals(True)
    try:
        self.table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(item))
    finally:
        self.table.blockSignals(False)
```

**Failure mode:** Slot called N times for N row additions instead of once after batch complete.

### 3. Use Parent Ownership for Timers

**Do** pass parent to `QTimer(parent)` because parent ownership ensures automatic cleanup on widget destruction, preventing timer leaks and crashes from dangling timer references.

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)  # Self is parent - auto-cleanup
        self.timer.timeout.connect(self.onTimeout)
```

**Failure mode:** Timer continues firing after widget destroyed → crash on slot access.

### 4. Provide Defaults When Reading Settings

**Do** provide default values in `settings.value(key, default)` because missing keys return `None` without defaults, causing type errors downstream.

```python
# Safe - returns int 12 if key missing
font_size = settings.value("editor/fontSize", 10, type=int)

# Unsafe - returns None if missing, crashes on int comparison
font_size = settings.value("editor/fontSize")  # type: ignore
```

**Failure mode:** `TypeError: '>' not supported between instances of 'NoneType' and 'int'`.

### 5. Use IniFormat for Portable Settings

**Do** use `QSettings.IniFormat` for cross-platform config files because NativeFormat stores in platform-specific locations (Windows registry, macOS plist), making settings non-portable.

```python
# Portable - same file on all platforms
settings = QSettings("config.ini", QSettings.IniFormat)

# Platform-specific - different storage per OS
settings = QSettings("MyCompany", "MyApp")  # Native format
```

**Failure mode:** Settings appear "lost" when moving between platforms or after OS reinstall.

### 6. End Groups/Arrays in Finally Blocks

**Do** wrap `beginGroup/endGroup` and `beginWriteArray/endArray` in try-finally because exceptions leave settings in incomplete state, corrupting the file.

```python
def saveSettings(self):
    settings = QSettings("config.ini", QSettings.IniFormat)
    try:
        settings.beginGroup("editor")
        settings.setValue("fontSize", 12)
        settings.endGroup()
    finally:
        settings.endGroup()  # Ensures cleanup even on error
```

**Failure mode:** Corrupted INI file with unclosed groups preventing future reads.

### 7. Stop Timers Before Destruction

**Do** explicitly stop timers in `closeEvent` because while parent ownership handles cleanup, stopping timers prevents late emissions during destruction sequence.

```python
def closeEvent(self, event):
    self.timer.stop()  # Stop before parent cleanup
    super().closeEvent(event)
```

**Failure mode:** Timer fires during widget teardown → slot accesses destroyed objects.

### 8. Check File Existence Before Operations

**Do** check `QFile.exists()` before read operations because `open()` silently fails on missing files, causing data loss if write mode is used accidentally.

```python
if QFile.exists("data.txt"):
    file = QFile("data.txt")
    if file.open(QIODevice.ReadOnly):
        data = file.readAll()
        file.close()
else:
    logger.warning("Data file not found, using defaults")
```

**Failure mode:** Silent data loss when file missing and code proceeds with empty data.

## Signal/Slot Reference

See `references/signals-slots.md` for complete signal declaration, slot declaration, and connection syntax.

## QTimer Reference

See `references/timers.md` for complete timer API including single-shot, periodic, and timer properties.

## QSettings Reference

See `references/settings.md` for complete settings API including groups, arrays, and format options.

## File I/O Reference

See `references/file-io.md` for complete file operations including QFile, QTextStream, and QDir.

## Deep Dives

- `references/signals-slots.md` - Signal/slot syntax, connection types, best practices
- `references/timers.md` - QTimer API, single-shot vs periodic, timer types
- `references/settings.md` - QSettings API, groups, arrays, formats
- `references/file-io.md` - QFile, QTextStream, QDir operations

## References

- **Qt for Python QtCore**: https://doc.qt.io/qtforpython-6/PySide6/QtCore/
- **Signals and Slots**: https://doc.qt.io/qtforpython-6/signalsslot.html
- **QTimer**: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTimer.html
- **QSettings**: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html
- **QFile**: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QFile.html
