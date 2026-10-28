> Loaded on demand from `SKILL.md` when the agent needs QInputDialog input modes and syntax.

# QInputDialog API Reference

## Input Modes

### Get Text
```python
text, ok = QInputDialog.getText(
    parent,
    "Input",
    "Enter name:",
    QLineEdit.EchoMode.Normal,  # Or QLineEdit.EchoMode.Password
    "Default value"
)
```

### Get Integer
```python
value, ok = QInputDialog.getInt(
    parent,
    "Input",
    "Enter age:",
    25,   # Default
    0,    # Min
    120,  # Max
    1     # Step
)
```

### Get Double
```python
price, ok = QInputDialog.getDouble(
    parent,
    "Input",
    "Enter price:",
    0.0,
    0.0,   # Min
    1000.0, # Max
    2      # Decimals
)
```

### Get Item from List
```python
items = ["Option 1", "Option 2", "Option 3"]
item, ok = QInputDialog.getItem(
    parent,
    "Select",
    "Choose an option:",
    items,
    0,    # Current index
    False # Editable
)
```

### Get Multi-line Text
```python
text, ok = QInputDialog.getMultiLineText(
    parent,
    "Input",
    "Enter description:",
    "Default\ntext"
)
```

---
*See official docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QInputDialog.html*
