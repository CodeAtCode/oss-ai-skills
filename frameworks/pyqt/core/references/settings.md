> Loaded on demand from `SKILL.md` when the agent needs complete QSettings API reference.

# QSettings Reference

## Basic Usage

```python
from PySide6.QtCore import QSettings

# Create settings (uses app name from QApplication)
settings = QSettings("MyCompany", "MyApp")

# Write values
settings.setValue("window/geometry", self.saveGeometry())
settings.setValue("window/state", self.saveState())
settings.setValue("editor/fontSize", 12)
settings.setValue("editor/fontFamily", "Monospace")

# Read values
geometry = settings.value("window/geometry")
font_size = settings.value("editor/fontSize", 10)  # Default 10
font_family = settings.value("editor/fontFamily", "Consolas")

# Check if key exists
if settings.contains("editor/theme"):
    theme = settings.value("editor/theme")

# Remove key
settings.remove("editor/temp")

# Clear all
settings.clear()
```

## Settings Groups

```python
settings = QSettings("MyCompany", "MyApp")

# Using beginGroup/endGroup
settings.beginGroup("editor")
settings.setValue("fontSize", 12)
settings.setValue("fontFamily", "Monospace")
settings.endGroup()

# Using array
settings.beginWriteArray("recentFiles")
for i, filepath in enumerate(recent_files):
    settings.setArrayIndex(i)
    settings.setValue("path", filepath)
settings.endArray()

# Read array
size = settings.beginReadArray("recentFiles")
for i in range(size):
    settings.setArrayIndex(i)
    path = settings.value("path")
settings.endArray()
```

## Settings Format

```python
from PySide6.QtCore import QSettings

# Native format (registry on Windows, plist on macOS, conf on Linux)
settings = QSettings("MyCompany", "MyApp")

# INI file format
settings = QSettings("config.ini", QSettings.IniFormat)

# Custom file location
settings = QSettings("/path/to/settings.conf", QSettings.IniFormat)

# Get file path
print(settings.fileName())
```
