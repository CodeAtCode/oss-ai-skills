---
name: pyqt-widgets
description: Use when building PyQt/PySide6 UIs with QtWidgets - display, input and container widgets, buttons, item views like QListWidget and QTableWidget, layout management, or event handling (mouse/keyboard events, event filters, shortcuts)
metadata:
  author: mte90
  version: 3.0.0
  tags:
    - python
    - qt
    - pyqt
    - pyside
    - widgets
    - gui
    - layouts
---

> **Objective:** Use this skill to reduce layout-breakage incidents (setGeometry + resize conflicts), event-handler bugs (missed accept()/ignore() calls), model-view sync failures (stale item references), and keyboard-shortcut conflicts (global filter overuse) by enforcing layout discipline, event-filter patterns, and model-view contract rules below.

# PyQt Widgets - QtWidgets Module

## Widget Selection Guide

### Display Widgets

**QLabel** - Use for showing text or images. Choose when:
- Displaying static text with optional rich text formatting
- Showing images with scaling control
- Creating clickable links (use `setOpenExternalLinks(True)`)

**Pitfall**: Don't use QLabel for editable content - use QLineEdit or QTextEdit instead.

See [widgets-api.md](references/widgets-api.md) for complete QLabel API.

**QProgressBar** - Use for visual progress indication. Choose when:
- Showing operation completion percentage (set range 0-100)
- Indeterminate mode for unknown duration (`setRange(0, 0)`)

**Pitfall**: Don't forget to update the value asynchronously for long operations.

See [widgets-api.md](references/widgets-api.md) for complete QProgressBar API.

**QLCDNumber** - Use for numeric display with digital appearance. Choose when:
- Showing numeric values with visual emphasis
- Need hex/octal/binary display modes

**Pitfall**: Limited use cases - most numeric displays are better with QLabel.

See [widgets-api.md](references/widgets-api.md) for complete QLCDNumber API.

### Input Widgets

**QLineEdit** - Use for single-line text input. Choose when:
- Collecting short text (names, search queries)
- Password input (`setEchoMode(Password)`)
- Validated input with `QValidator` subclasses

**Pitfall**: Don't use for multi-line text - use QTextEdit instead.

See [widgets-api.md](references/widgets-api.md) for complete QLineEdit API.

**QTextEdit** - Use for multi-line rich text editing. Choose when:
- Editing paragraphs or formatted content
- Need undo/redo support
- Displaying HTML content

**Pitfall**: Plain text operations use `toPlainText()`/`setPlainText()`, HTML uses `toHtml()`/`setHtml()` - don't mix.

See [widgets-api.md](references/widgets-api.md) for complete QTextEdit API.

**QSpinBox/QDoubleSpinBox** - Use for numeric input with constraints. Choose when:
- Integer values (QSpinBox) or decimals (QDoubleSpinBox)
- Need bounded range with step increments
- User should not type invalid values

**Pitfall**: Don't forget to set reasonable min/max values to prevent overflow.

See [widgets-api.md](references/widgets-api.md) for complete spin box API.

**QComboBox** - Use for dropdown selection. Choose when:
- Limited set of mutually exclusive options
- Space is constrained (collapses when not in use)
- Need editable mode for "type or select"

**Pitfall**: Use `currentIndexChanged` for index changes, `currentTextChanged` for text changes - they fire separately.

See [widgets-api.md](references/widgets-api.md) for complete QComboBox API.

**QCheckBox** - Use for boolean or tristate options. Choose when:
- Single on/off setting
- Need tristate (checked/unchecked/partiallyChecked)
- Group of independent options (not exclusive)

**Pitfall**: `stateChanged` fires for all three states in tristate mode; `toggled` only for checked/unchecked.

See [widgets-api.md](references/widgets-api.md) for complete QCheckBox API.

**QRadioButton** - Use for mutually exclusive selection. Choose when:
- User must pick exactly one option from a set
- Options are visible simultaneously (unlike QComboBox)

**Pitfall**: Group radio buttons with QButtonGroup or same parent for exclusivity.

See [widgets-api.md](references/widgets-api.md) for complete QRadioButton API.

**QSlider** - Use for continuous or stepped value selection. Choose when:
- Visual representation of range matters (volume, brightness)
- User should see current position at a glance
- Need coarse + fine control (page step + single step)

**Pitfall**: Don't use for precise input - pair with QSpinBox for exact value display.

See [widgets-api.md](references/widgets-api.md) for complete QSlider API.

### Buttons

**QPushButton** - Use for command execution. Choose when:
- Triggering an action (submit, cancel, save)
- Need icon + text combination
- Want context menu (`setMenu()`)

**Pitfall**: Use `clicked` for action, `pressed`/`released` for visual feedback control.

