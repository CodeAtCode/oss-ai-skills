> Loaded on demand from `SKILL.md` when the agent needs QColorDialog or QFontDialog API syntax.

# Color and Font Dialog APIs

## QColorDialog
```python
from PySide6.QtWidgets import QColorDialog
from PySide6.QtGui import QColor

# Get color
color = QColorDialog.getColor(
    QColor(255, 0, 0),  # Default color
    parent,
    "Select Color"
)

if color.isValid():
    print(f"Color: {color.name()}")  # "#ff0000"

# With alpha channel
color = QColorDialog.getColor(
    QColor(255, 0, 0, 128),
    parent,
    "Select Color with Alpha",
    QColorDialog.ColorDialogOption.ShowAlphaChannel
)

# With multiple options
options = (
    QColorDialog.ColorDialogOption.ShowAlphaChannel |
    QColorDialog.ColorDialogOption.NoButtons
)
color = QColorDialog.getColor(Qt.white, parent, "Color", options)
```

## QFontDialog
```python
from PySide6.QtWidgets import QFontDialog
from PySide6.QtGui import QFont

# Get font
font, ok = QFontDialog.getFont(
    QFont("Arial", 12),  # Default font
    parent,
    "Select Font"
)

if ok:
    print(f"Font: {font.family()}, Size: {font.pointSize()}")

# With options
font, ok = QFontDialog.getFont(
    QFont(),
    parent,
    "Select Font",
    QFontDialog.FontDialogOption.MonospacedFonts
)
```

---
*See official docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QColorDialog.html*
*See official docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QFontDialog.html*
