---
name: pyqt-styling
description: "Use when styling PyQt/PySide6 widgets with QSS - selectors and pseudo-states, stylesheet application, common style properties, widget-specific styling, or building a dark theme"
metadata:
  author: mte90
  version: 2.1.0
  tags:
    - python
    - qt
    - pyqt
    - pyside
    - styling
    - qss
    - css
    - themes
---

# PyQt Styling - QSS (Qt Style Sheets)

QSS (Qt Style Sheets) is Qt's styling system. It resembles CSS but has critical differences that cause cross-platform bugs.

## QSS Is Not CSS

QSS shares CSS syntax but differs in supported selectors, properties, and cascade behavior. These differences are the source of most cross-platform bugs.

### Unsupported or Different Selectors

| Selector | CSS | QSS |
|----------|-----|-----|
| `::pseudo-element` | Supported (e.g., `::before`, `::after`) | Limited support - only Qt-specific pseudo-elements like `::indicator`, `::drop-down`, `::item` |
| Descendant selector (`A B`) | Matches nested elements | **Does not work** in most widgets - Qt uses parent-to-child cascade instead |
| Child selector (`A > B`) | Matches direct children | Partially supported, but widget hierarchy matters more than DOM-like nesting |
| Sibling selector (`A + B`, `A ~ B`) | Supported | **Not supported** - widgets don't have sibling relationships like DOM |
| Attribute selectors (`[attr]`) | Full support | Supported via `setProperty()` but syntax differs (`[attr="value"]` works) |
| Class selector (`.my-class`) | Supported | **Not supported** - use `objectName` or custom properties instead |

### Properties Qt Ignores

Qt silently ignores CSS properties it doesn't implement:

- `box-shadow` - Qt uses custom properties or `qproperty-` prefix instead
- `text-shadow` - Not implemented
- `filter` - Not implemented (use `QGraphicsEffect` instead)
- `transform` - Not implemented (use widget geometry methods)
- `position: absolute/fixed` - Qt uses layouts or manual geometry
- `display: flex/grid` - Qt uses QLayout classes, not CSS display
- `::before`, `::after` - Not supported (use child widgets instead)

### Border-Radius Clipping Issue

`border-radius` on a parent widget **does not clip child widgets** unless the parent sets a mask:

```python
# Bad - children overflow rounded corners
parent.setStyleSheet("border-radius: 10px;")
parent.addWidget(child)  # child shows outside rounded area

# Good - use a mask
from PySide6.QtGui import QRegion
from PySide6.QtCore import QRect

parent.setMask(QRegion(QRect(0, 0, parent.width(), parent.height()), QRegion.Ellipse))
# Or use a custom paintEvent for rounded rectangle mask
```

### Cascade Behavior

Widgets cascade styles from parent to child differently from the DOM:

- **DOM**: Styles cascade through the document tree based on selector specificity
- **Qt**: Styles applied to a parent widget propagate to children **only if** the child has no explicit stylesheet
- **Key difference**: Setting `app.setStyleSheet()` applies globally, but `parent.setStyleSheet()` only affects children that don't have their own stylesheet set

```python
# Bad - child overrides parent
app.setStyleSheet("QPushButton { background: blue; }")
child_button.setStyleSheet("")  # Empty string clears inherited style

# Good - use custom properties for theming
app.setStyleSheet("QPushButton { background: $primary-color; }")
child_button.setProperty("primary-color", "#0078d4")
child_button.style().polish(child_button)
```

## Platform Differences

The same QSS renders differently across Windows, macOS, and Linux due to native widget rendering.

### Default Widget Metrics

- **Font sizes**: macOS uses larger default fonts; Windows uses smaller
- **Padding**: Native look varies - macOS buttons have more padding, Windows has less
- **Line heights**: Not consistent across platforms

**Fix**: Use explicit `min-height`, `padding` on critical widgets rather than relying on defaults.

### Native-Appearance Opt-Out

Qt widgets may render with native platform styling that ignores QSS:

```python
# Force QSS rendering on Windows/macOS
widget.setAttribute(Qt.WidgetAttribute.WA_StyleSheet)

# For QComboBox dropdown - native rendering ignores QSS
combo.setStyleSheet("QComboBox::drop-down { border: none; }")
combo.view().setAttribute(Qt.WidgetAttribute.WA_StyleSheet)
```

### High-DPI Scaling

QSS uses device-independent pixels, but scaling behavior varies:

```python
# Set high-DPI scaling policy (Qt 6)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

app = QApplication(sys.argv)
app.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

**Verification on a platform you don't have**: Use Qt's remote desktop or CI services (GitHub Actions with Xvfb), or test in a VM with the target OS.

## Theming Discipline

### Tokenize Your Theme

A theme should be a single QSS source with placeholder/palette substitution, not per-widget stylesheets:

```python
# Bad - per-widget stylesheets
class MainWindow(QMainWindow):
    def __init__(self):
        self.button1.setStyleSheet("background: #0078d4;")
        self.button2.setStyleSheet("background: #0078d4;")
        self.label.setStyleSheet("color: #333;")

