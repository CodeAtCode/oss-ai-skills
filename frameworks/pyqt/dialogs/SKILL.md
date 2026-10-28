---
name: pyqt-dialogs
description: Use when implementing PyQt/PySide6 dialogs - standard dialogs (QFileDialog, QMessageBox, QInputDialog, QColorDialog, QFontDialog), custom QDialog patterns, modal vs modeless dialogs, input validation, Qt 6 dialog APIs
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - qt
    - pyqt
    - pyside
    - dialogs
    - ui
---

# PyQt Dialogs

Standard and custom dialog patterns for PyQt/PySide6 applications.

> **Objective:** Use this skill to reduce modal-deadlock incidents, rejected-input data loss, dialog-sizing regressions, native-vs-custom dialog mismatches by enforcing modal discipline (exec() vs open()), validation-at-boundary rules, and QDialogButtonBox usage patterns.

## Modal vs Modeless Discipline

**Use `exec()` for modal dialogs because** `open()` returns immediately and callers race to access results before the user responds.

**Use `show()` for modeless dialogs because** blocking the UI prevents user interaction with other windows (search dialogs, find/replace).

```python
# ✅ Modal - blocks until user responds
dialog = MyDialog(parent)
if dialog.exec() == QDialog.Accepted:
    values = dialog.get_values()  # Safe: user has already responded

# ❌ BAD - race condition
dialog = MyDialog(parent)
dialog.open()  # Returns immediately
values = dialog.get_values()  # May read stale data before user responds

# ✅ Modeless - stays open, emits signals
dialog = SearchDialog(parent)
dialog.searchRequested.connect(self.perform_search)
dialog.show()  # Non-blocking
```

## Standard Dialogs — Decision Guide

### When to Use Each Dialog Type

- **QFileDialog** — File/directory selection. Use static methods for simple cases; subclass for custom behavior.
- **QMessageBox** — Confirmation, warnings, errors. Use static methods for quick yes/no/information.
- **QInputDialog** — Simple user input (text, number, selection). Use when you need a single value.
- **QColorDialog / QFontDialog** — Color/font selection. Use native dialogs for consistency.
- **Custom QDialog** — Complex input, multi-field forms, multi-page wizards.

### API Reference Relocation

See `references/qfiledialog-apis.md` for QFileDialog static method syntax.
See `references/qmessagebox-apis.md` for QMessageBox button flags and message types.
See `references/qinputdialog-apis.md` for QInputDialog input modes.
See `references/color-font-dialogs.md` for QColorDialog and QFontDialog APIs.

## Custom Dialogs

### Basic Custom Dialog Pattern

**Do subclass QDialog because** standard dialogs cannot handle complex multi-field forms or custom validation logic.

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDialogButtonBox, QFormLayout
)

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.setMinimumWidth(400)  # Prevent undersizing
        
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        form.addRow("Email:", self.email_edit)
        layout.addLayout(form)
        
        # Buttons - use QDialogButtonBox for correct platform ordering
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_values(self):
        return {
            "name": self.name_edit.text(),
            "email": self.email_edit.text()
        }

# Usage
dialog = InputDialog(parent)
if dialog.exec() == QDialog.Accepted:
    values = dialog.get_values()
```

### Validation at Boundary

**Do validate in `try_accept()` before calling `accept()` because** accepted dialogs with invalid data propagate errors downstream and force callers to handle bad state.

```python
class ValidatedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validated Input")
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.email_edit = QLineEdit()
        form.addRow("Age:", self.age_spin)
        form.addRow("Email:", self.email_edit)
        layout.addLayout(form)
        
        # Error label - show validation feedback
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)
        
        # Connect OK button to validation wrapper
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.try_accept)  # NOT self.accept
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    
    def try_accept(self):
        """Validate before accepting — prevents invalid state propagation."""
        if not self.validate():
            return  # Block accept() if validation fails
        self.accept()
    
    def validate(self):
        email = self.email_edit.text()
        if not email:
            self.error_label.setText("Email is required")
            return False
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_label.setText("Invalid email format")
            return False
        
        self.error_label.clear()
        return True
```

### Modeless Dialog Pattern

**Do use signals for modeless dialogs because** the dialog needs to communicate results without blocking the parent or requiring polling.

```python
class SearchDialog(QDialog):
    """Non-modal dialog that stays open and emits results via signals."""
    searchRequested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search")
        # Set window flags for modeless behavior
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(self)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter search term...")
        self.search_edit.returnPressed.connect(self.search)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search)
        
        layout.addWidget(self.search_edit)
        layout.addWidget(self.search_btn)
    
    def search(self):
        term = self.search_edit.text()
        if term:
            self.searchRequested.emit(term)  # Signal result to parent

# Usage
search_dialog = SearchDialog(parent)
search_dialog.searchRequested.connect(parent.perform_search)
search_dialog.show()  # Non-modal — dialog stays open
```

## Best Practices

1. **Use QDialogButtonBox for standard buttons because** it ensures correct button ordering per platform (OK/Cancel order varies by OS).

2. **Always provide Cancel button because** users need an escape path; dialogs without cancel trap users in error states.

3. **Pass parent to all dialogs because** dialogs without parents become orphaned windows that can appear behind main windows or lose modality.

4. **Set minimum size on custom dialogs because** dialogs that are too small truncate content and create poor UX.

5. **Validate before accept() because** downstream code assumes dialog data is valid after QDialog.Accepted.

6. **Use exec() for modal, show() for modeless because** mixing them causes race conditions (exec() blocks, show() doesn't).

## Qt 6 Modern Patterns

### QDialog Setup Pattern

```python
class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QVBoxLayout()
        # ... widgets ...
        
        # Use setLayout() instead of layout = ...; self.setLayout(layout)
        self.setLayout(layout)
        
        # Standard button box
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
```

## Deep Dives

For detailed API reference, see the following files loaded on demand:

- `references/qfiledialog-apis.md` — QFileDialog static methods and options
- `references/qmessagebox-apis.md` — QMessageBox button flags and message types
- `references/qinputdialog-apis.md` — QInputDialog input modes
- `references/color-font-dialogs.md` — QColorDialog and QFontDialog APIs

## References

- **QDialog**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html
- **QFileDialog**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QFileDialog.html
- **QMessageBox**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMessageBox.html
- **Dialogs**: https://doc.qt.io/qtforpython-6/dialogs.html
