> Loaded on demand from SKILL.md when the agent needs PySide6/PyQt6 registration syntax or signal/slot patterns.

# Python Backend Reference

## PySide6 vs PyQt6 Comparison

| Feature | PySide6 | PyQt6 |
|---------|---------|-------|
| Signal | `Signal` | `pyqtSignal` |
| Slot | `Slot` | `pyqtSlot` |
| Property | `Property` | `pyqtProperty` |
| License | LGPL | GPL |
| QML Registration | `@QmlElement` decorator | `qmlRegisterType()` |

## PySide6 Registration

```python
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "com.example.widget"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class WidgetBackend(QObject):
    pass
```

## PyQt6 Registration

```python
from PyQt6.QtQml import qmlRegisterType

qmlRegisterType(WidgetBackend, "com.example.widget", 1, 0, "WidgetBackend")
```