# Good - tokenized theme
class Theme:
    @staticmethod
    def apply(app):
        app.setStyleSheet("""
            QPushButton { background-color: $primary; }
            QLabel { color: $text-primary; }
        """.replace("$primary", "#0078d4").replace("$text-primary", "#333"))

# Or use a palette
from PySide6.QtGui import QPalette, QColor

class Theme:
    @staticmethod
    def apply_dark(app):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        app.setPalette(palette)
```

### Test a Theme Change Across Widget Types

Create a gallery page to verify theme changes:

```python
class ThemeGallery(QWidget):
    def __init__(self):
        super().__init__()
        # Create one of each widget type
        self.buttons = [QPushButton(f"Button {i}") for i in range(3)]
        self.inputs = [QLineEdit(f"Input {i}") for i in range(3)]
        self.labels = [QLabel(f"Label {i}") for i in range(3)]
        # Layout them all
        # Switch themes with a button to verify consistency
```

### When to Use Custom paintEvent/Delegates

Use custom painting instead of fighting QSS when:

- You need gradients, shadows, or complex shapes QSS can't express
- You need per-pixel control (e.g., custom progress bar animation)
- QSS performance is poor with many widgets
- You need platform-independent rendering (QSS varies by platform)

```python
class RoundedButton(QPushButton):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Custom rounded rectangle with gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, "#0078d4")
        gradient.setColorAt(1, "#106ebe")
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
```

## Basic Syntax (Quick Reference)

Assumes familiarity with CSS selectors and specificity. Focuses on Qt-specific syntax.

## Applying Styles

### Application-Wide

```python
from PySide6.QtWidgets import QApplication

app = QApplication()

# Inline
app.setStyleSheet("""
    QLabel { color: #333; }
    QPushButton { padding: 5px 10px; }
""")

# From file
with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())
```

### Widget-Specific

```python
button = QPushButton("Styled")
button.setStyleSheet("""
    QPushButton {
        background-color: blue;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: darkblue;
    }
""")
```

### Custom Properties

```python
# Set custom property
button = QPushButton("Primary")
button.setProperty("primary", True)

# Force style refresh
button.style().unpolish(button)
button.style().polish(button)
```

```css
/* Use in QSS */
QPushButton[primary="true"] {
    background-color: #0078d4;
    color: white;
}

QPushButton[primary="true"]:hover {
    background-color: #106ebe;
}
```

## Widget-Specific Styles

### QPushButton

```css
QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

/* Flat button */
QPushButton[flat="true"] {
    background-color: transparent;
    color: #0078d4;
    border: 1px solid #0078d4;
}
```

### QLineEdit

```css
QLineEdit {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: #0078d4;
}

QLineEdit:focus {
    border: 2px solid #0078d4;
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #999999;
}

/* Password field */
QLineEdit[echoMode="2"] {
    lineedit-password-character: 9679;  /* Unicode bullet */
}
```

### QComboBox

```css
QComboBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
}

QComboBox:hover {
    border-color: #999999;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

/* Dropdown list */
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #cccccc;
    selection-background-color: #0078d4;
}
```

### QTabWidget

```css
QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #f5f5f5;
    border: 1px solid #cccccc;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom-color: white;
}

QTabBar::tab:hover {
    background-color: #e5e5e5;
}
```

### QScrollBar

```css
/* Vertical scrollbar */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #999999;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
```

## Deep Dives

- **Dark Theme Example**: See [references/dark-theme.md](references/dark-theme.md) for a complete VS Code-inspired dark theme stylesheet.

## Best Practices

1. **Tokenize themes** - Single QSS source with placeholder substitution, not per-widget stylesheets
2. **Test on all platforms** - Colors, fonts, and native rendering vary significantly
3. **Use custom properties** - `setProperty()` for theme variables instead of hardcoding colors
4. **Prefer delegates for complex rendering** - Don't fight QSS for gradients, animations, or platform-independent drawing
5. **Verify border-radius clipping** - Use masks or custom paintEvent if children must respect rounded corners
6. **Block signals during bulk updates** - `widget.blockSignals(True)` before batch changes, then `blockSignals(False)`

## References

- **Qt Style Sheets**: https://doc.qt.io/qtforpython-6/overviews/stylesheet.html
- **QSS Reference**: https://doc.qt.io/qtforpython-6/overviews/stylesheet-reference.html
- **Qt Examples**: https://doc.qt.io/qtforpython-6/overviews/stylesheet-examples.html
