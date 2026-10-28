> Loaded on demand from `SKILL.md` when the agent needs QMessageBox button flags and message types.

# QMessageBox API Reference

## Standard Message Types
```python
# Question dialog
reply = QMessageBox.question(
    parent,
    "Confirm",
    "Are you sure?",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    QMessageBox.StandardButton.No
)

# Information
QMessageBox.information(parent, "Info", "Operation completed")

# Warning
QMessageBox.warning(parent, "Warning", "This action cannot be undone")

# Critical error
QMessageBox.critical(parent, "Error", "Failed to connect")

# About
QMessageBox.about(parent, "About", "My App v1.0")

# About Qt
QMessageBox.aboutQt(parent)
```

## Custom QMessageBox
```python
msg = QMessageBox(parent)
msg.setWindowTitle("Custom Dialog")
msg.setText("Continue?")
msg.setIcon(QMessageBox.Icon.Question)
msg.addButton("Yes", QMessageBox.ButtonRole.YesRole)
msg.addButton("No", QMessageBox.ButtonRole.NoRole)
msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

result = msg.exec()
```

## Button Roles
- `YesRole` - Yes buttons
- `NoRole` - No buttons
- `RejectRole` - Cancel/Close buttons
- `AcceptRole` - OK buttons
- `HelpRole` - Help buttons

---
*See official docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMessageBox.html*