See [widgets-api.md](references/widgets-api.md) for complete QPushButton API.

**QToolButton** - Use for toolbar or compact icon buttons. Choose when:
- Space-efficient icon buttons needed
- Toolbar or palette layout
- Auto-raise for hover effect

**Pitfall**: Not ideal for main action buttons - use QPushButton for primary actions.

See [widgets-api.md](references/widgets-api.md) for complete QToolButton API.

### Container Widgets

**QGroupBox** - Use for visual grouping of related controls. Choose when:
- Settings or options need visual separation
- Group should be toggleable (`setCheckable(True)`)

**Pitfall**: Remember to add a layout to the group box, not just widgets.

See [widgets-api.md](references/widgets-api.md) for complete QGroupBox API.

**QTabWidget** - Use for tabbed interfaces. Choose when:
- Multiple panels of content need switching
- Want to save vertical space
- Each tab represents a distinct mode/view

**Pitfall**: Use `currentChanged` to react to tab switches; don't store state in tab widgets directly.

See [widgets-api.md](references/widgets-api.md) for complete QTabWidget API.

**QScrollArea** - Use for scrolling content. Choose when:
- Content exceeds visible area
- Need to scroll a widget (not raw content)

**Pitfall**: Always set `setWidgetResizable(True)` unless you need precise scroll control.

See [widgets-api.md](references/widgets-api.md) for complete QScrollArea API.

**QSplitter** - Use for resizable panes. Choose when:
- User should control panel sizes (editor + preview)
- Need horizontal or vertical split
- Want to remember sizes (save `getSizes()` on exit)

**Pitfall**: Set `setChildrenCollapsible(False)` if a pane must have minimum content.

See [widgets-api.md](references/widgets-api.md) for complete QSplitter API.

**QStackedWidget** - Use for page-based navigation. Choose when:
- Multiple views, one visible at a time
- Wizard-style step progression
- Tab content that doesn't need tab bar (control via code)

**Pitfall**: Use `setCurrentIndex()` or `setCurrentWidget()` - don't rely on user navigation.

See [widgets-api.md](references/widgets-api.md) for complete QStackedWidget API.

## Layout Discipline

**Do use layouts, not setGeometry, because resize events break fixed positions.**

```python
# ✅ GOOD: Layouts adapt to resize
layout = QVBoxLayout()
layout.addWidget(button)
layout.setStretchFactor(widget, 1)  # Proportional sizing
```

```python
# ❌ BAD: Hardcoded positions fail on resize
button.setGeometry(10, 10, 100, 30)
```

**Do set size policies instead of fixed sizes because layouts need growth hints.**

```python
from PySide6.QtWidgets import QSizePolicy

widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
```

## Event Handling

See references/event-handling.md for event handlers, event filters, and shortcuts.

**Do call event.accept() in handlers because unaccepted events propagate up the tree.**

```python
class MyWidget(QWidget):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("Left click at", event.pos())
        event.accept()  # Stop propagation
```

**Do call event.ignore() in closeEvent because ignoring keeps the widget open.**

```python
def closeEvent(self, event):
    reply = QMessageBox.question(
        self, 'Exit',
        'Are you sure?',
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        event.accept()
    else:
        event.ignore()  # Widget stays open
```

**Do install event filters on specific targets because global filters intercept every event and kill performance.**

```python
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.textEdit.installEventFilter(self)  # Target-specific
    
    def eventFilter(self, obj, event):
        if obj == self.textEdit and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                return True  # Consumed
        return super().eventFilter(obj, event)
```

## Model-View Contract

See references/item-views-layouts.md for QListWidget, QTreeWidget, QTableWidget, and layout management.

**Do use data() / setData() for custom data because text() only stores display strings.**

```python
item.setData(Qt.ItemDataRole.UserRole, {"id": 123})
data = item.data(Qt.ItemDataRole.UserRole)
```

**Do check for None before accessing table items because empty cells return None.**

```python
item = table.item(0, 0)
text = item.text() if item else ""  # Avoid crash on empty cell
```

## State Management

**Do centralize state in a dedicated class because scattered widget state creates sync bugs.**

```python
class AppState:
    def __init__(self):
        self.data_changed = Signal()
        
state = AppState()
# Connect to signal for updates
```

## Deep Dives

See references for detailed content loaded on demand:
- [Item Views and Layouts](references/item-views-layouts.md) - QListWidget, QTreeWidget, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QStackedLayout
- [Event Handling](references/event-handling.md) - Event handlers, event filters, keyboard/mouse shortcuts

## References

- **Qt for Python Widgets**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/
- **Widget Gallery**: https://doc.qt.io/qtforpython-6/widgetgallery.html
- **Layout Management**: https://doc.qt.io/qtforpython-6/layouts.html
